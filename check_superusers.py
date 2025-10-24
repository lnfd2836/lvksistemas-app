#!/usr/bin/env python
"""
Script para verificar superusuários do sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User


def listar_superusers():
    """Lista todos os superusuários ativos"""
    print("🔑 SUPERUSUÁRIOS DO SISTEMA")
    print("=" * 50)
    
    superusers = User.objects.filter(is_superuser=True, is_active=True).order_by('id')
    
    if superusers.exists():
        print(f"📊 Total de superusuários ativos: {superusers.count()}")
        print()
        
        for user in superusers:
            print(f"👤 Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Nome: {user.get_full_name() or 'Não informado'}")
            print(f"   Último login: {user.last_login or 'Nunca'}")
            print(f"   Data criação: {user.date_joined}")
            print(f"   Staff: {'Sim' if user.is_staff else 'Não'}")
            print("-" * 40)
    else:
        print("❌ Nenhum superusuário ativo encontrado!")
        print("⚠️  ATENÇÃO: Sistema sem administrador!")


def verificar_usuario_especifico(username):
    """Verifica um usuário específico"""
    try:
        user = User.objects.get(username=username)
        print(f"👤 Usuário encontrado: {username}")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Superusuário: {'Sim' if user.is_superuser else 'Não'}")
        print(f"   Ativo: {'Sim' if user.is_active else 'Não'}")
        print(f"   Staff: {'Sim' if user.is_staff else 'Não'}")
        print(f"   Último login: {user.last_login or 'Nunca'}")
        
        # Verificar se tem loja associada
        try:
            from lojas.models import Loja
            lojas = Loja.objects.filter(admin_user=user)
            if lojas.exists():
                print(f"   Lojas administradas: {lojas.count()}")
                for loja in lojas:
                    print(f"     - {loja.nome} ({loja.status})")
            else:
                print(f"   Lojas administradas: Nenhuma")
        except:
            pass
            
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
        verificar_usuario_especifico(username)
    else:
        listar_superusers()