from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View

from lojas.models import Loja
from lojas.models_login import LoginPersonalizado, HistoricoLoginLoja
from usuarios.models import LogAcesso, SessaoAtiva
from dashboard.services.authentication import AuthenticationService
import logging
import json

logger = logging.getLogger(__name__)


def login_personalizado_loja(request, url_personalizada=None, loja_id=None):
    """View para login personalizado por loja"""
    
    # Determinar qual loja usar
    loja = None
    login_config = None
    
    try:
        if url_personalizada:
            # Buscar por URL personalizada
            login_config = get_object_or_404(
                LoginPersonalizado, 
                url_personalizada=url_personalizada,
                ativo=True
            )
            loja = login_config.loja
        elif loja_id:
            # Buscar por ID da loja
            loja = get_object_or_404(Loja, id=loja_id, status='ativa')
            try:
                login_config = LoginPersonalizado.objects.get(loja=loja, ativo=True)
            except LoginPersonalizado.DoesNotExist:
                # Criar configuração padrão se não existir
                login_config = criar_login_padrao(loja)
        else:
            raise Http404("Loja não especificada")
        
        # Verificar se a loja está ativa
        if loja.status != 'ativa':
            messages.error(request, 'Esta loja está temporariamente indisponível.')
            return redirect('simple_login')
        
        # Se já está autenticado, verificar o tipo de usuário
        if request.user.is_authenticated:
            # Super admins não podem usar login de loja
            if request.user.is_superuser:
                logger.warning(f"Super usuário {request.user.username} tentou acessar login de loja")
                messages.error(request, 'Super administradores devem usar o login exclusivo do sistema.')
                from django.contrib.auth import logout
                logout(request)
                return redirect('simple_login')
            
            # Verificar se pode acessar esta loja específica
            if AuthenticationService.can_access_store_dashboard(request.user, loja):
                logger.info(f"Usuário {request.user.username} já autenticado para loja {loja.nome}")
                return redirect('dashboard:loja')
            else:
                # Se não pode acessar esta loja específica, fazer logout
                from django.contrib.auth import logout
                logout(request)
        
        # Processar login
        if request.method == 'POST':
            return processar_login_personalizado(request, loja, login_config)
        
        # Preparar contexto para o template
        context = {
            'loja': loja,
            'login_config': login_config,
            'css_variaveis': login_config.get_css_variaveis(),
            'login_url': login_config.get_login_url(),
        }
        
        # Usar template baseado no tema
        template_name = login_config.get_template_name()
        
        logger.info(f"Exibindo login personalizado para loja {loja.nome} (tema: {login_config.tema})")
        return render(request, template_name, context)
        
    except LoginPersonalizado.DoesNotExist:
        logger.error(f"Configuração de login não encontrada para URL: {url_personalizada}")
        messages.error(request, 'Página de login não encontrada.')
        return redirect('simple_login')
    except Loja.DoesNotExist:
        logger.error(f"Loja não encontrada - ID: {loja_id}, URL: {url_personalizada}")
        messages.error(request, 'Loja não encontrada.')
        return redirect('simple_login')
    except Exception as e:
        logger.error(f"Erro no login personalizado: {str(e)}")
        messages.error(request, 'Erro interno. Tente novamente.')
        return redirect('simple_login')


