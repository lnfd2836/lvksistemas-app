"""
Middleware para forçar troca obrigatória de senha
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class MandatoryPasswordChangeMiddleware:
    """
    Middleware que intercepta requests e força usuários com senhas provisórias
    a alterarem suas senhas antes de acessar outras páginas do sistema.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que são isentas da verificação de troca de senha
        self.exempt_urls = [
            '/login/',
            '/logout/',
            '/usuarios/change-mandatory-password/',
            '/usuarios/password-change-success/',
            '/usuarios/api/check-password-requirement/',
            '/usuarios/api/password-strength/',
            '/static/',
            '/media/',
            '/admin/logout/',
            '/favicon.ico',
            '/webhook/',  # Todos os webhooks
            '/api/',  # Todas as APIs
            '/asaas-webhook',  # Webhooks do Asaas
            '/financeiro/asaas/webhook/',  # Webhook do Asaas não precisa de autenticação
            # URLs de reset de senha
            '/usuarios/password-reset/',
            '/usuarios/password-reset/done/',
            '/usuarios/reset/',
            # URLs públicas do CRM
            '/crm/orcamento/',
            '/crm/proposta/',
            '/crm/contrato/',
            '/crm/email/',
        ]
        
        # Prefixos de URLs que devem ser isentos
        self.exempt_prefixes = [
            '/static/',
            '/media/',
            '/webhook/',  # Todos os webhooks
            '/api/',  # Todas as APIs
            '/asaas-webhook',  # Webhooks do Asaas
            '/usuarios/reset/',  # Para URLs de reset com tokens
            '/crm/orcamento/',  # URLs públicas do CRM
            '/crm/proposta/',   # URLs públicas do CRM
            '/crm/contrato/',   # URLs públicas do CRM
            '/crm/email/',      # URLs de tracking do CRM
        ]
    
    def __call__(self, request):
        # Processa a request
        response = self.process_request(request)
        if response:
            return response
            
        # Continua com o processamento normal
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        """
        Processa a request e verifica se o usuário precisa trocar a senha
        """
        try:
            # Skip para usuários não autenticados
            if not request.user.is_authenticated:
                return None
            
            # Skip para URLs isentas
            if self.is_exempt_url(request.path):
                return None
            
            # Skip para superusuários acessando admin (opcional)
            if request.path.startswith('/admin/') and request.user.is_superuser:
                return None
            
            # Verifica se o usuário precisa trocar a senha
            if self.user_needs_password_change(request.user):
                # Log da ação
                logger.info(f'Redirecionando usuário {request.user.username} para troca obrigatória de senha')
                
                # Adiciona mensagem informativa (apenas uma vez por sessão)
                if not request.session.get('password_change_message_shown', False):
                    try:
                        messages.warning(
                            request, 
                            'Por segurança, você deve alterar sua senha provisória antes de continuar.'
                        )
                        request.session['password_change_message_shown'] = True
                    except Exception as msg_error:
                        logger.warning(f'Erro ao adicionar mensagem: {msg_error}')
                        request.session['password_change_message_shown'] = True
                
                # Redireciona para página de troca de senha
                return redirect('change_mandatory_password')
            
            # Remove a flag da mensagem se o usuário não precisa mais trocar senha
            if request.session.get('password_change_message_shown', False):
                del request.session['password_change_message_shown']
            
            return None
            
        except Exception as e:
            # Log do erro mas não bloqueia o processamento
            logger.error(f'Erro no middleware de troca de senha para {request.path}: {e}')
            return None
    
    def is_exempt_url(self, path):
        """
        Verifica se a URL está isenta da verificação de troca de senha
        """
        # Verifica URLs exatas
        if path in self.exempt_urls:
            return True
        
        # Verifica prefixos
        for prefix in self.exempt_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
    
    def user_needs_password_change(self, user):
        """
        Verifica se o usuário precisa trocar a senha
        """
        try:
            # Verifica se o usuário tem perfil
            if not hasattr(user, 'perfil'):
                return False
            
            try:
                perfil = user.perfil
                
                # Verifica se está marcado para troca obrigatória
                if perfil.requires_password_change:
                    return True
                
                # Verifica campo legado também (compatibilidade)
                if hasattr(perfil, 'deve_trocar_senha') and perfil.deve_trocar_senha:
                    return True
                
                return False
                
            except Exception as e:
                # Se houver qualquer erro (incluindo tabela não existir), não força troca de senha
                logger.warning(f'Erro ao verificar perfil do usuário {user.username}: {e}')
                return False
            
        except Exception as e:
            # Log do erro mas não bloqueia o usuário
            logger.error(f'Erro ao verificar necessidade de troca de senha para {user.username}: {e}')
            return False
    
    def process_exception(self, request, exception):
        """
        Processa exceções que podem ocorrer durante a verificação
        """
        # Log da exceção com mais detalhes
        logger.error(f'Exceção no middleware de troca de senha: {exception}')
        logger.error(f'Path: {request.path}, User: {request.user if hasattr(request, "user") else "N/A"}')
        
        # Não bloqueia o processamento normal
        return None