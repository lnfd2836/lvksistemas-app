"""
Middleware para tratamento de erros de URL e logging
"""
import logging
from django.http import HttpResponseServerError
from django.template import TemplateDoesNotExist
from django.urls.exceptions import NoReverseMatch
from django.shortcuts import render
from django.conf import settings

logger = logging.getLogger(__name__)


class URLErrorHandlingMiddleware:
    """
    Middleware para capturar e tratar erros de URL routing
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """
        Processa exceções relacionadas a URLs
        """
        if isinstance(exception, NoReverseMatch):
            # Log do erro de URL
            logger.error(
                f"NoReverseMatch error: {exception} - "
                f"Path: {request.path} - "
                f"User: {getattr(request.user, 'username', 'Anonymous')}"
            )
            
            # Em desenvolvimento, mostra o erro detalhado
            if settings.DEBUG:
                return None  # Deixa o Django mostrar o erro padrão
            
            # Em produção, mostra uma página de erro amigável
            try:
                return render(request, 'errors/url_error.html', {
                    'error_message': 'Erro de navegação. Tente novamente ou entre em contato com o suporte.',
                    'error_code': 'URL_ERROR'
                }, status=500)
            except TemplateDoesNotExist:
                # Fallback se o template não existir
                return HttpResponseServerError(
                    "Erro interno do servidor. Tente novamente mais tarde."
                )
        
        return None


class RequestLoggingMiddleware:
    """
    Middleware para logging de requisições
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log da requisição
        logger.info(
            f"Request: {request.method} {request.path} - "
            f"User: {getattr(request.user, 'username', 'Anonymous')} - "
            f"IP: {self.get_client_ip(request)}"
        )
        
        response = self.get_response(request)
        
        # Log da resposta se houver erro
        if response.status_code >= 400:
            logger.warning(
                f"Response: {response.status_code} for {request.method} {request.path} - "
                f"User: {getattr(request.user, 'username', 'Anonymous')}"
            )
        
        return response
    
    def get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip