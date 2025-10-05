from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta

from lojas.models import Loja, Cliente, Produto, Venda, BackupLoja
from dashboard.models import DashboardStats, Notificacao
from usuarios.models import LogAcesso, SessaoAtiva
from modulos.models import ModuloLoja, TipoLoja, CampoPersonalizado


@login_required
@login_required
def dashboard_principal(request):
    """Dashboard principal do sistema"""
    
    # Se é super usuário E não tem loja associada, mostra dashboard geral
    if request.user.is_superuser:
        try:
            # Verifica se o super usuário tem uma loja associada
            loja = request.user.loja_admin
            # Se tem loja associada, redireciona para dashboard da loja
            return dashboard_loja(request, loja)
        except:
            # Se não tem loja associada, mostra dashboard super admin
            return dashboard_super_admin(request)
    
    # Se é admin de loja, mostra dashboard da loja
    try:
        loja = request.user.loja_admin
        return dashboard_loja(request, loja)
    except:
        # Se não tem loja associada, mostra mensagem e redireciona para login
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('login')


@login_required
def dashboard_super_admin(request):
    """Dashboard do super administrador"""
    
    # Estatísticas gerais
    total_lojas = Loja.objects.count()
    lojas_ativas = Loja.objects.filter(status='ativa').count()
    lojas_inativas = Loja.objects.filter(status='inativa').count()
    
    context = {
        'total_lojas': total_lojas,
        'lojas_ativas': lojas_ativas,
        'lojas_inativas': lojas_inativas,
    }
    
    return render(request, 'dashboard/super_admin.html', context)


