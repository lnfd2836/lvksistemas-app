"""
Middleware para garantir isolamento completo de acesso por loja
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .models import Loja
from .models_login import LoginPersonalizado
from .services.isolamento_service import IsolamentoService
from .database_router_isolado import LojaContextManager, ensure_loja_database_exists
from dashboard.services.authentication import AuthenticationService

logger = logging.getLogger(__name__)


class LoginIsoladoMiddleware(MiddlewareMixin):
    """
    Middleware para garantir isolamento de acesso por loja
    """
    
    def process_request(self, request):
        """
        Processa a requisição para garantir isolamento por loja
        """
        
        # Pular para URLs que não precisam de verificação
        if self._should_skip_verification(request):
            return None
        
        # Se é uma URL de login personalizado, definir contexto da loja
        if self._is_custom_login_url(request):
            return self._handle_custom_login(request)
        
        # Se usuário está autenticado, verificar isolamento
        if request.user.is_authenticated:
            return self._verify_user_isolation(request)
        
        return None
    
    def _should_skip_verification(self, request):
        """Verifica se deve pular a verificação para esta URL"""
        
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/login/',  # Login principal
            '/logout/',
            '/password_reset/',
            '/api/',
            '/webhook/',
        ]
        
        path = request.path
        
        # Pular URLs específicas
        for skip_path in skip_paths:
            if path.startswith(skip_path):
                return True
        
        # Pular se não é usuário autenticado e não é login personalizado
        if not request.user.is_authenticated and not self._is_custom_login_url(request):
            return True
        
        return False
    
    def _is_custom_login_url(self, request):
        """Verifica se é uma URL de login personalizado"""
        path = request.path
        return path.startswith('/login/') and path != '/login/'
    
    def _handle_custom_login(self, request):
        """Processa login personalizado com isolamento"""
        
        try:
            # Extrair identificador da loja da URL
            path_parts = request.path.strip('/').split('/')
            
            if len(path_parts) >= 2 and path_parts[0] == 'login':
                loja_identifier = path_parts[1]
                
                # Buscar loja por URL personalizada ou ID
                loja = self._find_loja_by_identifier(loja_identifier)
                
                if loja:
                    # Definir contexto da loja na thread
                    self._set_loja_context(request, loja)
                    
                    # Se usuário já está autenticado, verificar se pode acessar esta loja
                    if request.user.is_authenticated:
                        if not self._can_user_access_loja(request.user, loja):
                            logger.warning(f"Usuário {request.user.username} tentou acessar loja {loja.nome} sem permissão")
                            logout(request)
                            messages.error(request, 'Você não tem permissão para acessar esta loja.')
                
        except Exception as e:
            logger.error(f"Erro ao processar login personalizado: {str(e)}")
        
        return None
    
    def _verify_user_isolation(self, request):
        """Verifica isolamento do usuário autenticado"""
        
        try:
            user = request.user
            
            # Super admins podem acessar tudo
            if user.is_superuser:
                return None
            
            # Validar acesso usando o serviço de isolamento
            current_loja = getattr(request, 'loja_atual', None)
            
            if current_loja:
                if not IsolamentoService.validate_user_loja_access(user, str(current_loja.id)):
                    logger.warning(f"Usuário {user.username} tentou acessar loja {current_loja.nome} sem permissão")
                    messages.error(request, 'Acesso negado: Você só pode acessar dados da sua loja.')
                    logout(request)
                    return redirect('root_redirect')
                
                # Configurar contexto da loja para isolamento de banco
                loja_context = IsolamentoService.get_user_loja_context(user)
                if loja_context and not loja_context['is_super_admin']:
                    ensure_loja_database_exists(str(current_loja.id))
        
        except Exception as e:
            logger.error(f"Erro ao verificar isolamento do usuário: {str(e)}")
        
        return None
    
    def _find_loja_by_identifier(self, identifier):
        """Encontra loja por URL personalizada ou ID"""
        
        try:
            # Primeiro, tentar por URL personalizada
            try:
                login_config = LoginPersonalizado.objects.get(
                    url_personalizada=identifier,
                    ativo=True
                )
                return login_config.loja
            except LoginPersonalizado.DoesNotExist:
                pass
            
            # Depois, tentar por ID da loja
            try:
                return Loja.objects.get(id=identifier, status='ativa')
            except (Loja.DoesNotExist, ValueError):
                pass
            
            logger.warning(f"Loja não encontrada para identificador: {identifier}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar loja por identificador {identifier}: {str(e)}")
            return None
    
    def _can_user_access_loja(self, user, loja):
        """Verifica se usuário pode acessar uma loja específica"""
        
        try:
            # Super admins não podem usar login de loja
            if user.is_superuser:
                return False
            
            # Verificar se é admin desta loja
            if hasattr(user, 'loja_admin') and user.loja_admin:
                return str(user.loja_admin.id) == str(loja.id)
            
            # Verificar se é funcionário desta loja
            if hasattr(user, 'funcionario') and user.funcionario:
                return (user.funcionario.ativo and 
                       str(user.funcionario.loja.id) == str(loja.id))
            
            # Verificar através do AuthenticationService
            user_loja = AuthenticationService.get_user_store(user)
            if user_loja:
                return str(user_loja.id) == str(loja.id)
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar acesso do usuário {user.username} à loja {loja.nome}: {str(e)}")
            return False
    
    def _set_loja_context(self, request, loja):
        """Define contexto da loja na requisição e thread"""
        
        try:
            # Definir na requisição
            request.loja_atual = loja
            
            # Definir na thread para o router de banco
            import threading
            thread = threading.current_thread()
            if not hasattr(thread, 'loja_context'):
                thread.loja_context = type('LojaContext', (), {})()
            thread.loja_context.loja_id = str(loja.id)
            
            logger.debug(f"Contexto da loja definido: {loja.nome} (ID: {loja.id})")
            
        except Exception as e:
            logger.error(f"Erro ao definir contexto da loja: {str(e)}")


class DatabaseIsolationMiddleware(MiddlewareMixin):
    """
    Middleware para garantir que cada loja use apenas seu banco de dados
    """
    
    def process_request(self, request):
        """
        Define o banco de dados correto baseado na loja atual
        """
        
        try:
            # Pular para super admins e URLs do sistema
            if self._should_skip_db_isolation(request):
                return None
            
            # Determinar loja atual
            loja_atual = self._get_current_loja(request)
            
            if loja_atual:
                # Definir banco da loja no contexto
                db_alias = f"loja_{loja_atual.id}"
                
                # Verificar se o banco existe
                from django.conf import settings
                if db_alias in settings.DATABASES:
                    # Definir no contexto da thread para o router
                    import threading
                    thread = threading.current_thread()
                    if not hasattr(thread, 'db_context'):
                        thread.db_context = type('DBContext', (), {})()
                    thread.db_context.db_alias = db_alias
                    thread.db_context.loja_id = str(loja_atual.id)
                    
                    logger.debug(f"Banco isolado definido: {db_alias} para loja {loja_atual.nome}")
        
        except Exception as e:
            logger.error(f"Erro no middleware de isolamento de banco: {str(e)}")
        
        return None
    
    def _should_skip_db_isolation(self, request):
        """Verifica se deve pular o isolamento de banco"""
        
        # Super admins usam banco principal
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        
        # URLs do sistema principal
        system_paths = [
            '/admin/',
            '/dashboard/',  # Dashboard principal
            '/static/',
            '/media/',
        ]
        
        for path in system_paths:
            if request.path.startswith(path):
                return True
        
        return False
    
    def _get_current_loja(self, request):
        """Obtém a loja atual da requisição"""
        
        try:
            # Verificar se já foi definida no contexto
            if hasattr(request, 'loja_atual'):
                return request.loja_atual
            
            # Se usuário está autenticado, buscar sua loja
            if request.user.is_authenticated:
                return AuthenticationService.get_user_store(request.user)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter loja atual: {str(e)}")
            return None