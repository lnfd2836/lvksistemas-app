#!/usr/bin/env python3
"""
Script para criar superusuário no Heroku
"""
import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Cria um superusuário se não existir"""
    
    # Verifica se já existe um superusuário
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superusuário já existe!")
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            print(f"   - {user.username} ({user.email})")
        return
    
    # Cria superusuário padrão
    username = 'admin'
    email = 'admin@lvksistemas.com.br'
    password = 'admin123456'  # Senha temporária
    
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Administrador',
            last_name='Sistema'
        )
        
        print("✅ Superusuário criado com sucesso!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Senha: {password}")
        print("   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")

if __name__ == '__main__':
    create_superuser()