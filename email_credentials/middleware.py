"""
Middleware para gerenciar contexto de loja e roteamento de banco
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .database_router import LojasDatabaseRouter
import logging

logger = logging.getLogger(__name__)


class LojaContextMiddleware:
    """
    Middleware para definir contexto da loja baseado no usuário logado
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.router = LojasDatabaseRouter()
    
    def __call__(self, request):
        # Definir contexto da loja antes de processar a request
        self.set_loja_context(request)
        
        response = self.get_response(request)
        
        # Limpar contexto após processar
        self.router.clear_loja_context()
        
        return response
    
    def set_loja_context(self, request):
        """Define o contexto da loja para a request atual"""
        
        if not request.user.is_authenticated:
            return
        
        try:
            # Verificar se tem perfil estendido
            if hasattr(request.user, 'extended_profile'):
                profile = request.user.extended_profile
                
                if profile.associated_loja:
                    # Definir contexto da loja
                    self.router.set_loja_context(profile.associated_loja.id)
                    
                    # Adicionar loja à request para fácil acesso
                    request.loja_atual = profile.associated_loja
                    request.loja_database = profile.database_alias
                    
                    logger.debug(f"Contexto da loja definido: {profile.associated_loja.nome}")
            
            # Fallback: verificar se é admin de loja
            elif hasattr(request.user, 'loja_admin'):
                loja = request.user.loja_admin
                self.router.set_loja_context(loja.id)
                request.loja_atual = loja
                request.loja_database = self.router.get_loja_database_alias(loja.id)
                
                logger.debug(f"Contexto da loja definido (fallback): {loja.nome}")
        
        except Exception as e:
            logger.warning(f"Erro ao definir contexto da loja: {str(e)}")


class DatabaseRoutingMiddleware:
    """
    Middleware para garantir roteamento correto de banco de dados
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar se o roteamento está funcionando corretamente
        self.validate_database_routing(request)
        
        response = self.get_response(request)
        
        return response
    
    def validate_database_routing(self, request):
        """Valida se o roteamento de banco está correto"""
        
        if not request.user.is_authenticated:
            return
        
        try:
            # Verificar se usuário tem acesso ao banco correto
            if hasattr(request, 'loja_atual') and hasattr(request, 'loja_database'):
                loja = request.loja_atual
                expected_db = f"loja_{loja.id}"
                
                if request.loja_database != expected_db:
                    logger.warning(
                        f"Inconsistência no roteamento de banco: "
                        f"esperado {expected_db}, atual {request.loja_database}"
                    )
        
        except Exception as e:
            logger.error(f"Erro na validação de roteamento: {str(e)}")


class PasswordChangeEnforcementMiddleware:
    """
    Middleware para forçar alteração de senha provisória
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar se precisa alterar senha antes de processar
        if self.requires_password_change(request):
            return self.redirect_to_password_change(request)
        
        response = self.get_response(request)
        
        return response
    
    def requires_password_change(self, request):
        """Verifica se o usuário precisa alterar a senha"""
        
        # URLs que não precisam de verificação
        excluded_paths = [
            '/login/',
            '/logout/',
            '/admin/',
            '/static/',
            '/media/',
            '/email-credentials/change-password/',
            '/avaliacao-qualidade/alterar-senha/',
            '/avaliacao-qualidade/meu-perfil/',
        ]
        
        # Verificar se a URL atual está nas exceções
        if any(request.path.startswith(path) for path in excluded_paths):
            return False
        
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se tem perfil estendido com senha provisória
        try:
            if hasattr(request.user, 'extended_profile'):
                profile = request.user.extended_profile
                return profile.requires_password_change()
            
            # Fallback: verificar perfil FATESA
            if hasattr(request.user, 'perfil_fatesa'):
                profile = request.user.perfil_fatesa
                return getattr(profile, 'deve_alterar_senha', False)
        
        except Exception as e:
            logger.warning(f"Erro ao verificar necessidade de alteração de senha: {str(e)}")
        
        return False
    
    def redirect_to_password_change(self, request):
        """Redireciona para página de alteração de senha"""
        
        try:
            # Determinar URL de alteração baseada no contexto
            if hasattr(request, 'loja_atual'):
                # Usuário de loja - usar sistema FATESA se disponível
                if request.path.startswith('/avaliacao-qualidade/'):
                    change_url = reverse('avaliacao_qualidade:alterar_minha_senha')
                else:
                    change_url = '/email-credentials/change-password/'
            else:
                # Super admin ou outros
                change_url = '/email-credentials/change-password/'
            
            messages.warning(
                request,
                'Por segurança, você deve alterar sua senha provisória antes de continuar.'
            )
            
            return redirect(change_url)
        
        except Exception as e:
            logger.error(f"Erro ao redirecionar para alteração de senha: {str(e)}")
            return redirect('/login/')


