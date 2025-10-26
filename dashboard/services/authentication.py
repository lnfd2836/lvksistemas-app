"""
Serviço centralizado de autenticação para gerenciar lógica de usuários e dashboards.
"""
import logging
from typing import Optional
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from lojas.models import Loja

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Serviço centralizado para gerenciar autenticação e determinação de dashboards.
    """
    
    # Constantes para tipos de dashboard
    DASHBOARD_SUPER_ADMIN = 'super_admin'
    DASHBOARD_STORE_ADMIN = 'store_admin'
    DASHBOARD_UNAUTHORIZED = 'unauthorized'
    
    # URLs dos dashboards
    DASHBOARD_URLS = {
        DASHBOARD_SUPER_ADMIN: '/dashboard/',
        DASHBOARD_STORE_ADMIN: '/dashboard/loja/',
        DASHBOARD_UNAUTHORIZED: '/'  # Página inicial com seleção de lojas
    }
    
    @staticmethod
    def determine_user_dashboard(user: User) -> str:
        """
        Determina qual dashboard o usuário deve acessar baseado em seu tipo e associações.
        
        Args:
            user: Instância do usuário Django
            
        Returns:
            str: URL do dashboard apropriado para o usuário
        """
        if not user or not user.is_authenticated:
            logger.info("Usuário não autenticado, redirecionando para login")
            return AuthenticationService.DASHBOARD_URLS[AuthenticationService.DASHBOARD_UNAUTHORIZED]
        
        try:
            # Verifica se é super usuário - sempre vai para dashboard super admin
            if user.is_superuser:
                logger.info(f"Super usuário {user.username} detectado - redirecionando para dashboard super admin")
                # Super admins sempre vão para o dashboard principal, independente de ter loja
                return AuthenticationService.DASHBOARD_URLS[AuthenticationService.DASHBOARD_SUPER_ADMIN]
            
            # Verifica se é administrador de loja
            elif AuthenticationService.can_access_store_dashboard(user):
                user_store = AuthenticationService.get_user_store(user)
                if user_store:
                    logger.info(f"Usuário {user.username} é admin da loja: {user_store.nome}")
                    return AuthenticationService.DASHBOARD_URLS[AuthenticationService.DASHBOARD_STORE_ADMIN]
                else:
                    logger.warning(f"Usuário {user.username} deveria ter loja mas não foi encontrada")
                    return AuthenticationService.DASHBOARD_URLS[AuthenticationService.DASHBOARD_UNAUTHORIZED]
            
            # Usuário comum sem permissões especiais
            else:
                logger.info(f"Usuário {user.username} sem permissões de dashboard")
                return AuthenticationService.DASHBOARD_URLS[AuthenticationService.DASHBOARD_UNAUTHORIZED]
                
        except Exception as e:
            logger.error(f"Erro ao determinar dashboard para usuário {user.username}: {str(e)}")
            return AuthenticationService.DASHBOARD_URLS[AuthenticationService.DASHBOARD_UNAUTHORIZED]
    
    @staticmethod
    def can_access_store_dashboard(user: User, store: Optional[Loja] = None) -> bool:
        """
        Verifica se o usuário pode acessar o dashboard de loja.
        IMPORTANTE: Super usuários NÃO podem acessar dashboards de loja via login personalizado.
        Eles devem usar o login super admin exclusivo.
        
        Args:
            user: Instância do usuário Django
            store: Loja específica (opcional)
            
        Returns:
            bool: True se o usuário pode acessar o dashboard de loja
        """
        if not user or not user.is_authenticated:
            return False
        
        try:
            # Super usuários NÃO podem acessar via login de loja
            # Eles devem usar o login super admin exclusivo
            if user.is_superuser:
                logger.debug(f"Super usuário {user.username} deve usar login super admin, não login de loja")
                return False
            
            # Verifica se o usuário tem loja associada
            user_store = AuthenticationService.get_user_store(user)
            if not user_store:
                logger.debug(f"Usuário {user.username} não tem loja associada")
                return False
            
            # Se uma loja específica foi fornecida, verifica se é a mesma do usuário
            if store and str(user_store.id) != str(store.id):
                logger.warning(f"Usuário {user.username} tentou acessar loja {store.id} mas está associado à loja {user_store.id}")
                return False
            
            logger.debug(f"Usuário {user.username} pode acessar dashboard da loja {user_store.nome}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar acesso ao dashboard de loja para usuário {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_store(user: User) -> Optional[Loja]:
        """
        Obtém a loja associada ao usuário de forma segura.
        
        Args:
            user: Instância do usuário Django
            
        Returns:
            Optional[Loja]: Loja associada ao usuário ou None se não houver
        """
        if not user or not user.is_authenticated:
            return None
        
        try:
            # Verifica se existe atributo loja_admin (relacionamento OneToOne)
            try:
                if hasattr(user, 'loja_admin') and user.loja_admin:
                    logger.debug(f"Loja encontrada via loja_admin para usuário {user.username}: {user.loja_admin.nome}")
                    return user.loja_admin
            except ObjectDoesNotExist:
                # Usuário não tem loja_admin associada
                logger.debug(f"Usuário {user.username} não tem loja_admin associada")
                pass
            except Exception as e:
                logger.warning(f"Erro ao acessar loja_admin para usuário {user.username}: {str(e)}")
                pass
            
            # Verifica se é funcionário de uma loja
            try:
                if hasattr(user, 'funcionario') and user.funcionario:
                    funcionario = user.funcionario
                    if funcionario.ativo:
                        logger.debug(f"Loja encontrada via funcionario para usuário {user.username}: {funcionario.loja.nome}")
                        return funcionario.loja
                    else:
                        logger.debug(f"Usuário {user.username} é funcionário inativo")
            except ObjectDoesNotExist:
                # Usuário não é funcionário
                logger.debug(f"Usuário {user.username} não é funcionário")
                pass
            except Exception as e:
                logger.warning(f"Erro ao acessar funcionario para usuário {user.username}: {str(e)}")
                pass
            
            # Tenta buscar através de relacionamentos alternativos
            # Verifica se existe relacionamento direto com Loja via admin_user
            try:
                from lojas.models import Loja
                loja_do_usuario = Loja.objects.filter(admin_user=user).first()
                
                if loja_do_usuario:
                    logger.debug(f"Loja encontrada via admin_user para usuário {user.username}: {loja_do_usuario.nome}")
                    return loja_do_usuario
            except Exception as e:
                logger.warning(f"Erro ao buscar loja via admin_user para usuário {user.username}: {str(e)}")
                pass
            
            logger.debug(f"Nenhuma loja encontrada para usuário {user.username}")
            return None
            
        except Exception as e:
            logger.error(f"Erro geral ao buscar loja do usuário {user.username}: {str(e)}")
            return None
    
    @staticmethod
    def is_store_user_only(user: User) -> bool:
        """
        Verifica se o usuário é exclusivamente um usuário de loja (não super admin).
        
        Args:
            user: Instância do usuário Django
            
        Returns:
            bool: True se o usuário é apenas de loja (admin ou funcionário)
        """
        if not user or not user.is_authenticated:
            return False
        
        # Super usuários não são usuários de loja
        if user.is_superuser:
            return False
        
        # Verificar se é admin de loja ou funcionário
        user_store = AuthenticationService.get_user_store(user)
        return user_store is not None
    
    @staticmethod
    def get_user_access_level(user: User) -> str:
        """
        Determina o nível de acesso do usuário.
        
        Args:
            user: Instância do usuário Django
            
        Returns:
            str: Nível de acesso ('super_admin', 'store_admin', 'store_employee', 'unauthorized')
        """
        if not user or not user.is_authenticated:
            return 'unauthorized'
        
        if user.is_superuser:
            return 'super_admin'
        
        # Verificar se é admin de loja
        try:
            if hasattr(user, 'loja_admin') and user.loja_admin:
                return 'store_admin'
        except:
            pass
        
        # Verificar se é funcionário
        try:
            if hasattr(user, 'funcionario') and user.funcionario and user.funcionario.ativo:
                return 'store_employee'
        except:
            pass
        
        return 'unauthorized'
    
    @staticmethod
    def validate_user_permissions(user: User, required_permission: str) -> bool:
        """
        Valida se o usuário tem a permissão necessária.
        
        Args:
            user: Instância do usuário Django
            required_permission: Nome da permissão necessária
            
        Returns:
            bool: True se o usuário tem a permissão
        """
        if not user or not user.is_authenticated:
            return False
        
        try:
            # Super usuários têm todas as permissões
            if user.is_superuser:
                return True
            
            # Verifica permissão específica
            if user.has_perm(required_permission):
                return True
            
            # Verifica permissões baseadas no tipo de usuário
            if required_permission == 'dashboard.access_store_dashboard':
                return AuthenticationService.can_access_store_dashboard(user)
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao validar permissões para usuário {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_type(user: User) -> str:
        """
        Determina o tipo do usuário para fins de logging e debugging.
        
        Args:
            user: Instância do usuário Django
            
        Returns:
            str: Tipo do usuário (super_admin, store_admin, funcionario, regular_user, anonymous)
        """
        if not user or not user.is_authenticated:
            return 'anonymous'
        
        try:
            # Super admin sempre tem prioridade, mesmo com loja associada
            if user.is_superuser:
                return 'super_admin'
            elif hasattr(user, 'loja_admin') and user.loja_admin:
                return 'store_admin'
            elif hasattr(user, 'funcionario') and user.funcionario and user.funcionario.ativo:
                return 'funcionario'
            elif AuthenticationService.can_access_store_dashboard(user):
                return 'store_admin'
            else:
                return 'regular_user'
        except Exception as e:
            logger.error(f"Erro ao determinar tipo do usuário {user.username}: {str(e)}")
            return 'unknown'
    
    @staticmethod
    def get_dashboard_context(user: User) -> dict:
        """
        Obtém contexto adicional para o dashboard do usuário.
        
        Args:
            user: Instância do usuário Django
            
        Returns:
            dict: Contexto com informações do usuário e loja
        """
        context = {
            'user_type': AuthenticationService.get_user_type(user),
            'can_access_store': False,
            'store': None,
            'dashboard_url': AuthenticationService.determine_user_dashboard(user)
        }
        
        if user and user.is_authenticated:
            try:
                context['can_access_store'] = AuthenticationService.can_access_store_dashboard(user)
                context['store'] = AuthenticationService.get_user_store(user)
            except Exception as e:
                logger.error(f"Erro ao obter contexto do dashboard para usuário {user.username}: {str(e)}")
        
        return context