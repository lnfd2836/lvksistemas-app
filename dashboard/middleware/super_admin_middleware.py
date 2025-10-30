"""
Middleware exclusivo para super admins - garante acesso prioritário ao admin
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class SuperAdminMiddleware:
    """
    Middleware exclusivo para super admins que garante acesso prioritário
    ao sistema de administração sem interferência de outros middlewares.
    
    Este middleware deve ser colocado no INÍCIO da lista de middlewares
    para ter prioridade máxima.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs exclusivas para super admins
        self.super_admin_urls = [
            '/admin/',
            '/admin-login/',
            '/super-admin/',
        ]
        
        # URLs que devem ser protegidas para super admins
        self.protected_admin_paths = [
            '/admin/login/',
            '/admin/logout/',
            '/admin/password_change/',
            '/admin/password_change/done/',
        ]
        
        # URLs de login de loja que super admins NÃO devem acessar
        self.store_login_patterns = [
            '/login/',  # Exceto quando é redirecionamento inteligente
            '/loja/login/',
        ]
        
        # URLs do dashboard que super admins PODEM acessar
        self.allowed_dashboard_paths = [
            '/dashboard/',
            '/financeiro/',
        ]
        
        # URLs públicas que NÃO devem ser interceptadas pelo middleware
        self.public_urls = [
            '/crm/orcamento/',   # URLs públicas do CRM
            '/crm/proposta/',    # URLs públicas do CRM
            '/crm/contrato/',    # URLs públicas do CRM
            '/crm/assinar/',     # URLs de assinatura digital do CRM
            '/crm/email/',       # URLs de tracking do CRM
            '/api/',             # APIs públicas
            '/webhook/',         # Webhooks
        ]
    
    def __call__(self, request):
        """
        Processa a requisição com prioridade para super admins
        """
        try:
            # PRIORIDADE 0: Permitir acesso a URLs públicas sem interceptação
            if self._is_public_url(request.path):
                return self.get_response(request)
            
            # PRIORIDADE 1: Verificar se é acesso a URLs de super admin
            if self._is_super_admin_url(request.path):
                return self._handle_super_admin_access(request)
            
            # PRIORIDADE 2: Verificar se super admin está tentando acessar login de loja
            if self._is_super_admin_accessing_store_login(request):
                return self._redirect_super_admin_to_admin(request)
            
            # PRIORIDADE 3: Verificar se é super admin autenticado acessando área protegida
            if self._is_authenticated_super_admin(request) and self._needs_admin_redirect(request):
                return self._handle_authenticated_super_admin(request)
            
            # Continuar com processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no SuperAdminMiddleware: {str(e)}")
            # Em caso de erro, continuar normalmente para não quebrar o sistema
            return self.get_response(request)
    
    def _is_public_url(self, path):
        """Verifica se é uma URL pública que não deve ser interceptada"""
        return any(path.startswith(public_url) for public_url in self.public_urls)
    
    def _is_super_admin_url(self, path):
        """Verifica se é uma URL exclusiva de super admin"""
        return any(path.startswith(admin_url) for admin_url in self.super_admin_urls)
    
    def _is_super_admin_accessing_store_login(self, request):
        """Verifica se um super admin está tentando acessar login de loja"""
        if not self._is_authenticated_super_admin(request):
            return False
        
        path = request.path
        
        # CORREÇÃO: Permitir acesso completo a URLs do dashboard
        if path.startswith('/dashboard/'):
            return False
        
        # CORREÇÃO: Permitir que super admins VISUALIZEM páginas de login das lojas (GET)
        # Mas bloquear tentativas de fazer login (POST)
        if request.method == 'GET':
            # Super admins podem visualizar páginas de login para administração/teste
            return False
        
        # Bloquear apenas tentativas de POST (fazer login)
        if request.method == 'POST':
            # Verificar se está tentando fazer login em loja
            if path.startswith('/login/') and path != '/login/':
                logger.warning(f"Super admin {request.user.username} tentando fazer login via loja: {path}")
                return True
            
            # Verificar outros padrões de login de loja
            for pattern in self.store_login_patterns:
                if path == pattern:
                    logger.warning(f"Super admin {request.user.username} tentando fazer login via: {path}")
                    return True
        
        return False
    
    def _is_authenticated_super_admin(self, request):
        """Verifica se é um super admin autenticado"""
        return (hasattr(request, 'user') and 
                request.user.is_authenticated and 
                request.user.is_superuser)
    
    def _needs_admin_redirect(self, request):
        """Verifica se super admin precisa ser redirecionado para admin"""
        path = request.path
        
        # Se está na página inicial, deve ir para dashboard
        if path == '/' or path == '':
            return True
        
        # CORREÇÃO: Não redirecionar se está acessando qualquer URL do dashboard ou financeiro
        if path.startswith('/dashboard/') or path.startswith('/financeiro/'):
            return False
        
        # Se está tentando acessar URLs de loja (exceto admin)
        if path.startswith('/loja/') and not path.startswith('/loja/admin/'):
            return True
        
        return False
    
    def _handle_super_admin_access(self, request):
        """Manipula acesso a URLs de super admin"""
        
        # Se já é super admin autenticado acessando /admin/, permitir
        if self._is_authenticated_super_admin(request):
            if request.path.startswith('/admin/') and request.path != '/admin-login/':
                return self.get_response(request)
        
        # Para /admin-login/ e /super-admin/, redirecionar para /admin/login/
        if request.path in ['/admin-login/', '/super-admin/']:
            logger.info(f"Redirecionando {request.path} para /admin/login/")
            try:
                messages.info(request, 'Acesso exclusivo para administradores do sistema.')
            except:
                pass  # Ignorar erro de mensagens
            return redirect('/admin/login/')
        
        # Continuar processamento normal para outras URLs /admin/
        return self.get_response(request)
    
    def _redirect_super_admin_to_admin(self, request):
        """Redireciona super admin para área administrativa"""
        
        logger.warning(f"Super admin {request.user.username} redirecionado de {request.path} para /admin/")
        
        try:
            messages.warning(
                request, 
                'Super administradores devem usar a área administrativa exclusiva. '
                'Você foi redirecionado automaticamente.'
            )
        except:
            pass  # Ignorar erro de mensagens
        
        return redirect('/admin/')
    
    def _handle_authenticated_super_admin(self, request):
        """Manipula super admin autenticado que precisa ser redirecionado"""
        
        path = request.path
        
        # Se está na página inicial, redirecionar para dashboard super admin
        if path == '/' or path == '':
            logger.info(f"Super admin {request.user.username} redirecionado da página inicial para dashboard")
            return redirect('/dashboard/')
        
        # Permitir que super admins acessem lojas para administração
        if path.startswith('/lojas/'):
            logger.info(f"Super admin {request.user.username} acessando administração de lojas: {path}")
            # Permitir acesso para administração de lojas
            return self.get_response(request)
        
        # CORREÇÃO: Permitir que super admins acessem páginas de login das lojas para administração/teste
        if path.startswith('/dashboard/loja/login'):
            logger.info(f"Super admin {request.user.username} acessando página de login da loja para administração")
            # Permitir acesso para que super admins possam visualizar e testar login das lojas
            return self.get_response(request)
        
        # Se está tentando acessar área operacional de loja específica (exceto login), redirecionar
        if path.startswith('/loja/') and not path.startswith('/lojas/'):
            logger.warning(f"Super admin {request.user.username} tentou acessar área operacional de loja: {path}")
            try:
                messages.info(request, 'Super admins administram lojas através do painel administrativo.')
            except:
                pass  # Ignorar erro de mensagens
            return redirect('/admin/')
        
        # Continuar processamento normal
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        """Processa exceções que podem ocorrer"""
        
        # Se é super admin e houve erro, tentar redirecionar para área segura
        if self._is_authenticated_super_admin(request):
            logger.error(f"Exceção para super admin {request.user.username}: {str(exception)}")
            
            # PERMITIR que super admins vejam erros em /lojas/, /dashboard/ e /financeiro/ para debug
            if (request.path.startswith('/lojas/') or 
                request.path.startswith('/dashboard/') or 
                request.path.startswith('/financeiro/')):
                logger.info(f"Permitindo que super admin veja erro em {request.path}")
                return None  # Deixar Django tratar o erro normalmente
            
            # Se não está em área administrativa (exceto as permitidas), redirecionar
            if not request.path.startswith('/admin/'):
                messages.error(request, 'Ocorreu um erro. Você foi redirecionado para a área administrativa.')
                return redirect('/admin/')
        
        # Não interferir no tratamento normal de exceções
        return None