def processar_login_personalizado(request, loja, login_config):
    """Processa o login personalizado da loja"""
    
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    remember_me = request.POST.get('remember_me') == 'on'
    
    if not username or not password:
        messages.error(request, 'Por favor, preencha todos os campos.')
        return render(request, login_config.get_template_name(), {
            'loja': loja,
            'login_config': login_config,
            'css_variaveis': login_config.get_css_variaveis(),
        })
    
    # Registrar tentativa de login
    def registrar_tentativa(sucesso=False):
        try:
            HistoricoLoginLoja.objects.create(
                loja=loja,
                usuario=username,
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                sucesso=sucesso,
                metodo_login='personalizado'
            )
        except Exception as e:
            logger.error(f"Erro ao registrar tentativa de login: {str(e)}")
    
    try:
        logger.info(f"Tentativa de login personalizado - Loja: {loja.nome}, Username: {username}")
        
        # Tentar autenticar com username
        user = authenticate(request, username=username, password=password)
        
        # Se falhar, tentar com email
        if user is None and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
                logger.debug(f"Tentativa de autenticação por email para loja {loja.nome}")
            except User.DoesNotExist:
                logger.warning(f"Email {username} não encontrado para loja {loja.nome}")
        
        if user is not None:
            if not user.is_active:
                logger.warning(f"Usuário inativo tentou login na loja {loja.nome}: {user.username}")
                messages.error(request, 'Esta conta está desativada.')
                registrar_tentativa(False)
                return render(request, login_config.get_template_name(), {
                    'loja': loja,
                    'login_config': login_config,
                    'css_variaveis': login_config.get_css_variaveis(),
                })
            
            # Bloquear super admins no login de loja
            if user.is_superuser:
                logger.warning(f"Super usuário {user.username} tentou login via página de loja {loja.nome}")
                messages.error(request, 'Super administradores devem usar o login exclusivo do sistema.')
                registrar_tentativa(False)
                return render(request, login_config.get_template_name(), {
                    'loja': loja,
                    'login_config': login_config,
                    'css_variaveis': login_config.get_css_variaveis(),
                })
            
            # Verificar se o usuário pode acessar esta loja
            if not AuthenticationService.can_access_store_dashboard(user, loja):
                logger.warning(f"Usuário {user.username} tentou acessar loja {loja.nome} sem permissão")
                messages.error(request, 'Você não tem permissão para acessar esta loja.')
                registrar_tentativa(False)
                return render(request, login_config.get_template_name(), {
                    'loja': loja,
                    'login_config': login_config,
                    'css_variaveis': login_config.get_css_variaveis(),
                })
            
            # Verificar senha provisória
            verificar_senha_provisoria(user, password, loja)
            
            # Fazer login
            login(request, user)
            
            # Configurar sessão
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)  # Até fechar o navegador
            
            # Criar sessão ativa
            criar_sessao_ativa(request, user, loja)
            
            # Registrar sucesso
            registrar_tentativa(True)
            
            # Log de acesso
            LogAcesso.objects.create(
                user=user,
                acao='LOGIN_PERSONALIZADO',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                sucesso=True,
                observacoes=f"Loja: {loja.nome}"
            )
            
            logger.info(f"Login personalizado bem-sucedido - Loja: {loja.nome}, Usuário: {user.username}")
            
            # Mensagem de boas-vindas personalizada
            if login_config.mensagem_boas_vindas:
                messages.success(request, login_config.mensagem_boas_vindas)
            else:
                messages.success(request, f'Bem-vindo(a) à {loja.nome}!')
            
            # Redirecionar para dashboard da loja
            return redirect('dashboard:loja')
            
        else:
            logger.warning(f"Falha na autenticação - Loja: {loja.nome}, Username: {username}")
            registrar_tentativa(False)
            
            # Mensagem de erro personalizada
            if '@' in username:
                messages.error(request, 'Email ou senha incorretos.')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
            
            return render(request, login_config.get_template_name(), {
                'loja': loja,
                'login_config': login_config,
                'css_variaveis': login_config.get_css_variaveis(),
            })
            
    except Exception as e:
        logger.error(f"Erro durante login personalizado da loja {loja.nome}: {str(e)}")
        registrar_tentativa(False)
        messages.error(request, 'Erro interno durante o login. Tente novamente.')
        return render(request, login_config.get_template_name(), {
            'loja': loja,
            'login_config': login_config,
            'css_variaveis': login_config.get_css_variaveis(),
        })


def verificar_senha_provisoria(user, password, loja):
    """Verifica se é uma senha provisória e marca para troca"""
    try:
        if loja.admin_user == user and loja.senha_provisoria == password:
            from usuarios.models import PerfilUsuario
            profile, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={'requires_password_change': True}
            )
            if not created:
                profile.requires_password_change = True
                profile.save()
            logger.info(f"Senha provisória detectada para usuário {user.username} na loja {loja.nome}")
    except Exception as e:
        logger.error(f"Erro ao verificar senha provisória: {str(e)}")


