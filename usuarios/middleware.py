from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse
from .models import SessaoAtiva


class SessaoUnicaMiddleware:
    """Middleware para garantir que cada usuário tenha apenas uma sessão ativa (incluindo Super Admins)"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs que não precisam de verificação de sessão
        excluded_paths = [
            '/admin/',
            '/login/',
            '/logout/',
            '/loja/login/',
            '/static/',
            '/media/',
        ]
        
        # Verifica se a URL atual está nas exceções
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)
        
        # Se o usuário não está autenticado, continua normalmente
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Verifica se a sessão atual é válida
        session_key = request.session.session_key
        if session_key:
            try:
                sessao_ativa = SessaoAtiva.objects.get(
                    user=request.user,
                    session_key=session_key,
                    ativa=True
                )
                # Atualiza a última atividade
                sessao_ativa.save()  # Isso atualiza o campo ultima_atividade
                
            except SessaoAtiva.DoesNotExist:
                # Sessão não é mais válida - faz logout para TODOS os usuários
                messages.warning(
                    request, 
                    'Sua sessão foi invalidada porque você fez login em outro local. '
                    'Por favor, faça login novamente.'
                )
                logout(request)
                return redirect('login')
        
        # Limpa sessões expiradas periodicamente
        SessaoAtiva.limpar_sessoes_expiradas()
        
        return self.get_response(request)
