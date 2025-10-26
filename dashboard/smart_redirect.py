from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


def smart_login_redirect(request):
    """
    Redirecionamento inteligente baseado no contexto do usuário
    
    Lógica:
    1. Se já autenticado → redireciona para dashboard apropriado
    2. Se tem apenas uma loja ativa → redireciona para login da loja
    3. Se tem múltiplas lojas → mostra seleção de loja
    4. Se não tem lojas → redireciona para admin login
    """
    
    # Se já está autenticado, redirecionar para dashboard apropriado
    if request.user.is_authenticated:
        try:
            dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
            logger.info(f"Usuário {request.user.username} já autenticado, redirecionando para {dashboard_url}")
            return redirect(dashboard_url)
        except Exception as e:
            logger.error(f"Erro ao determinar dashboard para usuário autenticado: {str(e)}")
            return redirect('dashboard:principal')
    
    # Buscar lojas ativas com login personalizado
    try:
        lojas_ativas = Loja.objects.filter(
            status='ativa'
        ).select_related('login_personalizado').order_by('nome')
        
        # Filtrar apenas lojas com login personalizado ativo
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
                # Criar configuração padrão se não existir
                try:
                    login_config = LoginPersonalizado.objects.create(
                        loja=loja,
                        titulo=f"Login - {loja.nome}",
                        subtitulo=f"Acesse sua conta na {loja.nome}",
                        mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                        tema='padrao',
                        ativo=True
                    )
                    lojas_com_login.append({
                        'loja': loja,
                        'login_config': login_config,
                        'login_url': login_config.get_login_url()
                    })
                    logger.info(f"Configuração de login padrão criada para loja {loja.nome}")
                except Exception as e:
                    logger.error(f"Erro ao criar login padrão para loja {loja.nome}: {str(e)}")
        
        # Decidir redirecionamento baseado no número de lojas
        if len(lojas_com_login) == 0:
            # Nenhuma loja ativa → redirecionar para admin
            logger.info("Nenhuma loja ativa encontrada, redirecionando para admin")
            messages.info(request, 'Nenhuma loja disponível. Acesse como administrador do sistema.')
            return redirect('/admin/login/')
            
        elif len(lojas_com_login) == 1:
            # Apenas uma loja → redirecionar diretamente
            loja_info = lojas_com_login[0]
            logger.info(f"Uma loja encontrada, redirecionando para {loja_info['loja'].nome}")
            return redirect(loja_info['login_url'])
            
        else:
            # Múltiplas lojas → mostrar seleção
            logger.info(f"{len(lojas_com_login)} lojas encontradas, mostrando seleção")
            return mostrar_selecao_loja(request, lojas_com_login)
            
    except Exception as e:
        logger.error(f"Erro no redirecionamento inteligente: {str(e)}")
        messages.error(request, 'Erro interno. Tente novamente.')
        return redirect('/admin/login/')


def mostrar_selecao_loja(request, lojas_com_login):
    """Mostra página de seleção de loja"""
    
    context = {
        'lojas': lojas_com_login,
        'total_lojas': len(lojas_com_login),
        'titulo_pagina': 'Selecione sua Loja',
        'subtitulo_pagina': 'Escolha a loja para fazer login'
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