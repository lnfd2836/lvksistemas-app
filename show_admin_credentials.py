#!/usr/bin/env python3
"""
Script para mostrar credenciais de admin disponíveis
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User


def show_all_credentials():
    """Mostra todas as credenciais de admin disponíveis"""
    
    print("🔐 CREDENCIAIS DE ADMIN DISPONÍVEIS")
    print("=" * 50)
    
    # Credenciais conhecidas do arquivo create_superuser.py
    known_credentials = [
        {
            'username': 'admin',
            'password': 'LVK@2024#Admin',
            'email': 'admin@lvksistemas.com.br',
            'description': 'Admin padrão'
        },
        {
            'username': 'lvk_admin', 
            'password': 'LVKSistemas@2024!',
            'email': 'suporte@lvksistemas.com.br',
            'description': 'Admin personalizado'
        },
        {
            'username': 'Kiko',
            'password': 'Kiko@LVK2024!',
            'email': 'email_do_kiko',
            'description': 'Usuário Kiko ativado'
        }
    ]
    
    print("📋 CREDENCIAIS CONHECIDAS:")
    print("-" * 30)
    
    for i, cred in enumerate(known_credentials, 1):
        # Verificar se usuário existe no banco
        try:
            user = User.objects.get(username=cred['username'])
            status = "✅ EXISTE" if user.is_active else "⚠️ INATIVO"
            superuser = "🔑 SUPER" if user.is_superuser else "👤 NORMAL"
        except User.DoesNotExist:
            status = "❌ NÃO EXISTE"
            superuser = ""
        
        print(f"{i}️⃣ {cred['description']}")
        print(f"   👤 Username: {cred['username']}")
        print(f"   🔑 Password: {cred['password']}")
        print(f"   📧 Email: {cred['email']}")
        print(f"   📊 Status: {status} {superuser}")
        print()
    
    # Mostrar todos os superusuários do banco
    print("🗄️ SUPERUSUÁRIOS NO BANCO DE DADOS:")
    print("-" * 35)
    
    superusers = User.objects.filter(is_superuser=True)
    
    for user in superusers:
        status = "✅ ATIVO" if user.is_active else "❌ INATIVO"
        last_login = user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else "Nunca"
        
        print(f"👤 {user.username}")
        print(f"   📧 {user.email}")
        print(f"   📊 {status}")
        print(f"   🕐 Último login: {last_login}")
        print()
    
    # URL de acesso
    print("🌐 URL DE ACESSO:")
    print("-" * 15)
    print("🔗 https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
    print()
    
    # Instruções
    print("💡 INSTRUÇÕES:")
    print("-" * 12)
    print("1. Use qualquer uma das credenciais acima")
    print("2. Acesse a URL do admin")
    print("3. Faça login com username e password")
    print("4. ⚠️ ALTERE A SENHA após o primeiro login!")
    print()
    
    # Comando para resetar senha se necessário
    print("🔧 PARA RESETAR SENHA (se necessário):")
    print("-" * 35)
    print("heroku run python manage.py shell -c \"")
    print("from django.contrib.auth.models import User")
    print("user = User.objects.get(username='admin')")
    print("user.set_password('nova_senha_aqui')")
    print("user.save()\"")


def test_login_credentials():
    """Testa se as credenciais funcionam"""
    
    print("\n🧪 TESTANDO CREDENCIAIS:")
    print("-" * 25)
    
    test_credentials = [
        ('admin', 'LVK@2024#Admin'),
        ('lvk_admin', 'LVKSistemas@2024!'),
        ('Kiko', 'Kiko@LVK2024!')
    ]
    
    from django.contrib.auth import authenticate
    
    for username, password in test_credentials:
        try:
            user = authenticate(username=username, password=password)
            if user and user.is_superuser:
                print(f"✅ {username}: Credenciais válidas")
            elif user:
                print(f"⚠️ {username}: Usuário válido mas não é superuser")
            else:
                print(f"❌ {username}: Credenciais inválidas")
        except Exception as e:
            print(f"💥 {username}: Erro ao testar - {str(e)}")


def main():
    print("🚀 VERIFICAÇÃO DE CREDENCIAIS DE ADMIN")
    print("=" * 60)
    
    show_all_credentials()
    test_login_credentials()
    
    print("\n🎯 RESUMO:")
    print("Use as credenciais mostradas acima para acessar o admin do Django")
    print("URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")


if __name__ == '__main__':
    main()