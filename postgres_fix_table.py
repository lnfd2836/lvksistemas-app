#!/usr/bin/env python3
"""
Script para corrigir tabelas no PostgreSQL do Heroku
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def main():
    print("🔧 CORREÇÃO POSTGRESQL - CONTROLE FINANCEIRO")
    print("=" * 60)
    
    try:
        with connection.cursor() as cursor:
            # 1. Verificar se a tabela existe (PostgreSQL)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'controle_financeiro_controlefinanceiro'
                );
            """)
            exists = cursor.fetchone()[0]
            print(f"📊 Tabela controle_financeiro_controlefinanceiro existe: {exists}")
            
            if not exists:
                print("❌ Tabela não existe! Criando agora...")
                
                # 2. Criar tabela PlanoFinanceiro primeiro
                print("1️⃣ Criando PlanoFinanceiro...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS controle_financeiro_planofinanceiro (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        descricao TEXT NOT NULL,
                        valor_mensal DECIMAL(10, 2) NOT NULL,
                        dias_trial INTEGER NOT NULL DEFAULT 30,
                        ativo BOOLEAN NOT NULL DEFAULT TRUE,
                        data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """)
                
                # 3. Inserir plano padrão se não existir
                print("2️⃣ Inserindo plano padrão...")
                cursor.execute("""
                    INSERT INTO controle_financeiro_planofinanceiro 
                    (nome, descricao, valor_mensal, dias_trial, ativo, data_criacao)
                    SELECT %s, %s, %s, %s, %s, NOW()
                    WHERE NOT EXISTS (
                        SELECT 1 FROM controle_financeiro_planofinanceiro WHERE nome = %s
                    );
                """, ["Plano Básico", "Plano básico para lojas", 29.90, 30, True, "Plano Básico"])
                
                # 4. Criar tabela ControleFinanceiro
                print("3️⃣ Criando ControleFinanceiro...")
                cursor.execute("""
                    CREATE TABLE controle_financeiro_controlefinanceiro (
                        id SERIAL PRIMARY KEY,
                        status VARCHAR(20) NOT NULL DEFAULT 'ativa',
                        data_inicio TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        data_vencimento TIMESTAMP WITH TIME ZONE NOT NULL,
                        data_bloqueio TIMESTAMP WITH TIME ZONE NULL,
                        data_ultimo_pagamento TIMESTAMP WITH TIME ZONE NULL,
                        valor_mensal DECIMAL(10, 2) NOT NULL,
                        valor_pago DECIMAL(10, 2) NOT NULL DEFAULT 0,
                        valor_pendente DECIMAL(10, 2) NOT NULL DEFAULT 0,
                        dias_grace_period INTEGER NOT NULL DEFAULT 5,
                        bloqueada BOOLEAN NOT NULL DEFAULT FALSE,
                        motivo_bloqueio TEXT NOT NULL DEFAULT '',
                        observacoes TEXT NOT NULL DEFAULT '',
                        data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        loja_id INTEGER NOT NULL UNIQUE,
                        plano_id INTEGER NOT NULL,
                        FOREIGN KEY (loja_id) REFERENCES lojas_loja (id),
                        FOREIGN KEY (plano_id) REFERENCES controle_financeiro_planofinanceiro (id)
                    );
                """)
                
                # 5. Criar outras tabelas essenciais
                print("4️⃣ Criando CobrancaAsaas...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS controle_financeiro_cobrancaasaas (
                        id UUID PRIMARY KEY,
                        asaas_id VARCHAR(100) NOT NULL UNIQUE,
                        customer_id VARCHAR(100) NOT NULL,
                        valor DECIMAL(10, 2) NOT NULL,
                        data_vencimento TIMESTAMP WITH TIME ZONE NOT NULL,
                        descricao TEXT NOT NULL,
                        status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
                        data_pagamento TIMESTAMP WITH TIME ZONE NULL,
                        invoice_url TEXT NOT NULL DEFAULT '',
                        bank_slip_url TEXT NOT NULL DEFAULT '',
                        invoice_number VARCHAR(100) NOT NULL DEFAULT '',
                        pix_qr_code TEXT NOT NULL DEFAULT '',
                        pix_copy_paste TEXT NOT NULL DEFAULT '',
                        pix_expires_date TIMESTAMP WITH TIME ZONE NULL,
                        api_response JSONB NOT NULL DEFAULT '{}',
                        external_reference VARCHAR(200) NOT NULL DEFAULT '',
                        observacoes TEXT NOT NULL DEFAULT '',
                        data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        controle_financeiro_id INTEGER NOT NULL,
                        FOREIGN KEY (controle_financeiro_id) REFERENCES controle_financeiro_controlefinanceiro (id)
                    );
                """)
                
                print("5️⃣ Criando SyncStatus...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS controle_financeiro_syncstatus (
                        id SERIAL PRIMARY KEY,
                        last_sync TIMESTAMP WITH TIME ZONE NULL,
                        sync_in_progress BOOLEAN NOT NULL DEFAULT FALSE,
                        last_error TEXT NOT NULL DEFAULT '',
                        total_charges INTEGER NOT NULL DEFAULT 0,
                        synced_charges INTEGER NOT NULL DEFAULT 0,
                        failed_charges INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """)
                
                # 6. Inserir registro inicial no SyncStatus
                cursor.execute("""
                    INSERT INTO controle_financeiro_syncstatus 
                    (last_sync, sync_in_progress, last_error, total_charges, synced_charges, failed_charges, created_at, updated_at)
                    SELECT NULL, FALSE, '', 0, 0, 0, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM controle_financeiro_syncstatus);
                """)
                
                # 7. Marcar migrações como aplicadas
                print("6️⃣ Marcando migrações como aplicadas...")
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
                        INSERT INTO django_migrations (app, name, applied)
                        SELECT %s, %s, NOW()
                        WHERE NOT EXISTS (
                            SELECT 1 FROM django_migrations 
                            WHERE app = %s AND name = %s
                        );
                    """, ['controle_financeiro', migration, 'controle_financeiro', migration])
                
                print("✅ TABELAS CRIADAS COM SUCESSO!")
                
            else:
                print("✅ Tabela já existe!")
            
            # 8. Verificar se funcionou
            print("7️⃣ Verificando criação...")
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'controle_financeiro_controlefinanceiro'
                );
            """)
            final_check = cursor.fetchone()[0]
            print(f"📊 Verificação final: {final_check}")
            
            # 9. Contar registros
            cursor.execute("SELECT COUNT(*) FROM controle_financeiro_planofinanceiro")
            planos_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM controle_financeiro_controlefinanceiro")
            controles_count = cursor.fetchone()[0]
            
            print(f"📊 Planos: {planos_count}")
            print(f"📊 Controles: {controles_count}")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        
        # Tentar via Django ORM como fallback
        print("\n🔧 Tentando via Django ORM...")
        try:
            from controle_financeiro.models import PlanoFinanceiro, ControleFinanceiro
            
            # Criar plano se não existir
            if not PlanoFinanceiro.objects.filter(nome="Plano Básico").exists():
                PlanoFinanceiro.objects.create(
                    nome="Plano Básico",
                    descricao="Plano básico para lojas",
                    valor_mensal=29.90,
                    dias_trial=30,
                    ativo=True
                )
                print("✅ Plano criado via ORM!")
            
            planos = PlanoFinanceiro.objects.count()
            controles = ControleFinanceiro.objects.count()
            print(f"📊 Via ORM - Planos: {planos}, Controles: {controles}")
            
        except Exception as e2:
            print(f"❌ Erro no ORM também: {e2}")
            
            # Última tentativa: executar migrações
            print("\n🔧 Última tentativa: executar migrações...")
            try:
                execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro', '--fake-initial'])
                execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro'])
                print("✅ Migrações executadas!")
            except Exception as e3:
                print(f"❌ Migrações falharam: {e3}")
    
    print("\n" + "=" * 60)
    print("🎉 PROCESSO CONCLUÍDO!")

if __name__ == "__main__":
    main()