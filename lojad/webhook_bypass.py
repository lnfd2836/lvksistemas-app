"""
Webhook direto sem Django - bypass completo
"""
from django.http import HttpResponse
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


def webhook_asaas_bypass(request):
    """
    Endpoint que bypassa TODOS os middlewares do Django
    """
    try:
        # Log detalhado
        logger.info(f"=== WEBHOOK ASAAS BYPASS ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'N/A')}")
        logger.info(f"Body length: {len(request.body)}")
        
        # Parsear dados
        webhook_data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Webhook recebido: {webhook_data}")
        
        # Processar usando serviço existente
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
        logger.error(f"Erro no webhook bypass: {str(e)}")
        return HttpResponse("Internal Error", status=500)
