from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from lojas.models import Loja
from usuarios.models import LogAcesso


def loja_login(request):
    """Página de login específica para administradores de loja"""
    
    if request.user.is_authenticated:
        # Se já está logado, verifica se é administrador de loja
        try:
            loja = request.user.loja_admin
            return redirect('dashboard_loja')
        except:
            # Se não tem loja associada, permite visualizar a página de login
            # para que super usuários possam testar credenciais de loja
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Tenta autenticar com username primeiro
        user = authenticate(request, username=username, password=password)
        
        # Se falhar, tenta com email
        if user is None and '@' in username:
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            
            # Verifica se o usuário tem uma loja associada
            try:
                loja = user.loja_admin
                
                # Registra o acesso
                try:
                    LogAcesso.objects.create(
                        user=user,
                        acao='LOGIN_LOJA',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        sucesso=True
                    )
                except:
                    pass
                
                messages.success(request, f'Bem-vindo ao dashboard da {loja.nome}!')
                return redirect('dashboard_loja')
                
            except Loja.DoesNotExist:
                # Se é super usuário, redireciona para dashboard principal
                if user.is_superuser:
                    messages.info(request, 'Login realizado como super usuário. Use o dashboard principal para gerenciar lojas.')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Este usuário não possui uma loja associada.')
                    return redirect('loja_login_direct')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'auth/loja_login_clean.html')


@login_required
def loja_logout(request):
    """Logout específico para administradores de loja"""
    try:
        loja = request.user.loja_admin
        
        # Registra o logout
        try:
            LogAcesso.objects.create(
                user=request.user,
                acao='LOGOUT_LOJA',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                sucesso=True
            )
        except:
            pass
        
        messages.info(request, f'Logout realizado com sucesso da {loja.nome}.')
        
    except:
        pass
    
    from django.contrib.auth import logout
    logout(request)
    return redirect('loja_login')
