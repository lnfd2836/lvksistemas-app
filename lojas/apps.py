from django.apps import AppConfig


class LojasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lojas'
    
    def ready(self):
        """Carrega signals quando app está pronto"""
        # Importar apenas o signal principal que envia email
        import lojas.signals
        
        # Importar signal de login (não envia email, apenas cria configuração)
        import lojas.signals_login
        
        # Importar signal de middleware (opcional)
        try:
            import lojas.signals_middleware
        except ImportError:
            pass

