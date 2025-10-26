#!/usr/bin/env python3
"""
Reset SIMPLES para Heroku - Senha básica
Execute: heroku run python simple_heroku_reset.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    print("🔧 RESET SIMPLES - HEROKU")
    print("=" * 30)
    
    # Credenciais super simples
    users_to_create = [
        ('admin', 'admin123'),
        ('root', 'root123'),
        ('super', 'super123')
    ]
    
    for username, password in users_to_create:
        try:
            # Deletar se existir
            User.objects.filter(username=username).delete()
            
            # Criar novo
            user = User.objects.create_superuser(
                username=username,
                email=f'{username}@lvk.com',
                password=password
            )
            
            print(f"✅ {username} / {password}")
            
        except Exception as e:
            print(f"❌ Erro com {username}: {str(e)}")
    
    print(f"\n🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/")
    print(f"🎯 TENTE: admin / admin123")

if __name__ == '__main__':
    main()