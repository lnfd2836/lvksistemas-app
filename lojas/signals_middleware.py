"""
Signal para criar middleware automaticamente quando loja é criada
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from lojas.models import Loja
from lojas.middleware.gerador_middleware_loja import MiddlewareLojaGenerator

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Loja)
def criar_middleware_loja(sender, instance, created, **kwargs):
    """
    Cria middleware exclusivo automaticamente quando loja é criada
    """
    if created:
        try:
            generator = MiddlewareLojaGenerator()
            resultado = generator.gerar_middleware_loja(instance)
            
            if resultado['success']:
                logger.info(f"Middleware criado automaticamente para loja: {instance.nome}")
                logger.info(f"Classe: {resultado['middleware_class']}")
                logger.info(f"Arquivo: {resultado['middleware_path']}")
                
                # Aqui você poderia adicionar lógica para:
                # 1. Atualizar settings.py dinamicamente
                # 2. Reiniciar servidor (em desenvolvimento)
                # 3. Notificar administradores
                
            else:
                logger.error(f"Falha ao criar middleware para loja {instance.nome}: {resultado['error']}")
                
        except Exception as e:
            logger.error(f"Erro no signal de criação de middleware: {str(e)}")


@receiver(post_delete, sender=Loja)
def remover_middleware_loja(sender, instance, **kwargs):
    """
    Remove middleware quando loja é deletada
    """
    try:
        generator = MiddlewareLojaGenerator()
        if generator.remover_middleware_loja(instance):
            logger.info(f"Middleware removido para loja deletada: {instance.nome}")
        
    except Exception as e:
        logger.error(f"Erro ao remover middleware da loja {instance.nome}: {str(e)}")
