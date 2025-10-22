"""
View completamente independente para webhook - sem Django decorators
"""
from django.http import HttpResponse
import json
import logging

logger = logging.getLogger(__name__)


def webhook_asaas_raw(request):
    """
    View completamente raw para webhook - sem decorators, sem middlewares
    """
    try:
        # Log básico
        logger.info(f"=== WEBHOOK ASAAS RAW ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        
        # Verifica se é POST
        if request.method != 'POST':
            return HttpResponse("Method not allowed", status=405)
        
        # Parsear dados
        try:
            webhook_data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Webhook recebido: {webhook_data}")
        except json.JSONDecodeError:
            logger.error("Webhook com JSON inválido")
            return HttpResponse("Invalid JSON", status=400)
        
        # Processar webhook usando serviço existente
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
            
    except Exception as e:
        logger.error(f"Erro no webhook raw: {str(e)}")
        return HttpResponse("Internal Error", status=500)
