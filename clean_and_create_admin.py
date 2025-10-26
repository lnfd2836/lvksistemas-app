#!/usr/bin/env python3
"""
Script para limpar todos os usuários e criar um super admin novo
Execute: heroku run python clean_and_create_admin.py --app lvksistemas-app
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate


def main():
    print("🧹 LIMPANDO TODOS OS USUÁRIOS E CRIANDO SUPER ADMIN")
    print("=" * 55)
    
    try:
        # 1. Mostrar usuários existentes
        existing_users = User.objects.all()
        print(f"📊 Usuários existentes: {existing_users.count()}")
        
        for user in existing_users:
            print(f"  - {user.username} | {user.email} | Super: {user.is_superuser}")
        
        # 2. DELETAR TODOS OS USUÁRIOS
        print(f"\n🗑️ DELETANDO TODOS OS USUÁRIOS...")
        deleted_count = User.objects.all().delete()[0]
        print(f"✅ {deleted_count} usuários deletados")
        
        # 3. CRIAR NOVO SUPER ADMIN
        print(f"\n👤 CRIANDO NOVO SUPER ADMIN...")
        
        # Credenciais super simples
        username = 'admin'
        password = 'admin123'
        email = 'admin@lvksistemas.com.br'
        
        new_admin = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print(f"✅ Super admin criado com sucesso!")
        
        # 4. VERIFICAR SE FUNCIONOU
        print(f"\n🧪 TESTANDO LOGIN...")
        test_user = authenticate(username=username, password=password)
        
        if test_user and test_user.is_superuser:
            print(f"✅ TESTE PASSOU! Login funcionando perfeitamente!")
        else:
            print(f"❌ TESTE FALHOU! Algo deu errado...")
            return False
        
        # 5. CRIAR USUÁRIO BACKUP
        print(f"\n🔄 CRIANDO USUÁRIO BACKUP...")
        backup_admin = User.objects.create_superuser(
            username='backup',
            email='backup@lvksistemas.com.br',
            password='backup123'
        )
        print(f"✅ Usuário backup criado!")
        
        # 6. MOSTRAR CREDENCIAIS FINAIS
        print(f"\n🔐 CREDENCIAIS PARA LOGIN:")
        print(f"=" * 30)
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"📧 Email: {email}")
        print(f"🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/")
        
        print(f"\n🔄 CREDENCIAIS BACKUP:")
        print(f"👤 Username: backup")
        print(f"🔑 Password: backup123")
        
        # 7. VERIFICAR USUÁRIOS FINAIS
        print(f"\n📊 USUÁRIOS FINAIS:")
        final_users = User.objects.all()
        for user in final_users:
            print(f"  ✅ {user.username} | {user.email} | Super: {user.is_superuser} | Ativo: {user.is_active}")
        
        print(f"\n🎉 LIMPEZA E CRIAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"🎯 USE: admin / admin123")
        
        return True
        
    except Exception as e:
        print(f"💥 ERRO: {str(e)}")
        
        # MÉTODO DE EMERGÊNCIA
        print(f"\n🚨 TENTANDO MÉTODO DE EMERGÊNCIA...")
        try:
            # Forçar criação mesmo com erro
            User.objects.all().delete()
            emergency_user = User.objects.create_user(
                username='emergency',
                email='emergency@lvk.com',
                password='emergency123'
            )
            emergency_user.is_superuser = True
            emergency_user.is_staff = True
            emergency_user.is_active = True
            emergency_user.save()
            
            print(f"✅ USUÁRIO DE EMERGÊNCIA CRIADO:")
            print(f"👤 Username: emergency")
            print(f"🔑 Password: emergency123")
            
            return True
            
        except Exception as e2:
            print(f"💥 ERRO DE EMERGÊNCIA: {str(e2)}")
            return False


if __name__ == '__main__':
    if main():
        print(f"\n🎯 SUCESSO! Tente fazer login agora!")
    else:
        print(f"\n❌ FALHA! Entre em contato para suporte")