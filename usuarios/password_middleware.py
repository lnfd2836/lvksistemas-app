"""
Middleware para verificar se o usuário precisa trocar a senha
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class PasswordChangeMiddleware(MiddlewareMixin):
    """
    Middleware que verifica se o usuário precisa trocar a senha
    """
    
    def process_request(self, request):
        # Verifica se o usuário está logado
        if not request.user.is_authenticated:
            return None
            
        # URLs que não precisam de verificação de senha
        exempt_urls = [
            '/login/',
            '/logout/',
            '/admin/',
            '/static/',
            '/media/',
            '/alterar-senha/',
            '/usuarios/alterar-senha/',
            '/usuarios/alterar-senha-normal/',
            '/api/',
        ]
        
        # Verifica se a URL atual está na lista de exceções
        current_path = request.path
        if any(current_path.startswith(url) for url in exempt_urls):
            return None
            
        # Verifica se o usuário tem perfil e precisa trocar a senha
        try:
            if hasattr(request.user, 'perfil') and request.user.perfil and hasattr(request.user.perfil, 'deve_trocar_senha') and request.user.perfil.deve_trocar_senha:
                # Redireciona para a página de troca de senha
                if current_path != '/alterar-senha/' and not current_path.startswith('/usuarios/alterar-senha'):
                    messages.warning(
                        request, 
                        'Você deve alterar sua senha antes de continuar usando o sistema.'
                    )
                    return redirect('alterar_senha_obrigatoria')
        except Exception as e:
            logger.error(f"Erro no middleware de troca de senha: {e}")
            # Se houver erro, não bloqueia o acesso
                
        return None
