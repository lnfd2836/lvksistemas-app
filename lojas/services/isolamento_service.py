"""
Serviço para gerenciar isolamento de dados por loja
"""
import logging
from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from django.db import connections, transaction
from django.conf import settings
from django.core.exceptions import PermissionDenied
from ..models import Loja
from ..database_router_isolado import LojaContextManager, get_current_loja_id, ensure_loja_database_exists
from dashboard.services.authentication import AuthenticationService

logger = logging.getLogger(__name__)


class IsolamentoService:
    """
    Serviço centralizado para gerenciar isolamento de dados por loja
    """
    
    @staticmethod
    def validate_user_loja_access(user: User, loja_id: str) -> bool:
        """
        Valida se o usuário pode acessar dados de uma loja específica
        
        Args:
            user: Usuário a ser validado
            loja_id: ID da loja
            
        Returns:
            bool: True se o usuário pode acessar a loja
        """
        try:
            if not user or not user.is_authenticated:
                logger.warning("Tentativa de acesso com usuário não autenticado")
                return False
            
            # Super admins podem acessar qualquer loja via dashboard principal
            if user.is_superuser:
                logger.debug(f"Super admin {user.username} pode acessar loja {loja_id}")
                return True
            
            # Verificar se o usuário pertence à loja
            user_loja = AuthenticationService.get_user_store(user)
            if not user_loja:
                logger.warning(f"Usuário {user.username} não tem loja associada")
                return False
            
            # Verificar se é a mesma loja
            if str(user_loja.id) != str(loja_id):
                logger.warning(f"Usuário {user.username} da loja {user_loja.id} tentou acessar loja {loja_id}")
                return False
            
            logger.debug(f"Usuário {user.username} autorizado para loja {loja_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar acesso do usuário {user.username} à loja {loja_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_loja_context(user: User) -> Optional[Dict[str, Any]]:
        """
        Obtém o contexto da loja do usuário
        
        Args:
            user: Usuário
            
        Returns:
            Dict com informações da loja ou None
        """
        try:
            if not user or not user.is_authenticated:
                return None
            
            # Super admins não têm contexto de loja específico
            if user.is_superuser:
                return {
                    'is_super_admin': True,
                    'loja': None,
                    'db_alias': 'default'
                }
            
            # Obter loja do usuário
            user_loja = AuthenticationService.get_user_store(user)
            if not user_loja:
                return None
            
            return {
                'is_super_admin': False,
                'loja': user_loja,
                'loja_id': str(user_loja.id),
                'db_alias': f"loja_{user_loja.id}",
                'loja_nome': user_loja.nome
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto da loja para usuário {user.username}: {str(e)}")
            return None
    
    @staticmethod
    def execute_with_loja_context(user: User, func, *args, **kwargs):
        """
        Executa uma função no contexto da loja do usuário
        
        Args:
            user: Usuário
            func: Função a ser executada
            *args, **kwargs: Argumentos da função
            
        Returns:
            Resultado da função
        """
        try:
            # Obter contexto da loja
            loja_context = IsolamentoService.get_user_loja_context(user)
            
            if not loja_context:
                raise PermissionDenied("Usuário não tem contexto de loja válido")
            
            # Super admins executam no contexto padrão
            if loja_context['is_super_admin']:
                logger.debug(f"Executando função para super admin {user.username}")
                return func(*args, **kwargs)
            
            # Usuários de loja executam no contexto isolado
            loja_id = loja_context['loja_id']
            
            # Garantir que o banco da loja existe
            ensure_loja_database_exists(loja_id)
            
            # Executar no contexto da loja
            with LojaContextManager(loja_id):
                logger.debug(f"Executando função para usuário {user.username} da loja {loja_id}")
                return func(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Erro ao executar função no contexto da loja: {str(e)}")
            raise
    
    @staticmethod
    def get_loja_database_connection(loja_id: str):
        """
        Obtém conexão com o banco de dados da loja
        
        Args:
            loja_id: ID da loja
            
        Returns:
            Conexão com o banco de dados
        """
        try:
            db_alias = f"loja_{loja_id}"
            
            # Verificar se o banco existe na configuração
            if db_alias not in settings.DATABASES:
                ensure_loja_database_exists(loja_id)
            
            # Obter conexão
            connection = connections[db_alias]
            logger.debug(f"Conexão obtida para banco da loja {loja_id}: {db_alias}")
            return connection
            
        except Exception as e:
            logger.error(f"Erro ao obter conexão do banco da loja {loja_id}: {str(e)}")
            raise
    
    @staticmethod
    def migrate_loja_database(loja_id: str) -> bool:
        """
        Executa migrações no banco de dados da loja
        
        Args:
            loja_id: ID da loja
            
        Returns:
            bool: True se as migrações foram executadas com sucesso
        """
        try:
            from django.core.management import call_command
            
            db_alias = f"loja_{loja_id}"
            
            # Garantir que o banco existe
            ensure_loja_database_exists(loja_id)
            
            # Executar migrações
            call_command('migrate', database=db_alias, verbosity=0)
            
            logger.info(f"Migrações executadas com sucesso para loja {loja_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar migrações para loja {loja_id}: {str(e)}")
            return False
    
    @staticmethod
    def validate_data_isolation(user: User, model_instance) -> bool:
        """
        Valida se o usuário pode acessar uma instância específica do modelo
        
        Args:
            user: Usuário
            model_instance: Instância do modelo
            
        Returns:
            bool: True se o acesso é permitido
        """
        try:
            # Super admins podem acessar tudo
            if user.is_superuser:
                return True
            
            # Verificar se o modelo tem campo loja
            if hasattr(model_instance, 'loja'):
                model_loja_id = str(model_instance.loja.id)
                return IsolamentoService.validate_user_loja_access(user, model_loja_id)
            
            # Verificar se o modelo tem campo loja_id
            elif hasattr(model_instance, 'loja_id'):
                model_loja_id = str(model_instance.loja_id)
                return IsolamentoService.validate_user_loja_access(user, model_loja_id)
            
            # Se não tem campo loja, permitir acesso (modelo do sistema)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar isolamento de dados: {str(e)}")
            return False
    
    @staticmethod
    def get_loja_queryset_filter(user: User) -> Dict[str, Any]:
        """
        Obtém filtros para QuerySet baseado na loja do usuário
        
        Args:
            user: Usuário
            
        Returns:
            Dict com filtros para aplicar no QuerySet
        """
        try:
            # Super admins veem todos os dados
            if user.is_superuser:
                return {}
            
            # Obter loja do usuário
            user_loja = AuthenticationService.get_user_store(user)
            if not user_loja:
                # Usuário sem loja não vê nenhum dado
                return {'loja_id': -1}  # Filtro que não retorna nada
            
            # Filtrar pela loja do usuário
            return {'loja_id': user_loja.id}
            
        except Exception as e:
            logger.error(f"Erro ao obter filtros de QuerySet: {str(e)}")
            return {'loja_id': -1}  # Filtro seguro que não retorna nada
    
    @staticmethod
    def create_loja_database(loja: Loja) -> bool:
        """
        Cria banco de dados para uma nova loja
        
        Args:
            loja: Instância da loja
            
        Returns:
            bool: True se o banco foi criado com sucesso
        """
        try:
            loja_id = str(loja.id)
            
            # Configurar banco na configuração do Django
            if not ensure_loja_database_exists(loja_id):
                return False
            
            # Executar migrações
            if not IsolamentoService.migrate_loja_database(loja_id):
                return False
            
            logger.info(f"Banco de dados criado com sucesso para loja {loja.nome} (ID: {loja_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar banco para loja {loja.nome}: {str(e)}")
            return False
    
    @staticmethod
    def delete_loja_database(loja_id: str) -> bool:
        """
        Remove banco de dados de uma loja (cuidado!)
        
        Args:
            loja_id: ID da loja
            
        Returns:
            bool: True se o banco foi removido com sucesso
        """
        try:
            db_alias = f"loja_{loja_id}"
            
            # Fechar conexões existentes
            if db_alias in connections:
                connections[db_alias].close()
                del connections[db_alias]
            
            # Remover da configuração
            if db_alias in settings.DATABASES:
                del settings.DATABASES[db_alias]
            
            logger.warning(f"Banco de dados removido para loja {loja_id}: {db_alias}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover banco da loja {loja_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_isolation_status() -> Dict[str, Any]:
        """
        Obtém status do isolamento do sistema
        
        Returns:
            Dict com informações de status
        """
        try:
            current_loja_id = get_current_loja_id()
            
            # Contar bancos de loja configurados
            loja_dbs = [db for db in settings.DATABASES.keys() if db.startswith('loja_')]
            
            # Contar lojas ativas
            lojas_ativas = Loja.objects.filter(status='ativa').count()
            
            return {
                'current_loja_id': current_loja_id,
                'configured_loja_databases': len(loja_dbs),
                'active_lojas': lojas_ativas,
                'loja_databases': loja_dbs,
                'isolation_active': current_loja_id is not None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status de isolamento: {str(e)}")
            return {
                'error': str(e),
                'isolation_active': False
            }


# Decorador para views que precisam de isolamento
def require_loja_isolation(view_func):
    """
    Decorador que garante que a view seja executada no contexto da loja do usuário
    """
    def wrapper(request, *args, **kwargs):
        try:
            user = request.user
            
            if not user.is_authenticated:
                raise PermissionDenied("Usuário não autenticado")
            
            # Executar view no contexto da loja
            return IsolamentoService.execute_with_loja_context(
                user, view_func, request, *args, **kwargs
            )
            
        except Exception as e:
            logger.error(f"Erro no decorador de isolamento: {str(e)}")
            raise
    
    return wrapper