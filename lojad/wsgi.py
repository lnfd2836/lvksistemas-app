"""
WSGI config for lojad project.
"""

import os
import json
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

logger = logging.getLogger(__name__)

# Aplicação Django original
django_application = get_wsgi_application()


def webhook_interceptor(environ, start_response):
    """
    Intercepta webhooks antes mesmo do Django processar
    """
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', '')
    
    # Verifica se é um webhook
    if method == 'POST' and path in ['/asaas-webhook-raw/', '/webhook-test-simple/']:
        logger.info(f"=== WEBHOOK INTERCEPTADO NO WSGI ===")
        logger.info(f"Path: {path}")
        logger.info(f"Method: {method}")
        
        # Lê o body da requisição
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            if content_length > 0:
                body = environ['wsgi.input'].read(content_length)
                logger.info(f"Body length: {len(body)}")
                
                # Tenta processar o webhook
                try:
                    webhook_data = json.loads(body.decode('utf-8'))
                    logger.info(f"Webhook recebido: {webhook_data}")
                    
                    # Processa usando serviço existente
                    from controle_financeiro.asaas_service import AsaasService
                    asaas_service = AsaasService()
                    resultado = asaas_service.processar_webhook(webhook_data)
                    
                    if resultado.get('success'):
                        logger.info(f"Webhook processado com sucesso: {resultado.get('message')}")
                        status = '200 OK'
                        headers = [('Content-Type', 'text/plain')]
                        start_response(status, headers)
                        return [b'OK']
                    else:
                        logger.error(f"Erro ao processar webhook: {resultado.get('error')}")
                        status = '400 Bad Request'
                        headers = [('Content-Type', 'text/plain')]
                        start_response(status, headers)
                        return [b'Error']
                        
                except json.JSONDecodeError:
                    logger.error("Webhook com JSON inválido")
                    status = '400 Bad Request'
                    headers = [('Content-Type', 'text/plain')]
                    start_response(status, headers)
                    return [b'Invalid JSON']
                    
                except Exception as e:
                    logger.error(f"Erro ao processar webhook: {str(e)}")
                    status = '500 Internal Server Error'
                    headers = [('Content-Type', 'text/plain')]
                    start_response(status, headers)
                    return [b'Processing Error']
            else:
                logger.error("Webhook sem body")
                status = '400 Bad Request'
                headers = [('Content-Type', 'text/plain')]
                start_response(status, headers)
                return [b'No Body']
                
        except Exception as e:
            logger.error(f"Erro no interceptor WSGI: {str(e)}")
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/plain')]
            start_response(status, headers)
            return [b'Internal Error']
    
    # Se não é webhook, passa para o Django
    return django_application(environ, start_response)


# Aplicação final com interceptor
application = webhook_interceptor

