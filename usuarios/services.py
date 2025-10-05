"""
Serviços de autenticação centralizados para o sistema de lojas.
"""
from typing import Optional, Tuple
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Serviço centralizado para gerenciar autenticação e determinação de dashboards.
    """
    
    @staticmethod
    def determine_user_dashboard(user: User) -> str:
        """
        Determina qual dashboard o usuário deve acessar baseado no seu tipo e associações.
        
        Args:
            user: Usuário autenticado
            
        Returns:
            Nome da URL do dashboard apropriado
        """
        try:
            # Verifica se é super usuário
            if user.is_superuser:
                # Verifica se tem loja associada
                if hasattr(user, 'loja_admin'):
                    try:
                        loja = user.loja_admin
                        if loja:
                            logger.info(f"Super admin {user.username} tem loja associada: {loja.nome}")
                            return 'dashboard_loja'
                    except Exception as e:
                        logger.warning(f"Erro ao verificar loja do super admin {user.username}: {e}")
                
                # Super admin sem loja associada
                logger.info(f"Super admin {user.username} sem loja associada, redirecionando para dashboard super admin")
                return 'dashboard:super_admin'
            
            # Usuário comum - verifica se tem loja associada
            if hasattr(user, 'loja_admin'):
                try:
                    loja = user.loja_admin
                    if loja:
                        logger.info(f"Usuário {user.username} tem loja associada: {loja.nome}")
                        return 'dashboard_loja'
                except Exception as e:
                    logger.warning(f"Erro ao verificar loja do usuário {user.username}: {e}")
            
            # Usuário sem loja associada
            logger.warning(f"Usuário {user.username} não tem loja associada")
            return 'login'  # Redireciona para login com erro
            
        except Exception as e:
            logger.error(f"Erro ao determinar dashboard para usuário {user.username}: {e}")
            return 'login'
    
    @staticmethod
    def can_access_store_dashboard(user: User, store=None) -> Tuple[bool, str]:
        """
        Verifica se o usuário pode acessar o dashboard de uma loja específica.
        
        Args:
            user: Usuário a ser verificado
            store: Loja específica (opcional)
            
        Returns:
            Tupla (pode_acessar, mensagem_erro)
        """
        try:
            if not user.is_authenticated:
                return False, "Usuário não autenticado"
            
            # Super usuários podem acessar qualquer loja
            if user.is_superuser:
                return True, ""
            
            # Usuários comuns só podem acessar sua própria loja
            if hasattr(user, 'loja_admin'):
                try:
                    user_store = user.loja_admin
                    if not user_store:
                        return False, "Usuário não tem loja associada"
                    
                    # Se uma loja específica foi fornecida, verifica se é a mesma
                    if store and user_store != store:
                        return False, "Usuário não tem permissão para acessar esta loja"
                    
                    return True, ""
                    
                except Exception as e:
                    logger.error(f"Erro ao verificar loja do usuário {user.username}: {e}")
                    return False, "Erro ao verificar associação com loja"
            
            return False, "Usuário não tem loja associada"
            
        except Exception as e:
            logger.error(f"Erro ao verificar acesso à loja para usuário {user.username}: {e}")
            return False, "Erro interno na verificação de permissões"
    
    @staticmethod
    def get_user_store(user: User) -> Optional['Loja']:
        """
        Obtém a loja associada ao usuário de forma segura.
        
        Args:
            user: Usuário
            
        Returns:
            Objeto Loja ou None se não houver associação
        """
        try:
            if hasattr(user, 'loja_admin'):
                return user.loja_admin
        except Exception as e:
            logger.error(f"Erro ao obter loja do usuário {user.username}: {e}")
        
        return None
    
    @staticmethod
    def validate_user_permissions(user: User, required_permission: str) -> bool:
        """
        Valida se o usuário tem a permissão necessária.
        
        Args:
            user: Usuário a ser verificado
            required_permission: Permissão necessária ('super_admin', 'store_admin', 'authenticated')
            
        Returns:
            True se o usuário tem a permissão, False caso contrário
        """
        try:
            if not user.is_authenticated:
                return False
            
            if required_permission == 'super_admin':
                return user.is_superuser
            
            elif required_permission == 'store_admin':
                return AuthenticationService.get_user_store(user) is not None
            
            elif required_permission == 'authenticated':
                return True
            
            else:
                logger.warning(f"Permissão desconhecida solicitada: {required_permission}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao validar permissões para usuário {user.username}: {e}")
            return False
    
    @staticmethod
    def get_safe_redirect_url(user: User, default_url: str = 'login') -> str:
        """
        Obtém uma URL de redirecionamento segura baseada no tipo de usuário.
        
        Args:
            user: Usuário autenticado
            default_url: URL padrão caso não seja possível determinar
            
        Returns:
            Nome da URL para redirecionamento
        """
        try:
            if user.is_authenticated:
                return AuthenticationService.determine_user_dashboard(user)
            else:
                return default_url
        except Exception as e:
            logger.error(f"Erro ao obter URL de redirecionamento segura: {e}")
            return default_url
    
    @staticmethod
    def handle_authentication_error(request, error_message: str, redirect_url: str = 'login'):
        """
        Manipula erros de autenticação de forma consistente.
        
        Args:
            request: Objeto de requisição Django
            error_message: Mensagem de erro para o usuário
            redirect_url: URL para redirecionamento
            
        Returns:
            HttpResponse de redirecionamento
        """
        try:
            messages.error(request, error_message)
            logger.warning(f"Erro de autenticação: {error_message}")
            return redirect(redirect_url)
        except Exception as e:
            logger.error(f"Erro ao manipular erro de autenticação: {e}")
            return redirect('simple_login')


class SessionService:
    """
    Serviço para gerenciamento seguro de sessões de usuários.
    """
    
    @staticmethod
    def create_user_session(request, user: User) -> bool:
        """
        Cria uma nova sessão para o usuário de forma segura.
        
        Args:
            request: Objeto de requisição Django
            user: Usuário para criar a sessão
            
        Returns:
            True se a sessão foi criada com sucesso, False caso contrário
        """
        try:
            # Garante que a sessão existe
            if not request.session.session_key:
                request.session.create()
            
            session_key = request.session.session_key
            
            if not session_key:
                logger.error(f"Falha ao criar session_key para usuário {user.username}")
                return False
            
            # Importa aqui para evitar circular import
            from usuarios.models import SessaoAtiva
            from django.db import IntegrityError
            
            # Invalida sessões anteriores do usuário (sessão única)
            SessionService.invalidate_user_sessions(user, session_key)
            
            # Verifica se já existe uma sessão ativa com esta session_key
            existing_session = SessaoAtiva.objects.filter(session_key=session_key).first()
            if existing_session:
                if existing_session.user == user:
                    # Sessão já existe para o mesmo usuário, apenas reativa
                    existing_session.ativa = True
                    existing_session.is_super_admin = user.is_superuser
                    existing_session.save()
                    logger.info(f"Sessão existente reativada para usuário {user.username}")
                    return True
                else:
                    # Sessão existe para outro usuário, invalida e cria nova
                    existing_session.ativa = False
                    existing_session.save()
                    logger.warning(f"Sessão {session_key} estava associada a outro usuário, invalidando")
            
            try:
                # Cria nova sessão ativa
                SessaoAtiva.objects.create(
                    user=user,
                    session_key=session_key,
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    ativa=True,
                    is_super_admin=user.is_superuser
                )
                
                logger.info(f"Sessão criada com sucesso para usuário {user.username}")
                return True
                
            except IntegrityError as e:
                # Se ainda houver erro de integridade, tenta atualizar a sessão existente
                logger.warning(f"Erro de integridade ao criar sessão para {user.username}, tentando atualizar existente: {e}")
                
                try:
                    existing_session = SessaoAtiva.objects.get(session_key=session_key)
                    existing_session.user = user
                    existing_session.ativa = True
                    existing_session.is_super_admin = user.is_superuser
                    existing_session.ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
                    existing_session.user_agent = request.META.get('HTTP_USER_AGENT', '')
                    existing_session.save()
                    
                    logger.info(f"Sessão existente atualizada para usuário {user.username}")
                    return True
                    
                except Exception as update_error:
                    logger.error(f"Erro ao atualizar sessão existente para {user.username}: {update_error}")
                    return False
            
        except Exception as e:
            logger.error(f"Erro geral ao criar sessão para usuário {user.username}: {e}")
            return False
    
    @staticmethod
    def validate_session(request) -> bool:
        """
        Valida se a sessão atual é válida e ativa.
        
        Args:
            request: Objeto de requisição Django
            
        Returns:
            True se a sessão é válida, False caso contrário
        """
        try:
            if not request.user.is_authenticated:
                return False
            
            session_key = request.session.session_key
            if not session_key:
                logger.warning(f"Session key não encontrada para usuário {request.user.username}")
                # Tenta criar uma nova sessão se não existir
                if SessionService.create_user_session(request, request.user):
                    logger.info(f"Nova sessão criada durante validação para usuário {request.user.username}")
                    return True
                return False
            
            # Importa aqui para evitar circular import
            from usuarios.models import SessaoAtiva
            
            # Verifica se existe uma sessão ativa válida
            try:
                sessao_ativa = SessaoAtiva.objects.get(
                    user=request.user,
                    session_key=session_key,
                    ativa=True
                )
                
                # Atualiza a última atividade
                sessao_ativa.save()  # Isso atualiza o campo ultima_atividade
                logger.debug(f"Sessão validada com sucesso para usuário {request.user.username}")
                return True
                
            except SessaoAtiva.DoesNotExist:
                logger.warning(f"Sessão ativa não encontrada para usuário {request.user.username}")
                # Tenta criar uma nova sessão
                if SessionService.create_user_session(request, request.user):
                    logger.info(f"Nova sessão criada após validação falhar para usuário {request.user.username}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Erro ao validar sessão: {e}")
            return False
    
    @staticmethod
    def invalidate_user_sessions(user: User, exclude_current: str = None):
        """
        Invalida todas as sessões de um usuário, opcionalmente excluindo a atual.
        
        Args:
            user: Usuário cujas sessões devem ser invalidadas
            exclude_current: Session key da sessão atual para não invalidar
        """
        try:
            # Importa aqui para evitar circular import
            from usuarios.models import SessaoAtiva
            
            query = SessaoAtiva.objects.filter(user=user, ativa=True)
            
            if exclude_current:
                query = query.exclude(session_key=exclude_current)
            
            # Pega as sessões antes de invalidar para logging
            sessions_to_invalidate = list(query.values_list('session_key', flat=True))
            
            invalidated_count = query.update(ativa=False)
            
            if invalidated_count > 0:
                logger.info(f"Invalidadas {invalidated_count} sessões para usuário {user.username}: {sessions_to_invalidate}")
            else:
                logger.debug(f"Nenhuma sessão ativa encontrada para invalidar para usuário {user.username}")
            
        except Exception as e:
            logger.error(f"Erro ao invalidar sessões do usuário {user.username}: {e}")
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Remove sessões que não existem mais no banco de sessões do Django.
        """
        try:
            # Importa aqui para evitar circular import
            from usuarios.models import SessaoAtiva
            
            # Pega todas as chaves de sessão ativas no nosso modelo
            sessoes_ativas = SessaoAtiva.objects.filter(ativa=True).values_list('session_key', flat=True)
            
            # Pega todas as sessões que ainda existem no Django
            sessoes_django = Session.objects.values_list('session_key', flat=True)
            
            # Remove sessões que não existem mais no Django
            sessoes_para_remover = set(sessoes_ativas) - set(sessoes_django)
            
            if sessoes_para_remover:
                removed_count = SessaoAtiva.objects.filter(
                    session_key__in=sessoes_para_remover
                ).update(ativa=False)
                
                logger.info(f"Limpas {removed_count} sessões expiradas")
            
            # Remove sessões muito antigas (mais de 30 dias)
            cutoff_date = timezone.now() - timedelta(days=30)
            old_sessions = SessaoAtiva.objects.filter(
                data_login__lt=cutoff_date,
                ativa=False
            )
            
            old_count = old_sessions.count()
            if old_count > 0:
                old_sessions.delete()
                logger.info(f"Removidas {old_count} sessões antigas do banco")
                
        except Exception as e:
            logger.error(f"Erro ao limpar sessões expiradas: {e}")
    
    @staticmethod
    def get_active_sessions_count(user: User) -> int:
        """
        Retorna o número de sessões ativas para um usuário.
        
        Args:
            user: Usuário para contar sessões
            
        Returns:
            Número de sessões ativas
        """
        try:
            # Importa aqui para evitar circular import
            from usuarios.models import SessaoAtiva
            
            return SessaoAtiva.objects.filter(user=user, ativa=True).count()
            
        except Exception as e:
            logger.error(f"Erro ao contar sessões ativas para usuário {user.username}: {e}")
            return 0
    
    @staticmethod
    def force_logout_user(user: User, reason: str = "Logout forçado"):
        """
        Força o logout de um usuário invalidando todas as suas sessões.
        
        Args:
            user: Usuário para forçar logout
            reason: Motivo do logout forçado
        """
        try:
            SessionService.invalidate_user_sessions(user)
            logger.info(f"Logout forçado para usuário {user.username}: {reason}")
            
        except Exception as e:
            logger.error(f"Erro ao forçar logout do usuário {user.username}: {e}")
    
    @staticmethod
    def is_session_expired(session_key: str, max_age_hours: int = 24) -> bool:
        """
        Verifica se uma sessão está expirada baseada na idade.
        
        Args:
            session_key: Chave da sessão
            max_age_hours: Idade máxima em horas (padrão: 24h)
            
        Returns:
            True se a sessão está expirada, False caso contrário
        """
        try:
            # Importa aqui para evitar circular import
            from usuarios.models import SessaoAtiva
            
            sessao = SessaoAtiva.objects.get(session_key=session_key, ativa=True)
            
            # Verifica se a sessão é muito antiga
            cutoff_time = timezone.now() - timedelta(hours=max_age_hours)
            
            return sessao.ultima_atividade < cutoff_time
            
        except SessaoAtiva.DoesNotExist:
            return True  # Se não existe, considera expirada
        except Exception as e:
            logger.error(f"Erro ao verificar expiração da sessão {session_key}: {e}")
            return True  # Em caso de erro, considera expirada por segurança


