from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import secrets
import string

from .models import Funcionario, TipoFuncionario, Loja
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def require_loja_admin(view_func):
    """Decorator para views que requerem acesso de administrador de loja"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('loja_login')
        
        # Verifica se é super admin ou admin de loja
        if not (request.user.is_superuser or hasattr(request.user, 'loja_admin')):
            messages.error(request, 'Você não tem permissão para acessar esta área.')
            return redirect('dashboard:loja')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@require_loja_admin
def funcionario_list(request):
    """Lista todos os funcionários da loja com filtros e paginação"""
    
    # Determina a loja do usuário
    if request.user.is_superuser:
        # Super admin pode ver funcionários de qualquer loja
        loja_id = request.GET.get('loja_id')
        if loja_id:
            loja = get_object_or_404(Loja, id=loja_id)
        else:
            # Se não especificou loja, redireciona para seleção
            lojas = Loja.objects.filter(status='ativa')
            return render(request, 'funcionarios/selecionar_loja.html', {'lojas': lojas})
    else:
        # Admin de loja vê apenas funcionários da sua loja
        loja = request.user.loja_admin
    
    # Query base
    funcionarios = Funcionario.objects.filter(loja=loja).select_related(
        'user', 'tipo_funcionario', 'loja'
    )
    
    # Filtros
    search = request.GET.get('search', '').strip()
    tipo_funcionario_id = request.GET.get('tipo_funcionario', '')
    status = request.GET.get('status', '')
    
    if search:
        funcionarios = funcionarios.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(codigo_funcionario__icontains=search)
        )
    
    if tipo_funcionario_id:
        funcionarios = funcionarios.filter(tipo_funcionario_id=tipo_funcionario_id)
    
    if status == 'ativo':
        funcionarios = funcionarios.filter(ativo=True)
    elif status == 'inativo':
        funcionarios = funcionarios.filter(ativo=False)
    
    # Ordenação
    funcionarios = funcionarios.order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(funcionarios, 20)  # 20 funcionários por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Tipos de funcionário para o filtro
    tipos_funcionario = TipoFuncionario.objects.filter(
        tipo_loja=loja.tipo_loja,
        ativo=True
    ).order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'funcionarios': page_obj,
        'loja': loja,
        'tipos_funcionario': tipos_funcionario,
        'search': search,
        'tipo_funcionario_selected': tipo_funcionario_id,
        'status_selected': status,
        'total_funcionarios': funcionarios.count(),
        'funcionarios_ativos': funcionarios.filter(ativo=True).count(),
        'funcionarios_inativos': funcionarios.filter(ativo=False).count(),
    }
    
    return render(request, 'funcionarios/list.html', context)


@login_required
@require_loja_admin
def funcionario_detail(request, funcionario_id):
    """Exibe detalhes completos de um funcionário"""
    
    # Determina a loja do usuário
    if request.user.is_superuser:
        funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    else:
        funcionario = get_object_or_404(
            Funcionario, 
            id=funcionario_id, 
            loja=request.user.loja_admin
        )
    
    context = {
        'funcionario': funcionario,
        'loja': funcionario.loja,
    }
    
    return render(request, 'funcionarios/detail.html', context)


def gerar_senha_temporaria():
    """Gera uma senha temporária segura"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(12))


