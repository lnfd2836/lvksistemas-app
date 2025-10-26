#!/usr/bin/env python3
"""
Script para verificar tabelas no PostgreSQL do Heroku
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import connection

def verificar_tabelas_postgres():
    """Verifica tabelas no PostgreSQL"""
    
    print("🔍 Verificando tabelas no PostgreSQL do Heroku...")
    
    with connection.cursor() as cursor:
        # PostgreSQL - listar tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tabelas = cursor.fetchall()
        
        print(f"📊 Total de tabelas encontradas: {len(tabelas)}")
        
        # Tabelas importantes para verificar
        tabelas_importantes = [
            'controle_financeiro_controlefinanceiro',
            'modulos_tipoloja',
            'lojas_loja',
            'auth_user',
            'django_migrations',
            'lojas_loginpersonalizado',
            'avaliacao_qualidade_curso'
        ]
        
        tabelas_existentes = [t[0] for t in tabelas]
        
        print("\n📋 Verificação de tabelas importantes:")
        for tabela in tabelas_importantes:
            existe = tabela in tabelas_existentes
            status = "✅" if existe else "❌"
            print(f"   {status} {tabela}")
        
        print(f"\n📝 Todas as tabelas encontradas:")
        for tabela in sorted(tabelas_existentes):
            print(f"   • {tabela}")
        
        return tabelas_existentes

def verificar_dados_importantes():
    """Verifica se existem dados importantes"""
    
    print("\n🔍 Verificando dados importantes...")
    
    try:
        from django.contrib.auth.models import User
        total_users = User.objects.count()
        print(f"   👤 Usuários: {total_users}")
        
        if total_users > 0:
            superusers = User.objects.filter(is_superuser=True).count()
            print(f"   👑 Superusers: {superusers}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar usuários: {str(e)}")
    
    try:
        from lojas.models import Loja
        total_lojas = Loja.objects.count()
        print(f"   🏪 Lojas: {total_lojas}")
        
        if total_lojas > 0:
            for loja in Loja.objects.all():
                print(f"      • {loja.nome} ({loja.status})")
    except Exception as e:
        print(f"   ❌ Erro ao verificar lojas: {str(e)}")
    
    try:
        from lojas.models_login import LoginPersonalizado
        total_logins = LoginPersonalizado.objects.count()
        print(f"   🔐 Logins personalizados: {total_logins}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar logins personalizados: {str(e)}")

def testar_urls_importantes():
    """Testa se as URLs importantes funcionam"""
    
    print("\n🧪 Testando URLs importantes...")
    
    from django.test import Client
    client = Client()
    
    urls_teste = [
        ('/', 'Página inicial'),
        ('/dashboard/', 'Dashboard principal'),
        ('/login/', 'Login principal'),
    ]
    
    for url, descricao in urls_teste:
        try:
            response = client.get(url)
            status = "✅" if response.status_code in [200, 302] else "❌"
            print(f"   {status} {descricao}: {url} (Status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ {descricao}: {url} - Erro: {str(e)}")

def main():
    """Função principal"""
    
    print("🚀 Verificando status do Heroku PostgreSQL...")
    
    try:
        # Verificar configuração do banco
        from django.conf import settings
        db_config = settings.DATABASES['default']
        print(f"🗄️ Banco: {db_config['ENGINE']}")
        print(f"📍 Host: {db_config.get('HOST', 'N/A')}")
        
        # Verificar tabelas
        tabelas = verificar_tabelas_postgres()
        
        # Verificar dados
        verificar_dados_importantes()
        
        # Testar URLs
        testar_urls_importantes()
        
        print("\n✅ Verificação concluída!")
        
        # Diagnóstico final
        if 'controle_financeiro_controlefinanceiro' in tabelas:
            print("✅ Tabela controle_financeiro_controlefinanceiro existe")
        else:
            print("❌ Tabela controle_financeiro_controlefinanceiro NÃO existe")
            
        if 'modulos_tipoloja' in tabelas:
            print("✅ Tabela modulos_tipoloja existe")
        else:
            print("❌ Tabela modulos_tipoloja NÃO existe")
        
    except Exception as e:
        print(f"\n❌ Erro durante verificação: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()