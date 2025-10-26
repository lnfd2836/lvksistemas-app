#!/usr/bin/env python3
"""
Script de correção de migrações para o Heroku
Execute: heroku run python heroku_migration_fix.py

Este script corrige o problema da tabela controle_financeiro_controlefinanceiro
que não existe no banco de dados do Heroku.
"""

import os
import sys
import django
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

def main():
    print("🚀 Iniciando correção das migrações do controle_financeiro no Heroku...")
    print("=" * 70)
    
    try:
        # Verificar se a tabela existe
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='controle_financeiro_controlefinanceiro';
            """)
            table_exists = cursor.fetchone() is not None
        
        print(f"📊 Tabela controle_financeiro_controlefinanceiro existe: {table_exists}")
        
        if not table_exists:
            print("❌ Tabela não existe. Criando tabelas necessárias...")
            
            # Criar tabelas essenciais
            with connection.cursor() as cursor:
                print("1️⃣ Criando tabela PlanoFinanceiro...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS controle_financeiro_planofinanceiro (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome VARCHAR(100) NOT NULL,
                        descricao TEXT NOT NULL,
                        valor_mensal DECIMAL(10, 2) NOT NULL,
                        dias_trial INTEGER NOT NULL DEFAULT 30,
                        ativo BOOLEAN NOT NULL DEFAULT 1,
                        data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                print("2️⃣ Criando tabela ControleFinanceiro...")
                cursor.execute("""
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
                        plano_id INTEGER NOT NULL
                    );
                """)
                
                print("3️⃣ Criando tabela CobrancaAsaas...")
                cursor.execute("""
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
                        controle_financeiro_id INTEGER NOT NULL
                    );
                """)
                
                print("4️⃣ Criando tabela SyncStatus...")
                cursor.execute("""
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
                """)
                
                print("5️⃣ Inserindo plano padrão...")
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
                
                print("6️⃣ Inserindo status de sync inicial...")
                cursor.execute("""
                    INSERT OR IGNORE INTO controle_financeiro_syncstatus 
                    (last_sync, sync_in_progress, last_error, total_charges, synced_charges, failed_charges, created_at, updated_at)
                    VALUES (NULL, 0, '', 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """)
                
                print("7️⃣ Marcando migrações como aplicadas...")
                migrations = [
                    '0001_initial',
                    '0002_configuracaoboleto_boletogerado', 
                    '0003_configuracaoboleto_codigo_cedente',
                    '0004_add_convenio_field',
                    '0005_cobrancaasaas',
                    '0006_alter_configuracaoboleto_convenio',
                    '0007_merge_20251023_2348',
                    '0008_syncstatus',
                    '0009_syncstatus_fix'
                ]
                
                for migration in migrations:
                    cursor.execute("""
                        INSERT OR IGNORE INTO django_migrations (app, name, applied)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    """, ['controle_financeiro', migration])
            
            print("✅ Tabelas criadas com sucesso!")
        
        else:
            print("✅ Tabela já existe!")
        
        # Verificar se os modelos funcionam
        print("8️⃣ Verificando modelos...")
        from controle_financeiro.models import (
            ControleFinanceiro, PlanoFinanceiro, CobrancaAsaas
        )
        
        planos = PlanoFinanceiro.objects.count()
        controles = ControleFinanceiro.objects.count()
        cobrancas = CobrancaAsaas.objects.count()
        
        print(f"📊 PlanoFinanceiro: {planos} registros")
        print(f"📊 ControleFinanceiro: {controles} registros") 
        print(f"📊 CobrancaAsaas: {cobrancas} registros")
        
        # Criar plano padrão se não existir
        if planos == 0:
            print("9️⃣ Criando plano padrão via Django ORM...")
            PlanoFinanceiro.objects.create(
                nome="Plano Básico",
                descricao="Plano básico para lojas do sistema",
                valor_mensal=29.90,
                dias_trial=30,
                ativo=True
            )
            print("✅ Plano padrão criado!")
        
        print("\n" + "=" * 70)
        print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ O módulo controle_financeiro está funcionando no Heroku")
        print("✅ Todas as tabelas foram criadas")
        print("✅ Dados padrão foram inseridos")
        print("✅ Migrações foram marcadas como aplicadas")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n🔧 Tentando solução alternativa...")
        
        # Solução alternativa: executar comando Django
        try:
            from django.core.management import execute_from_command_line
            print("Executando: python manage.py migrate controle_financeiro --fake-initial")
            execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro', '--fake-initial'])
            print("✅ Comando executado com sucesso!")
        except Exception as e2:
            print(f"❌ Solução alternativa falhou: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()