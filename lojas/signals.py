"""
Signals para envio automático de emails na criação de lojas
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import logging

from .models import Loja
from usuarios.email_utils import enviar_email_credenciais_loja, enviar_email_notificacao_admin

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Loja)
def enviar_email_criacao_loja(sender, instance, created, **kwargs):
    """
    Envia email quando uma nova loja é criada
    """
    if created:
        try:
            # Envia email com credenciais para o administrador da loja
            sucesso = enviar_email_credenciais_loja(
                loja=instance,
                senha_provisoria=instance.senha_provisoria
            )
            
            if sucesso:
                logger.info(f"Email de credenciais da loja enviado para {instance.email}")
            else:
                logger.error(f"Falha ao enviar email de credenciais da loja para {instance.email}")
            
            # Envia notificação para super administradores
            try:
                super_admins = User.objects.filter(
                    is_superuser=True,
                    is_active=True
                ).exclude(id=instance.admin_user.id)
                
                for admin in super_admins:
                    detalhes = {
                        'tipo_acao': 'Nova Loja Criada',
                        'usuario_responsavel': f"{instance.admin_user.first_name} {instance.admin_user.last_name}",
                        'data_hora': timezone.now().strftime('%d/%m/%Y às %H:%M'),
                        'detalhes_adicionais': f"Loja: {instance.nome} (CNPJ: {instance.cnpj})"
                    }
                    
                    enviar_email_notificacao_admin(
                        admin_user=admin,
                        tipo_acao='criacao_loja',
                        detalhes=detalhes
                    )
                    
                logger.info(f"Notificações de nova loja enviadas para {super_admins.count()} super administradores")
                
            except Exception as e:
                logger.error(f"Erro ao enviar notificações para super administradores: {e}")
                
        except Exception as e:
            logger.error(f"Erro ao processar criação de loja {instance.nome}: {e}")
