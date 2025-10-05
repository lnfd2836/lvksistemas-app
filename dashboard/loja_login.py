from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from lojas.models import Loja
from usuarios.models import LogAcesso, SessaoAtiva
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


def loja_login(request):
    """Página de login específica para administradores de loja - refatorada para usar AuthenticationService"""
    
    # Se já está autenticado, verificar se pode acessar dashboard de loja
    if request.user.is_authenticated:
        try:
            if AuthenticationService.can_access_store_dashboard(request.user):
                dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
                logger.info(f"Usuário {request.user.username} já autenticado, redirecionando para {dashboard_url}")
                return redirect(dashboard_url)
            else:
                # Se não pode acessar loja, permite visualizar página de login
                # para que super usuários possam testar credenciais de loja
                logger.info(f"Usuário {request.user.username} autenticado mas sem acesso à loja, mostrando página de login")
                pass
        except Exception as e:
            logger.error(f"Erro ao verificar acesso à loja para usuário {request.user.username}: {str(e)}")
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'auth/loja_login_clean.html')
        
        try:
            # Tenta autenticar com username primeiro
            user = authenticate(request, username=username, password=password)
            
            # Se falhar, tenta com email
            if user is None and '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                    logger.debug(f"Tentativa de login da loja com email {username} para usuário {user_obj.username}")
                except User.DoesNotExist:
                    logger.debug(f"Email {username} não encontrado no sistema")
                    pass
            
            if user is not None:
                if not user.is_active:
                    logger.warning(f"Tentativa de login da loja com usuário inativo: {user.username}")
                    messages.error(request, 'Esta conta está desativada.')
                    return render(request, 'auth/loja_login_clean.html')
                
                login(request, user)
                logger.info(f"Login da loja bem-sucedido para usuário {user.username}")
                
                # Verificar se o usuário pode acessar dashboard de loja usando AuthenticationService
                try:
                    if AuthenticationService.can_access_store_dashboard(user):
                        user_store = AuthenticationService.get_user_store(user)
                        
                        # Criar/atualizar sessão ativa
                        try:
                            # Remove sessões antigas do usuário
                            SessaoAtiva.objects.filter(user=user).update(ativa=False)
                            
                            # Cria nova sessão ativa
                            SessaoAtiva.objects.create(
                                user=user,
                                session_key=request.session.session_key or 'no-session-key',
                                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                                ativa=True,
                                is_super_admin=user.is_superuser
                            )
                            
                            # Registra o acesso
                            LogAcesso.objects.create(
                                user=user,
                                acao='LOGIN_LOJA',
                                ip_address=request.META.get('REMOTE_ADDR'),
                                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                                sucesso=True
                            )
                            
                        except Exception as e:
                            logger.error(f"Erro ao criar sessão da loja para usuário {user.username}: {str(e)}")
                            # Continua normalmente mesmo se houver erro na sessão
                        
                        # Mensagem de boas-vindas
                        if user_store:
                            messages.success(request, f'Bem-vindo ao dashboard da {user_store.nome}!')
                        elif user.is_superuser:
                            messages.success(request, 'Bem-vindo! Acesso de Super Administrador ao sistema de lojas.')
                        else:
                            messages.success(request, 'Bem-vindo ao dashboard da loja!')
                        
                        # Redirecionar para dashboard apropriado
                        dashboard_url = AuthenticationService.determine_user_dashboard(user)
                        return redirect(dashboard_url)
                        
                    else:
                        # Usuário não tem acesso à loja
                        if user.is_superuser:
                            logger.info(f"Super usuário {user.username} logado via loja_login, redirecionando para dashboard principal")
                            messages.info(request, 'Login realizado como Super Administrador. Redirecionando para dashboard principal.')
                            return redirect('dashboard:principal')
                        else:
                            logger.warning(f"Usuário {user.username} tentou login da loja mas não tem loja associada")
                            messages.error(request, 'Este usuário não possui uma loja associada.')
                            # Fazer logout do usuário já que não pode acessar
                            from django.contrib.auth import logout
                            logout(request)
                            return render(request, 'auth/loja_login_clean.html')
                            
                except Exception as e:
                    logger.error(f"Erro ao verificar acesso à loja após login para usuário {user.username}: {str(e)}")
                    messages.error(request, 'Erro interno ao verificar permissões. Tente novamente.')
                    return render(request, 'auth/loja_login_clean.html')
                    
            else:
                logger.warning(f"Tentativa de login da loja falhada para username/email: {username}")
                messages.error(request, 'Usuário ou senha incorretos.')
                
        except Exception as e:
            logger.error(f"Erro durante processo de login da loja: {str(e)}")
            messages.error(request, 'Erro interno durante o login. Tente novamente.')
    
    return render(request, 'auth/loja_login_clean.html')


@login_required
def loja_logout(request):
    """Logout específico para administradores de loja - refatorado para usar AuthenticationService"""
    
    try:
        user_store = AuthenticationService.get_user_store(request.user)
        user_type = AuthenticationService.get_user_type(request.user)
        
        # Registra o logout
        try:
            LogAcesso.objects.create(
                user=request.user,
                acao='LOGOUT_LOJA',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                sucesso=True
            )
            
            # Invalidar sessões ativas
            SessaoAtiva.objects.filter(user=request.user, ativa=True).update(ativa=False)
            
        except Exception as e:
            logger.error(f"Erro ao registrar logout da loja para usuário {request.user.username}: {str(e)}")
        
        # Mensagem de logout personalizada
        if user_store:
            messages.info(request, f'Logout realizado com sucesso da {user_store.nome}.')
        elif user_type == 'super_admin':
            messages.info(request, 'Logout realizado com sucesso do sistema de lojas.')
        else:
            messages.info(request, 'Logout realizado com sucesso.')
        
        logger.info(f"Logout da loja realizado para usuário {request.user.username}")
        
    except Exception as e:
        logger.error(f"Erro durante logout da loja para usuário {request.user.username}: {str(e)}")
        messages.info(request, 'Logout realizado.')
    
    from django.contrib.auth import logout
    logout(request)
    return redirect('loja_login')
