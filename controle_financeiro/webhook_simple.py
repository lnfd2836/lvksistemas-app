"""
Webhook simples para Asaas - sem middlewares complexos
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_asaas_simple(request):
    """
    Webhook simples para Asaas - apenas processa e retorna OK
    """
    try:
        # Log básico
        logger.info(f"=== WEBHOOK ASAAS SIMPLE ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")
        logger.info(f"Content-Length: {request.META.get('CONTENT_LENGTH', 'N/A')}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'N/A')}")
        logger.info(f"X-Forwarded-For: {request.META.get('HTTP_X_FORWARDED_FOR', 'N/A')}")
        
        # Verificar se tem body
        if not request.body:
            logger.warning("Webhook sem body")
            return HttpResponse("No body", status=400)
        
        # Parsear JSON
        try:
            webhook_data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Webhook data: {json.dumps(webhook_data, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido: {str(e)}")
            return HttpResponse("Invalid JSON", status=400)
        
        # Extrair informações básicas
        event = webhook_data.get('event', 'UNKNOWN')
        payment = webhook_data.get('payment', {})
        payment_id = payment.get('id', 'N/A')
        payment_status = payment.get('status', 'N/A')
        payment_value = payment.get('value', 'N/A')
        
        logger.info(f"Event: {event}")
        logger.info(f"Payment ID: {payment_id}")
        logger.info(f"Payment Status: {payment_status}")
        logger.info(f"Payment Value: {payment_value}")
        
        # Processar webhook usando o serviço
        try:
            from controle_financeiro.asaas_service import AsaasService
            asaas_service = AsaasService()
            resultado = asaas_service.processar_webhook(webhook_data)
            
            if resultado.get('success'):
                logger.info(f"✅ Webhook processado com sucesso: {resultado.get('message')}")
                return HttpResponse("OK - Processado com sucesso", status=200)
            else:
                logger.error(f"❌ Erro ao processar webhook: {resultado.get('error')}")
                return HttpResponse(f"Error: {resultado.get('error')}", status=400)
                
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return HttpResponse(f"Processing Error: {str(e)}", status=500)
        
    except Exception as e:
        logger.error(f"❌ Erro geral no webhook: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return HttpResponse(f"Internal Error: {str(e)}", status=500)


@csrf_exempt
def webhook_asaas_debug_only(request):
    """
    Webhook apenas para debug - não processa, apenas loga
    """
    try:
        logger.info(f"=== WEBHOOK DEBUG ONLY ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Body: {request.body.decode('utf-8') if request.body else 'Empty'}")
        
        if request.method == 'POST' and request.body:
            try:
                webhook_data = json.loads(request.body.decode('utf-8'))
                logger.info(f"Parsed JSON: {json.dumps(webhook_data, indent=2)}")
            except:
                logger.info("Could not parse JSON")
        
        return HttpResponse("DEBUG OK - Logged successfully", status=200)
        
    except Exception as e:
        logger.error(f"Debug webhook error: {str(e)}")
        return HttpResponse("DEBUG ERROR", status=500)