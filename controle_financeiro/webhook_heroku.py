"""
Webhook específico para Heroku - bypassa todos os middlewares
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
import json
import logging
import os

logger = logging.getLogger(__name__)


@csrf_exempt
@never_cache
@require_http_methods(["POST", "GET"])
def webhook_asaas_heroku(request):
    """
    Webhook específico para Heroku - máxima compatibilidade
    """
    try:
        # Log detalhado para debug no Heroku
        logger.info(f"=== WEBHOOK HEROKU ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")
        logger.info(f"Content-Length: {request.META.get('CONTENT_LENGTH', 'N/A')}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        logger.info(f"X-Forwarded-For: {request.META.get('HTTP_X_FORWARDED_FOR', 'N/A')}")
        logger.info(f"X-Forwarded-Proto: {request.META.get('HTTP_X_FORWARDED_PROTO', 'N/A')}")
        logger.info(f"Host: {request.META.get('HTTP_HOST', 'N/A')}")
        logger.info(f"Remote Addr: {request.META.get('REMOTE_ADDR', 'N/A')}")
        logger.info(f"Is Heroku: {'DYNO' in os.environ}")
        
        # Permitir GET para teste
        if request.method == 'GET':
            return HttpResponse("Webhook Heroku OK - GET", status=200)
        
        # Verificar se tem body
        if not request.body:
            logger.warning("Webhook sem body")
            return HttpResponse("No body", status=400)
        
        # Log do body raw
        body_str = request.body.decode('utf-8')
        logger.info(f"Body length: {len(body_str)}")
        logger.info(f"Body preview: {body_str[:500]}")
        
        # Parsear JSON
        try:
            webhook_data = json.loads(body_str)
            logger.info(f"JSON parsed successfully")
            
            # Log dos dados principais
            event = webhook_data.get('event', 'UNKNOWN')
            payment = webhook_data.get('payment', {})
            payment_id = payment.get('id', 'N/A')
            payment_status = payment.get('status', 'N/A')
            payment_value = payment.get('value', 'N/A')
            
            logger.info(f"Event: {event}")
            logger.info(f"Payment ID: {payment_id}")
            logger.info(f"Payment Status: {payment_status}")
            logger.info(f"Payment Value: {payment_value}")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido: {str(e)}")
            logger.error(f"Body que causou erro: {body_str}")
            return HttpResponse("Invalid JSON", status=400)
        
        # Processar webhook usando o serviço
        try:
            # Import dinâmico para evitar problemas de circular import
            from controle_financeiro.asaas_service import AsaasService
            
            asaas_service = AsaasService()
            resultado = asaas_service.processar_webhook(webhook_data)
            
            if resultado.get('success'):
                logger.info(f"✅ Webhook processado com sucesso: {resultado.get('message')}")
                return HttpResponse("OK - Processado com sucesso", status=200)
            else:
                logger.error(f"❌ Erro ao processar webhook: {resultado.get('error')}")
                return HttpResponse(f"Error: {resultado.get('error')}", status=400)
                
        except ImportError as e:
            logger.error(f"❌ Erro de import: {str(e)}")
            return HttpResponse(f"Import Error: {str(e)}", status=500)
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return HttpResponse(f"Processing Error: {str(e)}", status=500)
        
    except Exception as e:
        logger.error(f"❌ Erro geral no webhook Heroku: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return HttpResponse(f"Internal Error: {str(e)}", status=500)


@csrf_exempt
@never_cache
def webhook_asaas_test_heroku(request):
    """
    Webhook de teste para Heroku - apenas retorna OK
    """
    try:
        logger.info(f"=== WEBHOOK TEST HEROKU ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Is Heroku: {'DYNO' in os.environ}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        if request.body:
            logger.info(f"Body: {request.body.decode('utf-8')[:200]}")
        
        return HttpResponse("TEST HEROKU OK", status=200)
        
    except Exception as e:
        logger.error(f"Erro no webhook test Heroku: {str(e)}")
        return HttpResponse("TEST ERROR", status=500)