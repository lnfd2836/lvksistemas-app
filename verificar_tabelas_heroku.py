#!/usr/bin/env python3
"""
Script para verificar e criar tabelas no Heroku
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def main():
    print("🔍 Verificando tabelas avaliacao_qualidade...")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'avaliacao_qualidade%';")
        tables = cursor.fetchall()
        
        print(f"Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        if not tables:
            print("❌ Nenhuma tabela avaliacao_qualidade encontrada")
            print("🔧 Tentando criar tabelas...")
            
            # Forçar criação das tabelas
            execute_from_command_line(['manage.py', 'migrate', 'avaliacao_qualidade', '--run-syncdb'])
            print("✅ Comando de migração executado")
        else:
            print("✅ Tabelas já existem")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    main()