class UserProfileSyncMiddleware:
    """
    Middleware para sincronizar perfis entre banco principal e da loja
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Sincronizar perfis se necessário
        self.sync_user_profiles(request)
        
        response = self.get_response(request)
        
        return response
    
    def sync_user_profiles(self, request):
        """Sincroniza perfis do usuário entre bancos"""
        
        if not request.user.is_authenticated:
            return
        
        try:
            # Verificar se tem perfil estendido
            if not hasattr(request.user, 'extended_profile'):
                # Criar perfil estendido se não existir
                self.create_missing_extended_profile(request.user)
            
            # Verificar se tem perfil da loja
            if hasattr(request, 'loja_atual'):
                self.ensure_loja_profile_exists(request.user, request.loja_atual)
        
        except Exception as e:
            logger.warning(f"Erro na sincronização de perfis: {str(e)}")
    
    def create_missing_extended_profile(self, user):
        """Cria perfil estendido faltante"""
        
        try:
            from .models import ExtendedUserProfile
            from django.utils import timezone
            
            # Determinar tipo de usuário
            if user.is_superuser:
                user_type = 'super_admin'
            elif hasattr(user, 'loja_admin'):
                user_type = 'loja_admin'
            else:
                user_type = 'loja_user'
            
            # Encontrar loja associada
            loja = None
            if hasattr(user, 'loja_admin'):
                loja = user.loja_admin
            elif hasattr(user, 'perfil_fatesa') and user.perfil_fatesa.loja_associada:
                loja = user.perfil_fatesa.loja_associada
            
            # Criar perfil
            ExtendedUserProfile.objects.create(
                user=user,
                user_type=user_type,
                has_provisional_password=False,  # Usuários existentes têm senhas permanentes
                password_changed_at=timezone.now(),
                associated_loja=loja,
                database_alias=LojasDatabaseRouter.get_loja_database_alias(loja.id) if loja else 'default'
            )
            
            logger.info(f"Perfil estendido criado para {user.username}")
        
        except Exception as e:
            logger.error(f"Erro ao criar perfil estendido para {user.username}: {str(e)}")
    
    def ensure_loja_profile_exists(self, user, loja):
        """Garante que o perfil da loja existe"""
        
        try:
            from .models import LojaUserProfile
            
            db_alias = LojasDatabaseRouter.get_loja_database_alias(loja.id)
            
            # Verificar se perfil existe
            if not LojaUserProfile.objects.using(db_alias).filter(user_id=user.id).exists():
                # Determinar perfil de acesso
                access_profile = 'user'
                permissions = {}
                
                if hasattr(user, 'loja_admin') and user.loja_admin == loja:
                    access_profile = 'admin'
                    permissions = {
                        'can_manage_users': True,
                        'can_view_reports': True,
                        'can_manage_settings': True
                    }
                
                # Criar perfil da loja
                LojaUserProfile.objects.using(db_alias).create(
                    user_id=user.id,
                    username=user.username,
                    loja_access_profile=access_profile,
                    permissions=permissions,
                    settings={}
                )
                
                logger.info(f"Perfil da loja criado para {user.username} em {loja.nome}")
        
        except Exception as e:
            logger.warning(f"Erro ao garantir perfil da loja: {str(e)}")