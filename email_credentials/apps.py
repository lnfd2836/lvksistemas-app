from django.apps import AppConfig


class EmailCredentialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'email_credentials'
    verbose_name = 'Sistema de Credenciais por Email'
    
    def ready(self):
        """Inicializa configurações quando o app está pronto"""
        try:
            # Importar e inicializar configurações de banco das lojas
            from .database_config import loja_db_config_instance
            loja_db_config_instance.load_loja_databases()
        except Exception as e:
            # Não falhar se não conseguir carregar (pode ser durante migrações)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Não foi possível carregar configurações de banco das lojas: {str(e)}")