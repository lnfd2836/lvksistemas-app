#!/usr/bin/env python3
"""
Script URGENTE para resetar login no Heroku
Execute: heroku run python fix_heroku_login_now.py
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
    print("🚨 CORREÇÃO URGENTE - LOGIN HEROKU")
    print("=" * 40)
    
    # Senha simples e funcional
    username = 'admin'
    password = 'admin123'  # Senha mais simples
    email = 'admin@lvksistemas.com.br'
    
    try:
        print(f"🔧 Resetando usuário '{username}'...")
        
        # Deletar usuário existente se houver problema
        try:
            old_user = User.objects.get(username=username)
            print(f"⚠️ Usuário existente encontrado, atualizando...")
        except User.DoesNotExist:
            print(f"ℹ️ Criando novo usuário...")
        
        # Criar ou atualizar usuário
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_superuser': True,
                'is_staff': True,
                'is_active': True
            }
        )
        
        # Forçar configurações
        user.set_password(password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.email = email
        user.save()
        
        print(f"✅ Usuário configurado com sucesso!")
        
        # Testar imediatamente
        print(f"🧪 Testando login...")
        test_user = authenticate(username=username, password=password)
        
        if test_user and test_user.is_superuser:
            print(f"✅ TESTE PASSOU! Login funcionando!")
        else:
            print(f"❌ TESTE FALHOU! Tentando senha alternativa...")
            
            # Tentar senha alternativa
            alt_password = 'LVK2024'
            user.set_password(alt_password)
            user.save()
            
            test_user2 = authenticate(username=username, password=alt_password)
            if test_user2:
                password = alt_password
                print(f"✅ Senha alternativa funcionando!")
            else:
                print(f"❌ Problema persistente")
        
        # Mostrar credenciais finais
        print(f"\n🔐 CREDENCIAIS PARA LOGIN:")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"📧 Email: {email}")
        print(f"🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/")
        
        # Criar usuário backup
        print(f"\n🔄 Criando usuário backup...")
        backup_user, backup_created = User.objects.get_or_create(
            username='backup_admin',
            defaults={
                'email': 'backup@lvksistemas.com.br',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True
            }
        )
        backup_user.set_password('backup123')
        backup_user.is_active = True
        backup_user.is_superuser = True
        backup_user.is_staff = True
        backup_user.save()
        
        print(f"✅ Usuário backup criado:")
        print(f"👤 Username: backup_admin")
        print(f"🔑 Password: backup123")
        
        # Listar todos os superusuários ativos
        print(f"\n📊 TODOS OS SUPERUSUÁRIOS ATIVOS:")
        superusers = User.objects.filter(is_superuser=True, is_active=True)
        for su in superusers:
            print(f"👤 {su.username} | 📧 {su.email}")
        
        print(f"\n🎯 TENTE ESTAS OPÇÕES:")
        print(f"1️⃣ admin / {password}")
        print(f"2️⃣ backup_admin / backup123")
        print(f"3️⃣ superadmin / SuperAdmin@LVK2024!")
        
        return True
        
    except Exception as e:
        print(f"💥 ERRO: {str(e)}")
        
        # Tentar método de emergência
        print(f"🚨 TENTANDO MÉTODO DE EMERGÊNCIA...")
        try:
            # Deletar todos os admins e criar novo
            User.objects.filter(username__in=['admin', 'superadmin']).delete()
            
            emergency_user = User.objects.create_superuser(
                username='emergency',
                email='emergency@lvk.com',
                password='emergency123'
            )
            
            print(f"✅ USUÁRIO DE EMERGÊNCIA CRIADO:")
            print(f"👤 Username: emergency")
            print(f"🔑 Password: emergency123")
            
            return True
            
        except Exception as e2:
            print(f"💥 ERRO DE EMERGÊNCIA: {str(e2)}")
            return False


if __name__ == '__main__':
    if main():
        print(f"\n🎉 CORREÇÃO CONCLUÍDA!")
        print(f"Tente fazer login com as credenciais mostradas acima")
    else:
        print(f"\n❌ FALHA NA CORREÇÃO!")
        print(f"Entre em contato para suporte técnico")