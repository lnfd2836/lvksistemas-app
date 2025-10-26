"""
Middleware exclusivo para lojas específicas - criado automaticamente quando uma loja é criada
"""
import logging
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import resolve, Resolver404
from django.http import HttpResponse
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from dashboard.services.authentication import AuthenticationService

logger = logging.getLogger(__name__)


class LojaEspecificaMiddleware:
    """
    Middleware exclusivo para gerenciar login de lojas específicas
    
    Este middleware é criado automaticamente quando uma loja é criada
    e gerencia apenas o login dessa loja específica.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que este middleware deve processar
        self.loja_login_patterns = [
            '/login/',  # URLs de login personalizado
        ]
    
    def __call__(self, request):
        """
        Processa requisições para lojas específicas
        """
        try:
            # Verificar se é uma URL de login de loja
            if self._is_loja_login_url(request.path):
                return self._handle_loja_login(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no LojaEspecificaMiddleware: {str(e)}")
            return self.get_response(request)
    
    def _is_loja_login_url(self, path):
        """Verifica se é uma URL de login de loja"""
        return path.startswith('/login/') and path != '/login/'
    
    def _handle_loja_login(self, request):
        """Manipula login específico de loja"""
        
        try:
            # Extrair identificador da loja da URL
            path_parts = request.path.strip('/').split('/')
            
            if len(path_parts) >= 2 and path_parts[0] == 'login':
                url_personalizada = path_parts[1]
                
                # Buscar loja por URL personalizada
                loja = self._find_loja_by_url(url_personalizada)
                
                if not loja:
                    logger.warning(f"Loja não encontrada para URL: {url_personalizada}")
                    messages.error(request, 'Loja não encontrada.')
                    return redirect('/')
                
                # Verificar se loja está ativa
                if loja.status != 'ativa':
                    logger.warning(f"Tentativa de acesso a loja inativa: {loja.nome}")
                    messages.error(request, 'Esta loja está temporariamente indisponível.')
                    return redirect('/')
                
                # Buscar configuração de login
                try:
                    login_config = loja.login_personalizado
                    
                    if not login_config.ativo:
                        messages.error(request, 'Login desta loja está temporariamente indisponível.')
                        return redirect('/')
                    
                    # Processar login se for POST
                    if request.method == 'POST':
                        return self._processar_login_loja(request, loja, login_config)
                    
                    # Mostrar página de login
                    return self._mostrar_login_loja(request, loja, login_config)
                    
                except LoginPersonalizado.DoesNotExist:
                    # Criar configuração padrão automaticamente
                    login_config = self._criar_login_padrao(loja)
                    return self._mostrar_login_loja(request, loja, login_config)
            
            # Se chegou aqui, não conseguiu processar
            return redirect('/')
            
        except Exception as e:
            logger.error(f"Erro ao processar login de loja: {str(e)}")
            messages.error(request, 'Erro interno. Tente novamente.')
            return redirect('/')
    
    def _find_loja_by_url(self, url_personalizada):
        """Encontra loja por URL personalizada"""
        
        try:
            # Buscar por URL personalizada
            login_config = LoginPersonalizado.objects.get(
                url_personalizada=url_personalizada,
                ativo=True
            )
            return login_config.loja
            
        except LoginPersonalizado.DoesNotExist:
            # Tentar buscar por ID se for UUID
            try:
                return Loja.objects.get(id=url_personalizada, status='ativa')
            except (Loja.DoesNotExist, ValueError):
                return None
    
    def _mostrar_login_loja(self, request, loja, login_config):
        """Mostra a página de login da loja"""
        
        # Verificar se super admin está tentando acessar
        if request.user.is_authenticated and request.user.is_superuser:
            logger.info(f"Super admin {request.user.username} acessando login de loja {loja.nome}")
            # Permitir visualização para super admins (para administração)
        
        # Verificar se usuário já está autenticado para esta loja
        elif request.user.is_authenticated:
            if AuthenticationService.can_access_store_dashboard(request.user, loja):
                logger.info(f"Usuário {request.user.username} já autenticado para loja {loja.nome}")
                return redirect('dashboard:loja')
            else:
                # Usuário autenticado mas não para esta loja - fazer logout
                from django.contrib.auth import logout
                logout(request)
        
        # Preparar contexto
        context = {
            'loja': loja,
            'login_config': login_config,
            'css_variaveis': login_config.get_css_variaveis(),
            'login_url': login_config.get_login_url(),
            'is_loja_login': True,
        }
        
        # Usar template baseado no tema
        template_name = login_config.get_template_name()
        
        logger.info(f"Exibindo login personalizado para loja {loja.nome} (tema: {login_config.tema})")
        return render(request, template_name, context)
    
    def _processar_login_loja(self, request, loja, login_config):
        """Processa o login da loja"""
        
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return self._mostrar_login_loja(request, loja, login_config)
        
        try:
            # Bloquear super admins de fazer login via loja
            if request.user.is_authenticated and request.user.is_superuser:
                logger.warning(f"Super admin {request.user.username} tentou fazer login via loja {loja.nome}")
                messages.error(request, 'Super administradores devem usar o login exclusivo do sistema.')
                return redirect('/admin/')
            
            # Tentar autenticar
            user = authenticate(request, username=username, password=password)
            
            # Se falhar, tentar com email
            if user is None and '@' in username:
                try:
                    from django.contrib.auth.models import User
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Esta conta está desativada.')
                    return self._mostrar_login_loja(request, loja, login_config)
                
                # Bloquear super admins
                if user.is_superuser:
                    logger.warning(f"Super usuário {user.username} tentou login via loja {loja.nome}")
                    messages.error(request, 'Super administradores devem usar o login exclusivo do sistema.')
                    return redirect('/admin/')
                
                # Verificar se pode acessar esta loja
                if not AuthenticationService.can_access_store_dashboard(user, loja):
                    logger.warning(f"Usuário {user.username} tentou acessar loja {loja.nome} sem permissão")
                    messages.error(request, 'Você não tem permissão para acessar esta loja.')
                    return self._mostrar_login_loja(request, loja, login_config)
                
                # Fazer login
                login(request, user)
                logger.info(f"Login bem-sucedido na loja {loja.nome}: {user.username}")
                
                # Criar sessão ativa
                self._criar_sessao_ativa(request, user, loja)
                
                # Mensagem de boas-vindas
                if login_config.mensagem_boas_vindas:
                    messages.success(request, login_config.mensagem_boas_vindas)
                else:
                    messages.success(request, f'Bem-vindo(a) à {loja.nome}!')
                
                # Redirecionar para dashboard da loja
                return redirect('dashboard:loja_especifica', loja_id=loja.id)
                
            else:
                logger.warning(f"Falha na autenticação na loja {loja.nome}: {username}")
                messages.error(request, 'Usuário ou senha incorretos.')
                
        except Exception as e:
            logger.error(f"Erro durante login na loja {loja.nome}: {str(e)}")
            messages.error(request, 'Erro interno durante o login. Tente novamente.')
        
        return self._mostrar_login_loja(request, loja, login_config)
    
    def _criar_login_padrao(self, loja):
        """Cria configuração de login padrão para a loja"""
        
        try:
            login_config = LoginPersonalizado.objects.create(
                loja=loja,
                titulo=f"Login - {loja.nome}",
                subtitulo=f"Acesse sua conta na {loja.nome}",
                mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                tema='padrao',
                ativo=True
            )
            logger.info(f"Configuração de login padrão criada para loja {loja.nome}")
            return login_config
            
        except Exception as e:
            logger.error(f"Erro ao criar login padrão para loja {loja.nome}: {str(e)}")
            raise
    
    def _criar_sessao_ativa(self, request, user, loja):
        """Cria sessão ativa para o usuário da loja"""
        
        try:
            from usuarios.models import SessaoAtiva, LogAcesso
            
            # Remove sessões antigas
            SessaoAtiva.objects.filter(user=user).update(ativa=False)
            
            # Cria nova sessão
            session_key = request.session.session_key or f'loja-{loja.id}-{user.id}'
            SessaoAtiva.objects.filter(session_key=session_key).delete()
            
            SessaoAtiva.objects.create(
                user=user,
                session_key=session_key,
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ativa=True,
                is_super_admin=False
            )
            
            # Log de acesso
            LogAcesso.objects.create(
                user=user,
                acao='LOGIN_LOJA',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                sucesso=True,
                observacoes=f'Loja: {loja.nome}'
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão para usuário {user.username} na loja {loja.nome}: {str(e)}")


def criar_middleware_para_loja(loja):
    """
    Função para criar middleware específico para uma loja
    (chamada automaticamente quando uma loja é criada)
    """
    
    try:
        # Verificar se já existe configuração de login
        try:
            login_config = loja.login_personalizado
            logger.info(f"Configuração de login já existe para loja {loja.nome}")
        except LoginPersonalizado.DoesNotExist:
            # Criar configuração padrão
            login_config = LoginPersonalizado.objects.create(
                loja=loja,
                titulo=f"Login - {loja.nome}",
                subtitulo=f"Acesse sua conta na {loja.nome}",
                mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                tema='padrao',
                ativo=True
            )
            logger.info(f"Configuração de login criada automaticamente para loja {loja.nome}")
        
        # O middleware LojaEspecificaMiddleware já está configurado globalmente
        # e vai processar automaticamente as URLs desta loja
        
        logger.info(f"Middleware configurado para loja {loja.nome}: {login_config.get_login_url()}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar middleware para loja {loja.nome}: {str(e)}")
        return False