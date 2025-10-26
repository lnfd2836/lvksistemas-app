#!/usr/bin/env python
"""
Script para corrigir migrações do app avaliacao_qualidade no Heroku
Execute este script no Heroku usando: heroku run python fix_avaliacao_qualidade_migrations.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.conf import settings

def check_table_exists(table_name, cursor=None):
    """Verifica se uma tabela existe no banco de dados"""
    if cursor is None:
        cursor = connection.cursor()
    
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, [table_name])
    else:
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name=%s
        """, [table_name])
    
    return cursor.fetchone() is not None

def main():
    print("="*60)
    print("Correção de Migrações - avaliacao_qualidade")
    print("="*60)
    
    # Verificar se a tabela existe
    table_name = 'avaliacao_qualidade_perfilusuario'
    exists = check_table_exists(table_name)
    
    print(f"\nVerificando tabela: {table_name}")
    print(f"Tabela existe: {exists}")
    
    if exists:
        print("\nA tabela já existe. Nenhuma ação necessária.")
        return
    
    print("\nA tabela não existe. Executando migrações...")
    
    try:
        # Executar migrações apenas do app avaliacao_qualidade
        call_command('migrate', 'avaliacao_qualidade', verbosity=2, interactive=False)
        print("\nMigrações executadas com sucesso!")
        
        # Verificar novamente
        exists_after = check_table_exists(table_name)
        if exists_after:
            print(f"A tabela {table_name} foi criada com sucesso!")
        else:
            print(f"AVISO: A tabela {table_name} ainda não existe.")
            
    except Exception as e:
        print(f"\nErro ao executar migrações: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

