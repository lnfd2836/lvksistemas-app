"""
Gerador automático de middlewares exclusivos por loja
"""
import os
import logging
from django.template import Template, Context

logger = logging.getLogger(__name__)


class MiddlewareLojaGenerator:
    """
    Gerador automático de middlewares exclusivos por loja
    Cada loja terá seu próprio middleware com regras específicas
    """
    
    def __init__(self):
        self.template_middleware = self._get_template_middleware()
    
    def gerar_middleware_loja(self, loja):
        """Gera middleware exclusivo para uma loja"""
        
        try:
            # Preparar contexto
            context = {
                'loja_nome': loja.nome,
                'loja_id': str(loja.id),
                'loja_slug': self._generate_slug(loja.nome),
                'loja_tipo': loja.tipo_loja.nome if loja.tipo_loja else 'padrao',
                'loja_cidade': loja.cidade,
                'loja_estado': loja.estado,
                'loja_cnpj': loja.cnpj,
            }
            
            # Renderizar template
            template = Template(self.template_middleware)
            middleware_code = template.render(Context(context))
            
            # Criar arquivo do middleware
            middleware_path = f'lojas/middleware/loja_{context["loja_slug"]}_middleware.py'
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(middleware_path), exist_ok=True)
            
            # Escrever arquivo
            with open(middleware_path, 'w', encoding='utf-8') as f:
                f.write(middleware_code)
            
            logger.info(f"Middleware exclusivo criado para loja: {loja.nome}")
            
            return {
                'success': True,
                'middleware_path': middleware_path,
                'middleware_class': f'Loja{context["loja_slug"].title()}Middleware'
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar middleware para loja {loja.nome}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_slug(self, nome):
        """Gera slug para nome da loja"""
        import re
        slug = re.sub(r'[^a-zA-Z0-9]', '_', nome.lower())
        slug = re.sub(r'_+', '_', slug)
        return slug.strip('_')
    
    def _get_template_middleware(self):
        """Template para middleware de loja"""
        return '''"""
Middleware exclusivo para {{ loja_nome }}
Gerado automaticamente pelo sistema
"""'''
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from lojas.models import Loja

logger = logging.getLogger(__name__)


class Loja{{ loja_slug|title }}Middleware:
    """
    Middleware EXCLUSIVO para {{ loja_nome }}
    - ID da Loja: {{ loja_id }}
    - Tipo: {{ loja_tipo }}
    - Localização: {{ loja_cidade }}/{{ loja_estado }}
    - CNPJ: {{ loja_cnpj }}
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurações específicas da loja
        self.loja_id = '{{ loja_id }}'
        self.loja_nome = '{{ loja_nome }}'
        self.loja_tipo = '{{ loja_tipo }}'
        self.loja_slug = '{{ loja_slug }}'
        
        # URLs exclusivas desta loja
        self.loja_exclusive_urls = [
            '/login/{{ loja_slug }}/',
            '/dashboard/loja/{{ loja_id }}/',
            '/{{ loja_slug }}/',
        ]
        
        # Módulos disponíveis para esta loja
        self.loja_modulos = self._get_modulos_por_tipo()
        
        # Configurações de acesso
        self.require_loja_permission = True
        self.allow_super_admin_override = True
    
    def __call__(self, request):
        """Processa requisições específicas desta loja"""
        
        try:
            # Verificar se é requisição desta loja
            if self._is_loja_request(request):
                return self._handle_loja_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no middleware da loja {{ loja_nome }}: {str(e)}")
            return self.get_response(request)
    
    def _is_loja_request(self, request):
        """Verifica se é requisição desta loja"""
        path = request.path
        return any(path.startswith(url) for url in self.loja_exclusive_urls)
    
    def _handle_loja_request(self, request):
        """Processa requisições desta loja"""
        
        # Log de acesso
        logger.info(f"Acesso à loja {{ loja_nome }}: {request.path} por {request.user}")
        
        # Verificar permissões
        if not self._has_loja_permission(request):
            return self._deny_access(request)
        
        # Adicionar contexto da loja
        request.loja_context = {
            'loja_id': self.loja_id,
            'loja_nome': self.loja_nome,
            'loja_tipo': self.loja_tipo,
            'loja_modulos': self.loja_modulos,
            'is_loja_exclusive': True,
        }
        
        # Configurar sessão da loja
        request.session['current_loja_id'] = self.loja_id
        request.session['current_loja_nome'] = self.loja_nome
        
        return self.get_response(request)
    
    def _has_loja_permission(self, request):
        """Verifica se usuário tem permissão para acessar esta loja"""
        
        # Super admin sempre pode acessar
        if self.allow_super_admin_override and request.user.is_superuser:
            return True
        
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é admin desta loja
        try:
            loja = Loja.objects.get(id=self.loja_id)
            if loja.admin_user == request.user:
                return True
        except Loja.DoesNotExist:
            return False
        
        # Verificar se é funcionário desta loja
        if hasattr(request.user, 'funcionario'):
            funcionario = request.user.funcionario
            if str(funcionario.loja.id) == self.loja_id:
                return True
        
        return False
    
    def _deny_access(self, request):
        """Nega acesso à loja"""
        
        logger.warning(f"Acesso negado à loja {{ loja_nome }} para usuário: {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': f'Você não tem permissão para acessar {{ loja_nome }}'
            }, status=403)
        
        messages.error(request, f'Acesso negado. Você não tem permissão para acessar {{ loja_nome }}.')
        return redirect('root_redirect')
    
    def _get_modulos_por_tipo(self):
        """Retorna módulos disponíveis baseado no tipo da loja"""
        
        modulos_por_tipo = {
            'controle_qualidade': ['avaliacao', 'cursos', 'professores', 'relatorios'],
            'clinica_estetica': ['agendamento', 'procedimentos', 'clientes', 'produtos'],
            'lanchonete': ['pedidos', 'mesas', 'cardapio', 'estoque'],
            'padrao': ['vendas', 'clientes', 'produtos', 'relatorios'],
        }
        
        return modulos_por_tipo.get(self.loja_tipo, modulos_por_tipo['padrao'])
    
    def remover_middleware_loja(self, loja):
        """Remove middleware de uma loja"""
        
        try:
            loja_slug = self._generate_slug(loja.nome)
            middleware_path = f'lojas/middleware/loja_{loja_slug}_middleware.py'
            
            if os.path.exists(middleware_path):
                os.remove(middleware_path)
                logger.info(f"Middleware removido para loja: {loja.nome}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover middleware da loja {loja.nome}: {str(e)}")
            return False
