"""
Signals para automação de processos de assinatura digital
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import AssinaturaDigital
from .services.assinatura_validator import AssinaturaDataValidator

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AssinaturaDigital)
def handle_signature_completion(sender, instance, created, **kwargs):
    """
    Signal handler para processar automações após assinatura
    
    Ações executadas:
    1. Quando cliente assina, solicita assinatura da empresa
    2. Quando empresa assina após cliente, envia notificação de conclusão
    """
    # Só processar se não foi recém criado (evitar loops)
    if created:
        return
    
    try:
        # Verificar se a assinatura foi completada (status mudou para 'assinado')
        if instance.status != 'assinado' or not instance.data_assinatura:
            return
        
        # Processar assinatura do cliente
        if instance.tipo_signatario == 'cliente':
            _handle_client_signature_completion(instance)
        
        # Processar assinatura da empresa
        elif instance.tipo_signatario == 'empresa':
            _handle_company_signature_completion(instance)
            
    except Exception as e:
        logger.error(f"Erro no signal handler de assinatura: {str(e)}")


def _handle_client_signature_completion(assinatura_cliente):
    """
    Processa a conclusão da assinatura do cliente
    """
    try:
        # Validar se a assinatura do cliente está realmente completa
        if not AssinaturaDataValidator.validate_client_signature_completion(assinatura_cliente):
            logger.warning(f"Assinatura do cliente não está completa: {assinatura_cliente.id}")
            return
        
        # Obter documento associado
        documento = _get_documento_from_assinatura(assinatura_cliente)
        if not documento:
            logger.error(f"Documento não encontrado para assinatura: {assinatura_cliente.id}")
            return
        
        # Importar função de solicitação de assinatura da empresa
        from .views import _solicitar_assinatura_empresa_automatica
        
        # Solicitar assinatura da empresa automaticamente
        _solicitar_assinatura_empresa_automatica(documento, assinatura_cliente.tipo_documento)
        
        logger.info(f"Processo automático de assinatura da empresa iniciado para {assinatura_cliente.tipo_documento} {documento.numero}")
        
    except Exception as e:
        logger.error(f"Erro ao processar assinatura do cliente: {str(e)}")


def _handle_company_signature_completion(assinatura_empresa):
    """
    Processa a conclusão da assinatura da empresa
    """
    try:
        # Obter documento associado
        documento = _get_documento_from_assinatura(assinatura_empresa)
        if not documento:
            logger.error(f"Documento não encontrado para assinatura da empresa: {assinatura_empresa.id}")
            return
        
        # Verificar se o cliente também já assinou
        if _check_client_signature_exists(documento, assinatura_empresa.tipo_documento):
            # Importar função de envio de documento final
            from .views import _enviar_documento_final_assinado
            
            # Enviar notificação de documento totalmente assinado
            _enviar_documento_final_assinado(documento, assinatura_empresa.tipo_documento)
            
            logger.info(f"Documento totalmente assinado - notificação enviada para {assinatura_empresa.tipo_documento} {documento.numero}")
        
    except Exception as e:
        logger.error(f"Erro ao processar assinatura da empresa: {str(e)}")


def _get_documento_from_assinatura(assinatura):
    """
    Obtém o documento associado à assinatura
    """
    try:
        if assinatura.tipo_documento == 'orcamento' and assinatura.orcamento:
            return assinatura.orcamento
        elif assinatura.tipo_documento == 'proposta' and assinatura.proposta:
            return assinatura.proposta
        elif assinatura.tipo_documento == 'contrato' and assinatura.contrato:
            return assinatura.contrato
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao obter documento da assinatura: {str(e)}")
        return None


def _check_client_signature_exists(documento, tipo_documento):
    """
    Verifica se existe assinatura do cliente para o documento
    """
    try:
        filter_kwargs = {
            'tipo_signatario': 'cliente',
            'tipo_documento': tipo_documento,
            'status': 'assinado',
            tipo_documento: documento
        }
        
        return AssinaturaDigital.objects.filter(**filter_kwargs).exists()
        
    except Exception as e:
        logger.error(f"Erro ao verificar assinatura do cliente: {str(e)}")
        return False