def criar_sessao_ativa(request, user, loja):
    """Cria uma sessão ativa para o usuário"""
    try:
        # Remove sessões antigas do usuário
        SessaoAtiva.objects.filter(user=user).update(ativa=False)
        
        # Remove sessões com a mesma session_key
        session_key = request.session.session_key or f'no-session-{user.id}'
        SessaoAtiva.objects.filter(session_key=session_key).delete()
        
        # Cria nova sessão ativa
        SessaoAtiva.objects.create(
            user=user,
            session_key=session_key,
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ativa=True,
            is_super_admin=user.is_superuser
        )
    except Exception as e:
        logger.error(f"Erro ao criar sessão ativa: {str(e)}")


def criar_login_padrao(loja):
    """Cria uma configuração de login padrão para a loja"""
    try:
        login_config = LoginPersonalizado.objects.create(
            loja=loja,
            titulo=f"Login - {loja.nome}",
            subtitulo=f"Acesse sua conta na {loja.nome}",
            mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
            tema='padrao'
        )
        logger.info(f"Configuração de login padrão criada para loja {loja.nome}")
        return login_config
    except Exception as e:
        logger.error(f"Erro ao criar login padrão para loja {loja.nome}: {str(e)}")
        raise


@login_required
def gerenciar_login_personalizado(request, loja_id=None):
    """Gerencia as configurações de login personalizado"""
    
    # Verificar permissões
    if not request.user.is_superuser:
        # Verificar se é admin da loja
        if loja_id:
            loja = get_object_or_404(Loja, id=loja_id)
            if not AuthenticationService.can_access_store_dashboard(request.user, loja):
                messages.error(request, 'Você não tem permissão para gerenciar esta loja.')
                return redirect('dashboard:principal')
        else:
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('dashboard:principal')
    
    # Determinar loja
    if loja_id:
        loja = get_object_or_404(Loja, id=loja_id)
    else:
        # Super admin pode gerenciar qualquer loja
        if not request.user.is_superuser:
            messages.error(request, 'Loja não especificada.')
            return redirect('dashboard:principal')
        loja = None
    
    # Buscar ou criar configuração
    login_config = None
    if loja:
        try:
            login_config = LoginPersonalizado.objects.get(loja=loja)
        except LoginPersonalizado.DoesNotExist:
            login_config = criar_login_padrao(loja)
    
    if request.method == 'POST':
        return salvar_configuracao_login(request, loja, login_config)
    
    # Listar todas as configurações se for super admin sem loja específica
    if not loja and request.user.is_superuser:
        configuracoes = LoginPersonalizado.objects.all().order_by('loja__nome')
        context = {
            'configuracoes': configuracoes,
            'is_super_admin': True,
        }
        return render(request, 'lojas/gerenciar_logins_lista.html', context)
    
    # Formulário de edição
    context = {
        'loja': loja,
        'login_config': login_config,
        'temas': LoginPersonalizado.TEMA_CHOICES,
    }
    
    return render(request, 'lojas/gerenciar_login_personalizado.html', context)


