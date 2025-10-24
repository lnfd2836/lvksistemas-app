#!/usr/bin/env python
"""
Script para criar usuário temporário para transferir administração
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction


def criar_usuario_temporario():
    """Cria um usuário temporário para administração"""
    try:
        with transaction.atomic():
            # Verificar se existe temp_admin2 primeiro
            if User.objects.filter(username='temp_admin2').exists():
                user = User.objects.get(username='temp_admin2')
                print(f"✅ Usuário temporário 2 já existe: ID {user.id}")
                return user
            
            # Criar usuário temporário 2
            temp_user = User.objects.create_user(
                username='temp_admin2',
                email='temp2@lvksistemas.com',
                password='TempAdmin123!',
                first_name='Administrador',
                last_name='Temporário 2',
                is_superuser=True,
                is_staff=True,
                is_active=True
            )
            
            print(f"✅ Usuário temporário 2 criado com sucesso!")
            print(f"   ID: {temp_user.id}")
            print(f"   Username: {temp_user.username}")
            print(f"   Email: {temp_user.email}")
            
            return temp_user
            
            # Verificar se já existe temp_admin (código antigo)
            if User.objects.filter(username='temp_admin').exists():
                user = User.objects.get(username='temp_admin')
                print(f"✅ Usuário temporário já existe: ID {user.id}")
                return user
            
            print(f"✅ Usuário temporário criado com sucesso!")
            print(f"   ID: {temp_user.id}")
            print(f"   Username: {temp_user.username}")
            print(f"   Email: {temp_user.email}")
            
            return temp_user
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário temporário: {e}")
        return None


if __name__ == "__main__":
    print("🔧 Criando usuário temporário para administração...")
    criar_usuario_temporario()