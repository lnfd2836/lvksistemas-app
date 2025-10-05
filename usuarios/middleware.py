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
                # Verifica se existe alguma sessão ativa para o usuário
                try:
                    # Se não há sessão ativa registrada, cria uma nova
                    if not SessaoAtiva.objects.filter(user=request.user, ativa=True).exists():
                        SessaoAtiva.objects.create(
                            user=request.user,
                            session_key=session_key,
                            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                            user_agent=request.META.get('HTTP_USER_AGENT', ''),
                            ativa=True
                        )
                        return self.get_response(request)
                    else:
                        # Sessão não é mais válida - faz logout
                        messages.warning(
                            request, 
                            'Sua sessão foi invalidada porque você fez login em outro local. '
                            'Por favor, faça login novamente.'
                        )
                        logout(request)
                        return redirect('login')
                except Exception as e:
                    # Em caso de erro, permite continuar para evitar loops
                    return self.get_response(request)
        else:
            # Se não há session_key, tenta criar um
            if hasattr(request, 'session'):
                request.session.create()
        
        # Limpa sessões expiradas periodicamente
        try:
            SessaoAtiva.limpar_sessoes_expiradas()
        except:
            pass
        
        return self.get_response(request)
