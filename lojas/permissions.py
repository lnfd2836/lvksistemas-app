from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


def get_user_funcionario(user):
    """Retorna o funcionário associado ao usuário, se existir"""
    if hasattr(user, 'funcionario'):
        return user.funcionario
    return None


def user_has_permission(user, module, action):
    """Verifica se o usuário tem permissão para uma ação específica"""
    # Super admin tem todas as permissões
    if user.is_superuser:
        return True
    
    # Admin de loja tem todas as permissões na sua loja
    if hasattr(user, 'loja_admin'):
        return True
    
    # Funcionário - verifica permissões específicas
    funcionario = get_user_funcionario(user)
    if funcionario and funcionario.ativo:
        return funcionario.has_permission(module, action)
    
    return False


def require_permission(module, action, redirect_url='dashboard:loja', ajax_response=False):
    """
    Decorator para views que requerem permissões específicas
    
    Args:
        module: Módulo do sistema (ex: 'vendas', 'produtos')
        action: Ação específica (ex: 'read', 'write', 'delete')
        redirect_url: URL para redirecionamento em caso de negação
        ajax_response: Se True, retorna JSON em vez de redirect
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if ajax_response:
                    return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
                return redirect('dashboard:loja_login')
            
            if not user_has_permission(request.user, module, action):
                logger.warning(
                    f"Usuário {request.user.username} tentou acessar {module}.{action} sem permissão"
                )
                
                if ajax_response:
                    return JsonResponse({'error': 'Permissão negada'}, status=403)
                
                messages.error(request, 'Você não tem permissão para realizar esta ação.')
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_loja_access(view_func):
    """Decorator para views que requerem acesso à loja (admin ou funcionário)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Se veio de login personalizado, redirecionar para login simples
            # para evitar loop de redirecionamento
            return redirect('root_redirect')
        
        # Super admin sempre tem acesso
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Admin de loja tem acesso
        if hasattr(request.user, 'loja_admin'):
            return view_func(request, *args, **kwargs)
        
        # Funcionário ativo tem acesso
        funcionario = get_user_funcionario(request.user)
        if funcionario and funcionario.ativo:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Você não tem acesso a esta área.')
        return redirect('root_redirect')
    
    return wrapper


class PermissionMixin:
    """Mixin para views baseadas em classe que precisam de controle de permissões"""
    
    required_permission = None  # Tuple (module, action)
    permission_denied_message = 'Você não tem permissão para realizar esta ação.'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:loja_login')
        
        if self.required_permission:
            module, action = self.required_permission
            if not user_has_permission(request.user, module, action):
                messages.error(request, self.permission_denied_message)
                return redirect('dashboard:loja')
        
        return super().dispatch(request, *args, **kwargs)


class LojaAccessMixin:
    """Mixin para views que requerem acesso à loja"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:loja_login')
        
        # Super admin sempre tem acesso
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # Admin de loja tem acesso
        if hasattr(request.user, 'loja_admin'):
            return super().dispatch(request, *args, **kwargs)
        
        # Funcionário ativo tem acesso
        funcionario = get_user_funcionario(request.user)
        if funcionario and funcionario.ativo:
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, 'Você não tem acesso a esta área.')
        return redirect('login')


def get_user_loja(user):
    """Retorna a loja associada ao usuário"""
    if user.is_superuser:
        return None  # Super admin não tem loja específica
    
    if hasattr(user, 'loja_admin'):
        return user.loja_admin
    
    funcionario = get_user_funcionario(user)
    if funcionario:
        return funcionario.loja
    
    return None


def get_user_permissions(user):
    """Retorna todas as permissões do usuário"""
    if user.is_superuser:
        return {
            'dashboard': ['read', 'write'],
            'vendas': ['read', 'write', 'delete'],
            'produtos': ['read', 'write', 'delete'],
            'clientes': ['read', 'write', 'delete'],
            'funcionarios': ['read', 'write', 'delete'],
            'relatorios': ['read', 'write'],
            'configuracoes': ['read', 'write'],
            'estoque': ['read', 'write'],
            'pedidos': ['read', 'write', 'delete'],
            'servicos': ['read', 'write', 'delete'],
        }
    
    if hasattr(user, 'loja_admin'):
        return {
            'dashboard': ['read', 'write'],
            'vendas': ['read', 'write', 'delete'],
            'produtos': ['read', 'write', 'delete'],
            'clientes': ['read', 'write', 'delete'],
            'funcionarios': ['read', 'write'],
            'relatorios': ['read', 'write'],
            'configuracoes': ['read', 'write'],
            'estoque': ['read', 'write'],
            'pedidos': ['read', 'write', 'delete'],
            'servicos': ['read', 'write'],
        }
    
    funcionario = get_user_funcionario(user)
    if funcionario and funcionario.ativo:
        return funcionario.get_dashboard_permissions()
    
    return {}


def check_module_permission(user, module):
    """Verifica se o usuário tem alguma permissão no módulo"""
    permissions = get_user_permissions(user)
    return module in permissions and len(permissions[module]) > 0


def get_available_modules(user):
    """Retorna lista de módulos disponíveis para o usuário"""
    permissions = get_user_permissions(user)
    return list(permissions.keys())


# Context processor para templates
def permissions_context(request):
    """Context processor que adiciona informações de permissões aos templates"""
    if not request.user.is_authenticated:
        return {}
    
    return {
        'user_permissions': get_user_permissions(request.user),
        'user_loja': get_user_loja(request.user),
        'available_modules': get_available_modules(request.user),
    }