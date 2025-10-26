#!/usr/bin/env python3
"""
Script simples para executar migrações no Heroku
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def main():
    """Executa migrações no Heroku"""
    
    print("🚀 Executando migrações no Heroku...")
    
    try:
        # Executar migrações
        print("📝 Fazendo migrações...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("🔧 Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migrações concluídas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()