#!/usr/bin/env python
"""
Script para criar o usuário Wagner no Heroku
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from django.utils import timezone

def create_wagner_user():
    print('=== CRIANDO USUÁRIO WAGNER ===')
    
    # Verificar se já existe
    if User.objects.filter(username='waner').exists():
        print('❌ Usuário waner já existe')
        user = User.objects.get(username='waner')
        print(f'   Email: {user.email}')
        print(f'   Ativo: {user.is_active}')
        print(f'   Super usuário: {user.is_superuser}')
        
        # Verificar se a senha está correta
        if user.check_password('zDK$hNVlIVA&'):
            print('✅ Senha está correta')
        else:
            print('❌ Senha incorreta, atualizando...')
            user.set_password('zDK$hNVlIVA&')
            user.save()
            print('✅ Senha atualizada')
            
    else:
        # Criar usuário Wagner
        user = User.objects.create_user(
            username='waner',
            email='wagner@lvksistemas.com.br',
            first_name='Wagner',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        
        # Definir senha
        user.set_password('zDK$hNVlIVA&')
        user.save()
        
        print('✅ Usuário Wagner criado com sucesso!')
        print(f'   Username: {user.username}')
        print(f'   Email: {user.email}')
        print(f'   Super usuário: {user.is_superuser}')
    
    # Criar ou atualizar perfil
    profile, created = PerfilUsuario.objects.get_or_create(
        user=user,
        defaults={
            'is_super_admin': True,
            'requires_password_change': True,
            'provisional_password_created': timezone.now()
        }
    )
    
    if created:
        print('✅ Perfil criado')
    else:
        print('✅ Perfil já existia')
    
    print()
    print('=== DADOS DE ACESSO ===')
    print('URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/')
    print('Usuário: waner')
    print('Senha: zDK$hNVlIVA&')
    print()
    print('⚠️  IMPORTANTE: O usuário será obrigado a trocar a senha no primeiro login')

if __name__ == '__main__':
    create_wagner_user()