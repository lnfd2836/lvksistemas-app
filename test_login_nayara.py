#!/usr/bin/env python
"""
Script para testar login da loja Nayara
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth import authenticate
from lojas.models import Loja

def test_login_nayara():
    """Testa login da loja Nayara"""
    print("🔍 Testando Login da Loja Nayara")
    print("=" * 40)
    
    # Buscar loja Nayara
    loja = Loja.objects.get(email="pjluiz25@hotmail.com")
    
    print(f"📧 Email: {loja.email}")
    print(f"🔑 Senha atual: {loja.senha_provisoria}")
    print()
    
    # Testar autenticação
    user = authenticate(username=loja.email, password=loja.senha_provisoria)
    
    if user:
        print("✅ LOGIN FUNCIONOU!")
        print(f"   Usuário: {user.username}")
        print(f"   Nome: {user.first_name} {user.last_name}")
    else:
        print("❌ LOGIN FALHOU!")
        
        # Vamos regenerar a senha para corrigir
        print("\n🔧 Regenerando senha...")
        
        import secrets
        import string
        
        # Gerar nova senha
        password_chars = string.ascii_letters + string.digits + "!@#$%&*"
        nova_senha = ''.join(secrets.choice(password_chars) for _ in range(12))
        
        # Atualizar usuário
        admin_user = loja.admin_user
        admin_user.set_password(nova_senha)
        admin_user.save()
        
        # Atualizar loja
        loja.senha_provisoria = nova_senha
        loja.save()
        
        print(f"✅ Nova senha gerada: {nova_senha}")
        
        # Testar novamente
        user_new = authenticate(username=loja.email, password=nova_senha)
        if user_new:
            print("✅ LOGIN COM NOVA SENHA FUNCIONOU!")
        else:
            print("❌ LOGIN COM NOVA SENHA AINDA FALHOU!")

if __name__ == '__main__':
    test_login_nayara()