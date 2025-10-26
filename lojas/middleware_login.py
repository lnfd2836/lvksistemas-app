"""
Middleware para gerenciar redirecionamentos de login baseados no tipo de usuário
"""
import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from dashboard.services.authentication import AuthenticationService

logger = logging.getLogger(__name__)


class LoginRedirectMiddleware:
    """
    Middleware que garante que usuários usem o login correto baseado em seu tipo:
    - Super Admins → /login/ (login exclusivo)
    - Usuários de Loja → /login/{loja}/ (login personalizado da loja)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processar antes da view
        response = self.process_request(request)
        if response:
            return response
        
        # Continuar com a requisição normal
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        """
        Processa a requisição e redireciona se necessário
        """
        # Só processar se o usuário estiver autenticado
        if not request.user.is_authenticated:
            return None
        
        path = request.path
        
        # Verificar se super admin está tentando acessar login de loja
        if request.user.is_superuser:
            if self._is_store_login_path(path):
                logger.warning(f"Super usuário {request.user.username} redirecionado do login de loja para login super admin")
                messages.warning(request, 'Super administradores devem usar o login exclusivo do sistema.')
                return redirect('/admin/login/')
        
        # Verificar se usuário de loja está tentando acessar login super admin
        elif AuthenticationService.is_store_user_only(request.user):
            if path == '/login/' or path == '/login':
                user_store = AuthenticationService.get_user_store(request.user)
                if user_store and hasattr(user_store, 'login_personalizado'):
                    login_config = user_store.login_personalizado
                    if login_config.ativo and login_config.url_personalizada:
                        logger.info(f"Usuário de loja {request.user.username} redirecionado para login personalizado")
                        messages.info(request, f'Redirecionado para o login da {user_store.nome}.')
                        return redirect('login_personalizado_url', url_personalizada=login_config.url_personalizada)
        
        return None
    
    def _is_store_login_path(self, path):
        """
        Verifica se o caminho é um login de loja
        """
        # Padrões de login de loja
        store_login_patterns = [
            '/login/',  # Pode ser confundido, mas vamos tratar no contexto
            '/loja/login/',
        ]
        
        # Verificar se é login personalizado (formato /login/{url}/)
        if path.startswith('/login/') and path != '/login/' and path.count('/') >= 3:
            return True
        
        # Verificar se é login por ID (formato /login/loja/{uuid}/)
        if path.startswith('/login/loja/'):
            return True
        
        return path in store_login_patterns


class UserTypeValidationMiddleware:
    """
    Middleware que valida se o usuário está acessando as áreas corretas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Valida o acesso baseado no tipo de usuário
        """
        if not request.user.is_authenticated:
            return None
        
        path = request.path
        user_level = AuthenticationService.get_user_access_level(request.user)
        
        # Log do tipo de usuário para debug
        logger.debug(f"Usuário {request.user.username} ({user_level}) acessando {path}")
        
        # Validações específicas podem ser adicionadas aqui
        # Por exemplo, bloquear funcionários de acessar certas áreas
        
        return None