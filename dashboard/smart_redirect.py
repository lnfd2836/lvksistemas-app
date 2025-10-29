from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import Http404
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


def smart_login_redirect(request):
    """
    Página principal do sistema - Login de Super Admin
    
    ARQUITETURA CORRETA:
    1. Se já autenticado → redireciona para dashboard apropriado
    2. Se não autenticado → MOSTRA formulário de login de super admin
    
    A página principal é EXCLUSIVAMENTE para super admins!
    Lojas têm seus próprios URLs personalizados.
    """
    
    # Se já está autenticado, redirecionar para dashboard apropriado
    if request.user.is_authenticated:
        try:
            dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
            logger.info(f"Usuário {request.user.username} já autenticado, redirecionando para {dashboard_url}")
            
            # PROTEÇÃO CONTRA LOOP: Se o dashboard_url é a página atual, não redirecionar
            if dashboard_url == request.path or dashboard_url == '/':
                logger.warning(f"Detectado possível loop de redirecionamento para {dashboard_url}, forçando logout")
                from django.contrib.auth import logout
                logout(request)
                messages.error(request, 'Sessão inválida detectada. Faça login novamente.')
                # Não redirecionar, mostrar formulário de login
            else:
                return redirect(dashboard_url)
        except Exception as e:
            logger.error(f"Erro ao determinar dashboard para usuário autenticado: {str(e)}")
            # Em caso de erro, fazer logout para evitar loops
            from django.contrib.auth import logout
            logout(request)
            messages.error(request, 'Erro na sessão. Faça login novamente.')
    
    # CORREÇÃO: Mostrar DIRETAMENTE o formulário de login de super admin
    # Não redirecionar, mas renderizar o template de login
    logger.info("Exibindo formulário de login de super admin na página principal")
    
    # Processar login se for POST
    if request.method == 'POST':
        return processar_login_super_admin(request)
    
    # Mostrar formulário de login de super admin
    context = {
        'titulo_pagina': 'Login Super Admin - LVK Sistemas',
        'subtitulo_pagina': 'Acesso exclusivo para administradores do sistema',
        'is_super_admin_login': True,
        'login_url': '/',
        'admin_area': True
    }
    
    return render(request, 'auth/super_admin_login.html', context)


def processar_login_super_admin(request):
    """Processa o login do super admin na página principal"""
    
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    
    if not username or not password:
        messages.error(request, 'Por favor, preencha todos os campos.')
        return render(request, 'auth/super_admin_login.html', {
            'titulo_pagina': 'Login Super Admin - LVK Sistemas',
            'subtitulo_pagina': 'Acesso exclusivo para administradores do sistema',
            'is_super_admin_login': True,
            'login_url': '/',
            'admin_area': True
        })
    
    try:
        # Tentar autenticar
        user = authenticate(request, username=username, password=password)
        
        # Se falhar, tentar com email
        if user is None and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
                logger.debug(f"Tentativa de login com email {username}")
            except User.DoesNotExist:
                logger.debug(f"Email {username} não encontrado")
                pass
        
        if user is not None:
            if not user.is_active:
                logger.warning(f"Usuário inativo tentou login: {user.username}")
                messages.error(request, 'Esta conta está desativada.')
                return render(request, 'auth/super_admin_login.html', {
                    'titulo_pagina': 'Login Super Admin - LVK Sistemas',
                    'subtitulo_pagina': 'Acesso exclusivo para administradores do sistema',
                    'is_super_admin_login': True,
                    'login_url': '/',
                    'admin_area': True
                })
            
            # VERIFICAR SE É SUPER ADMIN
            if not user.is_superuser:
                logger.warning(f"Usuário não-super-admin tentou login na página principal: {user.username}")
                messages.error(request, 'Esta área é exclusiva para super administradores. Use o login da sua loja.')
                return render(request, 'auth/super_admin_login.html', {
                    'titulo_pagina': 'Login Super Admin - LVK Sistemas',
                    'subtitulo_pagina': 'Acesso exclusivo para administradores do sistema',
                    'is_super_admin_login': True,
                    'login_url': '/',
                    'admin_area': True
                })
            
            # Fazer login
            login(request, user)
            logger.info(f"Login de super admin bem-sucedido: {user.username}")
            
            # Criar sessão ativa
            try:
                from usuarios.models import SessaoAtiva, LogAcesso
                
                # Remove sessões antigas
                SessaoAtiva.objects.filter(user=user).update(ativa=False)
                
                # Cria nova sessão
                session_key = request.session.session_key or f'super-admin-{user.id}'
                SessaoAtiva.objects.filter(session_key=session_key).delete()
                
                SessaoAtiva.objects.create(
                    user=user,
                    session_key=session_key,
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    ativa=True,
                    is_super_admin=True
                )
                
                # Log de acesso
                LogAcesso.objects.create(
                    user=user,
                    acao='LOGIN_SUPER_ADMIN',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    sucesso=True,
                    observacoes='Login via página principal'
                )
                
            except Exception as e:
                logger.error(f"Erro ao criar sessão para super admin {user.username}: {str(e)}")
            
            # Redirecionar para dashboard super admin
            messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
            return redirect('/dashboard/')
            
        else:
            logger.warning(f"Falha na autenticação de super admin: {username}")
            messages.error(request, 'Usuário ou senha incorretos.')
            
    except Exception as e:
        logger.error(f"Erro durante login de super admin: {str(e)}")
        messages.error(request, 'Erro interno durante o login. Tente novamente.')
    
    # Retornar formulário com erro
    return render(request, 'auth/super_admin_login.html', {
        'titulo_pagina': 'Login Super Admin - LVK Sistemas',
        'subtitulo_pagina': 'Acesso exclusivo para administradores do sistema',
        'is_super_admin_login': True,
        'login_url': '/',
        'admin_area': True
    })


