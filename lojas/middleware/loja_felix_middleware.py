"""
Middleware exclusivo para Loja Felix - Clínica de Estética
Exemplo de middleware gerado automaticamente
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from lojas.models import Loja

logger = logging.getLogger(__name__)


class LojaFelixMiddleware:
    """
    Middleware EXCLUSIVO para Loja Felix - Clínica de Estética
    - Controla acesso apenas para admin e funcionários da Felix
    - Módulos específicos: agendamento, procedimentos, clientes
    - Tema moderno
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurações específicas da Felix
        self.loja_nome = 'Loja Felix'
        self.loja_tipo = 'clinica_estetica'
        
        # URLs exclusivas da Felix
        self.felix_exclusive_urls = [
            '/login/loja-felix/',
            '/modulos/estetica/',
            '/felix/',
        ]
        
        # Módulos disponíveis para Felix
        self.felix_modulos = [
            'agendamento',
            'procedimentos',
            'clientes',
            'produtos_esteticos'
        ]
        
        # Configurações de acesso
        self.require_felix_permission = True
        self.allow_super_admin_override = True
    
    def __call__(self, request):
        """Processa requisições específicas da Felix"""
        
        try:
            # Verificar se é requisição da Felix
            if self._is_felix_request(request):
                return self._handle_felix_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no middleware da Felix: {str(e)}")
            return self.get_response(request)
    
    def _is_felix_request(self, request):
        """Verifica se é requisição da Felix"""
        path = request.path
        return any(path.startswith(url) for url in self.felix_exclusive_urls)
    
    def _handle_felix_request(self, request):
        """Processa requisições da Felix"""
        
        # Log de acesso
        logger.info(f"Acesso à Felix: {request.path} por {request.user}")
        
        # Verificar permissões
        if not self._has_felix_permission(request):
            return self._deny_felix_access(request)
        
        # Adicionar contexto da Felix
        request.felix_context = {
            'loja_nome': self.loja_nome,
            'loja_tipo': self.loja_tipo,
            'modulos_disponiveis': self.felix_modulos,
            'tema': 'moderno',
            'is_felix_exclusive': True,
        }
        
        # Configurar sessão da Felix
        request.session['current_loja_tipo'] = 'felix'
        request.session['tema_ativo'] = 'moderno'
        
        return self.get_response(request)
    
    def _has_felix_permission(self, request):
        """Verifica se usuário tem permissão para acessar a Felix"""
        
        # Super admin NÃO pode acessar sistema da loja
        if request.user.is_superuser:
            logger.warning(f"Super admin {request.user.username} tentou acessar sistema da Felix")
            return False
        
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é admin da Felix
        try:
            felix = Loja.objects.get(nome__icontains='Felix')
            if felix.admin_user == request.user:
                return True
        except Loja.DoesNotExist:
            return False
        
        # Verificar se é funcionário da Felix
        if hasattr(request.user, 'funcionario'):
            funcionario = request.user.funcionario
            if 'felix' in funcionario.loja.nome.lower():
                return True
        
        return False
    
    def _deny_felix_access(self, request):
        """Nega acesso à Felix"""
        
        logger.warning(f"Acesso negado à Felix para usuário: {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Você não tem permissão para acessar a Loja Felix'
            }, status=403)
        
        messages.error(request, 'Acesso negado. Você não tem permissão para acessar a Loja Felix.')
        return redirect('root_redirect')
