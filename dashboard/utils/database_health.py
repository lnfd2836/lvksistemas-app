"""
Utilitários para verificação de saúde do banco de dados.
"""
import logging
from django.db import connection, connections
from django.core.management import execute_from_command_line
from django.core.management.base import CommandError
from django.conf import settings
import time
import sys
from io import StringIO

logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """
    Classe para verificar a saúde e conectividade do banco de dados.
    """
    
    @staticmethod
    def check_database_connectivity():
        """
        Verifica se o banco de dados está acessível e funcionando.
        
        Returns:
            dict: Informações sobre o status do banco de dados
        """
        health_info = {
            'status': 'unknown',
            'connection_time': None,
            'queries_working': False,
            'migrations_pending': False,
            'errors': [],
            'details': {}
        }
        
        try:
            # Testa tempo de conexão
            start_time = time.time()
            
            with connection.cursor() as cursor:
                # Teste básico de conectividade
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                if result and result[0] == 1:
                    health_info['queries_working'] = True
                    health_info['connection_time'] = time.time() - start_time
                    health_info['status'] = 'connected'
                    
            # Verifica informações da conexão
            health_info['details'] = {
                'vendor': connection.vendor,
                'database_name': connection.settings_dict.get('NAME', 'unknown'),
                'engine': connection.settings_dict.get('ENGINE', 'unknown'),
                'queries_count': len(connection.queries) if settings.DEBUG else 'N/A'
            }
            
            # Verifica migrações pendentes
            health_info['migrations_pending'] = DatabaseHealthChecker.check_pending_migrations()
            
        except Exception as e:
            health_info['status'] = 'error'
            health_info['errors'].append(f"Erro de conectividade: {str(e)}")
            logger.error(f"Erro ao verificar conectividade do banco: {e}")
            
        return health_info
    
    @staticmethod
    def check_pending_migrations():
        """
        Verifica se existem migrações pendentes.
        
        Returns:
            bool: True se existem migrações pendentes
        """
        try:
            # Captura a saída do comando showmigrations
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
                output = captured_output.getvalue()
                
                # Verifica se há migrações não aplicadas (linhas que começam com [ ])
                pending_migrations = []
                for line in output.split('\n'):
                    if line.strip().startswith('[ ]'):
                        pending_migrations.append(line.strip())
                
                return len(pending_migrations) > 0
                
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            logger.error(f"Erro ao verificar migrações pendentes: {e}")
            return False
    
    @staticmethod
    def test_critical_queries():
        """
        Testa queries críticas do sistema para verificar se estão funcionando.
        
        Returns:
            dict: Resultados dos testes de queries
        """
        query_tests = {
            'user_count': {'status': 'unknown', 'result': None, 'error': None},
            'loja_count': {'status': 'unknown', 'result': None, 'error': None},
            'session_count': {'status': 'unknown', 'result': None, 'error': None},
        }
        
        try:
            from django.contrib.auth.models import User
            from lojas.models import Loja
            from usuarios.models import SessaoAtiva
            
            # Teste 1: Contagem de usuários
            try:
                user_count = User.objects.count()
                query_tests['user_count']['status'] = 'success'
                query_tests['user_count']['result'] = user_count
            except Exception as e:
                query_tests['user_count']['status'] = 'error'
                query_tests['user_count']['error'] = str(e)
            
            # Teste 2: Contagem de lojas
            try:
                loja_count = Loja.objects.count()
                query_tests['loja_count']['status'] = 'success'
                query_tests['loja_count']['result'] = loja_count
            except Exception as e:
                query_tests['loja_count']['status'] = 'error'
                query_tests['loja_count']['error'] = str(e)
            
            # Teste 3: Contagem de sessões ativas
            try:
                session_count = SessaoAtiva.objects.filter(ativa=True).count()
                query_tests['session_count']['status'] = 'success'
                query_tests['session_count']['result'] = session_count
            except Exception as e:
                query_tests['session_count']['status'] = 'error'
                query_tests['session_count']['error'] = str(e)
                
        except ImportError as e:
            logger.error(f"Erro ao importar modelos para teste: {e}")
            for test in query_tests.values():
                test['status'] = 'error'
                test['error'] = f"Import error: {str(e)}"
        
        return query_tests
    
    @staticmethod
    def get_database_performance_info():
        """
        Obtém informações de performance do banco de dados.
        
        Returns:
            dict: Informações de performance
        """
        performance_info = {
            'slow_queries': [],
            'total_queries': 0,
            'average_query_time': 0,
            'connection_pool_info': {}
        }
        
        try:
            if settings.DEBUG and hasattr(connection, 'queries'):
                queries = connection.queries
                performance_info['total_queries'] = len(queries)
                
                if queries:
                    # Calcula tempo médio das queries
                    total_time = sum(float(q.get('time', 0)) for q in queries)
                    performance_info['average_query_time'] = total_time / len(queries)
                    
                    # Identifica queries lentas (> 0.1 segundos)
                    slow_queries = [q for q in queries if float(q.get('time', 0)) > 0.1]
                    performance_info['slow_queries'] = slow_queries[:5]  # Primeiras 5
            
            # Informações do pool de conexões (se disponível)
            try:
                db_config = settings.DATABASES.get('default', {})
                performance_info['connection_pool_info'] = {
                    'max_connections': db_config.get('CONN_MAX_AGE', 'N/A'),
                    'engine': db_config.get('ENGINE', 'unknown'),
                }
            except Exception as e:
                performance_info['connection_pool_info']['error'] = str(e)
                
        except Exception as e:
            logger.error(f"Erro ao obter informações de performance: {e}")
            performance_info['error'] = str(e)
        
        return performance_info
    
    @staticmethod
    def run_comprehensive_health_check():
        """
        Executa uma verificação completa de saúde do banco de dados.
        
        Returns:
            dict: Relatório completo de saúde
        """
        health_report = {
            'timestamp': time.time(),
            'overall_status': 'unknown',
            'connectivity': {},
            'query_tests': {},
            'performance': {},
            'recommendations': []
        }
        
        try:
            # Verifica conectividade
            health_report['connectivity'] = DatabaseHealthChecker.check_database_connectivity()
            
            # Testa queries críticas
            health_report['query_tests'] = DatabaseHealthChecker.test_critical_queries()
            
            # Informações de performance
            health_report['performance'] = DatabaseHealthChecker.get_database_performance_info()
            
            # Determina status geral
            if health_report['connectivity']['status'] == 'connected':
                failed_queries = sum(1 for test in health_report['query_tests'].values() 
                                   if test['status'] == 'error')
                
                if failed_queries == 0:
                    health_report['overall_status'] = 'healthy'
                elif failed_queries < len(health_report['query_tests']) / 2:
                    health_report['overall_status'] = 'degraded'
                else:
                    health_report['overall_status'] = 'unhealthy'
            else:
                health_report['overall_status'] = 'critical'
            
            # Gera recomendações
            health_report['recommendations'] = DatabaseHealthChecker.generate_recommendations(health_report)
            
        except Exception as e:
            health_report['overall_status'] = 'error'
            health_report['error'] = str(e)
            logger.error(f"Erro na verificação completa de saúde: {e}")
        
        return health_report
    
    @staticmethod
    def generate_recommendations(health_report):
        """
        Gera recomendações baseadas no relatório de saúde.
        
        Args:
            health_report: Relatório de saúde do banco
            
        Returns:
            list: Lista de recomendações
        """
        recommendations = []
        
        try:
            # Recomendações baseadas na conectividade
            if health_report['connectivity']['status'] != 'connected':
                recommendations.append("Verificar configuração de conexão com o banco de dados")
                recommendations.append("Verificar se o serviço do banco está rodando")
            
            # Recomendações baseadas em migrações
            if health_report['connectivity'].get('migrations_pending'):
                recommendations.append("Executar migrações pendentes: python manage.py migrate")
            
            # Recomendações baseadas em queries
            failed_queries = [name for name, test in health_report['query_tests'].items() 
                            if test['status'] == 'error']
            if failed_queries:
                recommendations.append(f"Investigar falhas nas queries: {', '.join(failed_queries)}")
            
            # Recomendações de performance
            performance = health_report.get('performance', {})
            if performance.get('slow_queries'):
                recommendations.append("Otimizar queries lentas identificadas")
            
            if performance.get('average_query_time', 0) > 0.05:
                recommendations.append("Considerar otimização geral de queries")
                
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            recommendations.append("Erro ao gerar recomendações automáticas")
        
        return recommendations