"""
Serviço centralizado para envio de credenciais por email
"""
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Dict, Any, Optional
import logging

from .password_generator import PasswordGenerator
from .email_template_service import EmailTemplateService
from .email_sender import EmailSender
from .database_router import LojasDatabaseRouter

logger = logging.getLogger(__name__)


class EmailCredentialsService:
    """
    Serviço centralizado para criação e envio de credenciais por email
    """
    
    def __init__(self):
        """Inicializa o serviço"""
        self.password_generator = PasswordGenerator()
        self.template_service = EmailTemplateService()
        self.email_sender = EmailSender()
        self.db_router = LojasDatabaseRouter()
    
    def create_user_credentials(self, username: str, email: str, first_name: str, 
                               last_name: str, user_type: str, loja=None, 
                               created_by=None, **kwargs) -> Dict[str, Any]:
        """
        Cria usuário completo com credenciais e envia por email
        
        Args:
            username: Nome de usuário
            email: Email do usuário
            first_name: Primeiro nome
            last_name: Sobrenome
            user_type: Tipo do usuário ('super_admin', 'loja_admin', 'loja_user')
            loja: Instância da loja (opcional)
            created_by: Usuário que está criando (opcional)
            
        Returns:
            dict: Resultado da criação
        """
        try:
            # Verificar se usuário já existe
            if User.objects.filter(username=username).exists():
                return {
                    'success': False,
                    'message': f'Usuário {username} já existe',
                    'error': 'USER_EXISTS'
                }
            
            if User.objects.filter(email=email).exists():
                return {
                    'success': False,
                    'message': f'Email {email} já está em uso',
                    'error': 'EMAIL_EXISTS'
                }
            
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            
            # Preparar contexto
            context = {
                'loja': loja,
                'created_by': created_by,
                **kwargs
            }
            
            # Enviar credenciais
            result = self.send_credentials(user, user_type, context)
            
            # Adicionar informações do usuário criado
            result.update({
                'user_created': True,
                'username': username,
                'user_id': user.id
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao criar usuário {username}: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'error': str(e),
                'user_created': False
            }
    
    def send_password_recovery(self, email_or_username: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Alias para generate_and_send_recovery (compatibilidade)
        """
        return self.generate_and_send_recovery(email_or_username, context)
    
    def send_credentials(self, user: User, user_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Envia credenciais por email para qualquer tipo de usuário
        
        Args:
            user: Instância do User
            user_type: 'super_admin', 'loja_admin', 'loja_user'
            context: Dados adicionais (loja, módulo, etc.)
            
        Returns:
            dict: Resultado do envio
        """
        try:
            # Gerar senha provisória
            password = self.password_generator.generate_secure_password()
            
            # Definir senha no usuário
            user.set_password(password)
            user.save()
            
            # Criar/atualizar perfil estendido
            self._create_or_update_extended_profile(user, user_type, context)
            
            # Preparar contexto completo para email
            email_context = self._prepare_email_context(user, password, user_type, context)
            
            # Renderizar email
            email_data = self.template_service.render_email(user_type, email_context)
            
            # Enviar email
            result = self.email_sender.send_email(
                to_email=user.email,
                subject=email_data['subject'],
                html_content=email_data['html'],
                text_content=email_data['text'],
                context=email_context
            )
            
            # Log da operação
            self._log_credentials_sent(user, user_type, result['success'], context)
            
            return {
                'success': result['success'],
                'message': result['message'],
                'user': user,
                'password': password if not result['success'] else None,  # Só retorna senha se falhou
                'email_sent': result['success'],
                'fallback_used': result.get('fallback_used', False)
            }
            
        except Exception as e:
            error_msg = f"Erro ao enviar credenciais para {user.username}: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'error': str(e),
                'user': user,
                'password': None,
                'email_sent': False,
                'fallback_used': False
            }
    
    def generate_and_send_recovery(self, email_or_username: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gera nova senha provisória e envia por email (recuperação)
        
        Args:
            email_or_username: Email ou username do usuário
            context: Contexto adicional
            
        Returns:
            dict: Resultado da recuperação
        """
        try:
            # Buscar usuário
            user = self._find_user_by_email_or_username(email_or_username)
            if not user:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado',
                    'error': 'USER_NOT_FOUND'
                }
            
            # Verificar rate limiting
            if not self._check_recovery_rate_limit(user):
                return {
                    'success': False,
                    'message': 'Muitas tentativas de recuperação. Tente novamente mais tarde.',
                    'error': 'RATE_LIMITED'
                }
            
            # Gerar nova senha provisória
            password = self.password_generator.generate_secure_password()
            
            # Definir senha no usuário
            user.set_password(password)
            user.save()
            
            # Marcar como senha provisória
            self._mark_password_as_provisional(user)
            
            # Preparar contexto para email de recuperação
            email_context = self._prepare_recovery_context(user, password, context)
            
            # Renderizar email de recuperação
            email_data = self.template_service.render_email('recovery', email_context)
            
            # Enviar email
            result = self.email_sender.send_email(
                to_email=user.email,
                subject=email_data['subject'],
                html_content=email_data['html'],
                text_content=email_data['text'],
                context=email_context
            )
            
            # Log da recuperação
            self._log_password_recovery(user, result['success'], context)
            
            return {
                'success': result['success'],
                'message': 'Nova senha enviada por email' if result['success'] else result['message'],
                'user': user,
                'email_sent': result['success'],
                'fallback_used': result.get('fallback_used', False)
            }
            
        except Exception as e:
            error_msg = f"Erro na recuperação de senha para {email_or_username}: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }
    
    def resend_credentials(self, user: User, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Reenvia credenciais para usuário existente
        
        Args:
            user: Usuário para reenvio
            context: Contexto adicional
            
        Returns:
            dict: Resultado do reenvio
        """
        try:
            # Determinar tipo de usuário
            user_type = self._determine_user_type(user)
            
            # Gerar nova senha se necessário
            if not self._has_provisional_password(user):
                password = self.password_generator.generate_secure_password()
                user.set_password(password)
                user.save()
                self._mark_password_as_provisional(user)
            else:
                # Usar senha existente (não podemos recuperá-la)
                password = "[SENHA ATUAL]"
            
            # Preparar contexto
            email_context = self._prepare_email_context(user, password, user_type, context)
            
            # Renderizar email
            email_data = self.template_service.render_email(user_type, email_context)
            
            # Enviar email
            result = self.email_sender.send_email(
                to_email=user.email,
                subject=email_data['subject'],
                html_content=email_data['html'],
                text_content=email_data['text'],
                context=email_context
            )
            
            return {
                'success': result['success'],
                'message': result['message'],
                'user': user,
                'email_sent': result['success']
            }
            
        except Exception as e:
            error_msg = f"Erro ao reenviar credenciais para {user.username}: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }
    
    def _create_or_update_extended_profile(self, user: User, user_type: str, context: Optional[Dict[str, Any]]):
        """
        Cria ou atualiza perfil estendido do usuário
        """
        try:
            from .models import ExtendedUserProfile
            
            # Obter loja do contexto
            loja = context.get('loja') if context else None
            
            # Criar ou atualizar perfil
            profile, created = ExtendedUserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': user_type,
                    'has_provisional_password': True,
                    'provisional_password_created': timezone.now(),
                    'associated_loja': loja,
                    'database_alias': self.db_router.get_loja_database_alias(loja.id) if loja else 'default'
                }
            )
            
            if not created:
                # Atualizar perfil existente
                profile.has_provisional_password = True
                profile.provisional_password_created = timezone.now()
                if loja and not profile.associated_loja:
                    profile.associated_loja = loja
                    profile.database_alias = self.db_router.get_loja_database_alias(loja.id)
                profile.save()
            
            # Criar perfil específico da loja se necessário
            if loja and user_type in ['loja_admin', 'loja_user']:
                self._create_loja_user_profile(user, loja, context)
            
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar perfil estendido para {user.username}: {str(e)}")
    
    def _create_loja_user_profile(self, user: User, loja, context: Optional[Dict[str, Any]]):
        """
        Cria perfil do usuário no banco específico da loja
        """
        try:
            # Definir contexto da loja para roteamento
            self.db_router.set_loja_context(loja.id)
            
            # Importar modelo específico da loja
            from .models import LojaUserProfile
            
            # Obter perfil de acesso do contexto
            access_profile = context.get('access_profile', 'user') if context else 'user'
            
            # Criar perfil no banco da loja
            loja_profile, created = LojaUserProfile.objects.using(
                self.db_router.get_loja_database_alias(loja.id)
            ).get_or_create(
                user_id=user.id,
                defaults={
                    'username': user.username,
                    'loja_access_profile': access_profile,
                    'permissions': {},
                    'settings': {}
                }
            )
            
            if created:
                logger.info(f"Perfil da loja criado para {user.username} na loja {loja.nome}")
            
        except Exception as e:
            logger.error(f"Erro ao criar perfil da loja para {user.username}: {str(e)}")
        finally:
            # Limpar contexto
            self.db_router.clear_loja_context()
    
    def _prepare_email_context(self, user: User, password: str, user_type: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepara contexto completo para renderização do email
        """
        email_context = {
            'user': user,
            'password': password,
            'user_type': user_type,
            'first_name': user.first_name or user.username,
            'username': user.username,
            'email': user.email,
        }
        
        # Adicionar contexto fornecido
        if context:
            email_context.update(context)
        
        return email_context
    
    def _prepare_recovery_context(self, user: User, password: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepara contexto para email de recuperação
        """
        recovery_context = {
            'user': user,
            'password': password,
            'first_name': user.first_name or user.username,
            'username': user.username,
            'email': user.email,
            'is_recovery': True,
        }
        
        # Adicionar contexto fornecido
        if context:
            recovery_context.update(context)
        
        return recovery_context
    
    def _find_user_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        """
        Busca usuário por email ou username
        """
        try:
            # Tentar por email primeiro
            if '@' in email_or_username:
                return User.objects.get(email=email_or_username)
            else:
                return User.objects.get(username=email_or_username)
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Se múltiplos usuários, pegar o primeiro ativo
            if '@' in email_or_username:
                return User.objects.filter(email=email_or_username, is_active=True).first()
            else:
                return User.objects.filter(username=email_or_username, is_active=True).first()
    
    def _check_recovery_rate_limit(self, user: User) -> bool:
        """
        Verifica rate limiting para recuperação de senha
        """
        try:
            from .models import EmailLog
            from datetime import timedelta
            
            # Verificar tentativas na última hora
            one_hour_ago = timezone.now() - timedelta(hours=1)
            recent_attempts = EmailLog.objects.filter(
                user=user,
                email_type='recovery',
                sent_at__gte=one_hour_ago
            ).count()
            
            # Máximo 3 tentativas por hora
            return recent_attempts < 3
            
        except Exception as e:
            logger.warning(f"Erro ao verificar rate limit: {str(e)}")
            return True  # Permitir em caso de erro
    
    def _mark_password_as_provisional(self, user: User):
        """
        Marca senha como provisória
        """
        try:
            from .models import ExtendedUserProfile
            
            profile, created = ExtendedUserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'has_provisional_password': True,
                    'provisional_password_created': timezone.now()
                }
            )
            
            if not created:
                profile.has_provisional_password = True
                profile.provisional_password_created = timezone.now()
                profile.save()
                
        except Exception as e:
            logger.error(f"Erro ao marcar senha como provisória: {str(e)}")
    
    def _has_provisional_password(self, user: User) -> bool:
        """
        Verifica se usuário tem senha provisória
        """
        try:
            from .models import ExtendedUserProfile
            
            profile = ExtendedUserProfile.objects.get(user=user)
            return profile.has_provisional_password
            
        except:
            return False
    
    def _determine_user_type(self, user: User) -> str:
        """
        Determina o tipo do usuário baseado em suas características
        """
        if user.is_superuser:
            return 'super_admin'
        
        # Verificar se é admin de loja
        if hasattr(user, 'loja_admin'):
            return 'loja_admin'
        
        # Verificar perfil estendido
        try:
            from .models import ExtendedUserProfile
            profile = ExtendedUserProfile.objects.get(user=user)
            return profile.user_type
        except:
            pass
        
        # Default
        return 'loja_user'
    
    def _log_credentials_sent(self, user: User, user_type: str, success: bool, context: Optional[Dict[str, Any]]):
        """
        Log do envio de credenciais
        """
        try:
            loja = context.get('loja') if context else None
            logger.info(f"Credenciais {'enviadas' if success else 'falharam'} para {user.username} "
                       f"(tipo: {user_type}, loja: {loja.nome if loja else 'N/A'})")
        except Exception as e:
            logger.warning(f"Erro ao fazer log de credenciais: {str(e)}")
    
    def _log_password_recovery(self, user: User, success: bool, context: Optional[Dict[str, Any]]):
        """
        Log da recuperação de senha
        """
        try:
            logger.info(f"Recuperação de senha {'bem-sucedida' if success else 'falhou'} para {user.username}")
        except Exception as e:
            logger.warning(f"Erro ao fazer log de recuperação: {str(e)}")