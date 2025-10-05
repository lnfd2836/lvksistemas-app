from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def simple_login(request):
    """View de login simples"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Cria ou atualiza a sessão ativa
            try:
                from usuarios.models import SessaoAtiva
                # Remove sessões antigas do usuário
                SessaoAtiva.objects.filter(user=user).update(ativa=False)
                
                # Cria nova sessão ativa
                SessaoAtiva.objects.create(
                    user=user,
                    session_key=request.session.session_key,
                    ativa=True
                )
            except Exception as e:
                # Se houver erro na criação da sessão, continua normalmente
                pass
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'auth/login.html')


