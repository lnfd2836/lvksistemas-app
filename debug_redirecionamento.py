#!/usr/bin/env python
"""
Script para debugar redirecionamentos em detalhes
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.test import Client, RequestFactory
from django.urls import resolve, reverse
from django.contrib.auth.models import AnonymousUser
import logging

# Configurar logging detalhado
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Debug detalhado de redirecionamentos"""
    
    print("🔍 DEBUG DETALHADO DE REDIRECIONAMENTOS")
    print("=" * 50)
    
    # 1. Verificar resolução de URLs
    print("\n1️⃣ VERIFICANDO RESOLUÇÃO DE URLS")
    verificar_urls()
    
    # 2. Testar middlewares individualmente
    print("\n2️⃣ TESTANDO MIDDLEWARES")
    testar_middlewares()
    
    # 3. Testar view diretamente
    print("\n3️⃣ TESTANDO VIEW DIRETAMENTE")
    testar_view_direta()
    
    print("\n✅ DEBUG CONCLUÍDO")

def verificar_urls():
    """Verifica a resolução de URLs"""
    
    urls_para_testar = [
        '/',
        '/login/',
        '/usuarios/login/',
        '/dashboard/',
        '/admin/',
    ]
    
    for url in urls_para_testar:
        try:
            resolver_match = resolve(url)
            print(f"   {url} → {resolver_match.view_name} ({resolver_match.func})")
        except Exception as e:
            print(f"   {url} → ERRO: {str(e)}")

def testar_middlewares():
    """Testa middlewares individualmente"""
    
    from django.conf import settings
    
    middlewares = settings.MIDDLEWARE
    print(f"   Total de middlewares: {len(middlewares)}")
    
    # Criar uma requisição de teste
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    request.session = {}
    
    for i, middleware_path in enumerate(middlewares):
        print(f"   [{i+1}] {middleware_path}")
        
        try:
            # Importar e instanciar o middleware
            module_path, class_name = middleware_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            middleware_class = getattr(module, class_name)
            
            # Testar se o middleware processa a requisição
            def dummy_get_response(req):
                return None
            
            middleware = middleware_class(dummy_get_response)
            
            # Verificar se tem process_request
            if hasattr(middleware, 'process_request'):
                result = middleware.process_request(request)
                if result:
                    print(f"       → INTERCEPTOU: {type(result)} - {getattr(result, 'url', 'N/A')}")
            
            # Verificar se tem __call__
            elif hasattr(middleware, '__call__'):
                try:
                    result = middleware(request)
                    if result and hasattr(result, 'status_code'):
                        if result.status_code in [301, 302]:
                            print(f"       → REDIRECIONOU: {getattr(result, 'url', 'N/A')}")
                        else:
                            print(f"       → RETORNOU: Status {result.status_code}")
                except Exception as e:
                    print(f"       → ERRO: {str(e)}")
            
        except Exception as e:
            print(f"       → ERRO AO CARREGAR: {str(e)}")

def testar_view_direta():
    """Testa a view diretamente"""
    
    try:
        from dashboard.smart_redirect import smart_login_redirect
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        
        # Criar requisição de teste
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        request.session = {}
        
        print("   Testando smart_login_redirect diretamente...")
        
        # Adicionar atributos necessários
        class MockMessages:
            def info(self, request, message):
                print(f"       MESSAGE INFO: {message}")
            def error(self, request, message):
                print(f"       MESSAGE ERROR: {message}")
        
        import django.contrib.messages as messages_module
        original_info = messages_module.info
        original_error = messages_module.error
        
        messages_module.info = lambda r, m: print(f"       MESSAGE INFO: {m}")
        messages_module.error = lambda r, m: print(f"       MESSAGE ERROR: {m}")
        
        try:
            response = smart_login_redirect(request)
            print(f"   Resultado: {type(response)}")
            if hasattr(response, 'status_code'):
                print(f"   Status: {response.status_code}")
                if hasattr(response, 'url'):
                    print(f"   URL: {response.url}")
        finally:
            messages_module.info = original_info
            messages_module.error = original_error
        
    except Exception as e:
        print(f"   ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()