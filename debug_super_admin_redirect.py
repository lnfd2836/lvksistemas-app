#!/usr/bin/env python
"""
Script para debugar especificamente o redirecionamento do super admin
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from dashboard.services.authentication import AuthenticationService
from dashboard.smart_redirect import smart_login_redirect
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Debug específico do super admin"""
    
    print("🔍 DEBUG SUPER ADMIN REDIRECT")
    print("=" * 50)
    
    # 1. Testar AuthenticationService diretamente
    print("\n1️⃣ TESTANDO AUTHENTICATIONSERVICE")
    testar_authentication_service()
    
    # 2. Testar smart_redirect com super admin
    print("\n2️⃣ TESTANDO SMART_REDIRECT COM SUPER ADMIN")
    testar_smart_redirect_super_admin()
    
    # 3. Testar via Client
    print("\n3️⃣ TESTANDO VIA CLIENT")
    testar_via_client()
    
    print("\n✅ DEBUG CONCLUÍDO")

def testar_authentication_service():
    """Testa o AuthenticationService diretamente"""
    
    try:
        # Buscar um super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ❌ Nenhum super admin encontrado")
            return
        
        print(f"   👤 Super admin encontrado: {super_admin.username}")
        print(f"   🔑 is_superuser: {super_admin.is_superuser}")
        print(f"   ✅ is_authenticated: {super_admin.is_authenticated}")
        
        # Testar determine_user_dashboard
        try:
            dashboard_url = AuthenticationService.determine_user_dashboard(super_admin)
            print(f"   🎯 Dashboard URL: {dashboard_url}")
            
            # Verificar as constantes
            print(f"   📋 DASHBOARD_URLS: {AuthenticationService.DASHBOARD_URLS}")
            
        except Exception as e:
            print(f"   ❌ Erro no determine_user_dashboard: {str(e)}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"   ❌ Erro geral: {str(e)}")

def testar_smart_redirect_super_admin():
    """Testa o smart_redirect com super admin"""
    
    try:
        # Buscar um super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ❌ Nenhum super admin encontrado")
            return
        
        # Criar requisição simulada
        factory = RequestFactory()
        request = factory.get('/')
        request.user = super_admin
        request.session = {}
        
        # Mock das mensagens
        import django.contrib.messages as messages_module
        original_info = messages_module.info
        original_error = messages_module.error
        
        messages_module.info = lambda r, m: print(f"       MESSAGE INFO: {m}")
        messages_module.error = lambda r, m: print(f"       MESSAGE ERROR: {m}")
        
        try:
            print(f"   👤 Testando com super admin: {super_admin.username}")
            response = smart_login_redirect(request)
            
            print(f"   📊 Tipo de resposta: {type(response)}")
            print(f"   📊 Status: {getattr(response, 'status_code', 'N/A')}")
            
            if hasattr(response, 'url'):
                print(f"   🔗 URL de redirecionamento: {response.url}")
            elif hasattr(response, 'content'):
                content_preview = response.content[:200].decode('utf-8', errors='ignore')
                print(f"   📄 Conteúdo (preview): {content_preview}")
                
        finally:
            messages_module.info = original_info
            messages_module.error = original_error
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

def testar_via_client():
    """Testa via Django Test Client"""
    
    try:
        # Buscar um super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ❌ Nenhum super admin encontrado")
            return
        
        client = Client()
        
        # Fazer login como super admin
        client.force_login(super_admin)
        print(f"   👤 Logado como: {super_admin.username}")
        
        # Testar página inicial
        response = client.get('/')
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   🔗 Redirecionamento para: {response.url}")
            
            # Seguir o redirecionamento
            if response.url:
                print(f"   🔄 Seguindo redirecionamento...")
                response2 = client.get(response.url)
                print(f"   📊 Status final: {response2.status_code}")
                
                if response2.status_code == 302:
                    print(f"   🔗 Segundo redirecionamento para: {response2.url}")
                elif response2.status_code == 200:
                    print("   ✅ Página carregada com sucesso")
                    content_preview = response2.content[:200].decode('utf-8', errors='ignore')
                    print(f"   📄 Conteúdo (preview): {content_preview}")
                    
        elif response.status_code == 200:
            print("   ✅ Página carregada diretamente")
            content_preview = response.content[:200].decode('utf-8', errors='ignore')
            print(f"   📄 Conteúdo (preview): {content_preview}")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()