class SuperAdminProtectionMiddleware:
    """
    Middleware adicional para proteger super admins de acessos indevidos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Protege super admins de acessar áreas inadequadas
        """
        try:
            # Verificar se super admin está tentando fazer login via loja
            if self._is_super_admin_in_store_login(request):
                return self._block_super_admin_store_login(request)
            
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no SuperAdminProtectionMiddleware: {str(e)}")
            return self.get_response(request)
    
    def _is_super_admin_in_store_login(self, request):
        """Verifica se super admin está tentando fazer login via loja"""
        
        if not (hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser):
            return False
        
        path = request.path
        
        # CORREÇÃO: Bloquear apenas tentativas de POST (fazer login)
        # Permitir GET (visualizar página) para administração
        if request.method == 'POST':
            # Verificar se está tentando fazer POST em login personalizado de loja
            if path.startswith('/login/') and path != '/login/':
                return True
            
            # Verificar se está tentando fazer POST em login de loja
            if path in ['/loja/login/', '/login/']:
                return True
        
        return False
    
    def _block_super_admin_store_login(self, request):
        """Bloqueia super admin de fazer login via loja"""
        
        logger.warning(f"Bloqueado acesso de super admin {request.user.username} ao login de loja")
        
        try:
            messages.error(
                request,
                'Super administradores não podem usar o login de loja. '
                'Use o login administrativo exclusivo.'
            )
        except:
            pass  # Ignorar erro de mensagens
        
        return redirect('/admin/login/')