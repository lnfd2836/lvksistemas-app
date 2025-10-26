"""
Router de banco de dados para garantir isolamento completo por loja
"""
import logging
import threading
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class LojaIsoladaDBRouter:
    """
    Router de banco de dados que garante isolamento completo por loja
    """
    
    # Modelos que sempre usam o banco principal (default)
    SYSTEM_MODELS = {
        'auth.user',
        'auth.group',
        'auth.permission',
        'contenttypes.contenttype',
        'sessions.session',
        'admin.logentry',
        'lojas.loja',
        'lojas.loginpersonalizado',
        'usuarios.usuario',
        'planos.plano',
        'planos.assinatura',
        'email_credentials.emailcredential',
        'email_credentials.passwordrecovery',
    }
    
    # Modelos que devem ser isolados por loja
    LOJA_MODELS = {
        'controle_financeiro',
        'avaliacao_qualidade',
        'modulos',
    }
    
    def db_for_read(self, model, **hints):
        """
        Determina qual banco usar para leitura
        """
        try:
            model_label = f"{model._meta.app_label}.{model._meta.model_name}"
            
            # Modelos do sistema sempre usam banco principal
            if model_label in self.SYSTEM_MODELS:
                return 'default'
            
            # Verificar se é modelo de loja
            if model._meta.app_label in self.LOJA_MODELS:
                return self._get_loja_database()
            
            # Por padrão, usar banco principal
            return 'default'
            
        except Exception as e:
            logger.error(f"Erro ao determinar banco para leitura do modelo {model}: {str(e)}")
            return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Determina qual banco usar para escrita
        """
        try:
            model_label = f"{model._meta.app_label}.{model._meta.model_name}"
            
            # Modelos do sistema sempre usam banco principal
            if model_label in self.SYSTEM_MODELS:
                return 'default'
            
            # Verificar se é modelo de loja
            if model._meta.app_label in self.LOJA_MODELS:
                return self._get_loja_database()
            
            # Por padrão, usar banco principal
            return 'default'
            
        except Exception as e:
            logger.error(f"Erro ao determinar banco para escrita do modelo {model}: {str(e)}")
            return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relações apenas entre objetos do mesmo banco
        """
        try:
            db_set = {'default'}
            
            # Adicionar bancos de loja se existirem
            for db_alias in settings.DATABASES.keys():
                if db_alias.startswith('loja_'):
                    db_set.add(db_alias)
            
            # Verificar se ambos os objetos estão no mesmo conjunto de bancos
            if obj1._state.db in db_set and obj2._state.db in db_set:
                return True
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao verificar relação entre objetos: {str(e)}")
            return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Controla quais migrações podem ser executadas em cada banco
        """
        try:
            model_label = f"{app_label}.{model_name}" if model_name else app_label
            
            # Banco principal (default)
            if db == 'default':
                # Permitir modelos do sistema no banco principal
                if model_label in self.SYSTEM_MODELS or app_label not in self.LOJA_MODELS:
                    return True
                # Não permitir modelos de loja no banco principal
                return False
            
            # Bancos de loja
            elif db.startswith('loja_'):
                # Permitir apenas modelos de loja nos bancos de loja
                if app_label in self.LOJA_MODELS:
                    return True
                # Não permitir modelos do sistema nos bancos de loja
                return False
            
            # Outros bancos - não permitir por padrão
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar migração para {db}: {str(e)}")
            return False
    
    def _get_loja_database(self):
        """
        Obtém o banco de dados da loja atual do contexto da thread
        """
        try:
            # Verificar contexto da thread
            thread = threading.current_thread()
            
            # Verificar se há contexto de banco definido
            if hasattr(thread, 'db_context') and hasattr(thread.db_context, 'db_alias'):
                db_alias = thread.db_context.db_alias
                
                # Verificar se o banco existe na configuração
                if db_alias in settings.DATABASES:
                    logger.debug(f"Usando banco isolado: {db_alias}")
                    return db_alias
            
            # Verificar contexto de loja
            if hasattr(thread, 'loja_context') and hasattr(thread.loja_context, 'loja_id'):
                loja_id = thread.loja_context.loja_id
                db_alias = f"loja_{loja_id}"
                
                # Verificar se o banco existe na configuração
                if db_alias in settings.DATABASES:
                    logger.debug(f"Usando banco da loja: {db_alias}")
                    return db_alias
            
            # Fallback para banco principal
            logger.debug("Nenhum contexto de loja encontrado, usando banco principal")
            return 'default'
            
        except Exception as e:
            logger.error(f"Erro ao obter banco da loja: {str(e)}")
            return 'default'


class LojaContextManager:
    """
    Gerenciador de contexto para definir loja ativa na thread
    """
    
    def __init__(self, loja_id):
        self.loja_id = str(loja_id)
        self.db_alias = f"loja_{loja_id}"
        self.thread = threading.current_thread()
        self.previous_context = None
    
    def __enter__(self):
        """
        Entra no contexto da loja
        """
        try:
            # Salvar contexto anterior se existir
            if hasattr(self.thread, 'loja_context'):
                self.previous_context = self.thread.loja_context
            
            # Definir novo contexto
            if not hasattr(self.thread, 'loja_context'):
                self.thread.loja_context = type('LojaContext', (), {})()
            
            self.thread.loja_context.loja_id = self.loja_id
            
            # Definir contexto de banco
            if not hasattr(self.thread, 'db_context'):
                self.thread.db_context = type('DBContext', (), {})()
            
            self.thread.db_context.db_alias = self.db_alias
            self.thread.db_context.loja_id = self.loja_id
            
            logger.debug(f"Contexto de loja ativado: {self.loja_id}")
            return self
            
        except Exception as e:
            logger.error(f"Erro ao ativar contexto da loja {self.loja_id}: {str(e)}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Sai do contexto da loja
        """
        try:
            # Restaurar contexto anterior
            if self.previous_context:
                self.thread.loja_context = self.previous_context
            elif hasattr(self.thread, 'loja_context'):
                delattr(self.thread, 'loja_context')
            
            # Limpar contexto de banco
            if hasattr(self.thread, 'db_context'):
                delattr(self.thread, 'db_context')
            
            logger.debug(f"Contexto de loja desativado: {self.loja_id}")
            
        except Exception as e:
            logger.error(f"Erro ao desativar contexto da loja {self.loja_id}: {str(e)}")


