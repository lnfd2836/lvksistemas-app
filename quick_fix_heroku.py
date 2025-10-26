#!/usr/bin/env python3
"""
Quick fix para o problema das migrações do controle_financeiro no Heroku
Execute: heroku run python quick_fix_heroku.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

print("🔧 Quick Fix - Controle Financeiro Heroku")
print("=" * 50)

try:
    # Tentar executar migrações primeiro
    print("1️⃣ Tentando migrações normais...")
    execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro'])
    print("✅ Migrações executadas!")
    
except Exception as e:
    print(f"❌ Migrações falharam: {e}")
    print("2️⃣ Criando tabela principal manualmente...")
    
    try:
        with connection.cursor() as cursor:
            # Criar apenas a tabela principal que está faltando
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
                )
            """)
            
            # Criar tabela de planos se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS controle_financeiro_planofinanceiro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR(100) NOT NULL,
                    descricao TEXT NOT NULL,
                    valor_mensal DECIMAL(10, 2) NOT NULL,
                    dias_trial INTEGER NOT NULL DEFAULT 30,
                    ativo BOOLEAN NOT NULL DEFAULT 1,
                    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Inserir plano padrão
            cursor.execute("""
                INSERT OR IGNORE INTO controle_financeiro_planofinanceiro 
                (nome, descricao, valor_mensal, dias_trial, ativo, data_criacao)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, ["Plano Básico", "Plano básico", 29.90, 30, 1])
            
            # Marcar migração principal como aplicada
            cursor.execute("""
                INSERT OR IGNORE INTO django_migrations (app, name, applied)
                VALUES ('controle_financeiro', '0001_initial', CURRENT_TIMESTAMP)
            """)
            
        print("✅ Tabelas criadas manualmente!")
        
        # Tentar migrações novamente
        print("3️⃣ Executando migrações restantes...")
        execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro'])
        
    except Exception as e2:
        print(f"❌ Erro na criação manual: {e2}")

# Verificar se funcionou
try:
    from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro
    planos = PlanoFinanceiro.objects.count()
    controles = ControleFinanceiro.objects.count()
    print(f"✅ Verificação: {planos} planos, {controles} controles")
    print("🎉 Fix concluído com sucesso!")
except Exception as e:
    print(f"❌ Ainda há problemas: {e}")