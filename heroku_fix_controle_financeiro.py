#!/usr/bin/env python3
"""
Script simples para corrigir o controle_financeiro no Heroku
Execute: heroku run python heroku_fix_controle_financeiro.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def main():
    print("🔧 Corrigindo controle_financeiro no Heroku...")
    
    try:
        # 1. Executar migrações forçadamente
        print("1️⃣ Executando migrações...")
        execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro', '--fake-initial'])
        
        # 2. Executar todas as migrações pendentes
        print("2️⃣ Aplicando migrações pendentes...")
        execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro'])
        
        # 3. Verificar se funcionou
        print("3️⃣ Verificando modelos...")
        from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro
        
        planos = PlanoFinanceiro.objects.count()
        controles = ControleFinanceiro.objects.count()
        
        print(f"✅ PlanoFinanceiro: {planos} registros")
        print(f"✅ ControleFinanceiro: {controles} registros")
        
        # 4. Criar plano padrão se necessário
        if planos == 0:
            print("4️⃣ Criando plano padrão...")
            PlanoFinanceiro.objects.create(
                nome="Plano Básico",
                descricao="Plano básico para lojas",
                valor_mensal=29.90,
                dias_trial=30,
                ativo=True
            )
            print("✅ Plano padrão criado!")
        
        print("🎉 Correção concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        
        # Tentar criar tabelas manualmente
        print("🔧 Tentando criar tabelas manualmente...")
        
        try:
            with connection.cursor() as cursor:
                # Criar tabela principal se não existir
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS controle_financeiro_controlefinanceiro (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        status VARCHAR(20) NOT NULL DEFAULT 'ativa',
                        data_inicio DATETIME NOT NULL,
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
                        data_criacao DATETIME NOT NULL,
                        data_atualizacao DATETIME NOT NULL,
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
                        data_criacao DATETIME NOT NULL
                    )
                """)
                
                print("✅ Tabelas criadas manualmente!")
                
                # Marcar migrações como aplicadas
                cursor.execute("""
                    INSERT OR IGNORE INTO django_migrations (app, name, applied)
                    VALUES ('controle_financeiro', '0001_initial', datetime('now'))
                """)
                
                print("✅ Migrações marcadas como aplicadas!")
                
        except Exception as e2:
            print(f"❌ Erro ao criar tabelas manualmente: {e2}")

if __name__ == "__main__":
    main()