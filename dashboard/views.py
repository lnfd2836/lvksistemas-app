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
from lojas.permissions import require_loja_access, get_user_permissions
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
        
        # Super admins sempre ficam no dashboard principal, mesmo com loja associada
        # (comentado para permitir que super admins vejam o dashboard principal)
        # if user_type == 'super_admin' and context['store']:
        #     logger.info(f"Super usuário {request.user.username} tem loja associada, redirecionando para dashboard da loja")
        #     return redirect('dashboard:loja')
        
        # Se é store admin, redirecionar para dashboard da loja
        if user_type == 'store_admin':
            logger.info(f"Store admin {request.user.username} redirecionando para dashboard da loja")
            return redirect('dashboard:loja')
        
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


@require_loja_access
def dashboard_loja(request, loja=None, loja_id=None):
    """Dashboard específico de uma loja - refatorado para usar AuthenticationService"""
    
    # Verificar se o usuário está autenticado
    if not request.user.is_authenticated:
        logger.info("Usuário não autenticado tentando acessar dashboard da loja")
        return redirect('simple_login')
    
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
                    # Aqui você pode redirecionar para uma página de seleção de lojas
                    return redirect('dashboard:principal')
                else:
                    logger.error(f"Usuário {request.user.username} deveria ter loja mas não foi encontrada")
                    messages.error(request, 'Nenhuma loja associada ao seu usuário.')
                    return redirect('login')
        
        # Verificar se a loja foi encontrada
        if not target_loja:
            logger.error(f"Nenhuma loja válida encontrada para usuário {request.user.username}")
            messages.error(request, 'Erro ao determinar loja para acesso.')
            return redirect('login')
    
        # VERIFICAR SE É UMA LOJA DO TIPO CONTROLE DE QUALIDADE (FATESA)
        try:
            if target_loja.tipo_loja and target_loja.tipo_loja.nome == "controle_qualidade":
                return dashboard_fatesa(request, target_loja)
        except Exception as e:
            # Se houver erro ao acessar tipo_loja (por exemplo, tabela não existe), continua normalmente
            logger.warning(f"Erro ao verificar tipo_loja para loja {target_loja.nome}: {str(e)}")
    
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
        
        # Estatísticas de funcionários
        from lojas.models import Funcionario
        total_funcionarios = Funcionario.objects.filter(loja=target_loja).count()
        funcionarios_ativos = Funcionario.objects.filter(loja=target_loja, ativo=True).count()
        funcionarios_inativos = total_funcionarios - funcionarios_ativos
        
        # Preparar contexto completo
        context = {
            'loja': target_loja,
            'controle_financeiro': controle_financeiro,
            'total_clientes': total_clientes,
            'total_produtos': total_produtos,
            'total_funcionarios': total_funcionarios,
            'funcionarios_ativos': funcionarios_ativos,
            'funcionarios_inativos': funcionarios_inativos,
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
    
    return render(request, 'dashboard/usuarios_super_admin.html', context)


@login_required
def criar_usuario_super_admin(request):
    """Cria um novo usuário super administrador com senha gerada automaticamente"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard:principal')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validações básicas
        if not username or not email:
            messages.error(request, 'Nome de usuário e email são obrigatórios.')
            return redirect('dashboard:admin_usuarios_criar')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe.')
            return redirect('dashboard:admin_usuarios_criar')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já está em uso.')
            return redirect('dashboard:admin_usuarios_criar')
        
        try:
            # Usar transação para garantir consistência
            from django.db import transaction
            from django.utils import timezone
            import secrets
            import string
            
            with transaction.atomic():
                # Gerar senha provisória automaticamente
                password_chars = string.ascii_letters + string.digits + "!@#$%&*"
                provisional_password = ''.join(secrets.choice(password_chars) for _ in range(12))
                
                # Criar usuário (marcando para evitar signal de email)
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    is_superuser=True,
                    is_staff=True,
                    is_active=True
                )
                user.set_password(provisional_password)
                user._password_set_manually = True  # Marca antes de salvar
                user.save()
                
                # Criar ou atualizar perfil com requisito de troca de senha
                from usuarios.models import PerfilUsuario
                profile, created = PerfilUsuario.objects.get_or_create(
                    user=user,
                    defaults={
                        'is_super_admin': True,
                        'requires_password_change': True,
                        'provisional_password_created': timezone.now(),
                        'password_change_reminders_sent': 0
                    }
                )
                
                if not created:
                    profile.is_super_admin = True
                    profile.requires_password_change = True
                    profile.provisional_password_created = timezone.now()
                    profile.password_change_reminders_sent = 0
                    profile.save()
                
                # Enviar email com credenciais
                email_sent = False
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    subject = 'Credenciais de Acesso - LVK Sistemas'
                    message = f"""Olá {first_name or username},

Sua conta de Super Administrador foi criada no sistema LVK Sistemas.

DADOS DE ACESSO:
URL: https://www.lvksistemas.com.br/login/
Usuário: {username}
Senha provisória: {provisional_password}

IMPORTANTE:
- Esta é uma senha provisória que deve ser alterada no primeiro acesso
- Por segurança, você será obrigado a trocar a senha no primeiro login
- Mantenha suas credenciais em local seguro

Atenciosamente,
Equipe LVK Sistemas"""
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    email_sent = True
                    
                except Exception as email_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Erro ao enviar email para {email}: {str(email_error)}')
                
                # Log da criação
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Usuário super administrador "{username}" criado com sucesso por {request.user.username}')
            
            # Mensagem de sucesso
            if email_sent:
                messages.success(request, 
                    f'Usuário super administrador "{username}" criado com sucesso! '
                    f'As credenciais foram enviadas para o email {email}.')
            else:
                messages.success(request, 
                    f'Usuário super administrador "{username}" criado com sucesso! '
                    f'ATENÇÃO: Não foi possível enviar o email. '
                    f'Senha provisória: {provisional_password}')
            
            return redirect('dashboard:admin_usuarios_lista')
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao criar usuário super admin "{username}": {str(e)}')
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
    """Gera nova senha automática para um usuário super administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard:principal')
    
    user = get_object_or_404(User, id=user_id, is_superuser=True)
    
    if request.method == 'POST':
        # Apenas geração automática de senha é permitida
        if 'gerar_automatica' in request.POST:
            return gerar_senha_automatica_usuario(request, user)
        else:
            messages.error(request, 'Ação não permitida.')
            return redirect('dashboard:admin_usuarios_alterar_senha', user_id=user_id)
    
    context = {
        'usuario': user,
    }
    
    return render(request, 'dashboard/alterar_senha_usuario_super_admin.html', context)


def gerar_senha_automatica_usuario(request, user):
    """Gera senha automática e envia por email"""
    try:
        from django.db import transaction
        from django.utils import timezone
        import secrets
        import string
        
        with transaction.atomic():
            # Gerar nova senha provisória
            password_chars = string.ascii_letters + string.digits + "!@#$%&*"
            nova_senha_provisoria = ''.join(secrets.choice(password_chars) for _ in range(12))
            
            # Alterar senha do usuário
            user.set_password(nova_senha_provisoria)
            user.save()
            
            # Atualizar perfil para marcar troca obrigatória
            from usuarios.models import PerfilUsuario
            profile, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    'is_super_admin': True,
                    'requires_password_change': True,
                    'provisional_password_created': timezone.now(),
                    'password_change_reminders_sent': 0
                }
            )
            
            if not created:
                profile.requires_password_change = True
                profile.provisional_password_created = timezone.now()
                profile.password_change_reminders_sent = 0
                profile.save()
            
            # Enviar email com nova senha
            email_sent = False
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                subject = 'Nova Senha Provisória - LVK Sistemas'
                message = f"""Olá {user.first_name or user.username},

Uma nova senha provisória foi gerada para sua conta no sistema LVK Sistemas.

DADOS DE ACESSO:
URL: https://www.lvksistemas.com.br/login/
Usuário: {user.username}
Nova Senha Provisória: {nova_senha_provisoria}

IMPORTANTE:
- Esta é uma senha provisória que deve ser alterada no primeiro acesso
- Por segurança, você será obrigado a trocar a senha no primeiro login
- Sua senha anterior não funciona mais

Motivo: Solicitação de nova senha pelo administrador do sistema.

Atenciosamente,
Equipe LVK Sistemas"""
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                email_sent = True
                
            except Exception as email_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao enviar email para {user.email}: {str(email_error)}')
            
            # Log da alteração
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Nova senha provisória gerada para usuário "{user.username}" por {request.user.username}')
        
        # Mensagem de sucesso
        if email_sent:
            messages.success(request, 
                f'Nova senha provisória gerada para "{user.username}"! '
                f'As credenciais foram enviadas para o email {user.email}.')
        else:
            messages.success(request, 
                f'Nova senha provisória gerada para "{user.username}"! '
                f'ATENÇÃO: Não foi possível enviar o email. '
                f'Nova senha: {nova_senha_provisoria}')
        
        return redirect('dashboard:admin_usuarios_lista')
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar senha automática para "{user.username}": {str(e)}')
        messages.error(request, f'Erro ao gerar nova senha: {str(e)}')
        return redirect('dashboard:admin_usuarios_alterar_senha', user_id=user.id)


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


