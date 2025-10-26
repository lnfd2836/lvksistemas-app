"""
Middleware de autenticação aprimorado para prevenir loops de redirecionamento
e gerenciar sessões de forma mais robusta.
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse, resolve, Resolver404
from django.http import HttpResponse
from django.conf import settings
from usuarios.services import SessionService, RedirectLoopPreventionService, AuthenticationService
import logging

logger = logging.getLogger(__name__)


class ImprovedAuthenticationMiddleware:
    """
    Middleware de autenticação aprimorado que substitui o SessaoUnicaMiddleware
    com melhor tratamento de erros e prevenção de loops.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que não precisam de verificação de sessão
        self.excluded_paths = [
            '/admin/',
            '/login/',
            '/logout/',
            '/loja/login/',
            '/loja/logout/',
            '/webhook/',  # Todos os webhooks
            '/api/',  # Todas as APIs
            '/asaas-webhook',  # Webhooks do Asaas
            '/financeiro/asaas/webhook/',  # Webhook do Asaas não precisa de autenticação
            '/financeiro/asaas/webhook-debug/',  # Webhook debug do Asaas
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        # URLs que são consideradas "login" para detecção de loops
        self.login_urls = [
            '/login/',
            '/loja/login/',
        ]
        
        # URLs que são consideradas "dashboard" para detecção de loops
        self.dashboard_urls = [
            '/dashboard/',
            '/dashboard/loja/dashboard/',
        ]
    
    def __call__(self, request):
        """
        Processa a requisição com verificação de autenticação aprimorada.
        """
        try:
            # Log de debug para webhook
            if '/asaas/webhook' in request.path:
                logger.info(f"=== IMPROVED MIDDLEWARE DEBUG ===")
                logger.info(f"Path: {request.path}")
                logger.info(f"Excluded paths: {self.excluded_paths}")
                logger.info(f"Is excluded: {self.is_excluded_path(request.path)}")
                logger.info(f"Is webhook: {getattr(request, 'is_webhook', False)}")
            
            # Verifica se é um webhook ou se a URL atual está nas exceções
            if getattr(request, 'is_webhook', False) or self.is_excluded_path(request.path):
                return self.get_response(request)
            
            # CORREÇÃO: Não interceptar a página inicial - deixar o smart_redirect lidar com isso
            if request.path == '/' or request.path == '':
                return self.get_response(request)
            
            # Detecta loops de redirecionamento antes de processar
            if self.detect_potential_loop(request):
                logger.warning(f"Loop potencial detectado na URL {request.path}")
                return RedirectLoopPreventionService.handle_redirect_loop(request, "middleware_detection")
            
            # Se o usuário não está autenticado, redireciona para login
            if not request.user.is_authenticated:
                return self.handle_unauthenticated_user(request)
            
            # Valida a sessão do usuário autenticado
            if not SessionService.validate_session(request):
                return self.handle_invalid_session(request)
            
            # Limpa sessões expiradas periodicamente (a cada 100 requisições)
            if hasattr(request, 'session') and request.session.session_key:
                session_key_hash = hash(request.session.session_key)
                if session_key_hash % 100 == 0:  # 1% das requisições
                    try:
                        SessionService.cleanup_expired_sessions()
                    except Exception as e:
                        logger.error(f"Erro na limpeza periódica de sessões: {e}")
            
            # Processa a requisição normalmente
            response = self.get_response(request)
            
            # Limpa rastreamento de redirecionamento em requisições bem-sucedidas
            if response.status_code == 200:
                RedirectLoopPreventionService.clear_redirect_tracking(request)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no middleware de autenticação: {e}")
            # Em caso de erro crítico, permite continuar para evitar quebrar o site
            return self.get_response(request)
    
    def is_excluded_path(self, path: str) -> bool:
        """
        Verifica se o caminho está na lista de exclusões.
        
        Args:
            path: Caminho da URL
            
        Returns:
            True se deve ser excluído da verificação
        """
        # Usa a função utilitária global para verificar webhooks
        if hasattr(settings, 'is_webhook_path') and settings.is_webhook_path(path):
            return True
            
        return any(path.startswith(excluded_path) for excluded_path in self.excluded_paths)
    
    def detect_potential_loop(self, request) -> bool:
        """
        Detecta potenciais loops baseado no padrão da URL atual.
        
        Args:
            request: Objeto de requisição Django
            
        Returns:
            True se detectou potencial loop
        """
        try:
            current_path = request.path
            
            # Verifica se está alternando entre login e dashboard
            if current_path in self.login_urls or current_path in self.dashboard_urls:
                return RedirectLoopPreventionService.detect_circular_pattern(request)
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao detectar loop potencial: {e}")
            return False
    
    def handle_unauthenticated_user(self, request) -> HttpResponse:
        """
        Manipula usuários não autenticados.
        
        Args:
            request: Objeto de requisição Django
            
        Returns:
            HttpResponse apropriada
        """
        try:
            # Verifica se não está criando loop para login
            if not RedirectLoopPreventionService.is_safe_redirect(request, 'root_redirect'):
                logger.warning("Loop detectado ao redirecionar usuário não autenticado para login")
                return RedirectLoopPreventionService.handle_redirect_loop(request, "unauthenticated_loop")
            
            return redirect('root_redirect')
            
        except Exception as e:
            logger.error(f"Erro ao manipular usuário não autenticado: {e}")
            return redirect('root_redirect')
    
    def handle_invalid_session(self, request) -> HttpResponse:
        """
        Manipula sessões inválidas.
        
        Args:
            request: Objeto de requisição Django
            
        Returns:
            HttpResponse apropriada
        """
        try:
            user = request.user
            
            # Verifica se existe alguma sessão ativa para o usuário
            active_sessions = SessionService.get_active_sessions_count(user)
            
            if active_sessions == 0:
                # Não há sessões ativas, tenta criar uma nova
                if SessionService.create_user_session(request, user):
                    logger.info(f"Nova sessão criada para usuário {user.username}")
                    return self.get_response(request)
            
            # Sessão não é mais válida - faz logout
            logger.warning(f"Sessão inválida para usuário {user.username}, forçando logout")
            
            messages.warning(
                request, 
                'Sua sessão foi invalidada porque você fez login em outro local. '
                'Por favor, faça login novamente.'
            )
            
            logout(request)
            
            # Verifica se não está criando loop
            if not RedirectLoopPreventionService.is_safe_redirect(request, 'root_redirect'):
                return RedirectLoopPreventionService.handle_redirect_loop(request, "invalid_session_loop")
            
            return redirect('root_redirect')
            
        except Exception as e:
            logger.error(f"Erro ao manipular sessão inválida: {e}")
            # Em caso de erro, permite continuar para evitar loops
            return self.get_response(request)
    
    def should_skip_validation(self, request) -> bool:
        """
        Determina se deve pular a validação para esta requisição.
        
        Args:
            request: Objeto de requisição Django
            
        Returns:
            True se deve pular a validação
        """
        try:
            # Pula validação para requisições AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return True
            
            # Pula validação para métodos que não são GET/POST
            if request.method not in ['GET', 'POST']:
                return True
            
            # Pula validação se já detectou muitos redirecionamentos
            if RedirectLoopPreventionService.REDIRECT_TRACKING_KEY in request.session:
                tracking = request.session[RedirectLoopPreventionService.REDIRECT_TRACKING_KEY]
                if len(tracking.get('urls', [])) > 10:
                    logger.warning("Muitos redirecionamentos detectados, pulando validação")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar se deve pular validação: {e}")
            return False