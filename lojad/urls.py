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
from dashboard.smart_redirect import smart_login_redirect, loja_por_codigo, admin_redirect
from lojas.views_login import login_personalizado_loja, api_validar_url_personalizada, recuperar_senha_loja, api_recuperar_senha
# Webhooks removidos - usando apenas asaas_views.py
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
    # WEBHOOK CONSOLIDADO - usando apenas asaas_views.py
    path('webhook/asaas/', webhook_asaas_bypass, name='webhook_asaas_main'),
    path('webhook-test-simple/', webhook_test_simple, name='webhook_test_simple'),
    
    path('admin/', admin.site.urls),
    # Root URL - redirecionamento inteligente
    path('', smart_login_redirect, name='root_redirect'),
    
    # URLs principais
    path('dashboard/', include('dashboard.urls')),
    path('lojas/', include('lojas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('planos/', include('planos.urls')),
    path('financeiro/', include('controle_financeiro.urls')),
    path('modulos/', include('modulos.urls')),
    path('avaliacao-qualidade/', include('avaliacao_qualidade.urls')),
    path('credenciais/', include('email_credentials.urls')),
    
    # Redirecionamento para clínica de estética
    path('estetica/', estetica_redirect, name='estetica_redirect'),
    path('estetica/<path:path>', lambda request, path: redirect(f'/modulos/estetica/{path}')),
    
    # Sistema de login simplificado
    path('admin-login/', admin_redirect, name='admin_redirect'),
    path('super-admin/', admin_redirect, name='super_admin_redirect'),  # URL alternativa para super admins
    path('loja/<str:codigo_loja>/', loja_por_codigo, name='loja_por_codigo'),
    
    # Login personalizado por loja (mantido para compatibilidade)
    path('login/<str:url_personalizada>/', login_personalizado_loja, name='login_personalizado_url'),
    path('login/loja/<uuid:loja_id>/', login_personalizado_loja, name='login_personalizado_id'),
    
    # Redirecionamentos para URLs antigas (compatibilidade)
    path('login/', smart_login_redirect, name='simple_login_redirect'),
    path('loja/login/', smart_login_redirect, name='loja_login_redirect'),
    
    # API para validação
    path('api/validar-url-personalizada/', api_validar_url_personalizada, name='api_validar_url_personalizada'),

    # URLs de recuperação de senha
    path('recuperar-senha/', recuperar_senha_loja, name='recuperar_senha_loja'),
    path('api/recuperar-senha/', api_recuperar_senha, name='api_recuperar_senha'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
