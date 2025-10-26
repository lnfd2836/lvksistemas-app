"""
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