def mostrar_selecao_loja(request, lojas_com_login=None):
    """
    Mostra página de seleção de loja (apenas quando explicitamente solicitada)
    Esta função agora é usada apenas para URLs específicas como /lojas/selecionar/
    """
    
    # Se não foram fornecidas lojas, buscar todas as ativas
    if lojas_com_login is None:
        try:
            lojas_ativas = Loja.objects.filter(status='ativa').select_related('login_personalizado').order_by('nome')
            lojas_com_login = []
            
            for loja in lojas_ativas:
                try:
                    login_config = loja.login_personalizado
                    if login_config.ativo:
                        lojas_com_login.append({
                            'loja': loja,
                            'login_config': login_config,
                            'login_url': login_config.get_login_url()
                        })
                except LoginPersonalizado.DoesNotExist:
                    continue
        except Exception as e:
            logger.error(f"Erro ao buscar lojas para seleção: {str(e)}")
            return redirect('/admin/login/')
    
    context = {
        'lojas': lojas_com_login,
        'total_lojas': len(lojas_com_login),
        'titulo_pagina': 'Selecione sua Loja',
        'subtitulo_pagina': 'Escolha a loja para fazer login',
        'mostrar_opcao_admin': True,  # Sempre mostrar opção de admin
        'admin_url': '/admin/login/'
    }
    
    return render(request, 'auth/selecao_loja.html', context)


def loja_por_codigo(request, codigo_loja=None):
    """
    Permite acesso direto à loja por código
    URL: /loja/<codigo>/
    """
    
    if not codigo_loja:
        return redirect('smart_login_redirect')
    
    try:
        # Buscar loja por código (pode ser ID, nome simplificado, etc.)
        loja = None
        
        # Tentar por ID primeiro
        try:
            loja = Loja.objects.get(id=codigo_loja, status='ativa')
        except (Loja.DoesNotExist, ValueError):
            pass
        
        # Tentar por nome simplificado
        if not loja:
            try:
                loja = Loja.objects.get(
                    nome__iexact=codigo_loja.replace('-', ' '),
                    status='ativa'
                )
            except Loja.DoesNotExist:
                pass
        
        # Tentar por slug/código personalizado se existir
        if not loja:
            try:
                login_config = LoginPersonalizado.objects.get(
                    url_personalizada=codigo_loja,
                    ativo=True
                )
                loja = login_config.loja
            except LoginPersonalizado.DoesNotExist:
                pass
        
        if not loja:
            logger.warning(f"Loja não encontrada para código: {codigo_loja}")
            messages.error(request, f'Loja "{codigo_loja}" não encontrada.')
            return redirect('root_redirect')
        
        # Verificar se tem login personalizado
        try:
            login_config = loja.loginpersonalizado
            if login_config.ativo:
                return redirect(login_config.get_login_url())
            else:
                messages.error(request, 'Login desta loja está temporariamente indisponível.')
                return redirect('root_redirect')
        except LoginPersonalizado.DoesNotExist:
            # Criar configuração padrão
            try:
                login_config = LoginPersonalizado.objects.create(
                    loja=loja,
                    titulo=f"Login - {loja.nome}",
                    subtitulo=f"Acesse sua conta na {loja.nome}",
                    mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                    tema='padrao',
                    ativo=True
                )
                return redirect(login_config.get_login_url())
            except Exception as e:
                logger.error(f"Erro ao criar login para loja {loja.nome}: {str(e)}")
                messages.error(request, 'Erro ao configurar login da loja.')
                return redirect('root_redirect')
                
    except Exception as e:
        logger.error(f"Erro ao buscar loja por código {codigo_loja}: {str(e)}")
        messages.error(request, 'Erro interno. Tente novamente.')
        return redirect('root_redirect')


def admin_redirect(request):
    """Redireciona para o admin do Django com mensagem explicativa"""
    
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('/admin/')
    
    messages.info(request, 'Esta área é exclusiva para administradores do sistema.')
    return redirect('/admin/login/')