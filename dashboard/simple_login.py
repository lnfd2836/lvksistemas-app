from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def simple_login(request):
    """View de login simples"""
    # Debug: verificar se o usuário está autenticado
    if request.user.is_authenticated:
        print(f"DEBUG: Usuário autenticado: {request.user.username}")
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'auth/login.html')


