"""
Configuração dinâmica de bancos de dados das lojas
"""
from django.conf import settings
import os


class LojaDBConfig:
    """Classe para gerenciar configurações de banco de dados por loja"""
    
    def __init__(self):
        self._loaded = False
    
    def load_loja_databases(self):
        """Carrega configurações de banco para todas as lojas"""
        if self._loaded:
            return
            
        try:
            # Importar modelo de Loja apenas quando necessário
            from lojas.models import Loja
            
            # Configurar banco para cada loja
            for loja in Loja.objects.all():
                self.setup_loja_database(loja.id)
            
            self._loaded = True
            
        except Exception as e:
            # Durante migrações ou quando o banco não existe ainda
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Não foi possível carregar lojas: {str(e)}")
    
    def setup_loja_database(self, loja_id):
        """
        Configura banco para uma loja específica
        
        Args:
            loja_id: ID da loja
            
        Returns:
            str: Alias do banco configurado
        """
        
        db_alias = get_loja_database_alias(loja_id)
        db_config = loja_db_config(loja_id)
        
        # Adicionar à configuração do Django
        if not hasattr(settings, 'DATABASES'):
            settings.DATABASES = {}
        
        settings.DATABASES[db_alias] = db_config
        
        return db_alias


# Instância global
loja_db_config_instance = LojaDBConfig()


def loja_db_config(loja_id):
    """
    Cria configuração de banco SQLite para uma loja específica
    
    Args:
        loja_id: ID da loja
        
    Returns:
        dict: Configuração do banco de dados
    """
    
    db_path = settings.BASE_DIR / f'db_{loja_id}.sqlite3'
    
    # Copiar configuração base do banco principal
    main_config = settings.DATABASES['default'].copy()
    
    # Personalizar para a loja
    config = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(db_path),
        'OPTIONS': {
            'timeout': 20,
        },
        'ATOMIC_REQUESTS': True,
        'AUTOCOMMIT': True,
        'TIME_ZONE': None,
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'TEST': {
            'NAME': None,
        },
    }
    
    # Adicionar configurações que podem estar no banco principal
    if 'CONN_MAX_AGE' in main_config:
        config['CONN_MAX_AGE'] = main_config['CONN_MAX_AGE']
    
    if 'CONN_HEALTH_CHECKS' in main_config:
        config['CONN_HEALTH_CHECKS'] = main_config['CONN_HEALTH_CHECKS']
    else:
        config['CONN_HEALTH_CHECKS'] = False  # Desabilitar health checks por padrão
    
    return config


def get_loja_database_alias(loja_id):
    """Retorna alias do banco para uma loja"""
    return f"loja_{loja_id}"


def is_loja_database(db_alias):
    """Verifica se é um banco de loja"""
    return db_alias.startswith('loja_')


def get_loja_id_from_alias(db_alias):
    """Extrai o ID da loja do alias do banco"""
    if is_loja_database(db_alias):
        return db_alias.replace('loja_', '')
    return None


# Função de compatibilidade
def setup_loja_database(loja_id):
    """
    Configura banco para uma loja específica
    
    Args:
        loja_id: ID da loja
        
    Returns:
        str: Alias do banco configurado
    """
    return loja_db_config_instance.setup_loja_database(loja_id)


def get_all_loja_database_aliases():
    """Retorna todos os aliases de banco de loja configurados"""
    return [
        db_alias for db_alias in settings.DATABASES.keys() 
        if is_loja_database(db_alias)
    ]