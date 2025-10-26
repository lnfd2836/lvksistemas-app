#!/usr/bin/env python
"""
Script para testar o cenário específico do Heroku (uma loja ativa)
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
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from dashboard.smart_redirect import smart_login_redirect
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Testa o cenário específico do Heroku"""
    
    print("🔍 TESTE CENÁRIO HEROKU (UMA LOJA ATIVA)")
    print("=" * 50)
    
    # 1. Simular cenário com apenas uma loja
    print("\n1️⃣ SIMULANDO CENÁRIO COM APENAS UMA LOJA")
    simular_uma_loja()
    
    # 2. Testar com super admin
    print("\n2️⃣ TESTANDO SUPER ADMIN COM UMA LOJA")
    testar_super_admin_uma_loja()
    
    # 3. Restaurar estado original
    print("\n3️⃣ RESTAURANDO ESTADO ORIGINAL")
    restaurar_estado()
    
    print("\n✅ TESTE CONCLUÍDO")

def simular_uma_loja():
    """Simula o cenário do Heroku com apenas uma loja ativa"""
    
    try:
        # Desativar todas as lojas exceto uma
        lojas = Loja.objects.all()
        print(f"   📊 Total de lojas: {lojas.count()}")
        
        # Manter apenas a primeira loja ativa
        primeira_loja = lojas.first()
        if primeira_loja:
            # Desativar todas as outras
            Loja.objects.exclude(id=primeira_loja.id).update(status='inativa')
            
            # Garantir que a primeira está ativa
            primeira_loja.status = 'ativa'
            primeira_loja.save()
            
            print(f"   ✅ Mantida apenas uma loja ativa: {primeira_loja.nome}")
            
            # Verificar se tem login personalizado
            try:
                login_config = primeira_loja.login_personalizado
                print(f"   🔑 Login personalizado: {login_config.ativo}")
                print(f"   🌐 URL: {login_config.get_login_url()}")
            except LoginPersonalizado.DoesNotExist:
                print("   ⚠️  Loja sem login personalizado")
        
        # Verificar quantas lojas ativas restaram
        lojas_ativas = Loja.objects.filter(status='ativa').count()
        print(f"   📊 Lojas ativas após simulação: {lojas_ativas}")
        
    except Exception as e:
        print(f"   ❌ Erro na simulação: {str(e)}")

def testar_super_admin_uma_loja():
    """Testa super admin com apenas uma loja ativa"""
    
    try:
        # Buscar super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ❌ Nenhum super admin encontrado")
            return
        
        print(f"   👤 Super admin: {super_admin.username}")
        
        # Teste 1: Via smart_redirect diretamente
        print("\n   🧪 TESTE 1: smart_redirect direto")
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
            response = smart_login_redirect(request)
            print(f"       Status: {getattr(response, 'status_code', 'N/A')}")
            if hasattr(response, 'url'):
                print(f"       URL: {response.url}")
                
                # Verificar se está indo para login de loja
                if '/login/' in response.url and response.url != '/login/':
                    print("       ❌ PROBLEMA: Super admin sendo redirecionado para login de loja!")
                elif response.url == '/dashboard/':
                    print("       ✅ CORRETO: Super admin indo para dashboard")
                else:
                    print(f"       ⚠️  INESPERADO: Redirecionamento para {response.url}")
                    
        finally:
            messages_module.info = original_info
            messages_module.error = original_error
        
        # Teste 2: Via Client
        print("\n   🧪 TESTE 2: Via Client")
        client = Client()
        client.force_login(super_admin)
        
        response = client.get('/')
        print(f"       Status: {response.status_code}")
        if response.status_code == 302:
            print(f"       URL: {response.url}")
            
            # Verificar se está indo para login de loja
            if '/login/' in response.url and response.url != '/login/':
                print("       ❌ PROBLEMA: Super admin sendo redirecionado para login de loja!")
            elif response.url == '/dashboard/':
                print("       ✅ CORRETO: Super admin indo para dashboard")
            else:
                print(f"       ⚠️  INESPERADO: Redirecionamento para {response.url}")
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()

def restaurar_estado():
    """Restaura o estado original das lojas"""
    
    try:
        # Reativar todas as lojas
        Loja.objects.all().update(status='ativa')
        lojas_ativas = Loja.objects.filter(status='ativa').count()
        print(f"   ✅ Restauradas {lojas_ativas} lojas ativas")
        
    except Exception as e:
        print(f"   ❌ Erro na restauração: {str(e)}")

if __name__ == '__main__':
    main()