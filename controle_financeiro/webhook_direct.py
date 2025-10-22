"""
Endpoint direto para webhook do Asaas - sem middlewares
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_asaas_direct(request):
    """
    Endpoint direto para webhook do Asaas - sem middlewares de autenticação
    """
    try:
        # Log detalhado da requisição
        logger.info(f"=== WEBHOOK ASAAS DIRETO ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'N/A')}")
        logger.info(f"Body length: {len(request.body)}")
        
        # Parsear dados do webhook
        webhook_data = json.loads(request.body.decode('utf-8'))
        
        logger.info(f"Webhook recebido do Asaas: {webhook_data}")
        
        # Processar webhook usando o serviço existente
        try:
            from controle_financeiro.asaas_service import AsaasService
            asaas_service = AsaasService()
            resultado = asaas_service.processar_webhook(webhook_data)
            
            if resultado.get('success'):
                logger.info(f"Webhook processado com sucesso: {resultado.get('message')}")
                return HttpResponse("OK", status=200)
            else:
                logger.error(f"Erro ao processar webhook: {resultado.get('error')}")
                return HttpResponse("Error", status=400)
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return HttpResponse("Processing Error", status=500)
            
    except json.JSONDecodeError:
        logger.error("Webhook com JSON inválido")
        return HttpResponse("Invalid JSON", status=400)
        
    except Exception as e:
        logger.error(f"Erro no webhook Asaas direto: {str(e)}")
        return HttpResponse("Internal Error", status=500)
