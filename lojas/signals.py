"""
Signals para lojas - configuração automática de middleware e login personalizado
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Loja
from .models_login import LoginPersonalizado
from .middleware_loja_especifica import criar_middleware_para_loja

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Loja)
def configurar_loja_automaticamente(sender, instance, created, **kwargs):
    """
    Signal executado automaticamente quando uma loja é criada ou atualizada
    
    Configura automaticamente:
    - Login personalizado
    - Middleware específico
    - URLs personalizadas
    """
    
    try:
        if created:
            # Loja recém-criada
            logger.info(f"Nova loja criada: {instance.nome} (ID: {instance.id})")
            
            # Criar middleware e configuração de login automaticamente
            sucesso = criar_middleware_para_loja(instance)
            
            if sucesso:
                logger.info(f"Configuração automática concluída para loja {instance.nome}")
            else:
                logger.error(f"Erro na configuração automática da loja {instance.nome}")
        
        else:
            # Loja atualizada
            if instance.status == 'ativa':
                # Verificar se tem configuração de login
                try:
                    login_config = instance.login_personalizado
                    if not login_config.ativo:
                        login_config.ativo = True
                        login_config.save()
                        logger.info(f"Login reativado para loja {instance.nome}")
                except LoginPersonalizado.DoesNotExist:
                    # Criar configuração se não existir
                    criar_middleware_para_loja(instance)
                    logger.info(f"Configuração de login criada para loja existente {instance.nome}")
            
            elif instance.status == 'inativa':
                # Desativar login se loja foi desativada
                try:
                    login_config = instance.login_personalizado
                    if login_config.ativo:
                        login_config.ativo = False
                        login_config.save()
                        logger.info(f"Login desativado para loja {instance.nome}")
                except LoginPersonalizado.DoesNotExist:
                    pass
    
    except Exception as e:
        logger.error(f"Erro no signal de configuração da loja {instance.nome}: {str(e)}")


@receiver(post_delete, sender=Loja)
def limpar_configuracao_loja(sender, instance, **kwargs):
    """
    Signal executado quando uma loja é deletada
    
    Remove automaticamente:
    - Configurações de login personalizado
    - Sessões ativas relacionadas
    """
    
    try:
        logger.info(f"Loja deletada: {instance.nome} (ID: {instance.id})")
        
        # Remover configurações de login personalizado
        try:
            login_config = instance.login_personalizado
            login_config.delete()
            logger.info(f"Configuração de login removida para loja {instance.nome}")
        except LoginPersonalizado.DoesNotExist:
            pass
        
        # Remover sessões ativas relacionadas à loja
        try:
            from usuarios.models import SessaoAtiva
            sessoes_loja = SessaoAtiva.objects.filter(
                session_key__contains=f'loja-{instance.id}'
            )
            count = sessoes_loja.count()
            sessoes_loja.delete()
            
            if count > 0:
                logger.info(f"Removidas {count} sessões ativas da loja {instance.nome}")
        
        except Exception as e:
            logger.error(f"Erro ao remover sessões da loja {instance.nome}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Erro no signal de limpeza da loja {instance.nome}: {str(e)}")


@receiver(post_save, sender=LoginPersonalizado)
def atualizar_configuracao_login(sender, instance, created, **kwargs):
    """
    Signal executado quando uma configuração de login personalizado é criada ou atualizada
    """
    
    try:
        if created:
            logger.info(f"Nova configuração de login criada para loja {instance.loja.nome}")
            logger.info(f"URL de acesso: {instance.get_login_url()}")
        else:
            logger.info(f"Configuração de login atualizada para loja {instance.loja.nome}")
            
            # Se foi desativada, log de aviso
            if not instance.ativo:
                logger.warning(f"Login desativado para loja {instance.loja.nome}")
            elif instance.ativo:
                logger.info(f"Login ativado para loja {instance.loja.nome}")
    
    except Exception as e:
        logger.error(f"Erro no signal de configuração de login: {str(e)}")