def with_loja_context(loja_id):
    """
    Decorator para executar função no contexto de uma loja específica
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with LojaContextManager(loja_id):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def get_current_loja_db():
    """
    Obtém o banco de dados da loja atual
    """
    try:
        thread = threading.current_thread()
        
        if hasattr(thread, 'db_context') and hasattr(thread.db_context, 'db_alias'):
            return thread.db_context.db_alias
        
        if hasattr(thread, 'loja_context') and hasattr(thread.loja_context, 'loja_id'):
            return f"loja_{thread.loja_context.loja_id}"
        
        return 'default'
        
    except Exception as e:
        logger.error(f"Erro ao obter banco atual: {str(e)}")
        return 'default'


def get_current_loja_id():
    """
    Obtém o ID da loja atual do contexto
    """
    try:
        thread = threading.current_thread()
        
        if hasattr(thread, 'loja_context') and hasattr(thread.loja_context, 'loja_id'):
            return thread.loja_context.loja_id
        
        if hasattr(thread, 'db_context') and hasattr(thread.db_context, 'loja_id'):
            return thread.db_context.loja_id
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao obter ID da loja atual: {str(e)}")
        return None


def ensure_loja_database_exists(loja_id):
    """
    Garante que o banco de dados da loja existe na configuração
    """
    try:
        from email_credentials.database_config import loja_db_config
        
        db_alias = f"loja_{loja_id}"
        
        if db_alias not in settings.DATABASES:
            settings.DATABASES[db_alias] = loja_db_config(loja_id)
            logger.info(f"Banco de dados configurado para loja {loja_id}: {db_alias}")
            return True
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao configurar banco da loja {loja_id}: {str(e)}")
        return False


def validate_loja_isolation():
    """
    Valida se o isolamento de loja está funcionando corretamente
    """
    try:
        current_loja = get_current_loja_id()
        current_db = get_current_loja_db()
        
        logger.info(f"Validação de isolamento - Loja: {current_loja}, Banco: {current_db}")
        
        # Verificar se o banco existe
        if current_db != 'default' and current_db not in settings.DATABASES:
            logger.error(f"Banco {current_db} não encontrado na configuração")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na validação de isolamento: {str(e)}")
        return False