from django.apps import AppConfig


class ControleFinanceiroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'controle_financeiro'
    verbose_name = 'Controle Financeiro'
    
    def ready(self):
        """Registra os signals quando a app estiver pronta"""
        import controle_financeiro.signals
