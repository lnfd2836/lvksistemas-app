"""
Middleware específico para webhooks do Asaas
"""
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


class WebhookMiddleware:
    """
    Middleware que intercepta webhooks do Asaas antes de qualquer verificação de autenticação
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verifica se é um webhook do Asaas
        if '/asaas/webhook' in request.path:
            logger.info(f"Webhook interceptado: {request.path}")
            # Marca a requisição como webhook para outros middlewares
            request.is_webhook = True
            # Processa a requisição normalmente
            response = self.get_response(request)
            return response
        
        # Para outras requisições, processa normalmente
        return self.get_response(request)
