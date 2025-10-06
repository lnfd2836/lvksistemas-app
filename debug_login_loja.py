#!/usr/bin/env python
"""
Script para diagnosticar problemas de login da loja
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from lojas.models import Loja

def debug_login_loja():
    """Diagnostica problemas de login da loja"""
    print("🔍 Diagnóstico de Login da Loja")
    print("=" * 50)
    
    # Credenciais do exemplo
    email_loja = "pjluiz25@hotmail.com"
    senha_provisoria = "ecO%g%enTcft"
    
    print(f"📧 Email da loja: {email_loja}")
    print(f"🔑 Senha provisória: {senha_provisoria}")
    print()
    
    # 1. Verificar se existe loja com esse email
    print("1️⃣ Verificando loja...")
    try:
        loja = Loja.objects.get(email=email_loja)
        print(f"✅ Loja encontrada: {loja.nome}")
        print(f"   - ID: {loja.id}")
        print(f"   - CNPJ: {loja.cnpj}")
        print(f"   - Status: {loja.status}")
        print(f"   - Admin User ID: {loja.admin_user.id}")
        print()
    except Loja.DoesNotExist:
        print(f"❌ Loja com email {email_loja} não encontrada!")
        return
    except Exception as e:
        print(f"❌ Erro ao buscar loja: {str(e)}")
        return
    
    # 2. Verificar usuário administrador
    print("2️⃣ Verificando usuário administrador...")
    admin_user = loja.admin_user
    print(f"✅ Usuário encontrado:")
    print(f"   - ID: {admin_user.id}")
    print(f"   - Username: {admin_user.username}")
    print(f"   - Email: {admin_user.email}")
    print(f"   - First Name: {admin_user.first_name}")
    print(f"   - Last Name: {admin_user.last_name}")
    print(f"   - Is Active: {admin_user.is_active}")
    print(f"   - Is Staff: {admin_user.is_staff}")
    print(f"   - Is Superuser: {admin_user.is_superuser}")
    print()
    
    # 3. Verificar se username é igual ao email
    print("3️⃣ Verificando consistência...")
    if admin_user.username == email_loja:
        print("✅ Username é igual ao email da loja")
    else:
        print(f"❌ Username ({admin_user.username}) diferente do email da loja ({email_loja})")
    
    if admin_user.email == email_loja:
        print("✅ Email do usuário é igual ao email da loja")
    else:
        print(f"❌ Email do usuário ({admin_user.email}) diferente do email da loja ({email_loja})")
    print()
    
    # 4. Testar autenticação com username
    print("4️⃣ Testando autenticação com username...")
    user_auth_username = authenticate(username=admin_user.username, password=senha_provisoria)
    if user_auth_username:
        print(f"✅ Autenticação com username SUCESSO: {user_auth_username.username}")
    else:
        print(f"❌ Autenticação com username FALHOU")
    print()
    
    # 5. Testar autenticação com email
    print("5️⃣ Testando autenticação com email...")
    user_auth_email = authenticate(username=email_loja, password=senha_provisoria)
    if user_auth_email:
        print(f"✅ Autenticação com email SUCESSO: {user_auth_email.username}")
    else:
        print(f"❌ Autenticação com email FALHOU")
    print()
    
    # 6. Verificar senha provisória na loja
    print("6️⃣ Verificando senha provisória na loja...")
    print(f"   - Senha provisória armazenada: {loja.senha_provisoria}")
    print(f"   - Senha provisória expirada: {loja.senha_provisoria_expirada}")
    
    if loja.senha_provisoria == senha_provisoria:
        print("✅ Senha provisória na loja confere")
    else:
        print(f"❌ Senha provisória na loja não confere")
        print(f"   Esperada: {senha_provisoria}")
        print(f"   Armazenada: {loja.senha_provisoria}")
    print()
    
    # 7. Verificar se senha foi definida no usuário
    print("7️⃣ Verificando senha do usuário...")
    if admin_user.has_usable_password():
        print("✅ Usuário tem senha utilizável")
        
        # Testar check_password
        if admin_user.check_password(senha_provisoria):
            print("✅ Senha confere com check_password")
        else:
            print("❌ Senha NÃO confere com check_password")
    else:
        print("❌ Usuário NÃO tem senha utilizável")
    print()
    
    # 8. Buscar usuário por email
    print("8️⃣ Buscando usuário por email...")
    try:
        user_by_email = User.objects.get(email=email_loja)
        print(f"✅ Usuário encontrado por email: {user_by_email.username}")
        
        if user_by_email.id == admin_user.id:
            print("✅ É o mesmo usuário administrador da loja")
        else:
            print("❌ É um usuário diferente!")
            
    except User.DoesNotExist:
        print(f"❌ Usuário com email {email_loja} não encontrado")
    except User.MultipleObjectsReturned:
        print(f"❌ Múltiplos usuários com email {email_loja} encontrados!")
        users = User.objects.filter(email=email_loja)
        for i, user in enumerate(users):
            print(f"   {i+1}. ID: {user.id}, Username: {user.username}")
    print()
    
    # 9. Resumo do diagnóstico
    print("📋 RESUMO DO DIAGNÓSTICO:")
    print("=" * 30)
    
    if user_auth_username or user_auth_email:
        print("✅ AUTENTICAÇÃO: Funcionando")
    else:
        print("❌ AUTENTICAÇÃO: Com problemas")
        
        # Sugestões de correção
        print("\n🔧 POSSÍVEIS SOLUÇÕES:")
        print("1. Regenerar senha do usuário")
        print("2. Verificar se senha foi definida corretamente")
        print("3. Verificar se usuário está ativo")
        print("4. Verificar logs de erro do Django")

if __name__ == '__main__':
    debug_login_loja()