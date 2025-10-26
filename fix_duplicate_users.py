#!/usr/bin/env python
"""
Script para corrigir usuários duplicados
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
from django.db.models import Count

def find_duplicate_users():
    """Encontra usuários duplicados"""
    print("🔍 PROCURANDO USUÁRIOS DUPLICADOS")
    print("=" * 35)
    
    # Buscar emails duplicados
    duplicate_emails = User.objects.values('email').annotate(
        count=Count('email')
    ).filter(count__gt=1, email__isnull=False).exclude(email='')
    
    if not duplicate_emails:
        print("✅ Nenhum email duplicado encontrado")
        return []
    
    duplicates = []
    for item in duplicate_emails:
        email = item['email']
        count = item['count']
        users = User.objects.filter(email=email)
        
        print(f"\n📧 Email duplicado: {email} ({count} usuários)")
        for user in users:
            print(f"   👤 {user.username} - Ativo: {user.is_active} - Super: {user.is_superuser} - Criado: {user.date_joined}")
        
        duplicates.append({
            'email': email,
            'users': list(users),
            'count': count
        })
    
    return duplicates

def fix_admin_duplicates():
    """Corrige duplicatas do admin@lvksistemas.com.br"""
    print("\n🔧 CORRIGINDO DUPLICATAS DO ADMIN")
    print("=" * 35)
    
    admin_email = 'admin@lvksistemas.com.br'
    admin_users = User.objects.filter(email=admin_email)
    
    if admin_users.count() <= 1:
        print("✅ Nenhuma duplicata encontrada para admin@lvksistemas.com.br")
        return True
    
    print(f"⚠️  Encontrados {admin_users.count()} usuários com email {admin_email}")
    
    # Manter apenas o usuário 'Kiko' (mais antigo e original)
    kiko_user = None
    users_to_delete = []
    
    for user in admin_users:
        if user.username == 'Kiko':
            kiko_user = user
            print(f"✅ Mantendo usuário: {user.username}")
        else:
            users_to_delete.append(user)
            print(f"❌ Marcado para remoção: {user.username}")
    
    # Se não encontrou Kiko, manter o mais antigo
    if not kiko_user and admin_users.exists():
        kiko_user = admin_users.order_by('date_joined').first()
        users_to_delete = [u for u in admin_users if u.id != kiko_user.id]
        print(f"✅ Mantendo usuário mais antigo: {kiko_user.username}")
    
    # Remover duplicatas
    for user in users_to_delete:
        try:
            print(f"🗑️  Removendo usuário: {user.username}")
            user.delete()
        except Exception as e:
            print(f"❌ Erro ao remover {user.username}: {e}")
    
    # Garantir que o usuário mantido está ativo
    if kiko_user:
        kiko_user.is_active = True
        kiko_user.is_superuser = True
        kiko_user.is_staff = True
        kiko_user.set_password('Kiko@LVK2024!')
        kiko_user.save()
        print(f"✅ Usuário {kiko_user.username} configurado corretamente")
    
    return True

def create_clean_admin():
    """Cria um admin limpo e único"""
    print("\n🆕 CRIANDO ADMIN LIMPO")
    print("=" * 25)
    
    # Remover todos os admins com email duplicado
    admin_email = 'admin@lvksistemas.com.br'
    User.objects.filter(email=admin_email).delete()
    print(f"🗑️  Removidos todos os usuários com email {admin_email}")
    
    # Criar novo admin único
    try:
        admin_user = User.objects.create_superuser(
            username='admin_lvk',
            email='admin@lvksistemas.com.br',
            password='AdminLVK@2024!'
        )
        
        print(f"✅ Novo admin criado:")
        print(f"   👤 Username: {admin_user.username}")
        print(f"   📧 Email: {admin_user.email}")
        print(f"   🔑 Senha: AdminLVK@2024!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        return False

def create_alternative_admin():
    """Cria admin alternativo com email único"""
    print("\n🔄 CRIANDO ADMIN ALTERNATIVO")
    print("=" * 30)
    
    try:
        # Verificar se já existe
        if User.objects.filter(username='superadmin').exists():
            user = User.objects.get(username='superadmin')
            print(f"⚠️  Usuário 'superadmin' já existe, atualizando...")
        else:
            user = User.objects.create_superuser(
                username='superadmin',
                email='superadmin@lvksistemas.com.br',
                password='SuperAdmin@2024!'
            )
            print(f"✅ Novo superadmin criado")
        
        # Garantir configurações
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.set_password('SuperAdmin@2024!')
        user.save()
        
        print(f"👤 Username: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Senha: SuperAdmin@2024!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superadmin: {e}")
        return False

def list_final_users():
    """Lista usuários finais"""
    print("\n📋 USUÁRIOS FINAIS")
    print("=" * 20)
    
    superusers = User.objects.filter(is_superuser=True, is_active=True)
    
    if not superusers.exists():
        print("❌ Nenhum superusuário ativo encontrado!")
        return
    
    print(f"✅ {superusers.count()} superusuário(s) ativo(s):")
    for user in superusers:
        print(f"   👤 {user.username} ({user.email})")
    
    # Verificar duplicatas
    emails = [u.email for u in superusers if u.email]
    duplicates = set([x for x in emails if emails.count(x) > 1])
    
    if duplicates:
        print(f"⚠️  Emails ainda duplicados: {duplicates}")
    else:
        print("✅ Nenhum email duplicado")

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE USUÁRIOS DUPLICADOS")
    print("=" * 40)
    
    # Encontrar duplicatas
    duplicates = find_duplicate_users()
    
    if not duplicates:
        print("\n✅ Sistema limpo, criando admin alternativo...")
        create_alternative_admin()
    else:
        # Corrigir duplicatas do admin
        fix_admin_duplicates()
        
        # Criar admin alternativo
        create_alternative_admin()
    
    # Listar resultado final
    list_final_users()
    
    print("\n🎉 CORREÇÃO CONCLUÍDA!")
    print("🌐 Teste o login em: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")

if __name__ == '__main__':
    main()