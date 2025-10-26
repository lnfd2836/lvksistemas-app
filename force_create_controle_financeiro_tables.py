#!/usr/bin/env python3
"""
Script para forçar a criação das tabelas do controle_financeiro no Heroku
"""

import os
import sys
import django
from django.db import connection, transaction
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

def create_tables_manually():
    """Cria as tabelas manualmente se as migrações falharem"""
    print("🔧 Criando tabelas do controle_financeiro manualmente...")
    
    sql_commands = [
        # Tabela PlanoFinanceiro
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
        
        # Tabela ControleFinanceiro
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
        
        # Tabela ConfiguracaoBoleto
        """
        CREATE TABLE IF NOT EXISTS controle_financeiro_configuracaoboleto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_banco VARCHAR(100) NOT NULL,
            codigo_banco VARCHAR(10) NOT NULL,
            agencia VARCHAR(10) NOT NULL,
            conta VARCHAR(20) NOT NULL,
            carteira VARCHAR(10) NOT NULL,
            codigo_cedente VARCHAR(20) NULL,
            convenio VARCHAR(20) NULL,
            nome_beneficiario VARCHAR(200) NOT NULL,
            cnpj_beneficiario VARCHAR(20) NOT NULL,
            endereco_beneficiario TEXT NOT NULL,
            instrucoes TEXT NOT NULL DEFAULT '',
            multa DECIMAL(5, 2) NOT NULL DEFAULT 2.00,
            juros DECIMAL(5, 2) NOT NULL DEFAULT 1.00,
            desconto DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
            ativo BOOLEAN NOT NULL DEFAULT 1,
            data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Tabela BoletoGerado
        """
        CREATE TABLE IF NOT EXISTS controle_financeiro_boletogerado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_boleto VARCHAR(50) NOT NULL,
            linha_digitavel VARCHAR(54) NOT NULL,
            codigo_barras VARCHAR(44) NOT NULL,
            valor DECIMAL(10, 2) NOT NULL,
            data_vencimento DATETIME NOT NULL,
            data_pagamento DATETIME NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pendente',
            observacoes TEXT NOT NULL DEFAULT '',
            data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            controle_financeiro_id INTEGER NOT NULL,
            configuracao_id INTEGER NOT NULL,
            FOREIGN KEY (controle_financeiro_id) REFERENCES controle_financeiro_controlefinanceiro (id),
            FOREIGN KEY (configuracao_id) REFERENCES controle_financeiro_configuracaoboleto (id)
        );
        """,
        
        # Tabela Pagamento
        """
        CREATE TABLE IF NOT EXISTS controle_financeiro_pagamento (
            id VARCHAR(36) PRIMARY KEY,
            valor DECIMAL(10, 2) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pendente',
            metodo_pagamento VARCHAR(50) NOT NULL,
            dados_pagamento TEXT NOT NULL DEFAULT '{}',
            data_pagamento DATETIME NULL,
            data_aprovacao DATETIME NULL,
            observacoes TEXT NOT NULL DEFAULT '',
            data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            controle_financeiro_id INTEGER NOT NULL,
            aprovado_por_id INTEGER NULL,
            FOREIGN KEY (controle_financeiro_id) REFERENCES controle_financeiro_controlefinanceiro (id),
            FOREIGN KEY (aprovado_por_id) REFERENCES auth_user (id)
        );
        """,
        
        # Tabela CobrancaAsaas
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
        
        # Tabela NotificacaoFinanceira
        """
        CREATE TABLE IF NOT EXISTS controle_financeiro_notificacaofinanceira (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo VARCHAR(20) NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            mensagem TEXT NOT NULL,
            enviada BOOLEAN NOT NULL DEFAULT 0,
            data_envio DATETIME NULL,
            data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            controle_financeiro_id INTEGER NOT NULL,
            FOREIGN KEY (controle_financeiro_id) REFERENCES controle_financeiro_controlefinanceiro (id)
        );
        """,
        
        # Tabela SyncStatus (do models_sync.py)
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
                print(f"📊 Executando comando {i}/{len(sql_commands)}...")
                cursor.execute(sql)
                
        print("✅ Tabelas criadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def insert_default_data():
    """Insere dados padrão necessários"""
    print("📋 Inserindo dados padrão...")
    
    try:
        with connection.cursor() as cursor:
            # Inserir plano padrão se não existir
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
            
            # Inserir status de sync inicial se não existir
            cursor.execute("""
                INSERT OR IGNORE INTO controle_financeiro_syncstatus 
                (last_sync, sync_in_progress, last_error, total_charges, synced_charges, failed_charges, created_at, updated_at)
                VALUES (NULL, 0, '', 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            
        print("✅ Dados padrão inseridos com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados padrão: {e}")
        return False

def mark_migrations_as_applied():
    """Marca as migrações como aplicadas no django_migrations"""
    print("📝 Marcando migrações como aplicadas...")
    
    migrations_to_mark = [
        ('controle_financeiro', '0001_initial'),
        ('controle_financeiro', '0002_configuracaoboleto_boletogerado'),
        ('controle_financeiro', '0003_configuracaoboleto_codigo_cedente'),
        ('controle_financeiro', '0004_add_convenio_field'),
        ('controle_financeiro', '0005_cobrancaasaas'),
        ('controle_financeiro', '0006_alter_configuracaoboleto_convenio'),
        ('controle_financeiro', '0007_merge_20251023_2348'),
        ('controle_financeiro', '0008_syncstatus'),
        ('controle_financeiro', '0009_syncstatus_fix'),
    ]
    
    try:
        with connection.cursor() as cursor:
            for app, migration in migrations_to_mark:
                cursor.execute("""
                    INSERT OR IGNORE INTO django_migrations (app, name, applied)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, [app, migration])
                
        print("✅ Migrações marcadas como aplicadas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao marcar migrações: {e}")
        return False

def verify_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("🔍 Verificando instalação...")
    
    try:
        from controle_financeiro.models import (
            ControleFinanceiro, PlanoFinanceiro, CobrancaAsaas
        )
        
        # Testar consultas
        planos_count = PlanoFinanceiro.objects.count()
        controles_count = ControleFinanceiro.objects.count()
        cobrancas_count = CobrancaAsaas.objects.count()
        
        print(f"📊 PlanoFinanceiro: {planos_count} registros")
        print(f"📊 ControleFinanceiro: {controles_count} registros")
        print(f"📊 CobrancaAsaas: {cobrancas_count} registros")
        
        print("✅ Verificação concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Forçando criação das tabelas do controle_financeiro...")
    print("=" * 60)
    
    # 1. Criar tabelas manualmente
    if not create_tables_manually():
        print("❌ Falha ao criar tabelas")
        sys.exit(1)
    
    # 2. Inserir dados padrão
    if not insert_default_data():
        print("❌ Falha ao inserir dados padrão")
        sys.exit(1)
    
    # 3. Marcar migrações como aplicadas
    if not mark_migrations_as_applied():
        print("❌ Falha ao marcar migrações")
        sys.exit(1)
    
    # 4. Verificar instalação
    if not verify_installation():
        print("❌ Falha na verificação")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Tabelas do controle_financeiro criadas com sucesso!")
    print("✅ O sistema está pronto para uso no Heroku")

if __name__ == "__main__":
    main()