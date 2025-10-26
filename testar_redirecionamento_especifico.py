#!/usr/bin/env python
"""
Script para testar redirecionamentos específicos e identificar loops
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
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Testa redirecionamentos específicos"""
    
    print("🔍 TESTE ESPECÍFICO DE REDIRECIONAMENTOS")
    print("=" * 50)
    
    client = Client()
    
    # Teste 1: Página inicial sem autenticação
    print("\n1️⃣ TESTANDO PÁGINA INICIAL (não autenticado)")
    test_url(client, '/')
    
    # Teste 2: Página inicial com usuário autenticado
    print("\n2️⃣ TESTANDO PÁGINA INICIAL (autenticado)")
    user = create_test_user()
    if user:
        client.force_login(user)
        test_url(client, '/')
        client.logout()
    
    # Teste 3: URLs de login antigas
    print("\n3️⃣ TESTANDO URLS DE LOGIN ANTIGAS")
    test_url(client, '/login/')
    test_url(client, '/usuarios/login/')
    test_url(client, '/dashboard/login/')
    
    # Teste 4: Login personalizado
    print("\n4️⃣ TESTANDO LOGIN PERSONALIZADO")
    loja = Loja.objects.filter(status='ativa').first()
    if loja:
        try:
            login_config = loja.login_personalizado
            login_url = login_config.get_login_url()
            test_url(client, login_url)
        except Exception as e:
            print(f"   ❌ Erro ao testar login personalizado: {str(e)}")
    
    # Teste 5: Admin
    print("\n5️⃣ TESTANDO ADMIN")
    test_url(client, '/admin/')
    test_url(client, '/admin-login/')
    
    print("\n✅ TESTES CONCLUÍDOS")

def test_url(client, url, max_redirects=5):
    """Testa uma URL específica e segue redirecionamentos"""
    
    print(f"\n   🧪 Testando: {url}")
    
    try:
        redirects = []
        current_url = url
        
        for i in range(max_redirects + 1):
            response = client.get(current_url, follow=False)
            
            print(f"   [{i}] {current_url} → Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Sucesso! Página carregada")
                break
            elif response.status_code in [301, 302]:
                redirect_url = response.url
                print(f"   🔄 Redirecionamento para: {redirect_url}")
                
                # Verificar se é um loop
                if redirect_url in redirects:
                    print(f"   ❌ LOOP DETECTADO! {redirect_url} já foi visitado")
                    print(f"   📋 Histórico: {' → '.join(redirects + [redirect_url])}")
                    break
                
                redirects.append(current_url)
                current_url = redirect_url
                
                # Verificar se é redirecionamento para si mesmo
                if current_url == url:
                    print(f"   ❌ LOOP DIRETO! Redirecionando para si mesmo")
                    break
            else:
                print(f"   ❌ Status inesperado: {response.status_code}")
                break
        
        if len(redirects) >= max_redirects:
            print(f"   ⚠️  Muitos redirecionamentos ({len(redirects)})")
            print(f"   📋 Histórico: {' → '.join(redirects)}")
    
    except Exception as e:
        print(f"   ❌ Erro ao testar {url}: {str(e)}")

def create_test_user():
    """Cria um usuário de teste"""
    
    try:
        # Tentar usar um usuário existente primeiro
        user = User.objects.filter(is_superuser=True).first()
        if user:
            print(f"   👤 Usando usuário existente: {user.username}")
            return user
        
        # Se não houver, criar um temporário
        user = User.objects.create_user(
            username='test_redirect_user',
            email='test@example.com',
            password='testpass123'
        )
        print(f"   👤 Usuário de teste criado: {user.username}")
        return user
        
    except Exception as e:
        print(f"   ❌ Erro ao criar usuário de teste: {str(e)}")
        return None

if __name__ == '__main__':
    main()