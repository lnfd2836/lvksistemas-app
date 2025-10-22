"""
URL configuration for lojad project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dashboard.views import redirect_to_appropriate_dashboard
from dashboard.loja_login import loja_login
from dashboard.simple_login import simple_login
import json
import logging

logger = logging.getLogger(__name__)

def estetica_redirect(request):
    """Redireciona /estetica/ para /modulos/estetica/"""
    return redirect('/modulos/estetica/')


@csrf_exempt
@require_http_methods(["POST"])
def webhook_test_simple(request):
    """
    Endpoint de teste simples - apenas retorna OK
    """
    return HttpResponse("OK", status=200)


@csrf_exempt
@require_http_methods(["POST"])
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

urlpatterns = [
    # WEBHOOK TEST SIMPLE - PRIMEIRA URL (teste básico)
    path('webhook-test-simple/', webhook_test_simple, name='webhook_test_simple'),
    
    # WEBHOOK BYPASS - PRIMEIRA URL (sem middlewares)
    path('asaas-webhook-bypass/', webhook_asaas_bypass, name='webhook_asaas_bypass'),
    
    # URLs de webhook direto - SEM MIDDLEWARES
    path('asaas-webhook-direct/', include('controle_financeiro.webhook_urls')),
    
    path('admin/', admin.site.urls),
    # Root URL redireciona inteligentemente baseado no usuário
    path('', redirect_to_appropriate_dashboard, name='root_redirect'),
    
    # URLs principais
    path('dashboard/', include('dashboard.urls')),
    path('lojas/', include('lojas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('planos/', include('planos.urls')),
    path('financeiro/', include('controle_financeiro.urls')),
    path('modulos/', include('modulos.urls')),
    
    # Redirecionamento para clínica de estética
    path('estetica/', estetica_redirect, name='estetica_redirect'),
    path('estetica/<path:path>', lambda request, path: redirect(f'/modulos/estetica/{path}')),
    
    # URLs de autenticação - ordem importante para evitar conflitos
    path('login/', simple_login, name='simple_login'),
    path('loja/login/', loja_login, name='loja_login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
