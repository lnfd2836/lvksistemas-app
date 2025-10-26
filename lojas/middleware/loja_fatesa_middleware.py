"""
Middleware exclusivo para Fatesa Escola de Ultrassonografia
Exemplo de middleware gerado automaticamente
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from lojas.models import Loja

logger = logging.getLogger(__name__)


class LojaFatesaMiddleware:
    """
    Middleware EXCLUSIVO para Fatesa Escola de Ultrassonografia
    - Controla acesso apenas para admin e funcionários da Fatesa
    - Módulos específicos: avaliação de qualidade, cursos, professores
    - Tema corporativo azul
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurações específicas da Fatesa
        self.loja_nome = 'Fatesa Escola de Ultrassonografia'
        self.loja_tipo = 'controle_qualidade'
        
        # URLs exclusivas da Fatesa
        self.fatesa_exclusive_urls = [
            '/login/fatesa-escola-de-ultrassonografia/',
            '/avaliacao-qualidade/',
            '/fatesa/',
        ]
        
        # Módulos disponíveis para Fatesa
        self.fatesa_modulos = [
            'avaliacao_qualidade',
            'cursos',
            'professores',
            'relatorios_academicos'
        ]
        
        # Configurações de acesso
        self.require_fatesa_permission = True
        self.allow_super_admin_override = True
    
    def __call__(self, request):
        """Processa requisições específicas da Fatesa"""
        
        try:
            # Verificar se é requisição da Fatesa
            if self._is_fatesa_request(request):
                return self._handle_fatesa_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no middleware da Fatesa: {str(e)}")
            return self.get_response(request)
    
    def _is_fatesa_request(self, request):
        """Verifica se é requisição da Fatesa"""
        path = request.path
        return any(path.startswith(url) for url in self.fatesa_exclusive_urls)
    
    def _handle_fatesa_request(self, request):
        """Processa requisições da Fatesa"""
        
        # Log de acesso
        logger.info(f"Acesso à Fatesa: {request.path} por {request.user}")
        
        # Verificar permissões
        if not self._has_fatesa_permission(request):
            return self._deny_fatesa_access(request)
        
        # Adicionar contexto da Fatesa
        request.fatesa_context = {
            'loja_nome': self.loja_nome,
            'loja_tipo': self.loja_tipo,
            'modulos_disponiveis': self.fatesa_modulos,
            'tema': 'corporativo_azul',
            'is_fatesa_exclusive': True,
        }
        
        # Configurar sessão da Fatesa
        request.session['current_loja_tipo'] = 'fatesa'
        request.session['tema_ativo'] = 'corporativo'
        
        return self.get_response(request)
    
    def _has_fatesa_permission(self, request):
        """Verifica se usuário tem permissão para acessar a Fatesa"""
        
        # Super admin NÃO pode acessar sistema da loja
        if request.user.is_superuser:
            logger.warning(f"Super admin {request.user.username} tentou acessar sistema da Fatesa")
            return False
        
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é admin da Fatesa
        try:
            fatesa = Loja.objects.get(nome__icontains='Fatesa')
            if fatesa.admin_user == request.user:
                logger.info(f"Admin da Fatesa {request.user.username} acessando")
                return True
        except Loja.DoesNotExist:
            logger.warning("Loja Fatesa não encontrada")
            return False
        
        # Verificar se é funcionário da Fatesa
        if hasattr(request.user, 'funcionario'):
            funcionario = request.user.funcionario
            if funcionario.loja.nome == self.loja_nome:
                logger.info(f"Funcionário da Fatesa {request.user.username} acessando")
                return True
        
        # Verificar se tem perfil específico da Fatesa
        if hasattr(request.user, 'perfil_fatesa'):
            logger.info(f"Usuário com perfil Fatesa {request.user.username} acessando")
            return True
        
        return False
    
    def _deny_fatesa_access(self, request):
        """Nega acesso à Fatesa"""
        
        logger.warning(f"Acesso negado à Fatesa para usuário: {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Você não tem permissão para acessar a Fatesa Escola de Ultrassonografia'
            }, status=403)
        
        messages.error(
            request, 
            'Acesso negado. Você não tem permissão para acessar a Fatesa Escola de Ultrassonografia.'
        )
        return redirect('root_redirect')
