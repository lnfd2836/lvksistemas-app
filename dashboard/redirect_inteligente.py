"""
Sistema de redirecionamento inteligente para simplificar logins
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


def redirect_to_store_login(request):
    """
    Redireciona inteligentemente para login personalizado baseado no contexto
    """
    
    # Se já está autenticado, vai para dashboard apropriado
    if request.user.is_authenticated:
        try:
            dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
            logger.info(f"Usuário {request.user.username} já autenticado, redirecionando para {dashboard_url}")
            return redirect(dashboard_url)
        except Exception as e:
            logger.error(f"Erro ao determinar dashboard para usuário {request.user.username}: {str(e)}")
            return redirect('dashboard:principal')
    
    # Se é acesso ao admin, redirecionar para Django admin
    if request.path.startswith('/admin/') or 'admin' in request.GET:
        return redirect('/admin/login/')
    
    # Buscar lojas ativas com login personalizado
    try:
        lojas_ativas = []
        for loja in Loja.objects.filter(status='ativa'):
            try:
                login_config = loja.login_personalizado
                if login_config.ativo:
                    lojas_ativas.append({
                        'loja': loja,
                        'login_config': login_config,
                        'login_url': login_config.get_login_url(),
                    })
            except LoginPersonalizado.DoesNotExist:
                # Loja sem login personalizado, pular
                continue
        
        # Se só tem uma loja ativa, redirecionar direto
        if len(lojas_ativas) == 1:
            loja_info = lojas_ativas[0]
            logger.info(f"Apenas uma loja ativa, redirecionando direto para: {loja_info['loja'].nome}")
            return redirect(loja_info['login_url'])
        
        # Se tem múltiplas lojas, mostrar seleção
        context = {
            'lojas_ativas': lojas_ativas,
            'total_lojas': len(lojas_ativas),
        }
        
        return render(request, 'auth/selecionar_loja.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao buscar lojas para seleção: {str(e)}")
        messages.error(request, 'Erro interno. Tente novamente.')
        
        # Fallback: mostrar página básica
        return render(request, 'auth/erro_sistema.html', {
            'erro': 'Não foi possível carregar as lojas disponíveis.'
        })


def login_universal(request):
    """
    Login universal que tenta identificar automaticamente a loja
    """
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect_to_store_login(request)
        
        try:
            # Tentar autenticar
            user = authenticate(request, username=username, password=password)
            
            # Se falhar, tentar com email
            if user is None and '@' in username:
                try:
                    from django.contrib.auth.models import User
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None and user.is_active:
                # Fazer login
                login(request, user)
                
                # Determinar dashboard apropriado
                dashboard_url = AuthenticationService.determine_user_dashboard(user)
                
                # Se é usuário de loja, redirecionar para dashboard da loja
                if AuthenticationService.can_access_store_dashboard(user):
                    user_store = AuthenticationService.get_user_store(user)
                    if user_store:
                        messages.success(request, f'Bem-vindo(a) à {user_store.nome}!')
                        return redirect('dashboard:loja_especifica', loja_id=user_store.id)
                
                # Outros casos
                return redirect(dashboard_url)
                
            else:
                messages.error(request, 'Credenciais inválidas.')
                
        except Exception as e:
            logger.error(f"Erro no login universal: {str(e)}")
            messages.error(request, 'Erro interno durante login.')
    
    # Mostrar seleção de loja
    return redirect_to_store_login(request)