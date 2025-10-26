"""
Views para o sistema de credenciais por email
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from typing import Dict, Any
import json
import logging

from .models import ExtendedUserProfile, EmailLog, PasswordRecoveryAttempt
from .email_credentials_service import EmailCredentialsService
from .password_generator import PasswordGenerator
from lojas.models import Loja

logger = logging.getLogger(__name__)


def is_super_admin(user):
    """Verifica se o usuário é super administrador"""
    return user.is_authenticated and user.is_superuser


def is_loja_admin(user):
    """Verifica se o usuário é administrador de loja"""
    if not user.is_authenticated:
        return False
    
    try:
        profile = ExtendedUserProfile.objects.get(user=user)
        return profile.user_type in ['super_admin', 'loja_admin']
    except ExtendedUserProfile.DoesNotExist:
        return user.is_superuser


@login_required
@user_passes_test(is_super_admin)
def dashboard_super_admin(request):
    """Dashboard principal para super administradores"""
    
    context = {
        'title': 'Dashboard - Credenciais',
        'stats': _get_dashboard_stats(),
        'recent_emails': _get_recent_emails(limit=10),
        'recent_users': _get_recent_users(limit=10),
        'lojas': Loja.objects.filter(status='ativa').count(),
    }
    
    return render(request, 'email_credentials/dashboard_super_admin.html', context)


@login_required
@user_passes_test(is_loja_admin)
def dashboard_loja_admin(request):
    """Dashboard para administradores de loja"""
    
    # Obter loja do usuário
    try:
        profile = ExtendedUserProfile.objects.get(user=request.user)
        loja = profile.associated_loja
        
        if not loja and not request.user.is_superuser:
            messages.error(request, 'Usuário não está associado a nenhuma loja.')
            return redirect('login')
            
    except ExtendedUserProfile.DoesNotExist:
        if request.user.is_superuser:
            return redirect('email_credentials:dashboard_super_admin')
        messages.error(request, 'Perfil de usuário não encontrado.')
        return redirect('login')
    
    context = {
        'title': f'Dashboard - {loja.nome if loja else "Admin"}',
        'loja': loja,
        'stats': _get_loja_stats(loja) if loja else _get_dashboard_stats(),
        'recent_emails': _get_recent_emails(loja=loja, limit=10),
        'recent_users': _get_recent_users(loja=loja, limit=10),
    }
    
    return render(request, 'email_credentials/dashboard_loja_admin.html', context)


@login_required
@user_passes_test(is_super_admin)
def listar_usuarios(request):
    """Lista todos os usuários do sistema"""
    
    # Filtros
    search = request.GET.get('search', '')
    user_type = request.GET.get('type', '')
    loja_id = request.GET.get('loja', '')
    
    # Query base
    users = User.objects.select_related('extended_profile').all()
    
    # Aplicar filtros
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if user_type:
        users = users.filter(extended_profile__user_type=user_type)
    
    if loja_id:
        users = users.filter(extended_profile__associated_loja_id=loja_id)
    
    # Paginação
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Usuários do Sistema',
        'page_obj': page_obj,
        'search': search,
        'user_type': user_type,
        'loja_id': loja_id,
        'lojas': Loja.objects.filter(status='ativa'),
        'user_types': ExtendedUserProfile.USER_TYPE_CHOICES,
    }
    
    return render(request, 'email_credentials/listar_usuarios.html', context)


@login_required
@user_passes_test(is_loja_admin)
def listar_usuarios_loja(request):
    """Lista usuários da loja do administrador"""
    
    # Obter loja do usuário
    try:
        profile = ExtendedUserProfile.objects.get(user=request.user)
        loja = profile.associated_loja
        
        if not loja and not request.user.is_superuser:
            messages.error(request, 'Usuário não está associado a nenhuma loja.')
            return redirect('login')
            
    except ExtendedUserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuário não encontrado.')
        return redirect('login')
    
    # Filtros
    search = request.GET.get('search', '')
    
    # Query base - usuários da loja
    users = User.objects.select_related('extended_profile').filter(
        extended_profile__associated_loja=loja
    )
    
    # Aplicar filtros
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': f'Usuários - {loja.nome}',
        'loja': loja,
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'email_credentials/listar_usuarios_loja.html', context)


@login_required
@user_passes_test(is_super_admin)
def criar_usuario(request):
    """Cria novo usuário com credenciais"""
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            user_type = request.POST.get('user_type', 'loja_user')
            loja_id = request.POST.get('loja_id')
            
            # Validações básicas
            if not all([username, email, first_name, last_name]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return render(request, 'email_credentials/criar_usuario.html', _get_create_user_context())
            
            # Obter loja se especificada
            loja = None
            if loja_id:
                try:
                    loja = Loja.objects.get(id=loja_id, status='ativa')
                except Loja.DoesNotExist:
                    messages.error(request, 'Loja selecionada não encontrada.')
                    return render(request, 'email_credentials/criar_usuario.html', _get_create_user_context())
            
            # Criar usuário usando o serviço
            service = EmailCredentialsService()
            result = service.create_user_credentials(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                loja=loja,
                created_by=request.user
            )
            
            if result['success']:
                messages.success(
                    request, 
                    f'Usuário {username} criado com sucesso! '
                    f'{"Email enviado." if result["email_sent"] else "Email não pôde ser enviado - verifique configurações."}'
                )
                return redirect('email_credentials:listar_usuarios')
            else:
                messages.error(request, f'Erro ao criar usuário: {result["message"]}')
                
        except Exception as e:
            logger.error(f'Erro ao criar usuário: {str(e)}')
            messages.error(request, 'Erro interno. Tente novamente.')
    
    context = _get_create_user_context()
    return render(request, 'email_credentials/criar_usuario.html', context)


@login_required
@user_passes_test(is_loja_admin)
def criar_usuario_loja(request):
    """Cria novo usuário para a loja do administrador"""
    
    # Obter loja do usuário
    try:
        profile = ExtendedUserProfile.objects.get(user=request.user)
        loja = profile.associated_loja
        
        if not loja and not request.user.is_superuser:
            messages.error(request, 'Usuário não está associado a nenhuma loja.')
            return redirect('login')
            
    except ExtendedUserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuário não encontrado.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            user_type = request.POST.get('user_type', 'loja_user')
            
            # Validações básicas
            if not all([username, email, first_name, last_name]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return render(request, 'email_credentials/criar_usuario_loja.html', {'loja': loja})
            
            # Restringir tipos de usuário para admins de loja
            if not request.user.is_superuser and user_type not in ['loja_user', 'loja_admin']:
                user_type = 'loja_user'
            
            # Criar usuário usando o serviço
            service = EmailCredentialsService()
            result = service.create_user_credentials(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                loja=loja,
                created_by=request.user
            )
            
            if result['success']:
                messages.success(
                    request, 
                    f'Usuário {username} criado com sucesso! '
                    f'{"Email enviado." if result["email_sent"] else "Email não pôde ser enviado - verifique configurações."}'
                )
                return redirect('email_credentials:listar_usuarios_loja')
            else:
                messages.error(request, f'Erro ao criar usuário: {result["message"]}')
                
        except Exception as e:
            logger.error(f'Erro ao criar usuário: {str(e)}')
            messages.error(request, 'Erro interno. Tente novamente.')
    
    context = {
        'title': f'Criar Usuário - {loja.nome}',
        'loja': loja,
        'user_types': [
            ('loja_user', 'Usuário da Loja'),
            ('loja_admin', 'Administrador da Loja'),
        ] if request.user.is_superuser else [('loja_user', 'Usuário da Loja')]
    }
    
    return render(request, 'email_credentials/criar_usuario_loja.html', context)


@login_required
@require_http_methods(["POST"])
def reenviar_credenciais(request, user_id):
    """Reenvia credenciais para um usuário"""
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Verificar permissões
        if not _can_manage_user(request.user, user):
            messages.error(request, 'Você não tem permissão para gerenciar este usuário.')
            return redirect('email_credentials:listar_usuarios')
        
        # Reenviar credenciais
        service = EmailCredentialsService()
        result = service.resend_credentials(user)
        
        if result['success']:
            messages.success(request, f'Credenciais reenviadas para {user.username}!')
        else:
            messages.error(request, f'Erro ao reenviar credenciais: {result["message"]}')
            
    except Exception as e:
        logger.error(f'Erro ao reenviar credenciais: {str(e)}')
        messages.error(request, 'Erro interno. Tente novamente.')
    
    return redirect(request.META.get('HTTP_REFERER', 'email_credentials:listar_usuarios'))


@login_required
def recuperar_senha_form(request):
    """Formulário de recuperação de senha"""
    
    if request.method == 'POST':
        email_or_username = request.POST.get('email_or_username', '').strip()
        
        if not email_or_username:
            messages.error(request, 'Digite seu email ou nome de usuário.')
            return render(request, 'email_credentials/recuperar_senha.html')
        
        try:
            service = EmailCredentialsService()
            result = service.send_password_recovery(email_or_username)
            
            if result['success']:
                messages.success(request, 'Nova senha enviada por email!')
                return redirect('login')
            else:
                messages.error(request, result['message'])
                
        except Exception as e:
            logger.error(f'Erro na recuperação de senha: {str(e)}')
            messages.error(request, 'Erro interno. Tente novamente.')
    
    return render(request, 'email_credentials/recuperar_senha.html')


@login_required
@user_passes_test(is_super_admin)
def logs_email(request):
    """Lista logs de email"""
    
    # Filtros
    success_filter = request.GET.get('success', '')
    email_type = request.GET.get('type', '')
    search = request.GET.get('search', '')
    
    # Query base
    logs = EmailLog.objects.select_related('user', 'loja').all()
    
    # Aplicar filtros
    if success_filter:
        logs = logs.filter(success=(success_filter == 'true'))
    
    if email_type:
        logs = logs.filter(email_type=email_type)
    
    if search:
        logs = logs.filter(
            Q(to_email__icontains=search) |
            Q(subject__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Ordenar por mais recente
    logs = logs.order_by('-sent_at')
    
    # Paginação
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Logs de Email',
        'page_obj': page_obj,
        'success_filter': success_filter,
        'email_type': email_type,
        'search': search,
        'email_types': EmailLog.EMAIL_TYPE_CHOICES,
        'stats': _get_email_stats(),
    }
    
    return render(request, 'email_credentials/logs_email.html', context)


@login_required
@require_http_methods(["GET"])
def api_gerar_senhas(request):
    """API para gerar múltiplas senhas"""
    
    try:
        count = int(request.GET.get('count', 5))
        length = int(request.GET.get('length', 12))
        
        # Limitar valores
        count = min(max(count, 1), 10)
        length = min(max(length, 8), 20)
        
        passwords = PasswordGenerator.generate_multiple_passwords(count, length)
        
        return JsonResponse({
            'success': True,
            'passwords': passwords
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def api_validar_senha(request):
    """API para validar força de senha"""
    
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
        
        if not password:
            return JsonResponse({
                'success': False,
                'error': 'Senha não fornecida'
            })
        
        strength = PasswordGenerator.estimate_strength(password)
        
        return JsonResponse({
            'success': True,
            'strength': strength
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# Funções auxiliares

def _get_dashboard_stats() -> Dict[str, Any]:
    """Obtém estatísticas para o dashboard"""
    
    try:
        from datetime import timedelta
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        return {
            'total_users': User.objects.count(),
            'total_lojas': Loja.objects.filter(status='ativa').count(),
            'emails_sent_30d': EmailLog.objects.filter(
                sent_at__gte=last_30_days,
                success=True
            ).count(),
            'emails_failed_30d': EmailLog.objects.filter(
                sent_at__gte=last_30_days,
                success=False
            ).count(),
            'users_with_provisional': ExtendedUserProfile.objects.filter(
                has_provisional_password=True
            ).count(),
        }
    except Exception as e:
        logger.error(f'Erro ao obter estatísticas: {str(e)}')
        return {}


def _get_loja_stats(loja) -> Dict[str, Any]:
    """Obtém estatísticas para uma loja específica"""
    
    try:
        from datetime import timedelta
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        return {
            'total_users': User.objects.filter(
                extended_profile__associated_loja=loja
            ).count(),
            'emails_sent_30d': EmailLog.objects.filter(
                loja=loja,
                sent_at__gte=last_30_days,
                success=True
            ).count(),
            'emails_failed_30d': EmailLog.objects.filter(
                loja=loja,
                sent_at__gte=last_30_days,
                success=False
            ).count(),
            'users_with_provisional': ExtendedUserProfile.objects.filter(
                associated_loja=loja,
                has_provisional_password=True
            ).count(),
        }
    except Exception as e:
        logger.error(f'Erro ao obter estatísticas da loja: {str(e)}')
        return {}


def _get_recent_emails(loja=None, limit=10):
    """Obtém emails recentes"""
    
    try:
        logs = EmailLog.objects.select_related('user', 'loja')
        
        if loja:
            logs = logs.filter(loja=loja)
        
        return logs.order_by('-sent_at')[:limit]
    except Exception as e:
        logger.error(f'Erro ao obter emails recentes: {str(e)}')
        return []


def _get_recent_users(loja=None, limit=10):
    """Obtém usuários recentes"""
    
    try:
        users = User.objects.select_related('extended_profile')
        
        if loja:
            users = users.filter(extended_profile__associated_loja=loja)
        
        return users.order_by('-date_joined')[:limit]
    except Exception as e:
        logger.error(f'Erro ao obter usuários recentes: {str(e)}')
        return []


def _get_create_user_context():
    """Contexto para criação de usuário"""
    
    return {
        'title': 'Criar Usuário',
        'lojas': Loja.objects.filter(status='ativa'),
        'user_types': ExtendedUserProfile.USER_TYPE_CHOICES,
    }


def _get_email_stats():
    """Estatísticas de email"""
    
    try:
        from datetime import timedelta
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        total = EmailLog.objects.filter(sent_at__gte=last_30_days).count()
        success = EmailLog.objects.filter(
            sent_at__gte=last_30_days,
            success=True
        ).count()
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        return {
            'total_30d': total,
            'success_30d': success,
            'failed_30d': total - success,
            'success_rate': round(success_rate, 1)
        }
    except Exception as e:
        logger.error(f'Erro ao obter estatísticas de email: {str(e)}')
        return {}


def _can_manage_user(manager_user, target_user):
    """Verifica se um usuário pode gerenciar outro"""
    
    # Super admin pode gerenciar qualquer um
    if manager_user.is_superuser:
        return True
    
    try:
        manager_profile = ExtendedUserProfile.objects.get(user=manager_user)
        target_profile = ExtendedUserProfile.objects.get(user=target_user)
        
        # Admin de loja só pode gerenciar usuários da mesma loja
        if manager_profile.user_type == 'loja_admin':
            return (manager_profile.associated_loja == target_profile.associated_loja and
                    target_profile.user_type != 'super_admin')
        
    except ExtendedUserProfile.DoesNotExist:
        pass
    
    return False