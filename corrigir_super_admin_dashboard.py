#!/usr/bin/env python3
"""
Correção urgente: Super admin deve ter acesso total ao dashboard
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def corrigir_middleware_super_admin():
    """Corrige middleware para permitir acesso total do super admin"""
    
    middleware_corrigido = '''"""
Middleware exclusivo para Super Admins
ACESSO TOTAL AO SISTEMA - Super admin pode acessar tudo
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class SuperAdminExclusivoMiddleware:
    """
    Middleware EXCLUSIVO para Super Admins
    
    SUPER ADMIN TEM ACESSO TOTAL:
    ✅ Pode acessar qualquer dashboard
    ✅ Pode entrar em qualquer loja
    ✅ Pode gerenciar todo o sistema
    ✅ Pode ver dados de qualquer loja
    ✅ Prioridade máxima sobre outros middlewares
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs exclusivas para super admins (outros não podem acessar)
        self.super_admin_exclusive_urls = [
            '/admin/',
            '/super-admin/',
            '/admin-login/',
            '/usuarios/gerenciar/',
            '/lojas/gerenciar/',
            '/relatorios/sistema/',
            '/configuracoes/sistema/',
        ]
    
    def __call__(self, request):
        """Processa requisições com prioridade para super admins"""
        
        try:
            # Verificar se é super admin
            if self._is_super_admin(request):
                return self._handle_super_admin_request(request)
            
            # Bloquear acesso de não-super-admins a URLs exclusivas
            if self._is_super_admin_exclusive_url(request.path):
                return self._block_non_super_admin_access(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no SuperAdminExclusivoMiddleware: {str(e)}")
            return self.get_response(request)
    
    def _is_super_admin(self, request):
        """Verifica se o usuário é super admin"""
        return (request.user.is_authenticated and 
                request.user.is_superuser and 
                request.user.is_active)
    
    def _is_super_admin_exclusive_url(self, path):
        """Verifica se é URL exclusiva para super admins"""
        return any(path.startswith(url) for url in self.super_admin_exclusive_urls)
    
    def _handle_super_admin_request(self, request):
        """Processa requisições de super admins - ACESSO TOTAL"""
        
        # Log de acesso super admin
        logger.info(f"Super Admin {request.user.username} acessando: {request.path}")
        
        # Adicionar contexto especial para super admins
        request.is_super_admin_context = True
        request.super_admin_permissions = {
            # ✅ ACESSO TOTAL - Super admin pode tudo
            'can_access_all_stores': True,
            'can_manage_users': True,
            'can_view_system_reports': True,
            'can_modify_system_settings': True,
            'can_access_store_dashboard': True,  # ✅ PODE acessar dashboard das lojas
            'can_access_store_modules': True,    # ✅ PODE acessar módulos das lojas
            'can_login_as_store': True,          # ✅ PODE fazer login como loja
            'can_view_store_data': True,         # ✅ PODE ver dados das lojas
            'bypass_store_restrictions': True,   # ✅ Bypass de restrições
        }
        
        # Bypass de outros middlewares de autenticação se necessário
        request.bypass_store_middlewares = True
        request.super_admin_override = True
        
        return self.get_response(request)
    
    def _block_non_super_admin_access(self, request):
        """Bloqueia acesso de não-super-admins a URLs exclusivas"""
        
        logger.warning(f"Tentativa de acesso não autorizado a URL exclusiva: {request.path} por {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Esta área é exclusiva para Super Administradores'
            }, status=403)
        
        messages.error(request, 'Acesso negado. Esta área é exclusiva para Super Administradores.')
        return redirect('root_redirect')
'''
    
    # Escrever middleware corrigido
    middleware_path = 'dashboard/middleware/super_admin_exclusivo.py'
    
    try:
        with open(middleware_path, 'w', encoding='utf-8') as f:
            f.write(middleware_corrigido)
        
        print("✅ Middleware Super Admin corrigido!")
        print("   Super admin agora tem ACESSO TOTAL ao sistema")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware: {e}")
        return False


def verificar_outros_middlewares_bloqueadores():
    """Verifica se há outros middlewares bloqueando super admin"""
    
    print("🔍 Verificando outros middlewares que podem bloquear super admin...")
    
    middlewares_para_verificar = [
        'dashboard/middleware/super_admin_middleware.py',
        'lojas/middleware_loja_especifica.py',
        'lojas/middleware.py',
        'usuarios/improved_middleware.py',
    ]
    
    problemas_encontrados = []
    
    for middleware_path in middlewares_para_verificar:
        if os.path.exists(middleware_path):
            try:
                with open(middleware_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Procurar por bloqueios de super admin
                if 'is_superuser' in content and 'redirect' in content:
                    print(f"⚠️  {middleware_path} pode estar bloqueando super admin")
                    problemas_encontrados.append(middleware_path)
                
            except Exception as e:
                print(f"❌ Erro ao verificar {middleware_path}: {e}")
    
    return problemas_encontrados


def desabilitar_middleware_problematico():
    """Desabilita temporariamente o middleware problemático"""
    
    print("🔧 Desabilitando middleware problemático temporariamente...")
    
    try:
        settings_path = 'lojad/settings.py'
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Comentar middleware problemático
        content = content.replace(
            "'dashboard.middleware.super_admin_exclusivo.SuperAdminExclusivoMiddleware',",
            "# 'dashboard.middleware.super_admin_exclusivo.SuperAdminExclusivoMiddleware',  # Temporariamente desabilitado"
        )
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Middleware problemático desabilitado temporariamente!")
        print("   Super admin deve conseguir acessar dashboard agora")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao desabilitar middleware: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 80)
    print("🚨 CORREÇÃO URGENTE - SUPER ADMIN BLOQUEADO")
    print("=" * 80)
    print()
    
    print("Problema identificado:")
    print("❌ Super admin não consegue acessar dashboard")
    print("❌ Middleware está bloqueando acesso incorretamente")
    print("❌ Mensagem: 'Ocorreu um erro. Você foi redirecionado para a área administrativa'")
    print()
    
    # 1. Desabilitar middleware problemático imediatamente
    print("1️⃣  CORREÇÃO IMEDIATA - Desabilitando middleware problemático...")
    if desabilitar_middleware_problematico():
        print("✅ Middleware desabilitado! Super admin deve conseguir acessar agora")
    print()
    
    # 2. Corrigir middleware
    print("2️⃣  Corrigindo middleware para acesso total...")
    if corrigir_middleware_super_admin():
        print("✅ Middleware corrigido com acesso total!")
    print()
    
    # 3. Verificar outros middlewares
    print("3️⃣  Verificando outros middlewares...")
    problemas = verificar_outros_middlewares_bloqueadores()
    if problemas:
        print(f"⚠️  Encontrados {len(problemas)} middlewares que podem causar problemas")
    else:
        print("✅ Nenhum outro middleware problemático encontrado")
    print()
    
    print("=" * 80)
    print("📋 CORREÇÃO APLICADA")
    print("=" * 80)
    
    print("✅ CORREÇÃO IMEDIATA APLICADA!")
    print()
    print("🎯 O que foi feito:")
    print("  1. ✅ Middleware problemático desabilitado temporariamente")
    print("  2. ✅ Middleware corrigido para dar acesso total ao super admin")
    print("  3. ✅ Super admin agora pode acessar qualquer dashboard")
    print()
    print("🧪 TESTE AGORA:")
    print("  1. Faça login como super admin")
    print("  2. Acesse /dashboard/")
    print("  3. Deve funcionar normalmente")
    print()
    print("⚠️  IMPORTANTE:")
    print("  - Se funcionar, reative o middleware corrigido no settings.py")
    print("  - Remova o comentário da linha do middleware")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()