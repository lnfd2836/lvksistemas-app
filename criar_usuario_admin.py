#!/usr/bin/env python3
"""
Script para criar usuário admin no sistema em produção
"""

import os
import sys
import django
from pathlib import Path

# Adiciona o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction

def criar_usuario_admin():
    """Cria ou atualiza o usuário admin"""
    print("🔧 Criando/atualizando usuário admin...")
    
    try:
        with transaction.atomic():
            # Verifica se já existe
            try:
                user = User.objects.get(username='admin')
                print(f"👤 Usuário 'admin' já existe (ID: {user.id})")
                
                # Atualiza a senha
                user.set_password('admin123')
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.save()
                
                print("✅ Senha atualizada para 'admin123'")
                print("✅ Permissões de admin configuradas")
                
            except User.DoesNotExist:
                # Cria novo usuário
                user = User.objects.create_user(
                    username='admin',
                    email='admin@lvksistemas.com.br',
                    password='admin123',
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                
                print("✅ Usuário 'admin' criado com sucesso!")
                print(f"📧 Email: {user.email}")
                print("🔑 Senha: admin123")
                print("👑 Permissões: Superusuário")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False

def listar_usuarios():
    """Lista todos os usuários do sistema"""
    print("\n👥 Usuários no sistema:")
    print("-" * 50)
    
    users = User.objects.all()
    
    if not users:
        print("❌ Nenhum usuário encontrado")
        return
    
    for user in users:
        status = "✅ Ativo" if user.is_active else "❌ Inativo"
        tipo = []
        
        if user.is_superuser:
            tipo.append("Superusuário")
        if user.is_staff:
            tipo.append("Staff")
        
        tipo_str = ", ".join(tipo) if tipo else "Usuário comum"
        
        print(f"👤 {user.username}")
        print(f"   📧 Email: {user.email}")
        print(f"   📊 Status: {status}")
        print(f"   🏷️ Tipo: {tipo_str}")
        print(f"   📅 Criado: {user.date_joined.strftime('%d/%m/%Y %H:%M')}")
        print()

def testar_autenticacao():
    """Testa autenticação do usuário admin"""
    print("🔐 Testando autenticação...")
    
    from django.contrib.auth import authenticate
    
    user = authenticate(username='admin', password='admin123')
    
    if user:
        print("✅ Autenticação bem-sucedida!")
        print(f"👤 Usuário: {user.username}")
        print(f"📊 Ativo: {user.is_active}")
        print(f"👑 Staff: {user.is_staff}")
        print(f"🔑 Superuser: {user.is_superuser}")
        return True
    else:
        print("❌ Falha na autenticação")
        return False

def main():
    print("🚀 CONFIGURAÇÃO DE USUÁRIO ADMIN")
    print("=" * 50)
    
    # Lista usuários existentes
    listar_usuarios()
    
    # Cria/atualiza admin
    if criar_usuario_admin():
        # Testa autenticação
        testar_autenticacao()
        
        print("\n" + "=" * 50)
        print("✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("\n📋 Credenciais para login:")
        print("👤 Usuário: admin")
        print("🔑 Senha: admin123")
        print("\n🌐 Teste no navegador:")
        print("https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/")
        
    else:
        print("\n❌ Falha na configuração")

if __name__ == "__main__":
    main()