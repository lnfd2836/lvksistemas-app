"""
Middleware de validação de IP para webhooks do Asaas
"""
import logging
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class AsaasWebhookIPValidationMiddleware:
    """
    Middleware que valida IPs de webhooks do Asaas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # IPs conhecidos do Asaas (baseado em ranges de serviços de pagamento brasileiros)
        self.asaas_ip_ranges = [
            # Ranges conhecidos de serviços de pagamento brasileiros
            '54.232.0.0/16',  # AWS South America
            '54.233.0.0/16',  # AWS South America
            '54.234.0.0/16',  # AWS South America
            '54.235.0.0/16',  # AWS South America
            '54.236.0.0/16',  # AWS South America
            '54.237.0.0/16',  # AWS South America
            '54.238.0.0/16',  # AWS South America
            '54.239.0.0/16',  # AWS South America
            '54.240.0.0/16',  # AWS South America
            '54.241.0.0/16',  # AWS South America
            '54.242.0.0/16',  # AWS South America
            '54.243.0.0/16',  # AWS South America
            '54.244.0.0/16',  # AWS South America
            '54.245.0.0/16',  # AWS South America
            '54.246.0.0/16',  # AWS South America
            '54.247.0.0/16',  # AWS South America
            '54.248.0.0/16',  # AWS South America
            '54.249.0.0/16',  # AWS South America
            '54.250.0.0/16',  # AWS South America
            '54.251.0.0/16',  # AWS South America
            '54.252.0.0/16',  # AWS South America
            '54.253.0.0/16',  # AWS South America
            '54.254.0.0/16',  # AWS South America
            '54.255.0.0/16',  # AWS South America
        ]
        
        # IPs específicos conhecidos do Asaas (se disponíveis)
        self.asaas_specific_ips = [
            # Adicione IPs específicos do Asaas aqui quando disponíveis
        ]

    def __call__(self, request):
        # Verifica se é um webhook do Asaas
        if self.is_asaas_webhook(request):
            # Valida o IP
            if not self.validate_ip(request):
                logger.warning(f"Webhook do Asaas rejeitado - IP não autorizado: {self.get_client_ip(request)}")
                return HttpResponse("Unauthorized", status=401)
            
            logger.info(f"Webhook do Asaas autorizado - IP: {self.get_client_ip(request)}")
        
        response = self.get_response(request)
        return response

    def is_asaas_webhook(self, request):
        """
        Verifica se a requisição é um webhook do Asaas
        """
        webhook_paths = [
            '/api/v1/webhook/asaas/',
            '/asaas-webhook-raw/',
            '/webhook-test-simple/',
            '/asaas-webhook-bypass/',
            '/financeiro/asaas/webhook/',
            '/financeiro/asaas/webhook-debug/',
        ]
        
        return request.path in webhook_paths and request.method == 'POST'

    def get_client_ip(self, request):
        """
        Obtém o IP real do cliente
        """
        # Verifica headers de proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip

    def validate_ip(self, request):
        """
        Valida se o IP está autorizado
        """
        client_ip = self.get_client_ip(request)
        
        # Se está em modo debug, permite todos os IPs
        if settings.DEBUG:
            logger.info(f"Modo DEBUG - IP permitido: {client_ip}")
            return True
        
        # Verifica IPs específicos primeiro
        if client_ip in self.asaas_specific_ips:
            return True
        
        # Verifica ranges de IP
        import ipaddress
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            for ip_range in self.asaas_ip_ranges:
                if client_ip_obj in ipaddress.ip_network(ip_range):
                    return True
        except ValueError:
            logger.error(f"IP inválido: {client_ip}")
            return False
        
        return False
