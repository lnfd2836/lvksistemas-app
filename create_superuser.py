#!/usr/bin/env python
"""
Script para criar superusuário no Heroku
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    sys.exit(1)

from django.contrib.auth.models import User

def create_superuser():
    """Cria superusuário"""
    print("🔧 CRIANDO SUPERUSUÁRIO")
    print("=" * 30)
    
    # Dados do superusuário
    username = 'admin'
    email = 'admin@lvksistemas.com.br'
    password = 'LVK@2024#Admin'  # Senha temporária - deve ser alterada
    
    try:
        # Verificar se já existe
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Usuário '{username}' já existe!")
            
            # Atualizar usuário existente
            user = User.objects.get(username=username)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.email = email
            user.set_password(password)
            user.save()
            
            print(f"✅ Usuário '{username}' atualizado com sucesso!")
        else:
            # Criar novo usuário
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Superusuário '{username}' criado com sucesso!")
        
        print(f"👤 Username: {username}")
        print(f"📧 Email: {email}")
        print(f"🔑 Senha: {password}")
        print(f"🌐 Admin URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
        print()
        print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def create_custom_superuser():
    """Cria superusuário personalizado"""
    print("🔧 CRIANDO SUPERUSUÁRIO PERSONALIZADO")
    print("=" * 40)
    
    # Dados personalizados
    username = 'lvk_admin'
    email = 'suporte@lvksistemas.com.br'
    password = 'LVKSistemas@2024!'
    
    try:
        # Verificar se já existe
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Usuário '{username}' já existe!")
            user = User.objects.get(username=username)
        else:
            # Criar novo usuário
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Superusuário '{username}' criado com sucesso!")
        
        # Garantir permissões
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print(f"👤 Username: {username}")
        print(f"📧 Email: {email}")
        print(f"🔑 Senha: {password}")
        print(f"🌐 Admin URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário personalizado: {e}")
        return False

def activate_existing_user():
    """Ativa usuário Kiko existente"""
    print("🔧 ATIVANDO USUÁRIO KIKO")
    print("=" * 25)
    
    try:
        user = User.objects.get(username='Kiko')
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        
        # Resetar senha
        new_password = 'Kiko@LVK2024!'
        user.set_password(new_password)
        user.save()
        
        print(f"✅ Usuário 'Kiko' ativado com sucesso!")
        print(f"👤 Username: Kiko")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Nova senha: {new_password}")
        print(f"🌐 Admin URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
        
        return True
        
    except User.DoesNotExist:
        print("❌ Usuário 'Kiko' não encontrado!")
        return False
    except Exception as e:
        print(f"❌ Erro ao ativar usuário Kiko: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 GERENCIAMENTO DE SUPERUSUÁRIOS - HEROKU")
    print("=" * 45)
    
    success_count = 0
    
    # Opção 1: Ativar usuário Kiko existente
    print("\n1️⃣ Ativando usuário Kiko existente...")
    if activate_existing_user():
        success_count += 1
    
    # Opção 2: Criar admin padrão
    print("\n2️⃣ Criando admin padrão...")
    if create_superuser():
        success_count += 1
    
    # Opção 3: Criar admin personalizado
    print("\n3️⃣ Criando admin personalizado...")
    if create_custom_superuser():
        success_count += 1
    
    print(f"\n🎉 {success_count} operação(ões) realizada(s) com sucesso!")
    
    # Listar todos os superusuários
    print("\n📋 SUPERUSUÁRIOS DISPONÍVEIS:")
    print("-" * 30)
    
    superusers = User.objects.filter(is_superuser=True, is_active=True)
    for user in superusers:
        print(f"👤 {user.username} ({user.email})")
    
    print(f"\n🌐 Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
    print("⚠️  Lembre-se de alterar as senhas após o primeiro login!")

if __name__ == '__main__':
    main()