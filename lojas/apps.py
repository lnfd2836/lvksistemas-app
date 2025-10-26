from django.apps import AppConfig


class LojasConfig(AppConfig):
    
    def ready(self):
        """Carrega signals quando app está pronto"""
        try:
            import lojas.signals_middleware
        except ImportError:
            pass
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lojas'
    
    def ready(self):
        import lojas.signals
        import lojas.signals_login

