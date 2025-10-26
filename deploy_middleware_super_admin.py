#!/usr/bin/env python
"""
Script para fazer deploy do middleware exclusivo de super admin
"""
import os
import sys
import subprocess
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
    """Deploy do middleware exclusivo de super admin"""
    
    print("🚀 DEPLOY MIDDLEWARE EXCLUSIVO SUPER ADMIN")
    print("=" * 50)
    
    # 1. Verificar middleware localmente
    print("\n1️⃣ VERIFICANDO MIDDLEWARE LOCALMENTE")
    if not verificar_middleware_local():
        print("❌ Middleware não funciona localmente. Abortando.")
        return False
    
    # 2. Fazer deploy
    print("\n2️⃣ FAZENDO DEPLOY NO HEROKU")
    if not fazer_deploy():
        print("❌ Erro no deploy.")
        return False
    
    # 3. Instruções finais
    print("\n3️⃣ INSTRUÇÕES FINAIS")
    mostrar_instrucoes_finais()
    
    print("\n✅ DEPLOY CONCLUÍDO COM SUCESSO!")
    return True

def verificar_middleware_local():
    """Verifica se o middleware funciona localmente"""
    
    try:
        # Verificar se middleware está na configuração
        middlewares = settings.MIDDLEWARE
        super_admin_middleware = 'dashboard.middleware.super_admin_middleware.SuperAdminMiddleware'
        
        if super_admin_middleware not in middlewares:
            print("   ❌ SuperAdminMiddleware não encontrado na configuração")
            return False
        
        print("   ✅ SuperAdminMiddleware encontrado na configuração")
        
        # Testar com super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ❌ Nenhum super admin encontrado")
            return False
        
        client = Client()
        client.force_login(super_admin)
        
        # Teste 1: Página inicial deve redirecionar para dashboard
        response = client.get('/')
        if response.status_code == 302 and response.url == '/dashboard/':
            print("   ✅ Super admin redirecionado corretamente da página inicial")
        else:
            print(f"   ❌ Redirecionamento incorreto: {response.status_code} → {getattr(response, 'url', 'N/A')}")
            return False
        
        # Teste 2: URLs de admin devem funcionar
        response = client.get('/admin-login/')
        if response.status_code == 302 and response.url == '/admin/login/':
            print("   ✅ /admin-login/ redirecionando corretamente")
        else:
            print(f"   ❌ /admin-login/ não funciona: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na verificação: {str(e)}")
        return False

def fazer_deploy():
    """Faz o deploy no Heroku"""
    
    try:
        # Commit das mudanças
        print("   📝 Fazendo commit...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        commit_message = "Implementar middleware exclusivo para super admins - correção definitiva"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push para Heroku
        print("   🚀 Fazendo push para Heroku...")
        result = subprocess.run(['git', 'push', 'heroku', 'main'], 
                              capture_output=True, text=True, check=True)
        
        print("   ✅ Deploy realizado com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e):
            print("   ℹ️  Nada para fazer commit, fazendo push...")
            try:
                subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
                print("   ✅ Push realizado com sucesso")
                return True
            except subprocess.CalledProcessError as push_error:
                print(f"   ❌ Erro no push: {str(push_error)}")
                return False
        else:
            print(f"   ❌ Erro no deploy: {str(e)}")
            return False

def mostrar_instrucoes_finais():
    """Mostra instruções finais para teste no Heroku"""
    
    print("   🎯 CORREÇÃO IMPLEMENTADA:")
    print("   ✅ Middleware exclusivo para super admins criado")
    print("   ✅ Prioridade máxima na lista de middlewares")
    print("   ✅ Proteção contra acesso a login de loja")
    print("   ✅ Redirecionamento automático para dashboard")
    print()
    print("   🧪 COMO TESTAR NO HEROKU:")
    print()
    print("   1. SUPER ADMIN AUTENTICADO:")
    print("      - Acesse: https://www.lvksistemas.com.br/")
    print("      - Deve ir DIRETO para /dashboard/ (sem mostrar seleção)")
    print()
    print("   2. SUPER ADMIN NÃO AUTENTICADO:")
    print("      - Acesse: https://www.lvksistemas.com.br/admin-login/")
    print("      - Deve ir para /admin/login/")
    print("      - Faça login com credenciais de super admin")
    print()
    print("   3. PROTEÇÃO CONTRA LOGIN DE LOJA:")
    print("      - Se super admin tentar acessar:")
    print("        https://www.lvksistemas.com.br/login/fatesa-escola-de-ultrassonografia/")
    print("      - Deve ser BLOQUEADO e redirecionado para /admin/")
    print()
    print("   4. URLs ALTERNATIVAS:")
    print("      - https://www.lvksistemas.com.br/super-admin/")
    print("      - https://www.lvksistemas.com.br/?admin=1")
    print()
    print("   🔧 FUNCIONAMENTO DO MIDDLEWARE:")
    print("   - SuperAdminMiddleware: Prioridade máxima, intercepta TODAS as requisições")
    print("   - SuperAdminProtectionMiddleware: Proteção adicional contra acessos indevidos")
    print("   - Posicionado ANTES de todos os outros middlewares de autenticação")
    print("   - Garante que super admins NUNCA vejam login de loja")
    print()
    print("   ⚠️  IMPORTANTE:")
    print("   - O middleware tem prioridade sobre smart_redirect")
    print("   - Super admins autenticados vão DIRETO para dashboard")
    print("   - Super admins não autenticados vão para /admin/login/")
    print("   - Tentativas de acesso a login de loja são BLOQUEADAS")

if __name__ == '__main__':
    main()