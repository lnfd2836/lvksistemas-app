from django.apps import AppConfig


class LojasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lojas'
    
    def ready(self):
        import lojas.signals
        import lojas.signals_login

