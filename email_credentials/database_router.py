"""
Roteador de banco de dados para isolamento por loja
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Import lazy para evitar dependência circular
def get_loja_db_config():
    from .database_config import setup_loja_database
    return setup_loja_database


class LojasDatabaseRouter:
    """
    Roteador para direcionar queries para bancos individuais das lojas
    """
    
    # Apps que ficam apenas no banco principal
    MAIN_DATABASE_APPS = {
        'auth',
        'contenttypes',
        'sessions',
        'admin',
        'email_credentials',
        'lojas',  # Modelo Loja fica no banco principal
        'usuarios',  # Controle de usuários no banco principal
        'dashboard',
        'planos',
        'controle_financeiro',  # Controle financeiro fica no banco principal
    }
    
    # Modelos que ficam no banco principal mesmo em apps de loja
    MAIN_DATABASE_MODELS = {
        'lojas.loja',
        'usuarios.perfilusuario',
        'email_credentials.emaillog',
        'email_credentials.extendeduserprofile',
    }
    
    # Apps que têm dados específicos por loja
    LOJA_SPECIFIC_APPS = {
        'avaliacao_qualidade',
        'modulos',
    }
    
    def db_for_read(self, model, **hints):
        """
        Determina qual banco usar para leitura
        """
        app_label = model._meta.app_label
        model_name = f"{app_label}.{model._meta.model_name}"
        
        # Modelos que sempre ficam no banco principal
        if (app_label in self.MAIN_DATABASE_APPS or 
            model_name in self.MAIN_DATABASE_MODELS):
            return 'default'
        
        # Modelos específicos de loja
        if app_label in self.LOJA_SPECIFIC_APPS:
            return self._get_loja_database_from_hints(hints)
        
        # Default para banco principal
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Determina qual banco usar para escrita
        """
        return self.db_for_read(model, **hints)
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relações apenas dentro do mesmo banco
        """
        db_set = {'default'}
        
        # Adicionar bancos das lojas se necessário
        if hasattr(obj1, '_state') and hasattr(obj2, '_state'):
            db_set.add(obj1._state.db)
            db_set.add(obj2._state.db)
        
        # Permitir relações se ambos estão no mesmo conjunto de bancos
        return len(db_set) <= 2  # default + um banco de loja
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Controla quais migrações aplicar em cada banco
        """
        model_full_name = f"{app_label}.{model_name}" if model_name else None
        
        # Banco principal (default)
        if db == 'default':
            # Apps que ficam no banco principal
            if app_label in self.MAIN_DATABASE_APPS:
                return True
            
            # Modelos específicos que ficam no banco principal
            if model_full_name in self.MAIN_DATABASE_MODELS:
                return True
            
            # Apps de loja não migram no banco principal
            if app_label in self.LOJA_SPECIFIC_APPS:
                return model_full_name in self.MAIN_DATABASE_MODELS
            
            return True
        
        # Bancos das lojas
        if db.startswith('loja_'):
            # Apps do banco principal não migram nos bancos das lojas
            if app_label in self.MAIN_DATABASE_APPS:
                return False
            
            # Modelos do banco principal não migram nos bancos das lojas
            if model_full_name in self.MAIN_DATABASE_MODELS:
                return False
            
            # Apps específicos de loja migram nos bancos das lojas
            if app_label in self.LOJA_SPECIFIC_APPS:
                return True
            
            return False
        
        # Outros bancos
        return False
    
    def _get_loja_database_from_hints(self, hints):
        """
        Extrai o banco da loja dos hints
        """
        # Tentar obter da instância
        if 'instance' in hints and hints['instance']:
            instance = hints['instance']
            
            # Se tem loja_associada
            if hasattr(instance, 'loja_associada') and instance.loja_associada:
                db_alias = self.get_loja_database_alias(instance.loja_associada.id)
                # Garantir que o banco existe
                get_loja_db_config()(instance.loja_associada.id)
                return db_alias
            
            # Se tem loja diretamente
            if hasattr(instance, 'loja') and instance.loja:
                db_alias = self.get_loja_database_alias(instance.loja.id)
                # Garantir que o banco existe
                get_loja_db_config()(instance.loja.id)
                return db_alias
        
        # Tentar obter do contexto da thread (se implementado)
        loja_id = self._get_current_loja_id()
        if loja_id:
            return self.get_loja_database_alias(loja_id)
        
        # Fallback para banco principal
        logger.warning("Não foi possível determinar banco da loja, usando banco principal")
        return 'default'
    
    def _get_current_loja_id(self):
        """
        Obtém o ID da loja atual do contexto da thread
        """
        try:
            import threading
            local_data = getattr(threading.current_thread(), 'loja_context', None)
            if local_data and hasattr(local_data, 'loja_id'):
                return local_data.loja_id
        except:
            pass
        
        return None
    
    @staticmethod
    def get_loja_database_alias(loja_id):
        """
        Retorna o alias do banco para uma loja específica
        """
        return f"loja_{loja_id}"
    
    @staticmethod
    def set_loja_context(loja_id):
        """
        Define o contexto da loja para a thread atual
        """
        try:
            import threading
            thread = threading.current_thread()
            if not hasattr(thread, 'loja_context'):
                thread.loja_context = type('LojaContext', (), {})()
            thread.loja_context.loja_id = loja_id
        except Exception as e:
            logger.warning(f"Erro ao definir contexto da loja: {str(e)}")
    
    @staticmethod
    def clear_loja_context():
        """
        Limpa o contexto da loja da thread atual
        """
        try:
            import threading
            thread = threading.current_thread()
            if hasattr(thread, 'loja_context'):
                delattr(thread, 'loja_context')
        except Exception as e:
            logger.warning(f"Erro ao limpar contexto da loja: {str(e)}")
    
    @staticmethod
    def get_all_loja_databases():
        """
        Retorna lista de todos os bancos de loja configurados
        """
        databases = []
        
        # Obter da configuração do Django
        django_databases = getattr(settings, 'DATABASES', {})
        
        for db_alias in django_databases.keys():
            if db_alias.startswith('loja_'):
                databases.append(db_alias)
        
        return databases
    
    @staticmethod
    def create_loja_database_config(loja_id, db_name=None, db_host='localhost', db_port=5432):
        """
        Cria configuração de banco para uma nova loja
        """
        if not db_name:
            db_name = f"loja_{loja_id}"
        
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'HOST': db_host,
            'PORT': db_port,
            'USER': getattr(settings, 'DATABASE_USER', 'postgres'),
            'PASSWORD': getattr(settings, 'DATABASE_PASSWORD', ''),
            'OPTIONS': {
                'charset': 'utf8',
            },
        }
    
    @staticmethod
    def add_loja_database_to_settings(loja_id, db_config):
        """
        Adiciona configuração de banco da loja às configurações do Django
        """
        try:
            alias = LojasDatabaseRouter.get_loja_database_alias(loja_id)
            
            # Adicionar às configurações
            if not hasattr(settings, 'DATABASES'):
                settings.DATABASES = {}
            
            settings.DATABASES[alias] = db_config
            
            logger.info(f"Configuração de banco adicionada para loja {loja_id}: {alias}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar configuração de banco para loja {loja_id}: {str(e)}")
            return False