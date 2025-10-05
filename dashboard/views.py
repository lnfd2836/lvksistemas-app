from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from lojas.models import Loja, Cliente, Produto, Venda, BackupLoja
from dashboard.models import DashboardStats, Notificacao
from usuarios.models import LogAcesso, SessaoAtiva
from modulos.models import ModuloLoja, TipoLoja, CampoPersonalizado
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


def redirect_to_appropriate_dashboard(request):
    """
    View helper para redirecionar usuários para o dashboard apropriado.
    Pode ser usada como view padrão para redirecionamentos.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
        logger.info(f"Redirecionando usuário {request.user.username} para dashboard apropriado: {dashboard_url}")
        return redirect(dashboard_url)
    except Exception as e:
        logger.error(f"Erro ao determinar dashboard para redirecionamento do usuário {request.user.username}: {str(e)}")
        messages.error(request, 'Erro ao determinar dashboard apropriado.')
        return redirect('login')


def require_store_access(view_func):
    """
    Decorator para views que requerem acesso ao dashboard de loja.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('loja_login')
        
        if not AuthenticationService.can_access_store_dashboard(request.user):
            messages.error(request, 'Você não tem permissão para acessar esta área.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def dashboard_principal(request):
    """Dashboard principal do sistema - refatorado para usar AuthenticationService"""
    
    try:
        # Verificar se o usuário deve estar neste dashboard
        expected_url = AuthenticationService.determine_user_dashboard(request.user)
        
        # Se a URL esperada não for a atual, redirecionar
        if expected_url != request.path and expected_url != '/dashboard/':
            logger.info(f"Redirecionando usuário {request.user.username} de {request.path} para {expected_url}")
            return redirect(expected_url)
        
        # Obter contexto do dashboard
        context = AuthenticationService.get_dashboard_context(request.user)
        user_type = context['user_type']
        
        # Se é super usuário com loja associada, redirecionar para dashboard da loja
        if user_type == 'super_admin' and context['store']:
            logger.info(f"Super usuário {request.user.username} tem loja associada, redirecionando para dashboard da loja")
            return redirect('dashboard_loja')
        
        # Se é store admin, redirecionar para dashboard da loja
        if user_type == 'store_admin':
            logger.info(f"Store admin {request.user.username} redirecionando para dashboard da loja")
            return redirect('dashboard_loja')
        
        # Se é super admin sem loja, mostrar dashboard super admin
        if user_type == 'super_admin':
            return dashboard_super_admin(request)
        
        # Usuário sem permissões adequadas
        logger.warning(f"Usuário {request.user.username} tentou acessar dashboard principal sem permissões adequadas")
        messages.error(request, 'Você não tem permissão para acessar o dashboard.')
        return redirect('login')
        
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard principal para usuário {request.user.username}: {str(e)}")
        messages.error(request, 'Erro interno. Tente novamente.')
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
    """Dashboard específico de uma loja - refatorado para usar AuthenticationService"""
    
    # Verificar se o usuário está autenticado
    if not request.user.is_authenticated:
        logger.info("Usuário não autenticado tentando acessar dashboard da loja")
        return redirect('loja_login')
    
    try:
        # Verificar se o usuário pode acessar dashboard de loja
        if not AuthenticationService.can_access_store_dashboard(request.user):
            logger.warning(f"Usuário {request.user.username} tentou acessar dashboard de loja sem permissão")
            messages.error(request, 'Você não tem permissão para acessar o dashboard da loja.')
            return redirect('login')
        
        # Determinar qual loja usar
        target_loja = None
        
        # Se foi passado loja_id, busca a loja específica
        if loja_id:
            try:
                target_loja = Loja.objects.get(id=loja_id)
                # Verificar se o usuário pode acessar esta loja específica
                if not AuthenticationService.can_access_store_dashboard(request.user, target_loja):
                    logger.warning(f"Usuário {request.user.username} tentou acessar loja {loja_id} sem permissão")
                    messages.error(request, 'Você não tem permissão para acessar esta loja.')
                    return redirect('login')
            except Loja.DoesNotExist:
                logger.error(f"Loja {loja_id} não encontrada")
                messages.error(request, 'Loja não encontrada.')
                return redirect('simple_login')
        
        # Se foi passada uma loja como parâmetro
        elif loja:
            if not AuthenticationService.can_access_store_dashboard(request.user, loja):
                logger.warning(f"Usuário {request.user.username} tentou acessar loja {loja.id} sem permissão")
                messages.error(request, 'Você não tem permissão para acessar esta loja.')
                return redirect('login')
            target_loja = loja
        
        # Se não foi especificada loja, obter a loja do usuário
        else:
            target_loja = AuthenticationService.get_user_store(request.user)
            
            # Se não encontrou loja associada
            if not target_loja:
                if request.user.is_superuser:
                    logger.info(f"Super usuário {request.user.username} sem loja específica, redirecionando para seleção")
                    messages.info(request, 'Selecione uma loja para acessar seu dashboard.')
                    # Aqui você pode redirecionar para uma página de seleção de lojas
                    return redirect('dashboard_principal')
                else:
                    logger.error(f"Usuário {request.user.username} deveria ter loja mas não foi encontrada")
                    messages.error(request, 'Nenhuma loja associada ao seu usuário.')
                    return redirect('login')
        
        # Verificar se a loja foi encontrada
        if not target_loja:
            logger.error(f"Nenhuma loja válida encontrada para usuário {request.user.username}")
            messages.error(request, 'Erro ao determinar loja para acesso.')
            return redirect('login')
    
        # Obter contexto do dashboard
        dashboard_context = AuthenticationService.get_dashboard_context(request.user)
        
        # Buscar controle financeiro da loja
        controle_financeiro = None
        try:
            from controle_financeiro.models import ControleFinanceiro
            controle_financeiro = ControleFinanceiro.objects.get(loja=target_loja)
            # Atualiza o status financeiro
            controle_financeiro.verificar_status()
        except ControleFinanceiro.DoesNotExist:
            logger.warning(f"Controle financeiro não encontrado para loja {target_loja.nome}")
        except Exception as e:
            logger.error(f"Erro ao buscar controle financeiro para loja {target_loja.nome}: {e}")
        
        # Calcular estatísticas da loja
        total_clientes = Cliente.objects.filter(loja=target_loja).count()
        total_produtos = Produto.objects.filter(loja=target_loja).count()
        
        # Vendas
        vendas_hoje = Venda.objects.filter(
            loja=target_loja,
            data_venda__date=timezone.now().date()
        ).count()
        
        vendas_semana = Venda.objects.filter(
            loja=target_loja,
            data_venda__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        vendas_mes = Venda.objects.filter(
            loja=target_loja,
            data_venda__month=timezone.now().month,
            data_venda__year=timezone.now().year
        ).count()
        
        # Receita
        receita_hoje = Venda.objects.filter(
            loja=target_loja,
            data_venda__date=timezone.now().date(),
            status='concluida'
        ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0')
        
        receita_semana = Venda.objects.filter(
            loja=target_loja,
            data_venda__gte=timezone.now() - timedelta(days=7),
            status='concluida'
        ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0')
        
        receita_mes = Venda.objects.filter(
            loja=target_loja,
            data_venda__month=timezone.now().month,
            data_venda__year=timezone.now().year,
            status='concluida'
        ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0')
        
        # Produtos com estoque baixo
        produtos_estoque_baixo = Produto.objects.filter(
            loja=target_loja,
            estoque__lte=5,
            ativo=True
        ).count()
        
        # Vendas recentes
        vendas_recentes = Venda.objects.filter(loja=target_loja).order_by('-data_venda')[:10]
        
        # Clientes recentes
        clientes_recentes = Cliente.objects.filter(loja=target_loja).order_by('-data_cadastro')[:10]
        
        # Produtos mais vendidos
        produtos_mais_vendidos = Produto.objects.filter(
            loja=target_loja
        ).annotate(
            total_vendido=Sum('itens_venda__quantidade')
        ).order_by('-total_vendido')[:5]
        
        # Módulos específicos do tipo de loja
        modulos_loja = []
        if target_loja.tipo_loja:
            modulos_loja = ModuloLoja.objects.filter(
                tipo_loja=target_loja.tipo_loja,
                ativo=True
            ).order_by('ordem')
        
        # Preparar contexto completo
        context = {
            'loja': target_loja,
            'controle_financeiro': controle_financeiro,
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
            # Adicionar contexto do AuthenticationService
            'user_type': dashboard_context['user_type'],
            'can_access_store': dashboard_context['can_access_store'],
            'page_title': f'Dashboard - {target_loja.nome}',
        }
        
        logger.info(f"Dashboard da loja {target_loja.nome} carregado para usuário {request.user.username}")
        return render(request, 'dashboard/loja.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard da loja para usuário {request.user.username}: {str(e)}")
        messages.error(request, 'Erro interno ao carregar dashboard da loja. Tente novamente.')
        return redirect('login')


@login_required
def gerenciar_modulos(request):
    """Gerenciar módulos de loja - refatorado para usar AuthenticationService"""
    
    try:
        # Verificar se é super usuário usando AuthenticationService
        user_type = AuthenticationService.get_user_type(request.user)
        if user_type != 'super_admin':
            logger.warning(f"Usuário {request.user.username} ({user_type}) tentou acessar gerenciamento de módulos")
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
            return redirect(dashboard_url)
        
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
            'user_type': user_type,
        }
        
        logger.info(f"Gerenciamento de módulos acessado por super usuário {request.user.username}")
        return render(request, 'dashboard/gerenciar_modulos.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao carregar gerenciamento de módulos para usuário {request.user.username}: {str(e)}")
        messages.error(request, 'Erro interno. Tente novamente.')
        dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
        return redirect(dashboard_url)


@login_required
def listar_usuarios_super_admin(request):
    """Lista todos os usuários super administradores"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard:principal')
    
    usuarios = User.objects.filter(is_superuser=True).order_by('-date_joined')
    
    context = {
        'usuarios': usuarios,
    }
    
    # Debug: usar template simplificado temporariamente
    return render(request, 'dashboard/usuarios_super_admin_debug.html', context)


@login_required
def criar_usuario_super_admin(request):
    """Cria um novo usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard:principal')
    
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
            return redirect('dashboard:admin_usuarios_criar')
        
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('dashboard:admin_usuarios_criar')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe.')
            return redirect('dashboard:admin_usuarios_criar')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já está em uso.')
            return redirect('dashboard:admin_usuarios_criar')
        
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
            return redirect('dashboard:admin_usuarios_lista')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
            return redirect('dashboard:admin_usuarios_criar')
    
    return render(request, 'dashboard/criar_usuario_super_admin.html')


@login_required
def editar_usuario_super_admin(request, user_id):
    """Edita um usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard:principal')
    
    user = get_object_or_404(User, id=user_id, is_superuser=True)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Verificar se email já existe em outro usuário
        if User.objects.filter(email=user.email).exclude(id=user.id).exists():
            messages.error(request, 'Email já está em uso por outro usuário.')
            return redirect('dashboard:admin_usuarios_editar', user_id=user_id)
        
        user.save()
        messages.success(request, f'Usuário "{user.username}" atualizado com sucesso!')
        return redirect('dashboard:admin_usuarios_lista')
    
    context = {
        'usuario': user,
    }
    
    return render(request, 'dashboard/editar_usuario_super_admin.html', context)


@login_required
def alterar_senha_usuario_super_admin(request, user_id):
    """Altera a senha de um usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard:principal')
    
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
            return redirect('dashboard:admin_usuarios_lista')
            
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
        return redirect('dashboard:principal')
    
    user = get_object_or_404(User, id=user_id, is_superuser=True)
    
    # Não permitir excluir o próprio usuário
    if user == request.user:
        messages.error(request, 'Você não pode excluir seu próprio usuário.')
        return redirect('dashboard:admin_usuarios_lista')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuário "{username}" excluído com sucesso!')
        return redirect('dashboard:admin_usuarios_lista')
    
    context = {
        'usuario': user,
    }
    
    return render(request, 'dashboard/excluir_usuario_super_admin.html', context)


def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        return redirect('dashboard:principal')
    
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
            
            return redirect('dashboard:principal')
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
def marcar_notificacao_lida(request, notificacao_id):
    """Marca uma notificação como lida"""
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    notificacao.marcar_como_lida()
    
    return JsonResponse({'success': True})


@login_required
def gerenciar_sessoes(request):
    """Gerencia sessões ativas dos usuários - refatorado para usar AuthenticationService"""
    
    try:
        # Verificar se é super usuário usando AuthenticationService
        user_type = AuthenticationService.get_user_type(request.user)
        if user_type != 'super_admin':
            logger.warning(f"Usuário {request.user.username} ({user_type}) tentou acessar gerenciamento de sessões")
            messages.error(request, 'Acesso negado. Apenas Super Administradores podem gerenciar sessões.')
            dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
            return redirect(dashboard_url)
        
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
            'user_type': user_type,
        }
        
        logger.info(f"Gerenciamento de sessões acessado por super usuário {request.user.username}")
        return render(request, 'dashboard/gerenciar_sessoes.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao carregar gerenciamento de sessões para usuário {request.user.username}: {str(e)}")
        messages.error(request, 'Erro interno. Tente novamente.')
        dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
        return redirect(dashboard_url)


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
