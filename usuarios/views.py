"""
Views para o app usuarios
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging
import re

from .forms import MandatoryPasswordChangeForm, UserPasswordResetForm

logger = logging.getLogger(__name__)


@login_required
def change_mandatory_password(request):
    """
    View para troca obrigatória de senha
    """
    # Verifica se o usuário realmente precisa trocar a senha
    try:
        perfil = request.user.perfil
        if not perfil.requires_password_change:
            messages.info(request, 'Você não precisa trocar sua senha no momento.')
            return redirect('dashboard:principal')
    except:
        # Se não tem perfil, não precisa trocar senha
        messages.info(request, 'Você não precisa trocar sua senha no momento.')
        return redirect('dashboard:principal')
    
    if request.method == 'POST':
        form = MandatoryPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                # Salva a nova senha
                user = form.save()
                
                # Atualiza a sessão para não deslogar o usuário
                update_session_auth_hash(request, user)
                
                # Log da ação
                logger.info(f'Usuário {user.username} alterou senha obrigatória com sucesso')
                
                # Mensagem de sucesso
                messages.success(
                    request, 
                    'Senha alterada com sucesso! Agora você pode usar o sistema normalmente.'
                )
                
                # Redireciona para o dashboard apropriado
                if user.is_superuser:
                    return redirect('dashboard:principal')
                else:
                    # Para usuários de loja, redireciona para dashboard da loja
                    return redirect('dashboard:principal')
                    
            except Exception as e:
                logger.error(f'Erro ao alterar senha obrigatória para {request.user.username}: {e}')
                messages.error(request, 'Erro interno. Tente novamente.')
        else:
            # Form tem erros - eles serão exibidos no template
            pass
    else:
        form = MandatoryPasswordChangeForm(request.user)
    
    # Informações do usuário para o template
    context = {
        'form': form,
        'user': request.user,
        'is_mandatory': True,
        'user_type': 'Super Administrador' if request.user.is_superuser else 'Administrador de Loja',
        'provisional_password_date': None
    }
    
    # Adiciona data da senha provisória se disponível
    try:
        perfil = request.user.perfil
        if perfil.provisional_password_created:
            context['provisional_password_date'] = perfil.provisional_password_created
    except:
        pass
    
    return render(request, 'usuarios/change_mandatory_password.html', context)


@login_required
def password_change_success(request):
    """
    View para página de sucesso após troca de senha
    """
    return render(request, 'usuarios/password_change_success.html')


@require_http_methods(["GET"])
def check_password_requirement(request):
    """
    API endpoint para verificar se usuário precisa trocar senha
    Usado pelo middleware para verificações AJAX
    """
    if not request.user.is_authenticated:
        return JsonResponse({'requires_change': False})
    
    try:
        perfil = request.user.perfil
        requires_change = perfil.requires_password_change
        
        return JsonResponse({
            'requires_change': requires_change,
            'user_type': 'super_admin' if request.user.is_superuser else 'store_admin',
            'provisional_date': perfil.provisional_password_created.isoformat() if perfil.provisional_password_created else None
        })
    except:
        return JsonResponse({'requires_change': False})


def password_strength_check(request):
    """
    API endpoint para verificar força da senha em tempo real
    """
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        # Critérios de validação
        checks = {
            'length': len(password) >= 8,
            'has_letter': bool(re.search(r'[A-Za-z]', password)),
            'has_number': bool(re.search(r'\d', password)),
            'not_common': password.lower() not in [
                '12345678', 'password', 'senha123', '123456789', 'qwerty123'
            ]
        }
        
        # Calcula score de força
        score = sum(checks.values())
        strength_levels = ['Muito Fraca', 'Fraca', 'Regular', 'Boa', 'Forte']
        strength = strength_levels[min(score, 4)]
        
        return JsonResponse({
            'checks': checks,
            'score': score,
            'strength': strength,
            'is_valid': score >= 3  # Pelo menos 3 critérios atendidos
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)