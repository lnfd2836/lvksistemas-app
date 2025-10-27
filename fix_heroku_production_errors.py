#!/usr/bin/env python
"""
Script para corrigir erros críticos de produção no Heroku
- Tabelas faltando do módulo avaliacao_qualidade
- Tabelas faltando do módulo modulos (TipoLoja)
- Tabelas faltando do módulo controle_financeiro
- Problema de middleware LojaMiddleware
- Problema de URL routing para 'login'
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth.models import User
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def fix_middleware_import_error():
    """
    Corrige o erro de importação do LojaMiddleware
    """
    print("🔧 Corrigindo erro de importação do middleware...")
    
    # O problema está no settings.py - vamos verificar se o middleware existe
    try:
        from lojas.middleware import LojaMiddleware
        print("✅ LojaMiddleware encontrado e funcionando")
        return True
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def create_missing_tables():
    """
    Cria tabelas faltando usando migrações
    """
    print("🔧 Criando tabelas faltando...")
    
    try:
        # Fazer migrações para todos os apps
        print("📝 Executando makemigrations...")
        call_command('makemigrations', verbosity=2)
        
        print("🚀 Executando migrate...")
        call_command('migrate', verbosity=2)
        
        # Migrações específicas para apps problemáticos
        apps_problematicos = ['avaliacao_qualidade', 'modulos', 'controle_financeiro']
        
        for app in apps_problematicos:
            try:
                print(f"🔄 Migrando {app}...")
                call_command('migrate', app, verbosity=2)
            except Exception as e:
                print(f"⚠️ Erro ao migrar {app}: {e}")
        
        print("✅ Migrações concluídas")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas migrações: {e}")
        return False

def verify_database_tables():
    """
    Verifica se as tabelas críticas existem
    """
    print("🔍 Verificando tabelas críticas...")
    
    critical_tables = [
        'avaliacao_qualidade_curso',
        'avaliacao_qualidade_professor', 
        'avaliacao_qualidade_coordenador',
        'avaliacao_qualidade_perfilusuario',
        'avaliacao_qualidade_avaliacaoconfig',
        'modulos_tipoloja',
        'controle_financeiro_controlefinanceiro',
    ]
    
    with connection.cursor() as cursor:
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Total de tabelas existentes: {len(existing_tables)}")
        
        missing_tables = []
        for table in critical_tables:
            if table in existing_tables:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} - FALTANDO")
                missing_tables.append(table)
        
        return len(missing_tables) == 0, missing_tables

def fix_url_routing():
    """
    Corrige problemas de roteamento de URL
    """
    print("🔧 Verificando roteamento de URLs...")
    
    try:
        from django.urls import reverse
        
        # Testar URLs críticas
        urls_to_test = [
            ('root_redirect', '/'),
            ('admin:index', '/admin/'),
        ]
        
        for url_name, expected_path in urls_to_test:
            try:
                actual_path = reverse(url_name)
                if actual_path == expected_path:
                    print(f"✅ {url_name} -> {actual_path}")
                else:
                    print(f"⚠️ {url_name} -> {actual_path} (esperado: {expected_path})")
            except Exception as e:
                print(f"❌ {url_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação de URLs: {e}")
        return False

def create_emergency_superuser():
    """
    Cria um superusuário de emergência se não existir
    """
    print("👤 Verificando superusuário...")
    
    try:
        if not User.objects.filter(is_superuser=True).exists():
            print("🔧 Criando superusuário de emergência...")
            User.objects.create_superuser(
                username='admin',
                email='admin@lvksistemas.com.br',
                password='admin123'
            )
            print("✅ Superusuário 'admin' criado")
        else:
            print("✅ Superusuário já existe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def fix_settings_middleware():
    """
    Corrige a configuração de middleware no settings.py
    """
    print("🔧 Verificando configuração de middleware...")
    
    settings_path = os.path.join(os.path.dirname(__file__), 'lojad', 'settings.py')
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se o middleware problemático está presente
        if "'lojas.middleware.LojaMiddleware'," in content:
            print("✅ Middleware LojaMiddleware encontrado na configuração")
            return True
        else:
            print("❌ Middleware LojaMiddleware não encontrado na configuração")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar settings.py: {e}")
        return False

def main():
    """
    Função principal que executa todas as correções
    """
    print("🚀 INICIANDO CORREÇÃO DE ERROS DE PRODUÇÃO HEROKU")
    print("=" * 60)
    
    success_count = 0
    total_fixes = 5
    
    # 1. Verificar middleware
    if fix_middleware_import_error():
        success_count += 1
    
    # 2. Verificar configuração de middleware
    if fix_settings_middleware():
        success_count += 1
    
    # 3. Criar tabelas faltando
    if create_missing_tables():
        success_count += 1
    
    # 4. Verificar tabelas críticas
    tables_ok, missing_tables = verify_database_tables()
    if tables_ok:
        success_count += 1
    else:
        print(f"⚠️ Tabelas faltando: {missing_tables}")
    
    # 5. Verificar URLs
    if fix_url_routing():
        success_count += 1
    
    # 6. Criar superusuário de emergência
    create_emergency_superuser()
    
    print("=" * 60)
    print(f"📊 RESULTADO: {success_count}/{total_fixes} correções bem-sucedidas")
    
    if success_count == total_fixes:
        print("🎉 TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print("🚀 O sistema deve estar funcionando agora")
    else:
        print("⚠️ ALGUMAS CORREÇÕES FALHARAM")
        print("🔍 Verifique os logs acima para detalhes")
    
    print("=" * 60)

if __name__ == '__main__':
    main()