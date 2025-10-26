"""
Middleware exclusivo para integração Asaas
Gerencia webhooks, pagamentos e sincronização
"""
import logging
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

logger = logging.getLogger(__name__)


class AsaasExclusivoMiddleware:
    """
    Middleware EXCLUSIVO para integração Asaas
    - Gerencia webhooks com prioridade
    - Valida IPs autorizados
    - Processa pagamentos automaticamente
    - Sincronização em tempo real
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs exclusivas para Asaas
        self.asaas_exclusive_urls = [
            '/webhook/asaas/',
            '/api/asaas/',
            '/financeiro/asaas/',
            '/pagamentos/asaas/',
            '/sync/asaas/',
        ]
        
        # IPs autorizados do Asaas (sandbox e produção)
        self.asaas_authorized_ips = [
            '18.229.47.223',
            '18.231.194.64',
            '52.67.73.224',
            '127.0.0.1',  # Para testes locais
            '0.0.0.0',    # Para desenvolvimento
        ]
        
        # Headers obrigatórios do Asaas
        self.required_asaas_headers = [
            'HTTP_USER_AGENT',
            'HTTP_CONTENT_TYPE',
        ]
    
    def __call__(self, request):
        """Processa requisições Asaas com prioridade máxima"""
        
        try:
            # Verificar se é requisição Asaas
            if self._is_asaas_request(request):
                return self._handle_asaas_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no AsaasExclusivoMiddleware: {str(e)}")
            return HttpResponse("Internal Error", status=500)
    
    def _is_asaas_request(self, path):
        """Verifica se é requisição do Asaas"""
        return any(path.startswith(url) for url in self.asaas_exclusive_urls)
    
    def _handle_asaas_request(self, request):
        """Processa requisições do Asaas"""
        
        # Log detalhado da requisição Asaas
        logger.info(f"Requisição Asaas recebida: {request.method} {request.path}")
        logger.info(f"IP: {self._get_client_ip(request)}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        
        # Validar IP (apenas em produção)
        if not settings.DEBUG and not self._validate_asaas_ip(request):
            logger.warning(f"IP não autorizado tentando acessar Asaas: {self._get_client_ip(request)}")
            return HttpResponse("Forbidden", status=403)
        
        # Validar headers obrigatórios
        if not self._validate_asaas_headers(request):
            logger.warning("Headers obrigatórios ausentes em requisição Asaas")
            return HttpResponse("Bad Request", status=400)
        
        # Adicionar contexto Asaas
        request.is_asaas_request = True
        request.asaas_validated = True
        
        # Bypass de middlewares desnecessários para performance
        request.bypass_auth_middlewares = True
        request.bypass_csrf = True
        
        # Processar webhook se for POST
        if request.method == 'POST' and '/webhook/' in request.path:
            return self._process_asaas_webhook(request)
        
        return self.get_response(request)
    
    def _validate_asaas_ip(self, request):
        """Valida se o IP é autorizado pelo Asaas"""
        client_ip = self._get_client_ip(request)
        return client_ip in self.asaas_authorized_ips
    
    def _validate_asaas_headers(self, request):
        """Valida headers obrigatórios do Asaas"""
        for header in self.required_asaas_headers:
            if not request.META.get(header):
                return False
        return True
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _process_asaas_webhook(self, request):
        """Processa webhook do Asaas"""
        try:
            # Parse do JSON
            webhook_data = json.loads(request.body.decode('utf-8'))
            
            # Log do webhook
            logger.info(f"Webhook Asaas processado: {webhook_data.get('event', 'unknown')}")
            
            # Processar usando serviço existente
            from controle_financeiro.asaas_service import AsaasService
            asaas_service = AsaasService()
            resultado = asaas_service.processar_webhook(webhook_data)
            
            if resultado.get('success'):
                return HttpResponse("OK", status=200)
            else:
                return HttpResponse("Processing Error", status=400)
                
        except json.JSONDecodeError:
            logger.error("Webhook Asaas com JSON inválido")
            return HttpResponse("Invalid JSON", status=400)
        except Exception as e:
            logger.error(f"Erro ao processar webhook Asaas: {str(e)}")
            return HttpResponse("Internal Error", status=500)
