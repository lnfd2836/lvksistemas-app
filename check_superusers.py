#!/usr/bin/env python
"""
Script para verificar superusuários no sistema
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

def main():
    print("🔍 VERIFICANDO SUPERUSUÁRIOS NO SISTEMA")
    print("=" * 40)
    
    try:
        # Buscar todos os superusuários
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            print("❌ Nenhum superusuário encontrado!")
            return
        
        print(f"✅ {superusers.count()} superusuário(s) encontrado(s):")
        print()
        
        for user in superusers:
            print(f"👤 Username: {user.username}")
            print(f"   Email: {user.email or 'Não informado'}")
            print(f"   Ativo: {'Sim' if user.is_active else 'Não'}")
            print(f"   Data de criação: {user.date_joined}")
            print(f"   Último login: {user.last_login or 'Nunca'}")
            print("-" * 30)
        
        # Verificar também usuários staff
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        if staff_users.exists():
            print(f"\n📋 {staff_users.count()} usuário(s) staff (não super):")
            for user in staff_users:
                print(f"   - {user.username} ({user.email or 'sem email'})")
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")

if __name__ == '__main__':
    main()