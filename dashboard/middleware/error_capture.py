"""
Middleware de captura de erros para diagnóstico detalhado de problemas 500.
"""
import logging
import traceback
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from django.db import connection
import sys
import os

logger = logging.getLogger(__name__)


class ErrorCaptureMiddleware:
    """
    Middleware que intercepta todos os erros 500 e registra informações detalhadas
    para diagnóstico e resolução de problemas.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Não intercepta exceções 404 - deixa o Django tratar normalmente
            from django.http import Http404
            if isinstance(e, Http404):
                raise e
            
            # Captura informações detalhadas do erro
            error_info = self.capture_error_details(request, e)
            
            # Log do erro com informações completas
            logger.error(f"500 Error captured: {error_info}")
            
            # Retorna resposta apropriada baseada no tipo de requisição
            return self.handle_error_response(request, error_info)
    
    def capture_error_details(self, request, exception):
        """
        Captura informações detalhadas sobre o erro para diagnóstico.
        """
        error_info = {
            'timestamp': timezone.now().isoformat(),
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'stack_trace': traceback.format_exc(),
            'request_info': {
                'path': request.path,
                'method': request.method,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                'session_key': request.session.session_key if hasattr(request, 'session') else None,
                'remote_addr': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'referer': request.META.get('HTTP_REFERER'),
            },
            'database_info': self.get_database_info(),
            'middleware_info': self.get_middleware_info(),
            'system_info': {
                'python_version': sys.version,
                'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
                'debug_mode': settings.DEBUG,
            }
        }
        
        # Adiciona informações específicas do usuário se disponível
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                error_info['user_info'] = {
                    'id': request.user.id,
                    'username': request.user.username,
                    'is_superuser': request.user.is_superuser,
                    'is_staff': request.user.is_staff,
                    'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                }
                
                # Verifica se tem loja associada
                if hasattr(request.user, 'loja_admin'):
                    try:
                        loja = request.user.loja_admin
                        error_info['user_info']['loja'] = {
                            'id': str(loja.id),
                            'nome': loja.nome,
                            'status': loja.status,
                        }
                    except Exception as e:
                        error_info['user_info']['loja_error'] = str(e)
                        
            except Exception as e:
                error_info['user_info_error'] = str(e)
        
        return error_info
    
    def get_database_info(self):
        """
        Obtém informações sobre o status do banco de dados.
        """
        db_info = {
            'connection_status': 'unknown',
            'queries_count': 0,
            'connection_errors': []
        }
        
        try:
            # Testa conexão básica
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_info['connection_status'] = 'connected'
                
            # Informações sobre queries
            db_info['queries_count'] = len(connection.queries)
            
            # Verifica configuração do banco
            db_config = settings.DATABASES.get('default', {})
            db_info['engine'] = db_config.get('ENGINE', 'unknown')
            db_info['name'] = db_config.get('NAME', 'unknown')
            
        except Exception as e:
            db_info['connection_status'] = 'error'
            db_info['connection_errors'].append(str(e))
            
        return db_info
    
    def get_middleware_info(self):
        """
        Obtém informações sobre o middleware configurado.
        """
        middleware_info = {
            'middleware_list': getattr(settings, 'MIDDLEWARE', []),
            'middleware_count': len(getattr(settings, 'MIDDLEWARE', [])),
        }
        
        return middleware_info
    
    def handle_error_response(self, request, error_info):
        """
        Retorna uma resposta apropriada baseada no tipo de requisição.
        """
        # Para requisições AJAX, retorna JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': 'Erro interno do servidor. Tente novamente.',
                'error_id': error_info.get('timestamp'),
                'debug_info': error_info if settings.DEBUG else None
            }, status=500)
        
        # Para requisições normais, renderiza página de erro
        try:
            context = {
                'error_info': error_info if settings.DEBUG else None,
                'error_id': error_info.get('timestamp'),
                'support_message': 'Entre em contato com o suporte técnico se o problema persistir.',
            }
            
            return render(request, 'errors/500.html', context, status=500)
            
        except Exception as template_error:
            # Se não conseguir renderizar template, retorna resposta básica
            logger.error(f"Erro ao renderizar template de erro: {template_error}")
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Erro Interno do Servidor</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .error-container {{ max-width: 600px; margin: 0 auto; }}
                    .error-id {{ color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1>Erro Interno do Servidor</h1>
                    <p>Ocorreu um erro interno. Nossa equipe técnica foi notificada.</p>
                    <p>Tente novamente em alguns minutos.</p>
                    <div class="error-id">ID do Erro: {error_info.get('timestamp', 'N/A')}</div>
                </div>
            </body>
            </html>
            """
            
            return HttpResponse(html_content, status=500, content_type='text/html')