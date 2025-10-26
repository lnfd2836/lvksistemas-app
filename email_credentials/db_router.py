"""
Router de banco de dados para separar dados por loja
"""
from django.conf import settings
from .database_config import get_loja_database_alias, is_loja_database


class LojaDBRouter:
    """
    Router que direciona operações de banco para bancos específicos por loja
    """
    
    # Apps que devem ser isolados por loja
    LOJA_APPS = {
        'avaliacao_qualidade',
        'controle_financeiro',
        'email_credentials',
    }
    
    # Apps que ficam no banco principal
    MAIN_APPS = {
        'admin',
        'auth',
        'contenttypes',
        'sessions',
        'lojas',
        'usuarios',
        'dashboard',
        'modulos',
        'planos',
    }
    
    def db_for_read(self, model, **hints):
        """Determina qual banco usar para leitura"""
        app_label = model._meta.app_label
        
        # Apps do sistema principal
        if app_label in self.MAIN_APPS:
            return 'default'
        
        # Apps que devem ser isolados por loja
        if app_label in self.LOJA_APPS:
            return self._get_loja_db_from_context(**hints)
        
        return None
    
    def db_for_write(self, model, **hints):
        """Determina qual banco usar para escrita"""
        app_label = model._meta.app_label
        
        # Apps do sistema principal
        if app_label in self.MAIN_APPS:
            return 'default'
        
        # Apps que devem ser isolados por loja
        if app_label in self.LOJA_APPS:
            return self._get_loja_db_from_context(**hints)
        
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Permite relações apenas dentro do mesmo banco"""
        db_set = {'default'}
        
        # Adicionar todos os bancos de loja
        for db_alias in settings.DATABASES.keys():
            if is_loja_database(db_alias):
                db_set.add(db_alias)
        
        # Permitir relações se ambos objetos estão no mesmo conjunto de bancos
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Controla quais migrações rodar em quais bancos"""
        
        # Apps do sistema principal só no banco default
        if app_label in self.MAIN_APPS:
            return db == 'default'
        
        # Apps de loja podem migrar em bancos de loja
        if app_label in self.LOJA_APPS:
            return db == 'default' or is_loja_database(db)
        
        # Outros apps só no banco principal
        return db == 'default'
    
    def _get_loja_db_from_context(self, **hints):
        """Tenta determinar qual banco de loja usar baseado no contexto"""
        
        # Verificar se há uma instância com loja associada
        instance = hints.get('instance')
        if instance:
            # Verificar se o modelo tem loja_associada
            if hasattr(instance, 'loja_associada') and instance.loja_associada:
                return get_loja_database_alias(instance.loja_associada.id)
            
            # Verificar se é um usuário com loja_admin
            if hasattr(instance, 'loja_admin') and instance.loja_admin:
                return get_loja_database_alias(instance.loja_admin.id)
        
        # Verificar thread local para loja atual
        try:
            from django.utils.deprecation import MiddlewareMixin
            import threading
            
            local = getattr(threading.current_thread(), 'loja_atual', None)
            if local and hasattr(local, 'id'):
                return get_loja_database_alias(local.id)
        except:
            pass
        
        # Fallback para banco principal
        return 'default'


class LojaMiddleware:
    """
    Middleware para definir a loja atual no contexto da thread
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Determinar loja atual
        loja_atual = self._get_loja_from_request(request)
        
        # Definir no contexto da thread
        import threading
        threading.current_thread().loja_atual = loja_atual
        
        # Adicionar ao request para fácil acesso
        request.loja_atual = loja_atual
        
        response = self.get_response(request)
        
        # Limpar contexto
        if hasattr(threading.current_thread(), 'loja_atual'):
            delattr(threading.current_thread(), 'loja_atual')
        
        return response
    
    def _get_loja_from_request(self, request):
        """Determina a loja atual baseada no request"""
        
        # Se usuário está logado
        if hasattr(request, 'user') and request.user.is_authenticated:
            
            # Verificar se é admin de uma loja
            if hasattr(request.user, 'loja_admin') and request.user.loja_admin:
                return request.user.loja_admin
            
            # Verificar se tem perfil FATESA com loja associada
            if hasattr(request.user, 'perfil_fatesa') and request.user.perfil_fatesa:
                if hasattr(request.user.perfil_fatesa, 'loja_associada') and request.user.perfil_fatesa.loja_associada:
                    return request.user.perfil_fatesa.loja_associada
        
        # Verificar subdomínio ou parâmetro na URL
        # TODO: Implementar lógica de subdomínio se necessário
        
        return None