"""
Comando para configurar e validar isolamento de dados por loja
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections
from lojas.models import Loja
from lojas.services.isolamento_service import IsolamentoService
from lojas.database_router_isolado import ensure_loja_database_exists
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Configura e valida isolamento de dados por loja'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--setup',
            action='store_true',
            help='Configura bancos de dados para todas as lojas ativas'
        )
        
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Valida configuração de isolamento'
        )
        
        parser.add_argument(
            '--migrate',
            action='store_true',
            help='Executa migrações em todos os bancos de loja'
        )
        
        parser.add_argument(
            '--loja-id',
            type=str,
            help='ID específico da loja para operações'
        )
        
        parser.add_argument(
            '--status',
            action='store_true',
            help='Mostra status do isolamento'
        )
    
    def handle(self, *args, **options):
        try:
            if options['status']:
                self.show_status()
            
            if options['setup']:
                self.setup_isolation(options.get('loja_id'))
            
            if options['validate']:
                self.validate_isolation()
            
            if options['migrate']:
                self.migrate_databases(options.get('loja_id'))
            
            if not any([options['setup'], options['validate'], options['migrate'], options['status']]):
                self.stdout.write(
                    self.style.WARNING('Nenhuma ação especificada. Use --help para ver opções.')
                )
                
        except Exception as e:
            raise CommandError(f'Erro ao executar comando: {str(e)}')
    
    def show_status(self):
        """Mostra status do isolamento"""
        self.stdout.write(self.style.SUCCESS('=== STATUS DO ISOLAMENTO ==='))
        
        try:
            status = IsolamentoService.get_isolation_status()
            
            self.stdout.write(f"Loja atual: {status.get('current_loja_id', 'Nenhuma')}")
            self.stdout.write(f"Bancos de loja configurados: {status.get('configured_loja_databases', 0)}")
            self.stdout.write(f"Lojas ativas: {status.get('active_lojas', 0)}")
            self.stdout.write(f"Isolamento ativo: {status.get('isolation_active', False)}")
            
            if status.get('loja_databases'):
                self.stdout.write("\nBancos configurados:")
                for db in status['loja_databases']:
                    self.stdout.write(f"  - {db}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao obter status: {str(e)}'))
    
    def setup_isolation(self, loja_id=None):
        """Configura isolamento para lojas"""
        self.stdout.write(self.style.SUCCESS('=== CONFIGURANDO ISOLAMENTO ==='))
        
        try:
            if loja_id:
                # Configurar loja específica
                try:
                    loja = Loja.objects.get(id=loja_id, status='ativa')
                    self.setup_loja_database(loja)
                except Loja.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Loja {loja_id} não encontrada ou inativa'))
                    return
            else:
                # Configurar todas as lojas ativas
                lojas = Loja.objects.filter(status='ativa')
                self.stdout.write(f'Configurando {lojas.count()} lojas ativas...')
                
                for loja in lojas:
                    self.setup_loja_database(loja)
            
            self.stdout.write(self.style.SUCCESS('Configuração de isolamento concluída!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro na configuração: {str(e)}'))
    
    def setup_loja_database(self, loja):
        """Configura banco de dados para uma loja"""
        try:
            self.stdout.write(f'Configurando loja: {loja.nome} (ID: {loja.id})')
            
            # Garantir que o banco existe na configuração
            if ensure_loja_database_exists(str(loja.id)):
                self.stdout.write(f'  ✓ Banco configurado: loja_{loja.id}')
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ Erro ao configurar banco para loja {loja.id}'))
                return
            
            # Testar conexão
            db_alias = f"loja_{loja.id}"
            try:
                connection = connections[db_alias]
                connection.ensure_connection()
                self.stdout.write(f'  ✓ Conexão testada com sucesso')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Erro na conexão: {str(e)}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao configurar loja {loja.nome}: {str(e)}'))
    
    def validate_isolation(self):
        """Valida configuração de isolamento"""
        self.stdout.write(self.style.SUCCESS('=== VALIDANDO ISOLAMENTO ==='))
        
        try:
            # Verificar lojas ativas
            lojas_ativas = Loja.objects.filter(status='ativa')
            self.stdout.write(f'Lojas ativas encontradas: {lojas_ativas.count()}')
            
            # Verificar bancos configurados
            loja_dbs = [db for db in settings.DATABASES.keys() if db.startswith('loja_')]
            self.stdout.write(f'Bancos de loja configurados: {len(loja_dbs)}')
            
            # Validar cada loja
            problemas = []
            
            for loja in lojas_ativas:
                db_alias = f"loja_{loja.id}"
                
                # Verificar se banco está configurado
                if db_alias not in settings.DATABASES:
                    problemas.append(f'Loja {loja.nome} (ID: {loja.id}) não tem banco configurado')
                    continue
                
                # Testar conexão
                try:
                    connection = connections[db_alias]
                    connection.ensure_connection()
                    self.stdout.write(f'  ✓ Loja {loja.nome}: banco OK')
                except Exception as e:
                    problemas.append(f'Loja {loja.nome}: erro na conexão - {str(e)}')
            
            # Verificar bancos órfãos
            for db_alias in loja_dbs:
                loja_id = db_alias.replace('loja_', '')
                if not lojas_ativas.filter(id=loja_id).exists():
                    problemas.append(f'Banco órfão encontrado: {db_alias}')
            
            # Mostrar resultados
            if problemas:
                self.stdout.write(self.style.WARNING('\nProblemas encontrados:'))
                for problema in problemas:
                    self.stdout.write(f'  ⚠ {problema}')
            else:
                self.stdout.write(self.style.SUCCESS('\n✓ Isolamento validado com sucesso!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro na validação: {str(e)}'))
    
    def migrate_databases(self, loja_id=None):
        """Executa migrações nos bancos de loja"""
        self.stdout.write(self.style.SUCCESS('=== EXECUTANDO MIGRAÇÕES ==='))
        
        try:
            if loja_id:
                # Migrar loja específica
                if IsolamentoService.migrate_loja_database(loja_id):
                    self.stdout.write(f'✓ Migrações executadas para loja {loja_id}')
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Erro nas migrações da loja {loja_id}'))
            else:
                # Migrar todas as lojas
                lojas = Loja.objects.filter(status='ativa')
                
                for loja in lojas:
                    self.stdout.write(f'Migrando loja: {loja.nome} (ID: {loja.id})')
                    
                    if IsolamentoService.migrate_loja_database(str(loja.id)):
                        self.stdout.write(f'  ✓ Migrações concluídas')
                    else:
                        self.stdout.write(self.style.ERROR(f'  ✗ Erro nas migrações'))
            
            self.stdout.write(self.style.SUCCESS('Migrações concluídas!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro nas migrações: {str(e)}'))