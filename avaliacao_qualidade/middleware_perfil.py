"""
Middleware para redirecionamento automático baseado no perfil do usuário
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class PerfilRedirectMiddleware(MiddlewareMixin):
    """
    Middleware que redireciona usuários para o dashboard apropriado
    baseado em seu grupo/perfil no módulo de avaliação de qualidade
    """
    
    def process_request(self, request):
        # Só processar se o usuário estiver autenticado
        if not request.user.is_authenticated:
            return None
        
        # Só processar URLs do módulo avaliacao_qualidade
        if not request.path.startswith('/avaliacao-qualidade/'):
            return None
        
        # Se está acessando o dashboard principal, redirecionar baseado no perfil
        if request.path == '/avaliacao-qualidade/' or request.path == '/avaliacao-qualidade/dashboard/':
            return self.redirect_by_profile(request)
        
        # Verificar se o usuário tem permissão para acessar dashboards específicos
        if '/dashboard/' in request.path:
            return self.check_dashboard_permission(request)
        
        return None
    
    def redirect_by_profile(self, request):
        """Redireciona para o dashboard apropriado baseado no perfil"""
        
        user = request.user
        
        # Verificar grupos do usuário e redirecionar
        if user.groups.filter(name='Admin_Completo').exists():
            # Admin completo pode acessar qualquer dashboard, manter no principal
            return None
        elif user.groups.filter(name='Avaliacao_Diretoria').exists():
            return redirect('avaliacao_qualidade:dashboard_diretoria')
        elif user.groups.filter(name='Avaliacao_Coordenacao').exists():
            return redirect('avaliacao_qualidade:dashboard_coordenacao')
        elif user.groups.filter(name='Avaliacao_Professor').exists():
            return redirect('avaliacao_qualidade:dashboard_professor')
        
        # Se não tem grupo específico, permitir acesso ao dashboard principal
        return None
    
    def check_dashboard_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o dashboard específico"""
        
        user = request.user
        path = request.path
        
        # Admin completo pode acessar qualquer dashboard
        if user.groups.filter(name='Admin_Completo').exists():
            return None
        
        # Verificar permissões específicas
        if '/dashboard/diretoria/' in path:
            if not user.groups.filter(name='Avaliacao_Diretoria').exists():
                return redirect('avaliacao_qualidade:dashboard_avaliacao')
        
        elif '/dashboard/coordenacao/' in path:
            if not user.groups.filter(name='Avaliacao_Coordenacao').exists():
                return redirect('avaliacao_qualidade:dashboard_avaliacao')
        
        elif '/dashboard/professor/' in path:
            if not user.groups.filter(name='Avaliacao_Professor').exists():
                return redirect('avaliacao_qualidade:dashboard_avaliacao')
        
        return None