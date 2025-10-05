#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User

print("=== Status dos Usuários ===")
print(f"Total de usuários: {User.objects.count()}")
print(f"Superusuários: {User.objects.filter(is_superuser=True).count()}")

if User.objects.filter(is_superuser=True).exists():
    print("\nSuperusuários existentes:")
    for user in User.objects.filter(is_superuser=True):
        print(f"- {user.username} ({user.email})")
else:
    print("\nNenhum superusuário encontrado!")
    print("Criando superusuário padrão...")
    
    User.objects.create_superuser(
        username='admin',
        email='admin@lvksistemas.com.br',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema'
    )
    print("Superusuário criado com sucesso!")
    print("Username: admin")
    print("Password: admin123")