"""
Comando para listar informações sobre bancos de dados das lojas
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from lojas.models import Loja
from email_credentials.database_config import get_loja_database_alias


class Command(BaseCommand):
    help = 'Lista informações sobre bancos de dados das lojas'
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📊 Informações dos bancos de dados por loja')
        )
        
        # Listar lojas
        lojas = Loja.objects.all()
        self.stdout.write(f'\n🏪 Lojas cadastradas: {lojas.count()}')
        
        for loja in lojas:
            db_alias = get_loja_database_alias(loja.id)
            db_configured = db_alias in settings.DATABASES
            
            self.stdout.write(f'\n  📦 {loja.nome} (ID: {loja.id})')
            self.stdout.write(f'    Alias do banco: {db_alias}')
            self.stdout.write(f'    Configurado: {"✅" if db_configured else "❌"}')
            
            if db_configured:
                db_config = settings.DATABASES[db_alias]
                db_file = db_config.get('NAME', 'N/A')
                self.stdout.write(f'    Arquivo: {db_file}')
                
                # Verificar se arquivo existe
                import os
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                    self.stdout.write(f'    Tamanho: {size} bytes')
                else:
                    self.stdout.write(f'    Status: Arquivo não existe')
        
        # Resumo dos bancos configurados
        all_databases = list(settings.DATABASES.keys())
        loja_databases = [db for db in all_databases if db.startswith('loja_')]
        
        self.stdout.write(f'\n📊 Resumo:')
        self.stdout.write(f'  Total de bancos: {len(all_databases)}')
        self.stdout.write(f'  Banco principal: default')
        self.stdout.write(f'  Bancos de loja: {len(loja_databases)}')
        
        if loja_databases:
            self.stdout.write(f'\n  Bancos de loja configurados:')
            for db in loja_databases:
                self.stdout.write(f'    - {db}')