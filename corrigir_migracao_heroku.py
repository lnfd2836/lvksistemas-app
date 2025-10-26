#!/usr/bin/env python3
"""
Script para corrigir problemas de migração no Heroku
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
import sys

def verificar_tabelas_existentes():
    """Verifica quais tabelas existem no banco"""
    
    print("🔍 Verificando tabelas existentes no banco...")
    
    with connection.cursor() as cursor:
        # SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"📊 Total de tabelas encontradas: {len(tabelas)}")
        
        tabelas_importantes = [
            'controle_financeiro_controlefinanceiro',
            'modulos_tipoloja',
            'lojas_loja',
            'auth_user',
            'django_migrations'
        ]
        
        for tabela in tabelas_importantes:
            existe = any(tabela in t[0] for t in tabelas)
            status = "✅" if existe else "❌"
            print(f"   {status} {tabela}")
        
        return [t[0] for t in tabelas]

def executar_migracoes():
    """Executa as migrações necessárias"""
    
    print("\n🔧 Executando migrações...")
    
    try:
        # Fazer migrações
        print("   📝 Criando arquivos de migração...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("   🚀 Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("   ✅ Migrações concluídas!")
        
    except Exception as e:
        print(f"   ❌ Erro nas migrações: {str(e)}")
        return False
    
    return True

def criar_superuser_se_necessario():
    """Cria superuser se não existir"""
    
    print("\n👤 Verificando superuser...")
    
    try:
        from django.contrib.auth.models import User
        
        if not User.objects.filter(is_superuser=True).exists():
            print("   📝 Criando superuser admin...")
            
            User.objects.create_superuser(
                username='admin',
                email='admin@lvksistemas.com.br',
                password='admin123'
            )
            
            print("   ✅ Superuser criado: admin / admin123")
        else:
            print("   ✅ Superuser já existe")
            
    except Exception as e:
        print(f"   ❌ Erro ao criar superuser: {str(e)}")

def verificar_apps_instalados():
    """Verifica se todos os apps estão instalados"""
    
    print("\n📱 Verificando apps instalados...")
    
    from django.conf import settings
    
    apps_necessarios = [
        'controle_financeiro',
        'modulos',
        'lojas',
        'usuarios',
        'dashboard',
        'planos',
        'avaliacao_qualidade'
    ]
    
    for app in apps_necessarios:
        if app in settings.INSTALLED_APPS:
            print(f"   ✅ {app}")
        else:
            print(f"   ❌ {app} - NÃO INSTALADO")

def main():
    """Função principal"""
    
    print("🚀 Iniciando correção de migrações no Heroku...")
    
    try:
        # Verificar apps
        verificar_apps_instalados()
        
        # Verificar tabelas antes
        print("\n" + "="*50)
        print("ANTES DAS MIGRAÇÕES")
        print("="*50)
        tabelas_antes = verificar_tabelas_existentes()
        
        # Executar migrações
        if executar_migracoes():
            # Verificar tabelas depois
            print("\n" + "="*50)
            print("DEPOIS DAS MIGRAÇÕES")
            print("="*50)
            tabelas_depois = verificar_tabelas_existentes()
            
            # Mostrar diferença
            novas_tabelas = set(tabelas_depois) - set(tabelas_antes)
            if novas_tabelas:
                print(f"\n🆕 Novas tabelas criadas: {len(novas_tabelas)}")
                for tabela in sorted(novas_tabelas):
                    print(f"   + {tabela}")
        
        # Criar superuser
        criar_superuser_se_necessario()
        
        print("\n✅ Correção concluída!")
        print("\n📋 Próximos passos:")
        print("1. Testar acesso ao sistema")
        print("2. Verificar se as páginas carregam")
        print("3. Testar login personalizado")
        
    except Exception as e:
        print(f"\n❌ Erro durante correção: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()