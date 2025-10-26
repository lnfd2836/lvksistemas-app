#!/usr/bin/env python
"""
Script para testar o middleware exclusivo de super admin
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
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Testa o middleware exclusivo de super admin"""
    
    print("🔧 TESTE MIDDLEWARE EXCLUSIVO SUPER ADMIN")
    print("=" * 50)
    
    # 1. Testar sem autenticação
    print("\n1️⃣ TESTANDO SEM AUTENTICAÇÃO")
    testar_sem_autenticacao()
    
    # 2. Testar com super admin
    print("\n2️⃣ TESTANDO COM SUPER ADMIN")
    testar_com_super_admin()
    
    # 3. Testar cenário Heroku (uma loja)
    print("\n3️⃣ TESTANDO CENÁRIO HEROKU")
    testar_cenario_heroku()
    
    print("\n✅ TESTES CONCLUÍDOS")

def testar_sem_autenticacao():
    """Testa comportamento sem autenticação"""
    
    try:
        client = Client()
        
        # Teste 1: Página inicial
        print("   🧪 Página inicial (/)...")
        response = client.get('/')
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print("      ✅ Mostra seleção de lojas")
        elif response.status_code == 302:
            print(f"      🔄 Redirecionamento para: {response.url}")
        
        # Teste 2: Admin login
        print("   🧪 Admin login (/admin-login/)...")
        response = client.get('/admin-login/')
        print(f"      Status: {response.status_code}")
        if response.status_code == 302:
            print(f"      🔄 Redirecionamento para: {response.url}")
        
        # Teste 3: Super admin
        print("   🧪 Super admin (/super-admin/)...")
        response = client.get('/super-admin/')
        print(f"      Status: {response.status_code}")
        if response.status_code == 302:
            print(f"      🔄 Redirecionamento para: {response.url}")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

def testar_com_super_admin():
    """Testa comportamento com super admin autenticado"""
    
    try:
        # Buscar super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ❌ Nenhum super admin encontrado")
            return
        
        client = Client()
        client.force_login(super_admin)
        print(f"   👤 Logado como: {super_admin.username}")
        
        # Teste 1: Página inicial
        print("   🧪 Página inicial (/)...")
        response = client.get('/')
        print(f"      Status: {response.status_code}")
        if response.status_code == 302:
            print(f"      🔄 Redirecionamento para: {response.url}")
            if response.url == '/dashboard/':
                print("      ✅ CORRETO: Redirecionado para dashboard super admin")
            else:
                print("      ❌ PROBLEMA: Redirecionamento incorreto")
        
        # Teste 2: Tentativa de acessar login de loja
        loja = Loja.objects.filter(status='ativa').first()
        if loja:
            try:
                login_config = loja.login_personalizado
                login_url = login_config.get_login_url()
                
                print(f"   🧪 Tentativa de acesso ao login de loja ({login_url})...")
                response = client.get(login_url)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 302:
                    print(f"      🔄 Redirecionamento para: {response.url}")
                    if '/admin/' in response.url:
                        print("      ✅ CORRETO: Super admin bloqueado e redirecionado para admin")
                    else:
                        print("      ❌ PROBLEMA: Redirecionamento incorreto")
                elif response.status_code == 200:
                    print("      ❌ PROBLEMA: Super admin conseguiu acessar login de loja")
                
            except Exception as e:
                print(f"      ⚠️  Erro ao testar login de loja: {str(e)}")
        
        # Teste 3: Acesso ao admin
        print("   🧪 Acesso ao admin (/admin/)...")
        response = client.get('/admin/')
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print("      ✅ CORRETO: Super admin acessa admin normalmente")
        elif response.status_code == 302:
            print(f"      🔄 Redirecionamento para: {response.url}")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

def testar_cenario_heroku():
    """Testa cenário específico do Heroku com uma loja"""
    
    try:
        # Simular cenário Heroku
        print("   🌐 Simulando cenário Heroku (uma loja ativa)...")
        
        # Desativar todas as lojas exceto uma
        lojas = Loja.objects.all()
        primeira_loja = lojas.first()
        
        if primeira_loja:
            Loja.objects.exclude(id=primeira_loja.id).update(status='inativa')
            primeira_loja.status = 'ativa'
            primeira_loja.save()
            print(f"      Mantida apenas: {primeira_loja.nome}")
        
        # Testar com super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if super_admin:
            client = Client()
            client.force_login(super_admin)
            
            # Teste página inicial
            print("   🧪 Super admin na página inicial (cenário Heroku)...")
            response = client.get('/')
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"      🔄 Redirecionamento para: {response.url}")
                if response.url == '/dashboard/':
                    print("      ✅ CORRETO: Super admin vai direto para dashboard")
                elif 'login' in response.url and 'admin' not in response.url:
                    print("      ❌ PROBLEMA: Super admin sendo redirecionado para login de loja")
                else:
                    print(f"      ⚠️  INESPERADO: {response.url}")
            elif response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'Acesso para Administradores' in content:
                    print("      ⚠️  Super admin vendo página de seleção (pode estar OK)")
                else:
                    print("      ❌ PROBLEMA: Página inesperada")
        
        # Restaurar estado original
        Loja.objects.all().update(status='ativa')
        print("   ✅ Estado original restaurado")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

if __name__ == '__main__':
    main()