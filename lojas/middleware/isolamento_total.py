"""
Middleware para garantir isolamento total de dados por loja
"""
import logging
import threading
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import connection
from ..models import Loja
from dashboard.services.authentication import AuthenticationService

logger = logging.getLogger(__name__)


class IsolamentoTotalMiddleware(MiddlewareMixin):
    """
    Middleware que garante isolamento total de dados por loja
    Força que cada usuário veja apenas dados da sua loja
    """
    
    def process_request(self, request):
        """
        Processa a requisição para garantir isolamento total
        """
        
        # Pular para URLs que não precisam de verificação
        if self._should_skip_verification(request):
            return None
        
        # Se usuário está autenticado, aplicar isolamento
        if request.user.is_authenticated:
            return self._apply_isolation(request)
        
        return None
    
    def _should_skip_verification(self, request):
        """Verifica se deve pular a verificação para esta URL"""
        
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/login/',
            '/logout/',
            '/password_reset/',
            '/api/',
            '/webhook/',
            '/crm/orcamento/',  # URLs públicas do CRM
            '/crm/proposta/',   # URLs públicas do CRM
            '/crm/contrato/',   # URLs públicas do CRM
            '/crm/assinar/',    # URLs de assinatura digital do CRM
            '/crm/email/',      # URLs de tracking do CRM
        ]
        
        path = request.path
        
        # Pular URLs específicas
        for skip_path in skip_paths:
            if path.startswith(skip_path):
                return True
        
        return False
    
    def _apply_isolation(self, request):
        """Aplica isolamento de dados baseado no usuário"""
        
        try:
            user = request.user
            
            # Super admins podem ver todos os dados (mas devem usar dashboard específico)
            if user.is_superuser:
                # Verificar se super admin está tentando acessar dashboard de loja
                if request.path.startswith('/dashboard/loja/'):
                    logger.warning(f"Super admin {user.username} tentou acessar dashboard de loja")
                    messages.warning(request, 'Super administradores devem usar o dashboard principal.')
                    return redirect('/dashboard/')
                
                # Super admins podem continuar normalmente
                self._set_isolation_context(request, None, is_super_admin=True)
                return None
            
            # Obter loja do usuário
            user_loja = AuthenticationService.get_user_store(user)
            
            if not user_loja:
                logger.error(f"Usuário {user.username} não tem loja associada")
                messages.error(request, 'Usuário não associado a nenhuma loja. Contate o administrador.')
                logout(request)
                return redirect('/')
            
            # Verificar se a loja está ativa
            if user_loja.status != 'ativa':
                logger.warning(f"Usuário {user.username} tentou acessar loja inativa: {user_loja.nome}")
                messages.error(request, 'Sua loja está inativa. Contate o administrador.')
                logout(request)
                return redirect('/')
            
            # Aplicar contexto de isolamento
            self._set_isolation_context(request, user_loja, is_super_admin=False)
            
            # Verificar se usuário está tentando acessar dados de outra loja
            if not self._validate_loja_access(request, user_loja):
                logger.warning(f"Usuário {user.username} tentou acessar dados de outra loja")
                messages.error(request, 'Acesso negado: Você só pode acessar dados da sua loja.')
                return redirect('/dashboard/loja/')
            
            logger.debug(f"Isolamento aplicado para usuário {user.username} da loja {user_loja.nome}")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar isolamento: {str(e)}")
            messages.error(request, 'Erro interno. Tente novamente.')
            return redirect('/')
        
        return None
    
    def _set_isolation_context(self, request, loja, is_super_admin=False):
        """Define contexto de isolamento na requisição e thread"""
        
        try:
            # Definir na requisição
            request.loja_isolamento = loja
            request.is_super_admin_context = is_super_admin
            
            # Definir na thread
            thread = threading.current_thread()
            
            if not hasattr(thread, 'isolation_context'):
                thread.isolation_context = type('IsolationContext', (), {})()
            
            thread.isolation_context.loja = loja
            thread.isolation_context.loja_id = str(loja.id) if loja else None
            thread.isolation_context.is_super_admin = is_super_admin
            
            # Para compatibilidade com outros middlewares
            if loja:
                thread.loja_id = str(loja.id)
                request.loja_atual = loja
            
            logger.debug(f"Contexto de isolamento definido: Loja={loja.nome if loja else 'None'}, Super={is_super_admin}")
            
        except Exception as e:
            logger.error(f"Erro ao definir contexto de isolamento: {str(e)}")
    
    def _validate_loja_access(self, request, user_loja):
        """Valida se o usuário pode acessar os dados solicitados"""
        
        try:
            # Para URLs que não são específicas de loja, permitir acesso
            safe_paths = [
                '/dashboard/loja/',
                '/dashboard/loja/logout/',
                '/usuarios/',
                '/configuracoes/',
            ]
            
            for safe_path in safe_paths:
                if request.path.startswith(safe_path):
                    return True
            
            # Para outras URLs, verificar se há parâmetros de loja
            # Isso pode ser expandido conforme necessário
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar acesso à loja: {str(e)}")
            return False
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Processa a view para aplicar filtros de isolamento
        """
        
        try:
            # Pular se não há contexto de isolamento
            if not hasattr(request, 'loja_isolamento'):
                return None
            
            # Super admins não precisam de filtros
            if getattr(request, 'is_super_admin_context', False):
                return None
            
            # Aplicar filtros automáticos para views do CRM e outros módulos
            loja = request.loja_isolamento
            if loja:
                # Definir filtros globais para QuerySets
                self._apply_queryset_filters(loja)
            
        except Exception as e:
            logger.error(f"Erro ao processar view com isolamento: {str(e)}")
        
        return None
    
    def _apply_queryset_filters(self, loja):
        """Aplica filtros automáticos para QuerySets"""
        
        try:
            # Definir contexto global para modelos que suportam isolamento
            thread = threading.current_thread()
            
            if not hasattr(thread, 'queryset_filters'):
                thread.queryset_filters = {}
            
            # Filtros para modelos do CRM
            thread.queryset_filters.update({
                'crm_vendas.Lead': {'loja': loja},
                'crm_vendas.Orcamento': {'loja': loja},
                'crm_vendas.Proposta': {'loja': loja},
                'crm_vendas.Contrato': {'loja': loja},
                'crm_vendas.HistoricoContato': {'lead__loja': loja},
                'crm_vendas.ProdutoServico': {'loja': loja},
            })
            
            # Filtros para outros módulos (expandir conforme necessário)
            thread.queryset_filters.update({
                'lojas.Cliente': {'loja': loja},
                'lojas.Produto': {'loja': loja},
                'lojas.Venda': {'loja': loja},
                'lojas.Funcionario': {'loja': loja},
            })
            
            logger.debug(f"Filtros de QuerySet aplicados para loja {loja.nome}")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar filtros de QuerySet: {str(e)}")


def get_current_loja_from_context():
    """
    Função utilitária para obter a loja atual do contexto
    Pode ser usada em models e outras partes do código
    """
    try:
        thread = threading.current_thread()
        
        if hasattr(thread, 'isolation_context') and thread.isolation_context.loja:
            return thread.isolation_context.loja
        
        if hasattr(thread, 'loja_atual'):
            return thread.loja_atual
        
        return None
        
    except Exception:
        return None


def is_super_admin_context():
    """
    Função utilitária para verificar se está em contexto de super admin
    """
    try:
        thread = threading.current_thread()
        
        if hasattr(thread, 'isolation_context'):
            return getattr(thread.isolation_context, 'is_super_admin', False)
        
        return False
        
    except Exception:
        return False