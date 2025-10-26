from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from ..models import Loja


class LojaMiddleware:
    """Middleware para controle de acesso por loja"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs que não precisam de verificação de loja
        excluded_paths = [
            '/',  # Página inicial - deixar o smart_redirect lidar com isso
            '/admin/',
            '/login/',
            '/logout/',
            '/dashboard/',
            '/dashboard/super-admin/',
            '/dashboard/loja/',
            '/dashboard/loja/dashboard/',
            '/lojas/criar/',
            '/loja/login/',  # Adiciona login específico da loja
            '/financeiro/asaas/webhook/',  # Webhook do Asaas não precisa de autenticação
            '/avaliacao-qualidade/',  # Sistema FATESA de avaliação de qualidade
            '/static/',
            '/media/',
        ]
        
        # Verifica se a URL atual está nas exceções
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)
        
        # Redirecionamento especial para /lojas/
        if request.path == '/lojas/' and request.user.is_authenticated:
            if not request.user.is_superuser:
                # Usuário administrador de loja - redireciona para dashboard da loja
                try:
                    loja = request.user.loja_admin
                    request.loja_atual = loja
                    return redirect('dashboard_loja')
                except:
                    messages.error(request, 'Você não tem uma loja associada.')
                    return redirect('root_redirect')
        
        # Se o usuário não está autenticado, redireciona para login
        if not request.user.is_authenticated:
            # Não redireciona se está tentando fazer login ou se é webhook do Asaas
            if request.path == '/loja/login/' or '/asaas/webhook' in request.path:
                return self.get_response(request)
            return redirect('root_redirect')
        
        # Se é super usuário, permite acesso a tudo
        if request.user.is_superuser:
            return self.get_response(request)
        
        # Verifica se o usuário tem uma loja associada
        try:
            loja = request.user.loja_admin
            request.loja_atual = loja
        except Loja.DoesNotExist:
            # Se não tem loja associada e não é super usuário, redireciona
            messages.error(request, 'Você não tem permissão para acessar esta área.')
            return redirect('root_redirect')
        
        return self.get_response(request)


__all__ = ['LojaMiddleware']

