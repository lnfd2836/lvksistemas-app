"""
Signals para envio automático de emails
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.conf import settings
import logging

from .models import PerfilUsuario
from .email_utils import enviar_email_credenciais_usuario, enviar_email_troca_senha_obrigatoria

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def enviar_email_criacao_usuario(sender, instance, created, **kwargs):
    """
    Envia email quando um novo usuário é criado
    """
    if created:
        try:
            # Gera senha provisória
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            senha_provisoria = ''.join(secrets.choice(alphabet) for _ in range(12))
            
            # Define a senha provisória
            instance.set_password(senha_provisoria)
            instance.save()
            
            # Determina o tipo de usuário
            tipo_usuario = "Usuário"
            if instance.is_superuser:
                tipo_usuario = "Super Administrador"
            elif hasattr(instance, 'perfil') and instance.perfil.is_loja_admin:
                tipo_usuario = "Administrador de Loja"
            
            # Envia email com credenciais
            sucesso = enviar_email_credenciais_usuario(
                user=instance,
                senha_provisoria=senha_provisoria,
                tipo_usuario=tipo_usuario
            )
            
            if sucesso:
                logger.info(f"Email de credenciais enviado para {instance.email}")
            else:
                logger.error(f"Falha ao enviar email de credenciais para {instance.email}")
                
        except Exception as e:
            logger.error(f"Erro ao processar criação de usuário {instance.username}: {e}")


@receiver(post_save, sender=PerfilUsuario)
def enviar_email_criacao_perfil(sender, instance, created, **kwargs):
    """
    Envia email quando um perfil de usuário é criado
    """
    if created and instance.is_super_admin:
        try:
            # Gera senha provisória para super admin
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            senha_provisoria = ''.join(secrets.choice(alphabet) for _ in range(12))
            
            # Define a senha provisória
            instance.user.set_password(senha_provisoria)
            instance.user.save()
            
            # Envia email com credenciais
            sucesso = enviar_email_credenciais_usuario(
                user=instance.user,
                senha_provisoria=senha_provisoria,
                tipo_usuario="Super Administrador"
            )
            
            if sucesso:
                logger.info(f"Email de credenciais de super admin enviado para {instance.user.email}")
            else:
                logger.error(f"Falha ao enviar email de credenciais de super admin para {instance.user.email}")
                
        except Exception as e:
            logger.error(f"Erro ao processar criação de perfil de super admin {instance.user.username}: {e}")


@receiver(user_logged_in)
def verificar_troca_senha_obrigatoria(sender, request, user, **kwargs):
    """
    Verifica se o usuário precisa trocar a senha no primeiro login
    """
    try:
        # Verifica se é o primeiro login (senha provisória)
        if hasattr(user, 'perfil'):
            # Se o usuário tem perfil, verifica se já fez login antes
            if not user.perfil.ultimo_acesso:
                # Primeiro login - obriga troca de senha
                logger.info(f"Primeiro login detectado para {user.username} - troca de senha obrigatória")
                
                # Envia email lembrando da troca de senha
                enviar_email_troca_senha_obrigatoria(user)
                
                # Marca que precisa trocar senha (implementar lógica específica)
                # Por enquanto, apenas loga a informação
                logger.info(f"Usuário {user.username} deve trocar a senha no primeiro login")
                
    except Exception as e:
        logger.error(f"Erro ao verificar troca de senha obrigatória para {user.username}: {e}")
