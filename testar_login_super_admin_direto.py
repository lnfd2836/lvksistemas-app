#!/usr/bin/env python
"""
Script para testar o login direto de super admin na página principal
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Testa o login direto de super admin"""
    
    print("🔑 TESTE LOGIN DIRETO SUPER ADMIN")
    print("=" * 50)
    
    # 1. Testar página principal sem autenticação
    print("\n1️⃣ TESTANDO PÁGINA PRINCIPAL SEM AUTENTICAÇÃO")
    testar_pagina_principal()
    
    # 2. Testar login de super admin
    print("\n2️⃣ TESTANDO LOGIN DE SUPER ADMIN")
    testar_login_super_admin()
    
    # 3. Testar login de usuário comum
    print("\n3️⃣ TESTANDO LOGIN DE USUÁRIO COMUM (deve falhar)")
    testar_login_usuario_comum()
    
    print("\n✅ TESTES CONCLUÍDOS")

def testar_pagina_principal():
    """Testa se a página principal mostra o formulário de login"""
    
    try:
        client = Client()
        
        # Teste GET na página principal
        print("   🧪 Acessando página principal (/)...")
        response = client.get('/')
        
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar se é o template de login de super admin
            if 'Super Admin' in content and 'form' in content:
                print("      ✅ CORRETO: Mostra formulário de login de super admin")
                
                # Verificar elementos específicos
                if 'name="username"' in content:
                    print("      ✅ Campo username presente")
                if 'name="password"' in content:
                    print("      ✅ Campo password presente")
                if 'csrf' in content:
                    print("      ✅ CSRF token presente")
                    
            elif 'Selecione sua Loja' in content:
                print("      ❌ PROBLEMA: Ainda mostra seleção de lojas")
            else:
                print("      ❌ PROBLEMA: Conteúdo inesperado")
                print(f"      Preview: {content[:200]}...")
                
        elif response.status_code == 302:
            print(f"      ❌ PROBLEMA: Redirecionamento para {response.url}")
        else:
            print(f"      ❌ PROBLEMA: Status inesperado {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

def testar_login_super_admin():
    """Testa login de super admin via POST"""
    
    try:
        # Buscar super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ❌ Nenhum super admin encontrado")
            return
        
        client = Client()
        
        print(f"   👤 Testando login com super admin: {super_admin.username}")
        
        # Fazer POST com credenciais
        response = client.post('/', {
            'username': super_admin.username,
            'password': 'admin123',  # Senha padrão de teste
        })
        
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"      🔄 Redirecionamento para: {response.url}")
            
            if response.url == '/dashboard/':
                print("      ✅ CORRETO: Super admin redirecionado para dashboard")
                
                # Verificar se está realmente autenticado
                response2 = client.get('/dashboard/')
                if response2.status_code == 200:
                    print("      ✅ CORRETO: Acesso ao dashboard confirmado")
                else:
                    print(f"      ⚠️  Dashboard retornou status {response2.status_code}")
                    
            else:
                print("      ❌ PROBLEMA: Redirecionamento incorreto")
                
        elif response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'incorretos' in content or 'erro' in content.lower():
                print("      ⚠️  Credenciais incorretas (esperado se senha não for 'admin123')")
            else:
                print("      ❌ PROBLEMA: Formulário retornado sem erro claro")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

def testar_login_usuario_comum():
    """Testa se usuário comum é bloqueado"""
    
    try:
        # Buscar usuário comum (não super admin)
        usuario_comum = User.objects.filter(is_superuser=False).first()
        if not usuario_comum:
            print("   ℹ️  Nenhum usuário comum encontrado para teste")
            return
        
        client = Client()
        
        print(f"   👤 Testando login com usuário comum: {usuario_comum.username}")
        
        # Tentar fazer POST com usuário comum
        response = client.post('/', {
            'username': usuario_comum.username,
            'password': 'senha123',  # Senha de teste
        })
        
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'exclusiva para super administradores' in content:
                print("      ✅ CORRETO: Usuário comum bloqueado com mensagem apropriada")
            elif 'incorretos' in content:
                print("      ⚠️  Credenciais incorretas (esperado)")
            else:
                print("      ❌ PROBLEMA: Usuário comum não foi bloqueado adequadamente")
        elif response.status_code == 302:
            print(f"      ❌ PROBLEMA: Usuário comum foi redirecionado para {response.url}")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

if __name__ == '__main__':
    main()