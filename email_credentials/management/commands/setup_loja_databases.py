"""
Comando para configurar bancos de dados individuais para cada loja
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections
from lojas.models import Loja
from email_credentials.database_config import setup_loja_database, get_loja_database_alias


class Command(BaseCommand):
    help = 'Configura bancos de dados individuais para cada loja'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--loja-id',
            type=str,
            help='ID específico da loja para configurar (opcional)'
        )
        parser.add_argument(
            '--migrate',
            action='store_true',
            help='Executar migrações nos bancos das lojas'
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Criar superusuário nos bancos das lojas'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Configurando bancos de dados por loja...')
        )
        
        # Filtrar lojas
        if options['loja_id']:
            lojas = Loja.objects.filter(id=options['loja_id'])
            if not lojas.exists():
                self.stdout.write(
                    self.style.ERROR(f'❌ Loja com ID {options["loja_id"]} não encontrada')
                )
                return
        else:
            lojas = Loja.objects.all()
        
        if not lojas.exists():
            self.stdout.write(
                self.style.WARNING('⚠️ Nenhuma loja encontrada')
            )
            return
        
        # Configurar banco para cada loja
        for loja in lojas:
            self.stdout.write(f'\n📦 Configurando loja: {loja.nome} (ID: {loja.id})')
            
            try:
                # Configurar banco
                db_alias = setup_loja_database(loja.id)
                self.stdout.write(f'  ✅ Banco configurado: {db_alias}')
                
                # Verificar conexão
                connection = connections[db_alias]
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result:
                        self.stdout.write(f'  ✅ Conexão testada com sucesso')
                
                # Executar migrações se solicitado
                if options['migrate']:
                    self.stdout.write(f'  🔄 Executando migrações...')
                    call_command('migrate', database=db_alias, verbosity=0)
                    self.stdout.write(f'  ✅ Migrações executadas')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Erro ao configurar loja {loja.id}: {str(e)}')
                )
        
        # Resumo
        self.stdout.write(f'\n📊 Resumo:')
        self.stdout.write(f'  Lojas processadas: {lojas.count()}')
        
        # Listar bancos configurados
        loja_databases = [
            db for db in settings.DATABASES.keys() 
            if db.startswith('loja_')
        ]
        self.stdout.write(f'  Bancos de loja configurados: {len(loja_databases)}')
        
        for db in loja_databases:
            self.stdout.write(f'    - {db}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Configuração concluída!')
        )
        
        # Instruções
        self.stdout.write(f'\n📋 Próximos passos:')
        if not options['migrate']:
            self.stdout.write(f'  1. Execute migrações: python manage.py setup_loja_databases --migrate')
        self.stdout.write(f'  2. Teste o sistema com diferentes lojas')
        self.stdout.write(f'  3. Verifique os arquivos de banco: db_<loja_id>.sqlite3')


