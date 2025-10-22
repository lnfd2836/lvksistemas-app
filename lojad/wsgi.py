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
    if method == 'POST' and path in ['/webhook/asaas/', '/api/v1/webhook/asaas/', '/asaas-webhook-raw/', '/webhook-test-simple/']:
        logger.info(f"=== WEBHOOK INTERCEPTADO NO WSGI ===")
        logger.info(f"Path: {path}")
        logger.info(f"Method: {method}")
        
        # Retorna OK simples para teste
        status = '200 OK'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'OK - INTERCEPTED BY WSGI']
    
    # Se não é webhook, passa para o Django
    return django_application(environ, start_response)


# Aplicação final com interceptor
application = webhook_interceptor