def dashboard_loja(request, loja=None, loja_id=None):
    """Dashboard específico de uma loja"""
    
    # Verifica se o usuário está autenticado
    if not request.user.is_authenticated:
        return redirect('loja_login_direct')
    
    # Verifica se o usuário tem permissão para acessar esta loja
    if request.user.is_superuser:
        # Super usuário pode acessar qualquer loja
        pass
    else:
        # Usuário comum só pode acessar sua própria loja
        if loja and hasattr(request.user, 'loja_admin'):
            if request.user.loja_admin != loja:
                messages.error(request, 'Você não tem permissão para acessar esta loja.')
                return redirect('loja_login')
    
    # Se foi passado loja_id, busca a loja
    if loja_id:
        from lojas.models import Loja
        try:
            loja = Loja.objects.get(id=loja_id)
        except Loja.DoesNotExist:
            messages.error(request, 'Loja não encontrada.')
            return redirect('loja_login')
    
    # Se não foi passada uma loja, tenta obter do middleware
    if loja is None:
        if hasattr(request, 'loja_atual'):
            loja = request.loja_atual
        else:
            # Se é super usuário, redireciona para listar lojas
            if request.user.is_superuser:
                messages.info(request, 'Selecione uma loja para acessar seu dashboard.')
                return redirect('listar_lojas')
            else:
                # Usuário comum sem loja associada - busca a loja do usuário
                try:
                    loja = request.user.loja_admin
                except:
                    messages.error(request, 'Você não tem uma loja associada.')
                    return redirect('loja_login')
    
    # Estatísticas da loja
    total_clientes = Cliente.objects.filter(loja=loja).count()
    total_produtos = Produto.objects.filter(loja=loja).count()
    
    # Vendas
    vendas_hoje = Venda.objects.filter(
        loja=loja,
        data_venda__date=timezone.now().date()
    ).count()
    
    vendas_semana = Venda.objects.filter(
        loja=loja,
        data_venda__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    vendas_mes = Venda.objects.filter(
        loja=loja,
        data_venda__month=timezone.now().month,
        data_venda__year=timezone.now().year
    ).count()
    
    # Receita
    receita_hoje = Venda.objects.filter(
        loja=loja,
        data_venda__date=timezone.now().date(),
        status='concluida'
    ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0')
    
    receita_semana = Venda.objects.filter(
        loja=loja,
        data_venda__gte=timezone.now() - timedelta(days=7),
        status='concluida'
    ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0')
    
    receita_mes = Venda.objects.filter(
        loja=loja,
        data_venda__month=timezone.now().month,
        data_venda__year=timezone.now().year,
        status='concluida'
    ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0')
    
    # Produtos com estoque baixo
    produtos_estoque_baixo = Produto.objects.filter(
        loja=loja,
        estoque__lte=5,
        ativo=True
    ).count()
    
    # Vendas recentes
    vendas_recentes = Venda.objects.filter(loja=loja).order_by('-data_venda')[:10]
    
    # Clientes recentes
    clientes_recentes = Cliente.objects.filter(loja=loja).order_by('-data_cadastro')[:10]
    
    # Produtos mais vendidos
    produtos_mais_vendidos = Produto.objects.filter(
        loja=loja
    ).annotate(
        total_vendido=Sum('itens_venda__quantidade')
    ).order_by('-total_vendido')[:5]
    
    # Módulos específicos do tipo de loja
    modulos_loja = []
    if loja.tipo_loja:
        modulos_loja = ModuloLoja.objects.filter(
            tipo_loja=loja.tipo_loja,
            ativo=True
        ).order_by('ordem')
    
    context = {
        'loja': loja,
        'total_clientes': total_clientes,
        'total_produtos': total_produtos,
        'vendas_hoje': vendas_hoje,
        'vendas_semana': vendas_semana,
        'vendas_mes': vendas_mes,
        'receita_hoje': receita_hoje,
        'receita_semana': receita_semana,
        'receita_mes': receita_mes,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'vendas_recentes': vendas_recentes,
        'clientes_recentes': clientes_recentes,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'modulos_loja': modulos_loja,
    }
    
    return render(request, 'dashboard/loja.html', context)


@login_required
def gerenciar_modulos(request):
    """Gerenciar módulos de loja"""
    
    # Verifica se é super usuário
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    # Busca todos os tipos de loja
    tipos_loja = TipoLoja.objects.all().order_by('nome')
    
    # Busca todos os módulos
    modulos = ModuloLoja.objects.all().order_by('tipo_loja', 'ordem')
    
    # Busca todos os campos personalizados
    campos = CampoPersonalizado.objects.all().order_by('tipo_loja', 'ordem')
    
    context = {
        'tipos_loja': tipos_loja,
        'modulos': modulos,
        'campos': campos,
    }
    
    return render(request, 'dashboard/gerenciar_modulos.html', context)


@login_required
def listar_usuarios_super_admin(request):
    """Lista todos os usuários super administradores"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    usuarios = User.objects.filter(is_superuser=True).order_by('-date_joined')
    
    context = {
        'usuarios': usuarios,
    }
    
    return render(request, 'dashboard/usuarios_super_admin.html', context)


@login_required
def criar_usuario_super_admin(request):
    """Cria um novo usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validações
        if not username or not email or not password:
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('criar_usuario_super_admin')
        
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('criar_usuario_super_admin')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe.')
            return redirect('criar_usuario_super_admin')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já está em uso.')
            return redirect('criar_usuario_super_admin')
        
        try:
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_superuser=True,
                is_staff=True,
                is_active=True
            )
            
            messages.success(request, f'Usuário super administrador "{username}" criado com sucesso!')
            return redirect('listar_usuarios_super_admin')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
            return redirect('criar_usuario_super_admin')
    
    return render(request, 'dashboard/criar_usuario_super_admin.html')


@login_required
def editar_usuario_super_admin(request, user_id):
    """Edita um usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id, is_superuser=True)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Verificar se email já existe em outro usuário
        if User.objects.filter(email=user.email).exclude(id=user.id).exists():
            messages.error(request, 'Email já está em uso por outro usuário.')
            return redirect('editar_usuario_super_admin', user_id=user_id)
        
        user.save()
        messages.success(request, f'Usuário "{user.username}" atualizado com sucesso!')
        return redirect('listar_usuarios_super_admin')
    
    context = {
        'usuario': user,
    }
    
    return render(request, 'dashboard/editar_usuario_super_admin.html', context)


@login_required
def alterar_senha_usuario_super_admin(request, user_id):
    """Altera a senha de um usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id, is_superuser=True)
    
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not nova_senha or not confirmar_senha:
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('alterar_senha_usuario_super_admin', user_id=user_id)
        
        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('alterar_senha_usuario_super_admin', user_id=user_id)
        
        if len(nova_senha) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            return redirect('alterar_senha_usuario_super_admin', user_id=user_id)
        
        try:
            user.set_password(nova_senha)
            user.save()
            messages.success(request, f'Senha do usuário "{user.username}" alterada com sucesso!')
            return redirect('listar_usuarios_super_admin')
            
        except Exception as e:
            messages.error(request, f'Erro ao alterar senha: {str(e)}')
            return redirect('alterar_senha_usuario_super_admin', user_id=user_id)
    
    context = {
        'usuario': user,
    }
    
    return render(request, 'dashboard/alterar_senha_usuario_super_admin.html')


@login_required
def excluir_usuario_super_admin(request, user_id):
    """Exclui um usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id, is_superuser=True)
    
    # Não permitir excluir o próprio usuário
    if user == request.user:
        messages.error(request, 'Você não pode excluir seu próprio usuário.')
        return redirect('listar_usuarios_super_admin')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuário "{username}" excluído com sucesso!')
        return redirect('listar_usuarios_super_admin')
    
    context = {
        'usuario': user,
    }
    
    return render(request, 'dashboard/excluir_usuario_super_admin.html', context)


def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Tenta autenticar com username primeiro
        user = authenticate(request, username=username, password=password)
        
        # Se falhar, tenta com email
        if user is None and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            
            # Registra o login
            try:
                LogAcesso.objects.create(
                    user=user,
                    acao='LOGIN',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    sucesso=True
                )
            except:
                pass  # Ignora erro se não conseguir criar log
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """View de logout"""
    if request.user.is_authenticated:
        # Registra o logout
        LogAcesso.objects.create(
            user=request.user,
            acao='LOGOUT',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            sucesso=True
        )
    
    logout(request)
    return redirect('login')


@login_required
def gerenciar_sessoes(request):
    """Gerencia sessões ativas (apenas para super usuários)"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    # Lista todas as sessões ativas
    sessoes_ativas = SessaoAtiva.objects.filter(ativa=True).order_by('-data_login')
    
    # Se foi uma requisição POST, processa a ação
    if request.method == 'POST':
        acao = request.POST.get('acao')
        sessao_id = request.POST.get('sessao_id')
        
        if acao == 'invalidar' and sessao_id:
            try:
                sessao = SessaoAtiva.objects.get(id=sessao_id)
                sessao.ativa = False
                sessao.save()
                messages.success(request, f'Sessão do usuário {sessao.user.username} foi invalidada.')
            except SessaoAtiva.DoesNotExist:
                messages.error(request, 'Sessão não encontrada.')
        
        elif acao == 'limpar_todas':
            SessaoAtiva.objects.filter(ativa=True).update(ativa=False)
            messages.success(request, 'Todas as sessões foram invalidadas.')
        
        return redirect('gerenciar_sessoes')
    
    context = {
        'sessoes_ativas': sessoes_ativas,
        'total_sessoes': sessoes_ativas.count(),
    }
    
    return render(request, 'dashboard/gerenciar_sessoes.html', context)


@login_required
def marcar_notificacao_lida(request, notificacao_id):
    """Marca uma notificação como lida"""
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    notificacao.marcar_como_lida()
    
    return JsonResponse({'success': True})


@login_required
def gerenciar_sessoes(request):
    """Gerencia sessões ativas dos usuários"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas Super Administradores podem gerenciar sessões.')
        return redirect('dashboard')
    
    # Filtros
    filtro_usuario = request.GET.get('usuario', '')
    filtro_super_admin = request.GET.get('super_admin', '')
    
    # Busca sessões ativas
    sessoes_ativas = SessaoAtiva.objects.filter(ativa=True)
    
    if filtro_usuario:
        sessoes_ativas = sessoes_ativas.filter(user__username__icontains=filtro_usuario)
    
    if filtro_super_admin == 'sim':
        sessoes_ativas = sessoes_ativas.filter(is_super_admin=True)
    elif filtro_super_admin == 'nao':
        sessoes_ativas = sessoes_ativas.filter(is_super_admin=False)
    
    sessoes_ativas = sessoes_ativas.order_by('-data_login')
    
    # Estatísticas
    total_sessoes = sessoes_ativas.count()
    sessoes_super_admin = sessoes_ativas.filter(is_super_admin=True).count()
    sessoes_usuarios = total_sessoes - sessoes_super_admin
    
    context = {
        'sessoes_ativas': sessoes_ativas,
        'total_sessoes': total_sessoes,
        'sessoes_super_admin': sessoes_super_admin,
        'sessoes_usuarios': sessoes_usuarios,
        'filtro_usuario': filtro_usuario,
        'filtro_super_admin': filtro_super_admin,
    }
    
    return render(request, 'dashboard/gerenciar_sessoes.html', context)


@login_required
def invalidar_sessao(request, sessao_id):
    """Invalida uma sessão específica"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        sessao = SessaoAtiva.objects.get(id=sessao_id, ativa=True)
        
        # Permite invalidar qualquer sessão (incluindo outras sessões do próprio Super Admin)
        sessao.ativa = False
        sessao.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Sessão de {sessao.user.username} invalidada com sucesso'
        })
        
    except SessaoAtiva.DoesNotExist:
        return JsonResponse({'error': 'Sessão não encontrada'}, status=404)


@login_required
def estatisticas_ajax(request):
    """Retorna estatísticas via AJAX"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    # Estatísticas em tempo real
    stats = {
        'total_lojas': Loja.objects.count(),
        'lojas_ativas': Loja.objects.filter(status='ativa').count(),
        'vendas_hoje': Venda.objects.filter(data_venda__date=timezone.now().date()).count(),
        'receita_hoje': float(Venda.objects.filter(
            data_venda__date=timezone.now().date(),
            status='concluida'
        ).aggregate(total=Sum('valor_final'))['total'] or 0),
    }
    
    return JsonResponse(stats)
