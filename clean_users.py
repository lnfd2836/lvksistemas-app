#!/usr/bin/env python
"""
Script para remover todos os usuários e criar apenas 1 super admin
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

def remove_all_users():
    """Remove todos os usuários do sistema"""
    print("🗑️  REMOVENDO TODOS OS USUÁRIOS")
    print("=" * 35)
    
    try:
        # Contar usuários antes
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        regular_users = User.objects.filter(is_superuser=False).count()
        
        print(f"📊 Usuários encontrados:")
        print(f"   Total: {total_users}")
        print(f"   Super admins: {superusers}")
        print(f"   Usuários regulares: {regular_users}")
        
        if total_users == 0:
            print("✅ Nenhum usuário para remover")
            return True
        
        # Listar usuários que serão removidos
        print(f"\n👥 Usuários que serão removidos:")
        for user in User.objects.all():
            status = "Super Admin" if user.is_superuser else "Regular"
            active = "Ativo" if user.is_active else "Inativo"
            print(f"   - {user.username} ({user.email}) - {status} - {active}")
        
        # Remover todos os usuários
        deleted_count = User.objects.all().delete()[0]
        
        print(f"\n✅ {deleted_count} usuário(s) removido(s) com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao remover usuários: {e}")
        return False

def create_single_admin():
    """Cria um único super admin"""
    print("\n🆕 CRIANDO SUPER ADMIN ÚNICO")
    print("=" * 30)
    
    # Dados do super admin
    username = 'admin'
    email = 'admin@lvksistemas.com.br'
    password = 'Admin@LVK2024!'
    
    try:
        # Verificar se já existe (não deveria existir após limpeza)
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Usuário '{username}' já existe, removendo...")
            User.objects.filter(username=username).delete()
        
        # Criar novo super admin
        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Garantir todas as permissões
        admin_user.is_active = True
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        print(f"✅ Super admin criado com sucesso!")
        print(f"👤 Username: {username}")
        print(f"📧 Email: {email}")
        print(f"🔑 Senha: {password}")
        print(f"🌐 Admin URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Erro ao criar super admin: {e}")
        return None

def verify_system():
    """Verifica se o sistema está limpo"""
    print("\n🔍 VERIFICANDO SISTEMA")
    print("=" * 20)
    
    try:
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True)
        active_users = User.objects.filter(is_active=True)
        
        print(f"📊 Estado final:")
        print(f"   Total de usuários: {total_users}")
        print(f"   Super admins: {superusers.count()}")
        print(f"   Usuários ativos: {active_users.count()}")
        
        if total_users == 1 and superusers.count() == 1:
            admin = superusers.first()
            print(f"\n✅ Sistema limpo com sucesso!")
            print(f"👤 Único usuário: {admin.username} ({admin.email})")
            
            # Testar login
            if admin.check_password('Admin@LVK2024!'):
                print("🔑 Senha verificada com sucesso!")
            else:
                print("⚠️  Problema com a senha!")
            
            return True
        else:
            print(f"⚠️  Sistema não está no estado esperado!")
            print(f"   Esperado: 1 usuário, 1 super admin")
            print(f"   Atual: {total_users} usuários, {superusers.count()} super admins")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def backup_info():
    """Mostra informações antes da limpeza"""
    print("📋 INFORMAÇÕES ANTES DA LIMPEZA")
    print("=" * 35)
    
    try:
        users = User.objects.all()
        
        if not users.exists():
            print("ℹ️  Nenhum usuário encontrado")
            return
        
        print(f"📊 {users.count()} usuário(s) encontrado(s):")
        
        for user in users:
            print(f"\n👤 {user.username}")
            print(f"   Email: {user.email or 'Não informado'}")
            print(f"   Super admin: {'Sim' if user.is_superuser else 'Não'}")
            print(f"   Ativo: {'Sim' if user.is_active else 'Não'}")
            print(f"   Criado em: {user.date_joined}")
            print(f"   Último login: {user.last_login or 'Nunca'}")
        
        print(f"\n⚠️  TODOS ESTES USUÁRIOS SERÃO REMOVIDOS!")
        
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")

def main():
    """Função principal"""
    print("🧹 LIMPEZA COMPLETA DE USUÁRIOS")
    print("=" * 35)
    print("⚠️  ATENÇÃO: Este script irá remover TODOS os usuários!")
    print("=" * 35)
    
    # Mostrar informações atuais
    backup_info()
    
    print(f"\n🔄 Iniciando limpeza...")
    
    # Remover todos os usuários
    if not remove_all_users():
        print("❌ Falha na remoção de usuários")
        return False
    
    # Criar único super admin
    admin_user = create_single_admin()
    if not admin_user:
        print("❌ Falha na criação do super admin")
        return False
    
    # Verificar resultado
    if verify_system():
        print("\n🎉 LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("=" * 35)
        print("✅ Sistema agora tem apenas 1 super admin")
        print("🔐 Credenciais de acesso:")
        print("   Username: admin")
        print("   Senha: Admin@LVK2024!")
        print("🌐 Login: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
        print("⚠️  Altere a senha após o primeiro login!")
        return True
    else:
        print("\n❌ PROBLEMA NA VERIFICAÇÃO!")
        print("🔍 Verifique manualmente o sistema")
        return False

if __name__ == '__main__':
    main()