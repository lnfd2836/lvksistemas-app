from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class ForcarAlteracaoSenhaMiddleware:
    """Middleware para forçar alteração de senha no primeiro acesso"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs que não precisam de verificação
        excluded_paths = [
            '/login/',
            '/logout/',
            '/avaliacao-qualidade/alterar-senha/',
            '/avaliacao-qualidade/meu-perfil/',
            '/static/',
            '/media/',
            '/admin/',
        ]
        
        # Verificar se a URL atual está nas exceções
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)
        
        # Verificar se o usuário está autenticado e tem perfil FATESA
        if (request.user.is_authenticated and 
            hasattr(request.user, 'perfil_fatesa') and
            request.path.startswith('/avaliacao-qualidade/')):
            
            perfil = request.user.perfil_fatesa
            
            # Se deve alterar senha, redirecionar
            if perfil.deve_alterar_senha:
                messages.warning(
                    request, 
                    'Por segurança, você deve alterar sua senha provisória antes de continuar.'
                )
                return redirect('avaliacao_qualidade:alterar_minha_senha')
        
        return self.get_response(request)