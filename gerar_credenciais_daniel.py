#!/usr/bin/env python
"""
Script para gerar novas credenciais para Loja Daniel
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from lojas.models import Loja
import secrets
import string

def gerar_credenciais_daniel():
    """Gera novas credenciais para Loja Daniel"""
    print("🔧 Gerando Credenciais para Loja Daniel")
    print("=" * 45)
    
    # Buscar Loja Daniel pelo CNPJ
    try:
        loja = Loja.objects.get(cnpj="24.758.458/0001-72")
        
        print(f"✅ Loja encontrada:")
        print(f"   - Nome: {loja.nome}")
        print(f"   - CNPJ: {loja.cnpj}")
        print(f"   - Email: {loja.email}")
        print(f"   - Admin User: {loja.admin_user.username}")
        print()
        
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
        
        print("🔑 NOVAS CREDENCIAIS GERADAS:")
        print("=" * 30)
        print(f"🏪 DADOS DA LOJA:")
        print(f"Nome: {loja.nome}")
        print(f"CNPJ: {loja.cnpj}")
        print(f"Email: {loja.email}")
        print(f"Telefone: {loja.telefone}")
        print()
        print(f"🔑 CREDENCIAIS DE ACESSO:")
        print(f"URL de Login: https://www.lvksistemas.com.br/loja/login/")
        print(f"Usuário: {loja.admin_user.username}")
        print(f"Nova Senha Provisória: {nova_senha}")
        print()
        print("⚠️ IMPORTANTE:")
        print("- Esta é uma senha provisória que DEVE ser alterada no primeiro acesso")
        print("- Por segurança, você será obrigado a trocar a senha no primeiro login")
        print("- Mantenha suas credenciais em local seguro")
        
        # Testar login
        from django.contrib.auth import authenticate
        user = authenticate(username=loja.admin_user.username, password=nova_senha)
        
        if user:
            print("\n✅ TESTE DE LOGIN: SUCESSO!")
        else:
            print("\n❌ TESTE DE LOGIN: FALHOU!")
            
    except Loja.DoesNotExist:
        print("❌ Loja Daniel com CNPJ 24.758.458/0001-72 não encontrada!")

if __name__ == '__main__':
    gerar_credenciais_daniel()