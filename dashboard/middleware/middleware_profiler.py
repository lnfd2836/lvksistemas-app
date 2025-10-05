"""
Middleware profiler para identificar problemas na cadeia de middleware.
"""
import logging
import time
import traceback
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class MiddlewareProfiler:
    """
    Middleware que monitora a execução de outros middlewares
    para identificar problemas e gargalos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.middleware_stats = {}
    
    def __call__(self, request):
        # Adiciona informações de profiling ao request
        request.middleware_profile = {
            'start_time': time.time(),
            'middleware_execution': [],
            'errors': [],
            'total_time': 0
        }
        
        try:
            # Executa a cadeia de middleware
            response = self.get_response(request)
            
            # Calcula tempo total
            request.middleware_profile['total_time'] = time.time() - request.middleware_profile['start_time']
            
            # Log das estatísticas se habilitado
            if settings.DEBUG or getattr(settings, 'MIDDLEWARE_PROFILING', False):
                self.log_middleware_stats(request)
            
            return response
            
        except Exception as e:
            # Registra erro na execução do middleware
            request.middleware_profile['errors'].append({
                'error_type': type(e).__name__,
                'error_message': str(e),
                'stack_trace': traceback.format_exc(),
                'timestamp': timezone.now().isoformat()
            })
            
            logger.error(f"Erro na cadeia de middleware: {e}")
            logger.error(f"Profile do middleware: {request.middleware_profile}")
            
            # Re-levanta a exceção para ser tratada pelo ErrorCaptureMiddleware
            raise
    
    def log_middleware_stats(self, request):
        """
        Registra estatísticas de execução do middleware.
        """
        profile = request.middleware_profile
        
        log_message = f"Middleware Profile - Path: {request.path}"
        log_message += f" | Total Time: {profile['total_time']:.4f}s"
        log_message += f" | Middleware Count: {len(profile['middleware_execution'])}"
        
        if profile['errors']:
            log_message += f" | Errors: {len(profile['errors'])}"
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Log detalhado se necessário
        if profile['total_time'] > 1.0:  # Requisições lentas
            logger.warning(f"Requisição lenta detectada: {request.path}")
            for middleware_info in profile['middleware_execution']:
                if middleware_info.get('execution_time', 0) > 0.1:
                    logger.warning(f"Middleware lento: {middleware_info}")


class MiddlewareExecutionTracker:
    """
    Classe para rastrear a execução individual de middlewares.
    """
    
    def __init__(self, middleware_name):
        self.middleware_name = middleware_name
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        # Registra informações de execução
        execution_info = {
            'middleware_name': self.middleware_name,
            'execution_time': execution_time,
            'timestamp': timezone.now().isoformat(),
            'success': exc_type is None
        }
        
        if exc_type:
            execution_info.update({
                'error_type': exc_type.__name__,
                'error_message': str(exc_val),
                'stack_trace': traceback.format_exc()
            })
        
        # Adiciona ao profile da requisição se disponível
        # (Isso seria usado por middlewares individuais)
        return False  # Não suprime exceções


class MiddlewareDebugWrapper:
    """
    Wrapper para adicionar debugging a middlewares existentes.
    """
    
    def __init__(self, middleware_class, middleware_name=None):
        self.middleware_class = middleware_class
        self.middleware_name = middleware_name or middleware_class.__name__
    
    def __call__(self, get_response):
        # Cria instância do middleware original
        middleware_instance = self.middleware_class(get_response)
        
        def wrapped_middleware(request):
            with MiddlewareExecutionTracker(self.middleware_name) as tracker:
                try:
                    # Adiciona informações ao profile da requisição
                    if hasattr(request, 'middleware_profile'):
                        request.middleware_profile['middleware_execution'].append({
                            'name': self.middleware_name,
                            'start_time': tracker.start_time,
                            'status': 'executing'
                        })
                    
                    # Executa middleware original
                    response = middleware_instance(request)
                    
                    # Atualiza status de sucesso
                    if hasattr(request, 'middleware_profile'):
                        for middleware_info in request.middleware_profile['middleware_execution']:
                            if (middleware_info['name'] == self.middleware_name and 
                                middleware_info['status'] == 'executing'):
                                middleware_info.update({
                                    'status': 'success',
                                    'execution_time': time.time() - tracker.start_time
                                })
                                break
                    
                    return response
                    
                except Exception as e:
                    # Atualiza status de erro
                    if hasattr(request, 'middleware_profile'):
                        for middleware_info in request.middleware_profile['middleware_execution']:
                            if (middleware_info['name'] == self.middleware_name and 
                                middleware_info['status'] == 'executing'):
                                middleware_info.update({
                                    'status': 'error',
                                    'execution_time': time.time() - tracker.start_time,
                                    'error_type': type(e).__name__,
                                    'error_message': str(e)
                                })
                                break
                    
                    # Log específico do middleware
                    logger.error(f"Erro no middleware {self.middleware_name}: {e}")
                    raise
        
        return wrapped_middleware


def create_middleware_diagnostics():
    """
    Cria informações de diagnóstico sobre a configuração de middleware.
    
    Returns:
        dict: Informações de diagnóstico
    """
    diagnostics = {
        'middleware_list': [],
        'potential_issues': [],
        'recommendations': []
    }
    
    try:
        middleware_list = getattr(settings, 'MIDDLEWARE', [])
        
        for i, middleware_path in enumerate(middleware_list):
            middleware_info = {
                'order': i,
                'path': middleware_path,
                'name': middleware_path.split('.')[-1],
                'status': 'unknown'
            }
            
            # Tenta importar o middleware para verificar se existe
            try:
                module_path, class_name = middleware_path.rsplit('.', 1)
                module = __import__(module_path, fromlist=[class_name])
                middleware_class = getattr(module, class_name)
                middleware_info['status'] = 'available'
                middleware_info['class'] = str(middleware_class)
            except ImportError as e:
                middleware_info['status'] = 'import_error'
                middleware_info['error'] = str(e)
                diagnostics['potential_issues'].append(
                    f"Middleware {middleware_path} não pode ser importado: {e}"
                )
            except AttributeError as e:
                middleware_info['status'] = 'class_not_found'
                middleware_info['error'] = str(e)
                diagnostics['potential_issues'].append(
                    f"Classe {class_name} não encontrada em {module_path}: {e}"
                )
            
            diagnostics['middleware_list'].append(middleware_info)
        
        # Verifica ordem dos middlewares críticos
        critical_middleware_order = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ]
        
        for critical_mw in critical_middleware_order:
            if critical_mw in middleware_list:
                current_position = middleware_list.index(critical_mw)
                for other_critical in critical_middleware_order:
                    if other_critical in middleware_list:
                        other_position = middleware_list.index(other_critical)
                        if (critical_middleware_order.index(critical_mw) < 
                            critical_middleware_order.index(other_critical) and 
                            current_position > other_position):
                            diagnostics['potential_issues'].append(
                                f"Ordem incorreta: {critical_mw} deve vir antes de {other_critical}"
                            )
        
        # Gera recomendações
        if diagnostics['potential_issues']:
            diagnostics['recommendations'].append("Corrigir problemas de importação de middleware")
            diagnostics['recommendations'].append("Verificar ordem dos middlewares críticos")
        
        if len(middleware_list) > 10:
            diagnostics['recommendations'].append("Considerar reduzir número de middlewares para melhor performance")
        
    except Exception as e:
        diagnostics['error'] = str(e)
        logger.error(f"Erro ao criar diagnóstico de middleware: {e}")
    
    return diagnostics