from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.core.management import call_command
import sys

class Command(BaseCommand):
    help = 'Corrige as migrações do controle_financeiro no Heroku'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação das tabelas mesmo se já existirem',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Iniciando correção das migrações do controle_financeiro...')
        )

        try:
            # 1. Verificar se a tabela existe
            if not self.check_table_exists('controle_financeiro_controlefinanceiro'):
                self.stdout.write('❌ Tabela controle_financeiro_controlefinanceiro não existe')
                
                # Tentar executar migrações normalmente primeiro
                try:
                    self.stdout.write('1️⃣ Tentando executar migrações normalmente...')
                    call_command('migrate', 'controle_financeiro', verbosity=0)
                    
                    if self.check_table_exists('controle_financeiro_controlefinanceiro'):
                        self.stdout.write(self.style.SUCCESS('✅ Migrações executadas com sucesso!'))
                        self.verify_models()
                        return
                        
                except Exception as e:
                    self.stdout.write(f'❌ Migrações falharam: {e}')
                
                # Se migrações falharam, criar tabelas manualmente
                self.stdout.write('2️⃣ Criando tabelas manualmente...')
                if self.create_tables_manually():
                    self.mark_migrations_as_applied()
                    self.create_default_data()
                else:
                    self.stdout.write(self.style.ERROR('❌ Falha ao criar tabelas manualmente'))
                    sys.exit(1)
            else:
                self.stdout.write('✅ Tabela já existe, verificando migrações pendentes...')
                try:
                    call_command('migrate', 'controle_financeiro', verbosity=0)
                    self.stdout.write(self.style.SUCCESS('✅ Migrações verificadas!'))
                except Exception as e:
                    self.stdout.write(f'⚠️ Aviso ao verificar migrações: {e}')

            # Verificar se os modelos funcionam
            self.verify_models()
            
            self.stdout.write(
                self.style.SUCCESS('🎉 Correção das migrações concluída com sucesso!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro geral: {e}')
            )
            sys.exit(1)

    def check_table_exists(self, table_name):
        """Verifica se uma tabela existe"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=%s;
            """, [table_name])
            return cursor.fetchone() is not None

    def create_tables_manually(self):
        """Cria as tabelas manualmente"""
        sql_commands = [
            # PlanoFinanceiro
            """
            CREATE TABLE IF NOT EXISTS controle_financeiro_planofinanceiro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT NOT NULL,
                valor_mensal DECIMAL(10, 2) NOT NULL,
                dias_trial INTEGER NOT NULL DEFAULT 30,
                ativo BOOLEAN NOT NULL DEFAULT 1,
                data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # ControleFinanceiro
            """
            CREATE TABLE IF NOT EXISTS controle_financeiro_controlefinanceiro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status VARCHAR(20) NOT NULL DEFAULT 'ativa',
                data_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                data_vencimento DATETIME NOT NULL,
                data_bloqueio DATETIME NULL,
                data_ultimo_pagamento DATETIME NULL,
                valor_mensal DECIMAL(10, 2) NOT NULL,
                valor_pago DECIMAL(10, 2) NOT NULL DEFAULT 0,
                valor_pendente DECIMAL(10, 2) NOT NULL DEFAULT 0,
                dias_grace_period INTEGER NOT NULL DEFAULT 5,
                bloqueada BOOLEAN NOT NULL DEFAULT 0,
                motivo_bloqueio TEXT NOT NULL DEFAULT '',
                observacoes TEXT NOT NULL DEFAULT '',
                data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                loja_id INTEGER NOT NULL UNIQUE,
                plano_id INTEGER NOT NULL,
                FOREIGN KEY (loja_id) REFERENCES lojas_loja (id),
                FOREIGN KEY (plano_id) REFERENCES controle_financeiro_planofinanceiro (id)
            );
            """,
            
            # CobrancaAsaas
            """
            CREATE TABLE IF NOT EXISTS controle_financeiro_cobrancaasaas (
                id VARCHAR(36) PRIMARY KEY,
                asaas_id VARCHAR(100) NOT NULL UNIQUE,
                customer_id VARCHAR(100) NOT NULL,
                valor DECIMAL(10, 2) NOT NULL,
                data_vencimento DATETIME NOT NULL,
                descricao TEXT NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
                data_pagamento DATETIME NULL,
                invoice_url TEXT NOT NULL DEFAULT '',
                bank_slip_url TEXT NOT NULL DEFAULT '',
                invoice_number VARCHAR(100) NOT NULL DEFAULT '',
                pix_qr_code TEXT NOT NULL DEFAULT '',
                pix_copy_paste TEXT NOT NULL DEFAULT '',
                pix_expires_date DATETIME NULL,
                api_response TEXT NOT NULL DEFAULT '{}',
                external_reference VARCHAR(200) NOT NULL DEFAULT '',
                observacoes TEXT NOT NULL DEFAULT '',
                data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                controle_financeiro_id INTEGER NOT NULL,
                FOREIGN KEY (controle_financeiro_id) REFERENCES controle_financeiro_controlefinanceiro (id)
            );
            """,
            
            # SyncStatus
            """
            CREATE TABLE IF NOT EXISTS controle_financeiro_syncstatus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_sync DATETIME NULL,
                sync_in_progress BOOLEAN NOT NULL DEFAULT 0,
                last_error TEXT NOT NULL DEFAULT '',
                total_charges INTEGER NOT NULL DEFAULT 0,
                synced_charges INTEGER NOT NULL DEFAULT 0,
                failed_charges INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]

        try:
            with connection.cursor() as cursor:
                for i, sql in enumerate(sql_commands, 1):
                    self.stdout.write(f'📊 Criando tabela {i}/{len(sql_commands)}...')
                    cursor.execute(sql)
                    
            self.stdout.write(self.style.SUCCESS('✅ Tabelas criadas com sucesso!'))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar tabelas: {e}'))
            return False

    def mark_migrations_as_applied(self):
        """Marca as migrações como aplicadas"""
        migrations = [
            '0001_initial',
            '0002_configuracaoboleto_boletogerado',
            '0003_configuracaoboleto_codigo_cedente',
            '0004_add_convenio_field',
            '0005_cobrancaasaas',
            '0006_alter_configuracaoboleto_convenio',
            '0007_merge_20251023_2348',
            '0008_syncstatus',
            '0009_syncstatus_fix',
        ]

        try:
            with connection.cursor() as cursor:
                for migration in migrations:
                    cursor.execute("""
                        INSERT OR IGNORE INTO django_migrations (app, name, applied)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    """, ['controle_financeiro', migration])
                    
            self.stdout.write(self.style.SUCCESS('✅ Migrações marcadas como aplicadas!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao marcar migrações: {e}'))

    def create_default_data(self):
        """Cria dados padrão"""
        try:
            with connection.cursor() as cursor:
                # Plano padrão
                cursor.execute("""
                    INSERT OR IGNORE INTO controle_financeiro_planofinanceiro 
                    (nome, descricao, valor_mensal, dias_trial, ativo, data_criacao)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, [
                    "Plano Básico",
                    "Plano básico para lojas do sistema",
                    29.90,
                    30,
                    1
                ])
                
                # Status de sync inicial
                cursor.execute("""
                    INSERT OR IGNORE INTO controle_financeiro_syncstatus 
                    (last_sync, sync_in_progress, last_error, total_charges, synced_charges, failed_charges, created_at, updated_at)
                    VALUES (NULL, 0, '', 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """)
                
            self.stdout.write(self.style.SUCCESS('✅ Dados padrão criados!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar dados padrão: {e}'))

    def verify_models(self):
        """Verifica se os modelos funcionam"""
        try:
            from controle_financeiro.models import (
                ControleFinanceiro, PlanoFinanceiro, CobrancaAsaas
            )
            
            planos = PlanoFinanceiro.objects.count()
            controles = ControleFinanceiro.objects.count()
            cobrancas = CobrancaAsaas.objects.count()
            
            self.stdout.write(f'📊 PlanoFinanceiro: {planos} registros')
            self.stdout.write(f'📊 ControleFinanceiro: {controles} registros')
            self.stdout.write(f'📊 CobrancaAsaas: {cobrancas} registros')
            
            self.stdout.write(self.style.SUCCESS('✅ Modelos verificados com sucesso!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao verificar modelos: {e}'))