class RedirectLoopPreventionService:
    """
    Serviço para detectar e prevenir loops de redirecionamento.
    """
    
    # Configurações
    MAX_REDIRECTS = 3
    REDIRECT_TRACKING_KEY = '_redirect_tracking'
    LOOP_DETECTION_KEY = '_loop_detection'
    
    @staticmethod
    def track_redirect(request, target_url: str) -> bool:
        """
        Rastreia um redirecionamento e verifica se está criando um loop.
        
        Args:
            request: Objeto de requisição Django
            target_url: URL de destino do redirecionamento
            
        Returns:
            True se o redirecionamento é seguro, False se detectou loop
        """
        try:
            # Inicializa o rastreamento se não existir
            if RedirectLoopPreventionService.REDIRECT_TRACKING_KEY not in request.session:
                request.session[RedirectLoopPreventionService.REDIRECT_TRACKING_KEY] = {
                    'count': 0,
                    'urls': [],
                    'last_url': '',
                    'start_time': timezone.now().isoformat()
                }
            
            tracking = request.session[RedirectLoopPreventionService.REDIRECT_TRACKING_KEY]
            
            # Verifica se é o mesmo URL consecutivo (loop direto)
            if tracking['last_url'] == target_url:
                tracking['count'] += 1
                
                if tracking['count'] >= RedirectLoopPreventionService.MAX_REDIRECTS:
                    logger.warning(f"Loop de redirecionamento detectado: {target_url} (tentativa {tracking['count']})")
                    return False
            else:
                # URL diferente, reseta o contador mas mantém histórico
                tracking['count'] = 1
                tracking['urls'].append(target_url)
                
                # Mantém apenas os últimos 10 URLs para não sobrecarregar a sessão
                if len(tracking['urls']) > 10:
                    tracking['urls'] = tracking['urls'][-10:]
            
            tracking['last_url'] = target_url
            request.session[RedirectLoopPreventionService.REDIRECT_TRACKING_KEY] = tracking
            request.session.modified = True
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao rastrear redirecionamento: {e}")
            return True  # Em caso de erro, permite o redirecionamento
    
    @staticmethod
    def detect_circular_pattern(request) -> bool:
        """
        Detecta padrões circulares nos redirecionamentos.
        
        Args:
            request: Objeto de requisição Django
            
        Returns:
            True se detectou padrão circular, False caso contrário
        """
        try:
            if RedirectLoopPreventionService.REDIRECT_TRACKING_KEY not in request.session:
                return False
            
            tracking = request.session[RedirectLoopPreventionService.REDIRECT_TRACKING_KEY]
            urls = tracking.get('urls', [])
            
            if len(urls) < 4:  # Precisa de pelo menos 4 URLs para detectar padrão
                return False
            
            # Verifica se há padrão A->B->A->B
            recent_urls = urls[-4:]
            if len(set(recent_urls)) == 2 and recent_urls[0] == recent_urls[2] and recent_urls[1] == recent_urls[3]:
                logger.warning(f"Padrão circular detectado: {recent_urls}")
                return True
            
            # Verifica se há muitos redirecionamentos em pouco tempo
            if len(urls) >= 5:
                logger.warning(f"Muitos redirecionamentos detectados: {len(urls)} URLs")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao detectar padrão circular: {e}")
            return False
    
    @staticmethod
    def clear_redirect_tracking(request):
        """
        Limpa o rastreamento de redirecionamentos da sessão.
        
        Args:
            request: Objeto de requisição Django
        """
        try:
            if RedirectLoopPreventionService.REDIRECT_TRACKING_KEY in request.session:
                del request.session[RedirectLoopPreventionService.REDIRECT_TRACKING_KEY]
                request.session.modified = True
                logger.debug("Rastreamento de redirecionamentos limpo")
                
        except Exception as e:
            logger.error(f"Erro ao limpar rastreamento de redirecionamentos: {e}")
    
    @staticmethod
    def handle_redirect_loop(request, loop_type: str = "generic") -> 'HttpResponse':
        """
        Manipula um loop de redirecionamento detectado.
        
        Args:
            request: Objeto de requisição Django
            loop_type: Tipo de loop detectado
            
        Returns:
            HttpResponse apropriada para quebrar o loop
        """
        try:
            # Limpa o rastreamento
            RedirectLoopPreventionService.clear_redirect_tracking(request)
            
            # Se o usuário está autenticado, força logout para quebrar o loop
            if hasattr(request, 'user') and request.user.is_authenticated:
                from django.contrib.auth import logout
                
                logger.warning(f"Loop de redirecionamento detectado para usuário {request.user.username}. Forçando logout.")
                
                messages.error(
                    request, 
                    'Detectamos um problema na sua sessão. Por favor, faça login novamente.'
                )
                
                logout(request)
            else:
                messages.error(
                    request,
                    'Ocorreu um problema no redirecionamento. Tente fazer login novamente.'
                )
            
            # Redireciona para login com parâmetro especial
            return redirect('simple_login')
            
        except Exception as e:
            logger.error(f"Erro ao manipular loop de redirecionamento: {e}")
            return redirect('simple_login')
    
    @staticmethod
    def is_safe_redirect(request, target_url: str) -> bool:
        """
        Verifica se um redirecionamento é seguro (não vai causar loop).
        
        Args:
            request: Objeto de requisição Django
            target_url: URL de destino
            
        Returns:
            True se o redirecionamento é seguro, False caso contrário
        """
        try:
            # Verifica se não está criando loop direto
            if not RedirectLoopPreventionService.track_redirect(request, target_url):
                return False
            
            # Verifica se não há padrão circular
            if RedirectLoopPreventionService.detect_circular_pattern(request):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar segurança do redirecionamento: {e}")
            return True  # Em caso de erro, permite o redirecionamento
    
    @staticmethod
    def safe_redirect(request, target_url: str, fallback_url: str = 'login') -> 'HttpResponse':
        """
        Executa um redirecionamento seguro com verificação de loops.
        
        Args:
            request: Objeto de requisição Django
            target_url: URL de destino preferida
            fallback_url: URL de fallback se houver problema
            
        Returns:
            HttpResponse de redirecionamento seguro
        """
        try:
            if RedirectLoopPreventionService.is_safe_redirect(request, target_url):
                return redirect(target_url)
            else:
                logger.warning(f"Redirecionamento inseguro detectado para {target_url}, usando fallback {fallback_url}")
                return RedirectLoopPreventionService.handle_redirect_loop(request, "unsafe_redirect")
                
        except Exception as e:
            logger.error(f"Erro no redirecionamento seguro: {e}")
            return redirect(fallback_url)