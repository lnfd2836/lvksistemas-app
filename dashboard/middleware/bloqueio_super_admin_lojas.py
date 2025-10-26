"""
Middleware de bloqueio geral - Impede super admins de acessar sistema das lojas
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class BloqueioSuperAdminLojasMiddleware:
    """
    Middleware que BLOQUEIA super admins de acessar qualquer sistema de loja
    
    REGRA FUNDAMENTAL:
    - Super Admin = Administração (gerenciar lojas, usuários, sistema)
    - Admin/Funcionário da Loja = Operação (trabalhar no sistema da loja)
    
    SEPARAÇÃO TOTAL entre administração e operação
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Padrões de URLs de sistema de lojas (BLOQUEADAS para super admin)
        self.loja_system_patterns = [
            '/login/',                    # Qualquer login de loja
            '/dashboard/loja/',           # Dashboard das lojas
            '/avaliacao-qualidade/',      # Módulos específicos
            '/modulos/',                  # Módulos das lojas
            '/pedidos/',                  # Operações
            '/clientes/',                 # Dados das lojas
            '/produtos/',                 # Dados das lojas
            '/vendas/',                   # Operações
            '/agendamento/',              # Módulos específicos
            '/procedimentos/',            # Módulos específicos
            '/mesas/',                    # Módulos específicos
            '/cardapio/',                 # Módulos específicos
        ]
        
        # URLs de administração (PERMITIDAS para super admin)
        self.admin_allowed_patterns = [
            '/admin/',
            '/super-admin/',
            '/usuarios/gerenciar/',
            '/lojas/gerenciar/',
            '/relatorios/sistema/',
            '/configuracoes/',
        ]
    
    def __call__(self, request):
        """Bloqueia super admins de acessar sistema das lojas"""
        
        try:
            # Verificar se é super admin tentando acessar sistema de loja
            if self._is_super_admin_accessing_loja_system(request):
                return self._block_super_admin_loja_access(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no BloqueioSuperAdminLojasMiddleware: {str(e)}")
            return self.get_response(request)
    
    def _is_super_admin_accessing_loja_system(self, request):
        """Verifica se super admin está tentando acessar sistema de loja"""
        
        # Deve ser super admin
        if not (request.user.is_authenticated and request.user.is_superuser):
            return False
        
        # Deve ser URL de sistema de loja
        path = request.path
        
        # Permitir URLs de administração
        if any(path.startswith(pattern) for pattern in self.admin_allowed_patterns):
            return False
        
        # Bloquear URLs de sistema de loja
        return any(path.startswith(pattern) for pattern in self.loja_system_patterns)
    
    def _block_super_admin_loja_access(self, request):
        """Bloqueia acesso e redireciona para administração"""
        
        logger.warning(
            f"BLOQUEIO: Super Admin {request.user.username} "
            f"tentou acessar sistema de loja: {request.path}"
        )
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Super Admins administram lojas, não operam o sistema das lojas',
                'redirect': '/admin/',
                'explanation': 'Use o painel de administração para gerenciar lojas'
            }, status=403)
        
        messages.error(
            request,
            '🚫 Super Admins ADMINISTRAM lojas, mas não operam o sistema das lojas. '
            'Use o painel de administração para gerenciar lojas, usuários e configurações.'
        )
        
        return redirect('/admin/')
