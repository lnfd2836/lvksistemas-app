#!/usr/bin/env python
"""
Script para verificar e criar superuser se necessário
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User

def verificar_superuser():
    """Verifica se existe pelo menos um superuser"""
    
    print("🔍 VERIFICANDO SUPERUSERS")
    print("=" * 50)
    
    superusers = User.objects.filter(is_superuser=True)
    
    if superusers.exists():
        print("✅ Superusers encontrados:")
        for user in superusers:
            print(f"   - {user.username} ({user.email})")
            print(f"     Ativo: {'Sim' if user.is_active else 'Não'}")
            print(f"     Staff: {'Sim' if user.is_staff else 'Não'}")
            print(f"     Último login: {user.last_login or 'Nunca'}")
            print()
        return True
    else:
        print("❌ Nenhum superuser encontrado!")
        return False

def criar_superuser():
    """Cria um superuser básico"""
    
    print("🔧 CRIANDO SUPERUSER")
    print("=" * 50)
    
    try:
        # Verificar se já existe
        if User.objects.filter(username='admin').exists():
            print("⚠️  Usuário 'admin' já existe")
            return False
        
        # Criar superuser
        user = User.objects.create_superuser(
            username='admin',
            email='admin@lvksistemas.com',
            password='admin123'
        )
        
        print("✅ Superuser criado com sucesso!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: admin123")
        print()
        print("🔐 IMPORTANTE: Altere a senha após o primeiro login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superuser: {e}")
        return False

def main():
    """Executa verificação e criação se necessário"""
    
    print("🚀 VERIFICAÇÃO DE SUPERUSER")
    print("=" * 50)
    print("Verificando se você tem acesso de administrador...")
    print()
    
    if verificar_superuser():
        print("✅ TUDO OK!")
        print()
        print("Para acessar a configuração Asaas:")
        print("1. Faça login com um dos superusers acima")
        print("2. Acesse: /financeiro/asaas/configurar/")
        print()
        return True
    else:
        print("🔧 Criando superuser para você...")
        print()
        
        if criar_superuser():
            print("✅ PROBLEMA RESOLVIDO!")
            print()
            print("Para acessar a configuração Asaas:")
            print("1. Faça login com:")
            print("   Username: admin")
            print("   Password: admin123")
            print("2. Acesse: /financeiro/asaas/configurar/")
            print()
            print("🔐 LEMBRE-SE: Altere a senha após o primeiro login!")
            return True
        else:
            print("❌ Não foi possível criar superuser")
            return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)