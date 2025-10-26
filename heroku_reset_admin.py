#!/usr/bin/env python3
"""
Script para resetar senha do admin no Heroku
Execute: heroku run python heroku_reset_admin.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User


def main():
    print("🔧 RESETANDO SENHAS NO HEROKU")
    print("=" * 35)
    
    # Credenciais para resetar
    users_to_reset = [
        {
            'username': 'admin',
            'password': 'Admin@LVK2024!',
            'email': 'admin@lvksistemas.com.br'
        },
        {
            'username': 'superadmin', 
            'password': 'SuperAdmin@LVK2024!',
            'email': 'admin@lvksistemas.com.br'
        },
        {
            'username': 'luiz',
            'password': 'Luiz@LVK2024!',
            'email': 'pjluiz25@hotmail.com'
        }
    ]
    
    success_count = 0
    
    for user_data in users_to_reset:
        username = user_data['username']
        password = user_data['password']
        email = user_data['email']
        
        try:
            # Tentar encontrar usuário existente
            try:
                user = User.objects.get(username=username)
                print(f"✅ Usuário '{username}' encontrado")
            except User.DoesNotExist:
                # Criar usuário se não existir
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                print(f"✅ Usuário '{username}' criado")
            
            # Resetar senha e garantir permissões
            user.set_password(password)
            user.is_active = True
            user.is_superuser = True
            user.is_staff = True
            user.email = email
            user.save()
            
            print(f"🔑 Senha resetada para '{username}'")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Erro com '{username}': {str(e)}")
    
    print(f"\n🎯 {success_count} usuários configurados com sucesso!")
    
    # Mostrar credenciais finais
    print("\n🔐 CREDENCIAIS PARA LOGIN:")
    print("-" * 25)
    
    for user_data in users_to_reset:
        try:
            user = User.objects.get(username=user_data['username'])
            if user.is_active and user.is_superuser:
                print(f"👤 {user_data['username']} | 🔑 {user_data['password']}")
        except User.DoesNotExist:
            pass
    
    print(f"\n🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/")
    print(f"🔗 Admin: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
    
    # Testar uma credencial
    print(f"\n🧪 TESTANDO LOGIN:")
    try:
        from django.contrib.auth import authenticate
        user = authenticate(username='admin', password='Admin@LVK2024!')
        if user:
            print(f"✅ Login do 'admin' funcionando!")
        else:
            print(f"❌ Login do 'admin' falhou")
    except Exception as e:
        print(f"💥 Erro no teste: {str(e)}")
    
    print(f"\n💡 RECOMENDAÇÃO:")
    print(f"Use: admin / Admin@LVK2024!")


if __name__ == '__main__':
    main()