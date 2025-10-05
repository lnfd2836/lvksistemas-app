"""
Views para troca de senha obrigatória
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


@login_required
def alterar_senha_obrigatoria(request):
    """
    View para troca de senha obrigatória no primeiro login
    """
    # Verifica se o usuário realmente precisa trocar a senha
    if not hasattr(request.user, 'perfil') or not request.user.perfil.deve_trocar_senha:
        return redirect('dashboard:principal')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            # Atualiza a senha
            user = form.save()
            update_session_auth_hash(request, user)
            
            # Marca que a senha foi alterada
            request.user.perfil.deve_trocar_senha = False
            request.user.perfil.senha_alterada_em = timezone.now()
            request.user.perfil.save()
            
            messages.success(
                request, 
                'Senha alterada com sucesso! Agora você pode usar o sistema normalmente.'
            )
            
            logger.info(f"Usuário {request.user.username} alterou a senha com sucesso")
            
            return redirect('dashboard:principal')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Alterar Senha Obrigatória',
        'subtitle': 'Por motivos de segurança, você deve alterar sua senha antes de continuar.',
        'is_obligatory': True,
    }
    
    return render(request, 'usuarios/alterar_senha_obrigatoria.html', context)


@login_required
def alterar_senha_normal(request):
    """
    View para troca de senha normal (não obrigatória)
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            # Atualiza a senha
            user = form.save()
            update_session_auth_hash(request, user)
            
            # Atualiza o perfil
            request.user.perfil.senha_alterada_em = timezone.now()
            request.user.perfil.save()
            
            messages.success(request, 'Senha alterada com sucesso!')
            
            logger.info(f"Usuário {request.user.username} alterou a senha voluntariamente")
            
            return redirect('dashboard:principal')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Alterar Senha',
        'subtitle': 'Altere sua senha para manter a segurança da sua conta.',
        'is_obligatory': False,
    }
    
    return render(request, 'usuarios/alterar_senha.html', context)
