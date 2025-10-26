#!/usr/bin/env python3
"""
Script para corrigir migrações do controle_financeiro no Heroku
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection, transaction
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

def check_table_exists(table_name):
    """Verifica se uma tabela existe no banco"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=%s;
        """, [table_name])
        return cursor.fetchone() is not None

def fix_migrations():
    """Corrige as migrações do controle_financeiro"""
    print("🔧 Iniciando correção das migrações do controle_financeiro...")
    
    # Verificar se a tabela principal existe
    table_exists = check_table_exists('controle_financeiro_controlefinanceiro')
    print(f"📊 Tabela controle_financeiro_controlefinanceiro existe: {table_exists}")
    
    if not table_exists:
        print("❌ Tabela não existe. Executando migrações...")
        
        try:
            # 1. Fazer fake da migração inicial se necessário
            print("1️⃣ Verificando estado das migrações...")
            execute_from_command_line(['manage.py', 'showmigrations', 'controle_financeiro'])
            
            # 2. Executar migrações do controle_financeiro
            print("2️⃣ Executando migrações do controle_financeiro...")
            execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro', '--verbosity=2'])
            
            # 3. Verificar se a tabela foi criada
            table_exists_after = check_table_exists('controle_financeiro_controlefinanceiro')
            print(f"✅ Tabela criada com sucesso: {table_exists_after}")
            
            if table_exists_after:
                print("🎉 Migrações do controle_financeiro executadas com sucesso!")
                return True
            else:
                print("❌ Falha ao criar a tabela")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao executar migrações: {e}")
            return False
    else:
        print("✅ Tabela já existe. Verificando se todas as migrações foram aplicadas...")
        
        try:
            # Executar migrações pendentes
            execute_from_command_line(['manage.py', 'migrate', 'controle_financeiro'])
            print("✅ Migrações verificadas/aplicadas com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao verificar migrações: {e}")
            return False

def verify_models():
    """Verifica se os modelos estão funcionando"""
    print("\n🔍 Verificando modelos do controle_financeiro...")
    
    try:
        from controle_financeiro.models import (
            ControleFinanceiro, PlanoFinanceiro, Pagamento, 
            NotificacaoFinanceira, CobrancaAsaas
        )
        
        # Testar consultas básicas
        print(f"📊 PlanoFinanceiro: {PlanoFinanceiro.objects.count()} registros")
        print(f"📊 ControleFinanceiro: {ControleFinanceiro.objects.count()} registros")
        print(f"📊 CobrancaAsaas: {CobrancaAsaas.objects.count()} registros")
        print(f"📊 Pagamento: {Pagamento.objects.count()} registros")
        print(f"📊 NotificacaoFinanceira: {NotificacaoFinanceira.objects.count()} registros")
        
        print("✅ Todos os modelos estão funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar modelos: {e}")
        return False

def create_default_plan():
    """Cria um plano padrão se não existir"""
    print("\n📋 Verificando plano padrão...")
    
    try:
        from controle_financeiro.models import PlanoFinanceiro
        
        if not PlanoFinanceiro.objects.exists():
            plano = PlanoFinanceiro.objects.create(
                nome="Plano Básico",
                descricao="Plano básico para lojas",
                valor_mensal=29.90,
                dias_trial=30,
                ativo=True
            )
            print(f"✅ Plano padrão criado: {plano}")
        else:
            print("✅ Plano padrão já existe")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar plano padrão: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando correção das migrações do Heroku...")
    print("=" * 50)
    
    # 1. Corrigir migrações
    if not fix_migrations():
        print("❌ Falha ao corrigir migrações")
        sys.exit(1)
    
    # 2. Verificar modelos
    if not verify_models():
        print("❌ Falha ao verificar modelos")
        sys.exit(1)
    
    # 3. Criar plano padrão
    if not create_default_plan():
        print("❌ Falha ao criar plano padrão")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Correção das migrações concluída com sucesso!")
    print("✅ O sistema está pronto para uso")

if __name__ == "__main__":
    main()