def gerar_username_unico(nome, sobrenome):
    """Gera um username único baseado no nome"""
    base_username = f"{nome.lower()}.{sobrenome.lower()}"
    base_username = ''.join(c for c in base_username if c.isalnum() or c == '.')
    
    username = base_username
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username
@login_r
equired
@require_loja_admin
def funcionario_create(request):
    """Cria um novo funcionário"""
    
    # Determina a loja do usuário
    if request.user.is_superuser:
        loja_id = request.GET.get('loja_id') or request.POST.get('loja_id')
        if loja_id:
            loja = get_object_or_404(Loja, id=loja_id)
        else:
            # Se não especificou loja, redireciona para seleção
            lojas = Loja.objects.filter(status='ativa')
            return render(request, 'funcionarios/selecionar_loja.html', {'lojas': lojas})
    else:
        loja = request.user.loja_admin
    
    # Tipos de funcionário disponíveis para esta loja
    tipos_funcionario = TipoFuncionario.objects.filter(
        tipo_loja=loja.tipo_loja,
        ativo=True
    ).order_by('nome')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Dados do formulário
                nome = request.POST.get('nome', '').strip()
                sobrenome = request.POST.get('sobrenome', '').strip()
                email = request.POST.get('email', '').strip()
                telefone = request.POST.get('telefone', '').strip()
                tipo_funcionario_id = request.POST.get('tipo_funcionario')
                data_admissao = request.POST.get('data_admissao')
                salario = request.POST.get('salario', '').strip()
                observacoes = request.POST.get('observacoes', '').strip()
                
                # Validações
                if not all([nome, sobrenome, email, tipo_funcionario_id, data_admissao]):
                    messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                    raise ValueError('Campos obrigatórios não preenchidos')
                
                # Verifica se email já existe
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Este email já está cadastrado no sistema.')
                    raise ValueError('Email duplicado')
                
                # Busca o tipo de funcionário
                tipo_funcionario = get_object_or_404(
                    TipoFuncionario, 
                    id=tipo_funcionario_id,
                    tipo_loja=loja.tipo_loja
                )
                
                # Cria o usuário Django
                username = gerar_username_unico(nome, sobrenome)
                senha_temporaria = gerar_senha_temporaria()
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=nome,
                    last_name=sobrenome,
                    password=senha_temporaria
                )
                
                # Cria o funcionário
                funcionario = Funcionario.objects.create(
                    user=user,
                    loja=loja,
                    tipo_funcionario=tipo_funcionario,
                    data_admissao=data_admissao,
                    salario=salario if salario else None,
                    observacoes=observacoes
                )
                
                # Configura perfil do usuário se existir
                if hasattr(user, 'perfil'):
                    user.perfil.telefone = telefone
                    user.perfil.deve_trocar_senha = True
                    user.perfil.requires_password_change = True
                    user.perfil.provisional_password_created = timezone.now()
                    user.perfil.save()
                
                logger.info(f"Funcionário {funcionario.nome_completo} criado na loja {loja.nome}")
                
                messages.success(
                    request, 
                    f'Funcionário {funcionario.nome_completo} criado com sucesso! '
                    f'Username: {username}, Senha temporária: {senha_temporaria}'
                )
                
                return redirect('funcionarios:detail', funcionario_id=funcionario.id)
                
        except Exception as e:
            logger.error(f"Erro ao criar funcionário: {str(e)}")
            messages.error(request, 'Erro ao criar funcionário. Tente novamente.')
    
    context = {
        'loja': loja,
        'tipos_funcionario': tipos_funcionario,
    }
    
    return render(request, 'funcionarios/create.html', context)