def dashboard_fatesa(request, loja):
    """Dashboard específico para FATESA - Sistema de Controle de Qualidade"""
    
    try:
        # Importar modelos do sistema de avaliação
        from avaliacao_qualidade.models import (
            Curso, Coordenador, Professor, AvaliacaoConfig, AvaliacaoResposta
        )
        from django.db.models import Avg, Count
        from datetime import timedelta
        
        # Estatísticas gerais
        total_cursos = Curso.objects.filter(ativo=True).count()
        total_coordenadores = Coordenador.objects.filter(ativo=True).count()
        total_professores = Professor.objects.filter(ativo=True).count()
        
        # Avaliações
        avaliacoes_ativas = AvaliacaoConfig.objects.filter(status='ativa').count()
        total_respostas = AvaliacaoResposta.objects.count()
        
        # Avaliações recentes
        avaliacoes_recentes = AvaliacaoConfig.objects.all().order_by('-data_criacao')[:10]
        
        # Respostas recentes
        respostas_recentes = AvaliacaoResposta.objects.all().order_by('-data_resposta')[:10]
        
        # Estatísticas por período
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        
        respostas_mes = AvaliacaoResposta.objects.filter(
            data_resposta__date__gte=inicio_mes
        ).count()
        
        # Médias gerais
        medias = AvaliacaoResposta.objects.aggregate(
            media_professor=Avg('nota_relacionamento_professor'),
            media_didatica=Avg('nota_didatica_professor'),
            media_dominio=Avg('nota_dominio_assunto'),
            media_teorico=Avg('nota_conteudo_teorico'),
            media_pratico=Avg('nota_atividade_pratica'),
            media_administracao=Avg('nota_portaria')
        )
        
        context = {
            'loja': loja,
            'total_cursos': total_cursos,
            'total_coordenadores': total_coordenadores,
            'total_professores': total_professores,
            'avaliacoes_ativas': avaliacoes_ativas,
            'total_respostas': total_respostas,
            'respostas_mes': respostas_mes,
            'avaliacoes_recentes': avaliacoes_recentes,
            'respostas_recentes': respostas_recentes,
            'medias': medias,
        }
        
        logger.info(f"Dashboard FATESA carregado para usuário {request.user.username}")
        return render(request, 'avaliacao_qualidade/dashboard_fatesa.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard FATESA: {str(e)}")
        # Em caso de erro, mostrar dashboard normal da loja
        messages.warning(request, 'Sistema FATESA temporariamente indisponível. Mostrando dashboard padrão.')
        
        # Retornar contexto básico para dashboard normal
        context = {
            'loja': loja,
            'total_clientes': 0,
            'total_produtos': 0,
            'vendas_hoje': 0,
            'receita_hoje': 0,
        }
        return render(request, 'dashboard/loja.html', context)

@login_required
def dashboard_fatesa(request, loja):
    """Dashboard personalizado para lojas do tipo controle de qualidade (FATESA)"""
    
    try:
        # Verificar se o usuário pode acessar esta loja
        if not AuthenticationService.can_access_store_dashboard(request.user, loja):
            logger.warning(f"Usuário {request.user.username} tentou acessar loja FATESA {loja.nome} sem permissão")
            messages.error(request, 'Você não tem permissão para acessar esta loja.')
            return redirect('login')
        
        # Obter contexto do dashboard
        dashboard_context = AuthenticationService.get_dashboard_context(request.user)
        
        # Estatísticas específicas para controle de qualidade
        context = {
            'loja': loja,
            'is_fatesa': True,
            'page_title': f'Dashboard - {loja.nome}',
            'user_type': dashboard_context['user_type'],
            'can_access_store': dashboard_context['can_access_store'],
        }
        
        # Tentar obter dados específicos do módulo de avaliação de qualidade
        try:
            from avaliacao_qualidade.models import Curso, Professor, Avaliacao
            
            # Estatísticas básicas
            total_cursos = Curso.objects.filter(loja=loja).count()
            total_professores = Professor.objects.filter(loja=loja).count()
            total_avaliacoes = Avaliacao.objects.filter(curso__loja=loja).count()
            
            # Adicionar ao contexto
            context.update({
                'total_cursos': total_cursos,
                'total_professores': total_professores,
                'total_avaliacoes': total_avaliacoes,
                'modulo_ativo': 'avaliacao_qualidade',
            })
            
        except Exception as e:
            logger.warning(f"Erro ao obter dados de avaliação de qualidade para loja {loja.nome}: {str(e)}")
            # Continuar com contexto básico
            context.update({
                'total_cursos': 0,
                'total_professores': 0,
                'total_avaliacoes': 0,
                'modulo_ativo': 'avaliacao_qualidade',
            })
        
        # Usar template específico do FATESA se existir
        template_paths = [
            'avaliacao_qualidade/dashboard_fatesa.html',
            'dashboard/loja_fatesa.html',
            'dashboard/loja.html'  # Fallback
        ]
        
        for template_path in template_paths:
            try:
                return render(request, template_path, context)
            except Exception:
                continue
        
        # Se nenhum template funcionar, usar o padrão
        logger.warning(f"Nenhum template específico encontrado para FATESA, usando template padrão")
        return render(request, 'dashboard/loja.html', context)
                
    except Exception as e:
        logger.error(f"Erro no dashboard FATESA para loja {loja.nome}: {str(e)}")
        messages.error(request, 'Erro interno ao carregar dashboard da loja. Tente novamente.')
        return redirect('login')