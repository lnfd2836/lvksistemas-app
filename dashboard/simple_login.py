from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


def simple_login(request):
    """View de login simples - refatorada para usar AuthenticationService"""
    
    # Se já está autenticado, redirecionar para dashboard apropriado
    if request.user.is_authenticated:
        try:
            dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
            logger.info(f"Usuário {request.user.username} já autenticado, redirecionando para {dashboard_url}")
            return redirect(dashboard_url)
        except Exception as e:
            logger.error(f"Erro ao determinar dashboard para usuário autenticado {request.user.username}: {str(e)}")
            # Fallback para dashboard padrão
            return redirect('dashboard:principal')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'auth/login.html')
        
        try:
            # Tenta autenticar com username primeiro
            user = authenticate(request, username=username, password=password)
            
            # Se falhar, tenta com email
            if user is None and '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                    logger.debug(f"Tentativa de login com email {username} para usuário {user_obj.username}")
                except User.DoesNotExist:
                    logger.debug(f"Email {username} não encontrado no sistema")
                    pass
            
            if user is not None:
                if not user.is_active:
                    logger.warning(f"Tentativa de login com usuário inativo: {user.username}")
                    messages.error(request, 'Esta conta está desativada.')
                    return render(request, 'auth/login.html')
                
                login(request, user)
                logger.info(f"Login bem-sucedido para usuário {user.username}")
                
                # Cria ou atualiza a sessão ativa
                try:
                    from usuarios.models import SessaoAtiva, LogAcesso
                    
                    # Remove sessões antigas do usuário
                    SessaoAtiva.objects.filter(user=user).update(ativa=False)
                    
                    # Remove sessões com a mesma session_key para evitar duplicatas
                    session_key = request.session.session_key or f'no-session-{user.id}'
                    SessaoAtiva.objects.filter(session_key=session_key).delete()
                    
                    # Cria nova sessão ativa
                    SessaoAtiva.objects.create(
                        user=user,
                        session_key=session_key,
                        ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        ativa=True,
                        is_super_admin=user.is_superuser
                    )
                    
                    # Registra o login
                    LogAcesso.objects.create(
                        user=user,
                        acao='LOGIN',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        sucesso=True
                    )
                    
                except Exception as e:
                    logger.error(f"Erro ao criar sessão para usuário {user.username}: {str(e)}")
                    # Continua normalmente mesmo se houver erro na sessão
                
                # Determinar dashboard apropriado usando AuthenticationService
                try:
                    dashboard_url = AuthenticationService.determine_user_dashboard(user)
                    logger.info(f"Redirecionando usuário {user.username} para {dashboard_url}")
                    
                    # Adicionar mensagem de boas-vindas baseada no tipo de usuário
                    user_type = AuthenticationService.get_user_type(user)
                    if user_type == 'super_admin':
                        messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}! Acesso de Super Administrador.')
                    elif user_type == 'store_admin':
                        user_store = AuthenticationService.get_user_store(user)
                        store_name = user_store.nome if user_store else 'sua loja'
                        messages.success(request, f'Bem-vindo ao dashboard da {store_name}!')
                    else:
                        messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                    
                    return redirect(dashboard_url)
                    
                except Exception as e:
                    logger.error(f"Erro ao determinar dashboard após login para usuário {user.username}: {str(e)}")
                    # Fallback para dashboard padrão
                    messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:principal')
                    
            else:
                logger.warning(f"Tentativa de login falhada para username/email: {username}")
                messages.error(request, 'Usuário ou senha incorretos.')
                
        except Exception as e:
            logger.error(f"Erro durante processo de login: {str(e)}")
            messages.error(request, 'Erro interno durante o login. Tente novamente.')
    
    return render(request, 'auth/login.html')


