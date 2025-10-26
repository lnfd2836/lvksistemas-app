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
    Envia email quando uma nova loja é criada e cria perfil FATESA se necessário
    """
    if created:
        try:
            logger.info(f"Processando criação da loja: {instance.nome} ({instance.email})")
            
            # Garantir vinculação correta do admin à loja (isolamento total)
            if instance.admin_user:
                try:
                    from .utils.admin_vinculacao import vincular_admin_loja, criar_perfil_fatesa_se_necessario
                    
                    # Vincular admin à loja
                    resultado_vinculacao = vincular_admin_loja(instance, instance.admin_user)
                    if resultado_vinculacao['success']:
                        logger.info(f"✅ {resultado_vinculacao['message']}")
                    else:
                        logger.warning(f"⚠️  {resultado_vinculacao['message']}")
                    
                    # Criar perfil FATESA se for a loja específica
                    resultado_fatesa = criar_perfil_fatesa_se_necessario(instance, instance.admin_user)
                    if resultado_fatesa['success']:
                        logger.info(f"✅ {resultado_fatesa['message']}")
                        if resultado_fatesa.get('perfil_criado'):
                            logger.info(f"🎓 Perfil FATESA ID {resultado_fatesa.get('perfil_id')} criado para loja {instance.nome}")
                    else:
                        logger.error(f"❌ {resultado_fatesa['message']}")
                        
                except Exception as vinculacao_error:
                    logger.error(f"❌ Erro na vinculação automática para loja {instance.nome}: {vinculacao_error}")
                    # Não falha a criação da loja por causa disso
            
            # Envia email com credenciais para o administrador da loja
            try:
                logger.info(f"Tentando enviar email de credenciais para loja {instance.nome}")
                sucesso = enviar_email_credenciais_loja(
                    loja=instance,
                    senha_provisoria=instance.senha_provisoria
                )
                
                if sucesso:
                    logger.info(f"✅ Email de credenciais da loja enviado com sucesso para {instance.email}")
                else:
                    logger.warning(f"⚠️  Falha ao enviar email de credenciais da loja para {instance.email}")
                    logger.info(f"📧 Credenciais da loja {instance.nome}: Email: {instance.email}, Senha: {instance.senha_provisoria}")
                    
            except Exception as email_error:
                logger.error(f"❌ Erro ao enviar email de credenciais da loja {instance.nome}: {email_error}")
                logger.info(f"📧 Credenciais da loja {instance.nome}: Email: {instance.email}, Senha: {instance.senha_provisoria}")
                logger.info(f"ℹ️  Loja {instance.nome} foi criada com sucesso, mas o email não foi enviado")
            
            # Envia notificação para super administradores
            try:
                logger.info(f"Enviando notificações para super administradores sobre nova loja: {instance.nome}")
                super_admins = User.objects.filter(
                    is_superuser=True,
                    is_active=True
                ).exclude(id=instance.admin_user.id if instance.admin_user else None)
                
                if super_admins.exists():
                    for admin in super_admins:
                        try:
                            detalhes = {
                                'tipo_acao': 'Nova Loja Criada',
                                'usuario_responsavel': f"{instance.admin_user.first_name} {instance.admin_user.last_name}" if instance.admin_user else "Sistema",
                                'data_hora': timezone.now().strftime('%d/%m/%Y às %H:%M'),
                                'detalhes_adicionais': f"Loja: {instance.nome} (CNPJ: {instance.cnpj})"
                            }
                            
                            sucesso_notif = enviar_email_notificacao_admin(
                                admin_user=admin,
                                tipo_acao='criacao_loja',
                                detalhes=detalhes
                            )
                            
                            if sucesso_notif:
                                logger.info(f"✅ Notificação enviada para super admin {admin.username}")
                            else:
                                logger.warning(f"⚠️  Falha ao enviar notificação para super admin {admin.username}")
                                
                        except Exception as notif_error:
                            logger.error(f"❌ Erro ao enviar notificação para super admin {admin.username}: {notif_error}")
                    
                    logger.info(f"ℹ️  Processadas notificações para {super_admins.count()} super administradores")
                else:
                    logger.info("ℹ️  Nenhum super administrador encontrado para notificar")
                
            except Exception as notif_error:
                logger.error(f"❌ Erro ao processar notificações para super administradores: {notif_error}")
                logger.info(f"ℹ️  Loja {instance.nome} foi criada com sucesso, mas as notificações falharam")
                
        except Exception as e:
            logger.error(f"❌ Erro geral ao processar criação de loja {instance.nome}: {e}")
            logger.info(f"ℹ️  Loja pode ter sido criada, mas houve problemas no processamento de emails")
