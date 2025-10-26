#!/usr/bin/env python3
"""
Comando para executar migrações nos bancos individuais das lojas
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections
from lojas.models import Loja
from email_credentials.database_config import loja_db_config
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Executa migrações nos bancos individuais das lojas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--loja-id',
            type=int,
            help='ID específico da loja para migrar (opcional)'
        )
        parser.add_argument(
            '--create-only',
            action='store_true',
            help='Apenas criar os bancos, sem executar migrações'
        )
        parser.add_argument(
            '--migrate-only',
            action='store_true',
            help='Apenas executar migrações, assumindo que bancos existem'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar recriação de bancos existentes'
        )
    
    def handle(self, *args, **options):
        """Executa as migrações nos bancos das lojas"""
        
        self.stdout.write("="*80)
        self.stdout.write(self.style.SUCCESS("MIGRAÇÕES DOS BANCOS DAS LOJAS"))
        self.stdout.write("="*80)
        
        # Filtrar lojas
        if options['loja_id']:
            lojas = Loja.objects.filter(id=options['loja_id'])
            if not lojas.exists():
                self.stdout.write(
                    self.style.ERROR(f"Loja com ID {options['loja_id']} não encontrada")
                )
                return
        else:
            lojas = Loja.objects.filter(status='ativa')
        
        self.stdout.write(f"\n📊 Processando {lojas.count()} loja(s)...")
        
        success_count = 0
        error_count = 0
        
        for loja in lojas:
            try:
                self.stdout.write(f"\n🏪 Processando: {loja.nome} (ID: {loja.id})")
                
                # Configurar banco da loja
                db_alias = f"loja_{loja.id}"
                db_config = loja_db_config(loja.id)
                
                # Adicionar à configuração do Django
                settings.DATABASES[db_alias] = db_config
                
                # Criar/verificar banco se necessário
                if not options['migrate_only']:
                    self._setup_database(db_alias, db_config, options['force'])
                
                # Executar migrações se necessário
                if not options['create_only']:
                    self._run_migrations(db_alias, loja)
                
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ {loja.nome}: Concluído com sucesso")
                )
                
            except Exception as e:
                error_count += 1
                logger.error(f"Erro ao processar loja {loja.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"   ❌ {loja.nome}: Erro - {str(e)}")
                )
        
        # Resumo final
        self.stdout.write("\n" + "="*80)
        self.stdout.write("📊 RESUMO DAS MIGRAÇÕES")
        self.stdout.write("="*80)
        self.stdout.write(f"✅ Sucessos: {success_count}")
        self.stdout.write(f"❌ Erros: {error_count}")
        self.stdout.write(f"📊 Total processado: {success_count + error_count}")
        
        if error_count == 0:
            self.stdout.write(
                self.style.SUCCESS("\n🎉 Todas as migrações concluídas com sucesso!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"\n⚠️ {error_count} erro(s) encontrado(s). Verifique os logs.")
            )
    
    def _setup_database(self, db_alias, db_config, force=False):
        """Configura o banco de dados da loja"""
        import os
        
        db_path = db_config['NAME']
        
        # Verificar se banco já existe
        if os.path.exists(db_path) and not force:
            self.stdout.write(f"   📁 Banco já existe: {os.path.basename(db_path)}")
            return
        
        # Criar diretório se necessário
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            self.stdout.write(f"   📁 Diretório criado: {db_dir}")
        
        # Testar conexão (isso criará o arquivo SQLite)
        try:
            connection = connections[db_alias]
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            self.stdout.write(f"   🗄️ Banco criado: {os.path.basename(db_path)}")
            
        except Exception as e:
            raise Exception(f"Erro ao criar banco: {str(e)}")
    
    def _run_migrations(self, db_alias, loja):
        """Executa migrações no banco da loja"""
        
        # Apps que devem ter tabelas no banco da loja
        loja_apps = [
            'email_credentials',  # LojaUserProfile
            'auth',              # User, Group, Permission (cópia)
            'contenttypes',      # ContentType
        ]
        
        self.stdout.write(f"   🔄 Executando migrações no banco {db_alias}...")
        
        for app in loja_apps:
            try:
                # Executar migrate para o app específico no banco da loja
                call_command(
                    'migrate',
                    app,
                    database=db_alias,
                    verbosity=0,
                    interactive=False
                )
                
                self.stdout.write(f"     ✅ {app}: Migrado")
                
            except Exception as e:
                # Alguns apps podem não ter migrações ou já estar migrados
                self.stdout.write(f"     ⚠️ {app}: {str(e)}")
        
        self.stdout.write(f"   ✅ Migrações concluídas para {db_alias}")
    
    def _verify_database_setup(self, db_alias):
        """Verifica se o banco foi configurado corretamente"""
        try:
            connection = connections[db_alias]
            
            # Testar conexão
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'email_credentials_lojauserprofile',
                'auth_user',
                'auth_group',
                'django_migrations'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠️ Tabelas faltando: {missing_tables}")
                )
            else:
                self.stdout.write(f"   ✅ Todas as tabelas necessárias presentes")
            
            return len(missing_tables) == 0
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Erro na verificação: {str(e)}")
            )
            return False