@login_required
@require_loja_admin
def funcionario_edit(request, funcionario_id):
    """Edita um funcionário existente"""
    
    # Determina a loja do usuário
    if request.user.is_superuser:
        funcionario = get_object_or_404(Funcionario, id=funcionario_id)
        loja = funcionario.loja
    else:
        funcionario = get_object_or_404(
            Funcionario, 
            id=funcionario_id, 
            loja=request.user.loja_admin
        )
        loja = funcionario.loja
    
    # Tipos de funcionário disponíveis para esta loja
    tipos_funcionario = TipoFuncionario.objects.filter(
        tipo_loja=loja.tipo_loja,
        ativo=True
    ).order_by('nome')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Dados do formulário
                nome = request.POST.get('nome', '').strip()
                sobrenome = request.POST.get('sobrenome', '').strip()
                email = request.POST.get('email', '').strip()
                telefone = request.POST.get('telefone', '').strip()
                tipo_funcionario_id = request.POST.get('tipo_funcionario')
                data_admissao = request.POST.get('data_admissao')
                salario = request.POST.get('salario', '').strip()
                observacoes = request.POST.get('observacoes', '').strip()
                
                # Validações
                if not all([nome, sobrenome, email, tipo_funcionario_id, data_admissao]):
                    messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                    raise ValueError('Campos obrigatórios não preenchidos')
                
                # Verifica se email já existe (exceto para o próprio usuário)
                if User.objects.filter(email=email).exclude(id=funcionario.user.id).exists():
                    messages.error(request, 'Este email já está cadastrado no sistema.')
                    raise ValueError('Email duplicado')
                
                # Busca o tipo de funcionário
                tipo_funcionario = get_object_or_404(
                    TipoFuncionario, 
                    id=tipo_funcionario_id,
                    tipo_loja=loja.tipo_loja
                )
                
                # Atualiza o usuário Django
                funcionario.user.first_name = nome
                funcionario.user.last_name = sobrenome
                funcionario.user.email = email
                funcionario.user.save()
                
                # Atualiza o funcionário
                funcionario.tipo_funcionario = tipo_funcionario
                funcionario.data_admissao = data_admissao
                funcionario.salario = salario if salario else None
                funcionario.observacoes = observacoes
                funcionario.save()
                
                # Atualiza perfil do usuário se existir
                if hasattr(funcionario.user, 'perfil'):
                    funcionario.user.perfil.telefone = telefone
                    funcionario.user.perfil.save()
                
                logger.info(f"Funcionário {funcionario.nome_completo} atualizado na loja {loja.nome}")
                
                messages.success(request, f'Funcionário {funcionario.nome_completo} atualizado com sucesso!')
                
                return redirect('funcionarios:detail', funcionario_id=funcionario.id)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar funcionário: {str(e)}")
            messages.error(request, 'Erro ao atualizar funcionário. Tente novamente.')
    
    context = {
        'funcionario': funcionario,
        'loja': loja,
        'tipos_funcionario': tipos_funcionario,
    }
    
    return render(request, 'funcionarios/edit.html', context)


@login_required
@require_loja_admin
@require_http_methods(["POST"])
def funcionario_toggle_status(request, funcionario_id):
    """Ativa/desativa um funcionário"""
    
    # Determina a loja do usuário
    if request.user.is_superuser:
        funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    else:
        funcionario = get_object_or_404(
            Funcionario, 
            id=funcionario_id, 
            loja=request.user.loja_admin
        )
    
    try:
        funcionario.ativo = not funcionario.ativo
        funcionario.save()
        
        # Também desativa/ativa o usuário Django
        funcionario.user.is_active = funcionario.ativo
        funcionario.user.save()
        
        status_text = "ativado" if funcionario.ativo else "desativado"
        logger.info(f"Funcionário {funcionario.nome_completo} {status_text}")
        
        messages.success(
            request, 
            f'Funcionário {funcionario.nome_completo} {status_text} com sucesso!'
        )
        
    except Exception as e:
        logger.error(f"Erro ao alterar status do funcionário: {str(e)}")
        messages.error(request, 'Erro ao alterar status do funcionário.')
    
    return redirect('funcionarios:list')


@login_required
@require_loja_admin
def funcionario_reset_password(request, funcionario_id):
    """Reseta a senha de um funcionário"""
    
    # Determina a loja do usuário
    if request.user.is_superuser:
        funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    else:
        funcionario = get_object_or_404(
            Funcionario, 
            id=funcionario_id, 
            loja=request.user.loja_admin
        )
    
    if request.method == 'POST':
        try:
            nova_senha = gerar_senha_temporaria()
            funcionario.user.set_password(nova_senha)
            funcionario.user.save()
            
            # Configura perfil para trocar senha
            if hasattr(funcionario.user, 'perfil'):
                funcionario.user.perfil.deve_trocar_senha = True
                funcionario.user.perfil.requires_password_change = True
                funcionario.user.perfil.provisional_password_created = timezone.now()
                funcionario.user.perfil.save()
            
            logger.info(f"Senha resetada para funcionário {funcionario.nome_completo}")
            
            messages.success(
                request, 
                f'Nova senha gerada para {funcionario.nome_completo}: {nova_senha}'
            )
            
        except Exception as e:
            logger.error(f"Erro ao resetar senha: {str(e)}")
            messages.error(request, 'Erro ao resetar senha.')
    
    return redirect('funcionarios:detail', funcionario_id=funcionario_id)