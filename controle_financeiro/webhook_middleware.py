"""
Middleware específico para webhooks - bypassa todos os outros middlewares
"""
import logging

logger = logging.getLogger(__name__)


class WebhookBypassMiddleware:
    """
    Middleware que identifica webhooks e marca a request para bypass
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Paths que são webhooks
        self.webhook_paths = [
            '/webhook/',
            '/api/webhook/',
            '/asaas-webhook',
            '/financeiro/asaas/webhook',
        ]
    
    def __call__(self, request):
        # Marcar se é webhook
        if self.is_webhook_request(request):
            request.is_webhook = True
            logger.info(f"Webhook detectado: {request.path}")
        else:
            request.is_webhook = False
        
        response = self.get_response(request)
        return response
    
    def is_webhook_request(self, request):
        """
        Verifica se a request é um webhook
        """
        # Verifica pelo path
        for webhook_path in self.webhook_paths:
            if request.path.startswith(webhook_path):
                return True
        
        # Verifica pelo User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        webhook_agents = ['asaas', 'webhook', 'bot', 'curl']
        
        for agent in webhook_agents:
            if agent in user_agent:
                return True
        
        # Verifica pelo Content-Type
        content_type = request.META.get('CONTENT_TYPE', '').lower()
        if 'application/json' in content_type and request.method == 'POST':
            # Pode ser um webhook
            return True
        
        return False