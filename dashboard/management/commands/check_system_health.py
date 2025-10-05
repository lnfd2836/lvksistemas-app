"""
Comando de gerenciamento para verificar a saúde do sistema.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from dashboard.utils.database_health import DatabaseHealthChecker
from dashboard.middleware.middleware_profiler import create_middleware_diagnostics
import json
import sys


class Command(BaseCommand):
    help = 'Verifica a saúde geral do sistema e identifica problemas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='Formato de saída (text ou json)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Saída detalhada'
        )
        parser.add_argument(
            '--check-db',
            action='store_true',
            help='Verifica apenas o banco de dados'
        )
        parser.add_argument(
            '--check-middleware',
            action='store_true',
            help='Verifica apenas os middlewares'
        )
    
    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.format = options['format']
        
        try:
            # Executa verificações baseadas nos argumentos
            if options['check_db']:
                results = self.check_database_only()
            elif options['check_middleware']:
                results = self.check_middleware_only()
            else:
                results = self.check_full_system()
            
            # Exibe resultados no formato solicitado
            if self.format == 'json':
                self.stdout.write(json.dumps(results, indent=2, default=str))
            else:
                self.display_text_results(results)
            
            # Define código de saída baseado no status
            if results.get('overall_status') in ['critical', 'error']:
                sys.exit(1)
            elif results.get('overall_status') in ['degraded', 'unhealthy']:
                sys.exit(2)
            else:
                sys.exit(0)
                
        except Exception as e:
            raise CommandError(f'Erro ao executar verificação de saúde: {e}')
    
    def check_database_only(self):
        """Verifica apenas o banco de dados."""
        self.stdout.write("Verificando saúde do banco de dados...")
        
        db_health = DatabaseHealthChecker.run_comprehensive_health_check()
        
        return {
            'type': 'database_only',
            'database': db_health,
            'overall_status': db_health.get('overall_status', 'unknown')
        }
    
    def check_middleware_only(self):
        """Verifica apenas os middlewares."""
        self.stdout.write("Verificando configuração de middlewares...")
        
        middleware_diagnostics = create_middleware_diagnostics()
        
        # Determina status baseado nos problemas encontrados
        if middleware_diagnostics.get('potential_issues'):
            status = 'degraded' if len(middleware_diagnostics['potential_issues']) < 3 else 'unhealthy'
        else:
            status = 'healthy'
        
        return {
            'type': 'middleware_only',
            'middleware': middleware_diagnostics,
            'overall_status': status
        }
    
    def check_full_system(self):
        """Executa verificação completa do sistema."""
        self.stdout.write("Executando verificação completa do sistema...")
        
        results = {
            'type': 'full_system',
            'timestamp': DatabaseHealthChecker.run_comprehensive_health_check()['timestamp'],
            'checks': {}
        }
        
        # Verifica banco de dados
        self.stdout.write("  → Verificando banco de dados...")
        results['checks']['database'] = DatabaseHealthChecker.run_comprehensive_health_check()
        
        # Verifica middlewares
        self.stdout.write("  → Verificando middlewares...")
        results['checks']['middleware'] = create_middleware_diagnostics()
        
        # Verifica configurações básicas
        self.stdout.write("  → Verificando configurações...")
        results['checks']['settings'] = self.check_settings()
        
        # Verifica estrutura de arquivos
        self.stdout.write("  → Verificando estrutura de arquivos...")
        results['checks']['files'] = self.check_file_structure()
        
        # Determina status geral
        results['overall_status'] = self.determine_overall_status(results['checks'])
        
        return results
    
    def check_settings(self):
        """Verifica configurações críticas do Django."""
        settings_check = {
            'status': 'healthy',
            'issues': [],
            'warnings': []
        }
        
        # Verifica DEBUG em produção
        import os
        if hasattr(settings, 'DEBUG') and settings.DEBUG and 'DYNO' in os.environ:
            settings_check['issues'].append("DEBUG=True em produção (Heroku)")
            settings_check['status'] = 'unhealthy'
        
        # Verifica SECRET_KEY
        if not getattr(settings, 'SECRET_KEY', None) or settings.SECRET_KEY == 'django-insecure-change-this-in-production':
            settings_check['issues'].append("SECRET_KEY não configurada adequadamente")
            settings_check['status'] = 'unhealthy'
        
        # Verifica ALLOWED_HOSTS
        if not getattr(settings, 'ALLOWED_HOSTS', None):
            settings_check['issues'].append("ALLOWED_HOSTS não configurado")
            settings_check['status'] = 'unhealthy'
        
        # Verifica configuração de banco
        databases = getattr(settings, 'DATABASES', {})
        if not databases or 'default' not in databases:
            settings_check['issues'].append("Configuração de banco de dados ausente")
            settings_check['status'] = 'critical'
        
        # Verifica apps instalados críticos
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        critical_apps = ['django.contrib.auth', 'django.contrib.sessions', 'dashboard', 'lojas', 'usuarios']
        
        for app in critical_apps:
            if app not in installed_apps:
                settings_check['issues'].append(f"App crítico ausente: {app}")
                settings_check['status'] = 'unhealthy'
        
        return settings_check
    
    def check_file_structure(self):
        """Verifica se arquivos críticos existem."""
        import os
        
        file_check = {
            'status': 'healthy',
            'missing_files': [],
            'missing_directories': []
        }
        
        # Arquivos críticos
        critical_files = [
            'manage.py',
            'lojad/settings.py',
            'lojad/urls.py',
            'dashboard/views.py',
            'lojas/models.py',
            'usuarios/models.py',
        ]
        
        # Diretórios críticos
        critical_dirs = [
            'templates',
            'static',
            'dashboard',
            'lojas',
            'usuarios',
        ]
        
        base_dir = getattr(settings, 'BASE_DIR', '.')
        
        for file_path in critical_files:
            full_path = os.path.join(base_dir, file_path)
            if not os.path.isfile(full_path):
                file_check['missing_files'].append(file_path)
        
        for dir_path in critical_dirs:
            full_path = os.path.join(base_dir, dir_path)
            if not os.path.isdir(full_path):
                file_check['missing_directories'].append(dir_path)
        
        if file_check['missing_files'] or file_check['missing_directories']:
            file_check['status'] = 'unhealthy'
        
        return file_check
    
    def determine_overall_status(self, checks):
        """Determina o status geral baseado em todas as verificações."""
        statuses = []
        
        # Coleta todos os status
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict):
                if 'overall_status' in check_result:
                    statuses.append(check_result['overall_status'])
                elif 'status' in check_result:
                    statuses.append(check_result['status'])
        
        # Determina prioridade (pior status ganha)
        if 'critical' in statuses or 'error' in statuses:
            return 'critical'
        elif 'unhealthy' in statuses:
            return 'unhealthy'
        elif 'degraded' in statuses:
            return 'degraded'
        elif 'healthy' in statuses:
            return 'healthy'
        else:
            return 'unknown'
    
    def display_text_results(self, results):
        """Exibe resultados em formato texto."""
        status_colors = {
            'healthy': self.style.SUCCESS,
            'degraded': self.style.WARNING,
            'unhealthy': self.style.ERROR,
            'critical': self.style.ERROR,
            'error': self.style.ERROR,
            'unknown': self.style.NOTICE
        }
        
        overall_status = results.get('overall_status', 'unknown')
        color_func = status_colors.get(overall_status, self.style.NOTICE)
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(color_func(f"STATUS GERAL: {overall_status.upper()}"))
        self.stdout.write("="*60)
        
        if results['type'] == 'database_only':
            self.display_database_results(results['database'])
        elif results['type'] == 'middleware_only':
            self.display_middleware_results(results['middleware'])
        else:
            self.display_full_results(results['checks'])
        
        self.stdout.write("\n" + "="*60)
    
    def display_database_results(self, db_results):
        """Exibe resultados da verificação do banco."""
        self.stdout.write("\n📊 BANCO DE DADOS:")
        
        connectivity = db_results.get('connectivity', {})
        self.stdout.write(f"  Status: {connectivity.get('status', 'unknown')}")
        self.stdout.write(f"  Tempo de conexão: {connectivity.get('connection_time', 'N/A')}")
        self.stdout.write(f"  Migrações pendentes: {'Sim' if connectivity.get('migrations_pending') else 'Não'}")
        
        if connectivity.get('errors'):
            self.stdout.write(self.style.ERROR("  Erros:"))
            for error in connectivity['errors']:
                self.stdout.write(f"    - {error}")
        
        # Testes de queries
        query_tests = db_results.get('query_tests', {})
        if query_tests:
            self.stdout.write("\n  Testes de Queries:")
            for test_name, test_result in query_tests.items():
                status_icon = "✅" if test_result['status'] == 'success' else "❌"
                self.stdout.write(f"    {status_icon} {test_name}: {test_result['status']}")
                if test_result.get('error'):
                    self.stdout.write(f"      Erro: {test_result['error']}")
        
        # Recomendações
        recommendations = db_results.get('recommendations', [])
        if recommendations:
            self.stdout.write("\n  Recomendações:")
            for rec in recommendations:
                self.stdout.write(f"    • {rec}")
    
    def display_middleware_results(self, mw_results):
        """Exibe resultados da verificação de middleware."""
        self.stdout.write("\n⚙️ MIDDLEWARES:")
        
        middleware_list = mw_results.get('middleware_list', [])
        self.stdout.write(f"  Total de middlewares: {len(middleware_list)}")
        
        # Mostra status de cada middleware
        for mw in middleware_list:
            status_icon = "✅" if mw['status'] == 'available' else "❌"
            self.stdout.write(f"    {status_icon} {mw['name']} ({mw['status']})")
            if mw.get('error'):
                self.stdout.write(f"      Erro: {mw['error']}")
        
        # Problemas potenciais
        issues = mw_results.get('potential_issues', [])
        if issues:
            self.stdout.write("\n  Problemas encontrados:")
            for issue in issues:
                self.stdout.write(f"    ⚠️ {issue}")
        
        # Recomendações
        recommendations = mw_results.get('recommendations', [])
        if recommendations:
            self.stdout.write("\n  Recomendações:")
            for rec in recommendations:
                self.stdout.write(f"    • {rec}")
    
    def display_full_results(self, checks):
        """Exibe resultados da verificação completa."""
        for check_name, check_result in checks.items():
            if check_name == 'database':
                self.display_database_results(check_result)
            elif check_name == 'middleware':
                self.display_middleware_results(check_result)
            elif check_name == 'settings':
                self.display_settings_results(check_result)
            elif check_name == 'files':
                self.display_files_results(check_result)
    
    def display_settings_results(self, settings_results):
        """Exibe resultados da verificação de configurações."""
        self.stdout.write("\n⚙️ CONFIGURAÇÕES:")
        
        status = settings_results.get('status', 'unknown')
        status_icon = "✅" if status == 'healthy' else "❌"
        self.stdout.write(f"  Status: {status_icon} {status}")
        
        issues = settings_results.get('issues', [])
        if issues:
            self.stdout.write("  Problemas:")
            for issue in issues:
                self.stdout.write(f"    ❌ {issue}")
        
        warnings = settings_results.get('warnings', [])
        if warnings:
            self.stdout.write("  Avisos:")
            for warning in warnings:
                self.stdout.write(f"    ⚠️ {warning}")
    
    def display_files_results(self, files_results):
        """Exibe resultados da verificação de arquivos."""
        self.stdout.write("\n📁 ESTRUTURA DE ARQUIVOS:")
        
        status = files_results.get('status', 'unknown')
        status_icon = "✅" if status == 'healthy' else "❌"
        self.stdout.write(f"  Status: {status_icon} {status}")
        
        missing_files = files_results.get('missing_files', [])
        if missing_files:
            self.stdout.write("  Arquivos ausentes:")
            for file_path in missing_files:
                self.stdout.write(f"    ❌ {file_path}")
        
        missing_dirs = files_results.get('missing_directories', [])
        if missing_dirs:
            self.stdout.write("  Diretórios ausentes:")
            for dir_path in missing_dirs:
                self.stdout.write(f"    ❌ {dir_path}")