def salvar_configuracao_login(request, loja, login_config):
    """Salva as configurações de login personalizado"""
    try:
        # Atualizar campos
        login_config.titulo = request.POST.get('titulo', login_config.titulo)
        login_config.subtitulo = request.POST.get('subtitulo', login_config.subtitulo)
        login_config.tema = request.POST.get('tema', login_config.tema)
        login_config.cor_primaria = request.POST.get('cor_primaria', login_config.cor_primaria)
        login_config.cor_secundaria = request.POST.get('cor_secundaria', login_config.cor_secundaria)
        login_config.cor_fundo = request.POST.get('cor_fundo', login_config.cor_fundo)
        login_config.cor_texto = request.POST.get('cor_texto', login_config.cor_texto)
        login_config.mensagem_boas_vindas = request.POST.get('mensagem_boas_vindas', login_config.mensagem_boas_vindas)
        login_config.mensagem_rodape = request.POST.get('mensagem_rodape', login_config.mensagem_rodape)
        login_config.css_personalizado = request.POST.get('css_personalizado', login_config.css_personalizado)
        
        # Checkboxes
        login_config.mostrar_logo = request.POST.get('mostrar_logo') == 'on'
        login_config.mostrar_nome_loja = request.POST.get('mostrar_nome_loja') == 'on'
        login_config.permitir_lembrar_senha = request.POST.get('permitir_lembrar_senha') == 'on'
        login_config.mostrar_link_recuperar_senha = request.POST.get('mostrar_link_recuperar_senha') == 'on'
        login_config.ativo = request.POST.get('ativo') == 'on'
        
        # Upload de arquivos
        if 'logo' in request.FILES:
            login_config.logo = request.FILES['logo']
        
        if 'imagem_fundo' in request.FILES:
            login_config.imagem_fundo = request.FILES['imagem_fundo']
        
        login_config.save()
        
        messages.success(request, 'Configurações de login atualizadas com sucesso!')
        logger.info(f"Configurações de login atualizadas para loja {loja.nome} por {request.user.username}")
        
        return redirect('lojas:gerenciar_login_personalizado', loja_id=loja.id)
        
    except Exception as e:
        logger.error(f"Erro ao salvar configurações de login para loja {loja.nome}: {str(e)}")
        messages.error(request, f'Erro ao salvar configurações: {str(e)}')
        return redirect('lojas:gerenciar_login_personalizado', loja_id=loja.id)


@login_required
def preview_login_personalizado(request, loja_id):
    """Preview do login personalizado"""
    loja = get_object_or_404(Loja, id=loja_id)
    
    # Verificar permissões
    if not request.user.is_superuser and not AuthenticationService.can_access_store_dashboard(request.user, loja):
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    try:
        login_config = LoginPersonalizado.objects.get(loja=loja)
    except LoginPersonalizado.DoesNotExist:
        login_config = criar_login_padrao(loja)
    
    context = {
        'loja': loja,
        'login_config': login_config,
        'css_variaveis': login_config.get_css_variaveis(),
        'is_preview': True,
    }
    
    return render(request, login_config.get_template_name(), context)


@login_required
def historico_login_loja(request, loja_id):
    """Exibe o histórico de logins da loja"""
    loja = get_object_or_404(Loja, id=loja_id)
    
    # Verificar permissões
    if not request.user.is_superuser and not AuthenticationService.can_access_store_dashboard(request.user, loja):
        messages.error(request, 'Você não tem permissão para ver este histórico.')
        return redirect('dashboard:principal')
    
    # Filtros
    filtro_usuario = request.GET.get('usuario', '')
    filtro_sucesso = request.GET.get('sucesso', '')
    
    historico = HistoricoLoginLoja.objects.filter(loja=loja)
    
    if filtro_usuario:
        historico = historico.filter(usuario__icontains=filtro_usuario)
    
    if filtro_sucesso == 'sim':
        historico = historico.filter(sucesso=True)
    elif filtro_sucesso == 'nao':
        historico = historico.filter(sucesso=False)
    
    historico = historico.order_by('-data_tentativa')[:100]  # Últimas 100 tentativas
    
    context = {
        'loja': loja,
        'historico': historico,
        'filtro_usuario': filtro_usuario,
        'filtro_sucesso': filtro_sucesso,
    }
    
    return render(request, 'lojas/historico_login_loja.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_validar_url_personalizada(request):
    """API para validar se uma URL personalizada está disponível"""
    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip().lower()
        loja_id = data.get('loja_id')
        
        if not url:
            return JsonResponse({'valida': False, 'erro': 'URL não pode estar vazia'})
        
        # Verificar se já existe
        query = LoginPersonalizado.objects.filter(url_personalizada=url)
        if loja_id:
            query = query.exclude(loja_id=loja_id)
        
        if query.exists():
            return JsonResponse({'valida': False, 'erro': 'Esta URL já está em uso'})
        
        return JsonResponse({'valida': True})
        
    except Exception as e:
        return JsonResponse({'valida': False, 'erro': 'Erro interno'})