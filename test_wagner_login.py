#!/usr/bin/env python
"""
Script para testar o login do usuário Wagner
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def test_wagner_login():
    print('=== TESTANDO LOGIN DO WAGNER ===')
    
    # Testar autenticação
    user = authenticate(username='waner', password='zDK$hNVlIVA&')
    if user:
        print('✅ SUCESSO: Wagner pode fazer login!')
        print(f'   Username: {user.username}')
        print(f'   Email: {user.email}')
        print(f'   Super usuário: {user.is_superuser}')
        print(f'   Ativo: {user.is_active}')
        
        # Verificar perfil
        try:
            from usuarios.models import PerfilUsuario
            profile = PerfilUsuario.objects.get(user=user)
            print(f'   Perfil Super Admin: {profile.is_super_admin}')
            print(f'   Requer troca de senha: {profile.requires_password_change}')
        except:
            print('   Perfil não encontrado')
            
    else:
        print('❌ ERRO: Não foi possível autenticar')
        
        # Verificar se usuário existe
        try:
            user = User.objects.get(username='waner')
            print(f'Usuário existe: {user.username}')
            print(f'Ativo: {user.is_active}')
            print('Problema pode ser na senha...')
            
            # Testar senha manualmente
            if user.check_password('zDK$hNVlIVA&'):
                print('✅ Senha está correta no banco')
            else:
                print('❌ Senha incorreta no banco')
                
        except User.DoesNotExist:
            print('Usuário não existe!')
    
    print()
    print('=== INSTRUÇÕES PARA WAGNER ===')
    print('1. Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/')
    print('2. Use as credenciais:')
    print('   Usuário: waner')
    print('   Senha: zDK$hNVlIVA&')
    print('3. Você será obrigado a trocar a senha no primeiro login')
    print('4. Após trocar a senha, terá acesso completo ao sistema')

if __name__ == '__main__':
    test_wagner_login()