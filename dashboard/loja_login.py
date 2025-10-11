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
            logger.info(f"Tentativa de login da loja - Username/Email: {username}")
            
            # Tenta autenticar com username primeiro
            user = authenticate(request, username=username, password=password)
            logger.debug(f"Autenticação com username '{username}': {'Sucesso' if user else 'Falhou'}")
            
            # Se falhar, tenta com email
            if user is None and '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    logger.debug(f"Usuário encontrado por email {username}: {user_obj.username}")
                    user = authenticate(request, username=user_obj.username, password=password)
                    logger.debug(f"Autenticação com email {username} (username: {user_obj.username}): {'Sucesso' if user else 'Falhou'}")
                    
                    # Verificar se é administrador de loja
                    try:
                        loja = Loja.objects.get(admin_user=user_obj)
                        logger.info(f"Usuário {user_obj.username} é administrador da loja: {loja.nome}")
                    except Loja.DoesNotExist:
                        logger.warning(f"Usuário {user_obj.username} não é administrador de nenhuma loja")
                        
                except User.DoesNotExist:
                    logger.warning(f"Email {username} não encontrado no sistema")
                    pass
                except Exception as e:
                    logger.error(f"Erro ao buscar usuário por email {username}: {str(e)}")
                    pass
            
            if user is not None:
                logger.info(f"Autenticação bem-sucedida para usuário: {user.username}")
                
                if not user.is_active:
                    logger.warning(f"Tentativa de login da loja com usuário inativo: {user.username}")
                    messages.error(request, 'Esta conta está desativada. Entre em contato com o suporte.')
                    return render(request, 'auth/loja_login_clean.html')
                
                # Verificar se é uma senha provisória
                try:
                    loja = Loja.objects.get(admin_user=user)
                    if loja.senha_provisoria and password == loja.senha_provisoria:
                        logger.info(f"Login com senha provisória detectado para loja: {loja.nome}")
                        # Marcar que precisa trocar a senha
                        from usuarios.models import PerfilUsuario
                        profile, created = PerfilUsuario.objects.get_or_create(
                            user=user,
                            defaults={'requires_password_change': True}
                        )
                        if not created:
                            profile.requires_password_change = True
                            profile.save()
                except Loja.DoesNotExist:
                    logger.debug(f"Usuário {user.username} não é administrador de loja")
                    pass
                except Exception as e:
                    logger.error(f"Erro ao verificar senha provisória: {str(e)}")
                    pass
                
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
                        
                        # Redirecionar para dashboard apropriado
                        dashboard_url = AuthenticationService.determine_user_dashboard(user)
                        return redirect(dashboard_url)
                        
                    else:
                        # Usuário não tem acesso à loja
                        if user.is_superuser:
                            logger.info(f"Super usuário {user.username} logado via loja_login, redirecionando para dashboard principal")
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
                
                # Verificar se o email existe no sistema
                if '@' in username:
                    try:
                        user_obj = User.objects.get(email=username)
                        logger.info(f"Email {username} existe no sistema (usuário: {user_obj.username}), mas senha incorreta")
                        messages.error(request, 'Senha incorreta. Verifique sua senha provisória ou entre em contato com o suporte.')
                    except User.DoesNotExist:
                        logger.info(f"Email {username} não encontrado no sistema")
                        messages.error(request, 'Email não encontrado no sistema. Verifique se o email está correto.')
                else:
                    messages.error(request, 'Usuário ou senha incorretos. Use o email da loja como usuário.')
                
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
