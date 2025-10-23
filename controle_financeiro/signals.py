"""
Signals para automação do sistema financeiro
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

from lojas.models import Loja
from .models import ControleFinanceiro, PlanoFinanceiro
from .asaas_service import AsaasService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Loja)
def criar_cobranca_asaas_automatica(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma cobrança do Asaas quando uma loja é criada
    """
    if created:  # Apenas para lojas recém-criadas
        try:
            logger.info(f"Nova loja criada: {instance.nome}. Gerando cobrança automática do Asaas...")
            
            # Usar get_or_create para evitar duplicatas
            from django.db import transaction
            with transaction.atomic():
                # Buscar plano padrão
                plano_padrao = PlanoFinanceiro.objects.filter(ativo=True).first()
                
                if not plano_padrao:
                    logger.warning(f"Nenhum plano ativo encontrado para loja {instance.nome}")
                    return
                
                # Usar get_or_create para evitar duplicatas
                controle, controle_created = ControleFinanceiro.objects.get_or_create(
                    loja=instance,
                    defaults={
                        'plano': plano_padrao,
                        'data_inicio': timezone.now(),
                        'data_vencimento': timezone.now() + timedelta(days=30),
                        'valor_mensal': plano_padrao.valor_mensal,
                        'status': 'ativo'
                    }
                )
                
                if controle_created:
                    logger.info(f"Controle financeiro criado para {instance.nome}")
                else:
                    logger.info(f"Controle financeiro já existe para {instance.nome}")
            
            # Gerar cobrança via API do Asaas
            asaas_service = AsaasService()
            
            # Verificar se API está funcionando
            if not asaas_service.validar_configuracao():
                logger.warning(f"API Asaas não configurada. Cobrança para {instance.nome} não foi gerada.")
                return
            
            # Gerar cobrança
            resultado = asaas_service.gerar_cobranca_com_pix(
                controle, 
                dias_vencimento=30,
                descricao=f"Primeira mensalidade - {instance.nome}"
            )
            
            if resultado.get('success'):
                cobranca_id = resultado['cobranca']['id']
                logger.info(f"✅ Cobrança Asaas {cobranca_id} gerada automaticamente para {instance.nome}")
            else:
                error_msg = resultado.get('error', 'Erro desconhecido')
                logger.error(f"❌ Erro ao gerar cobrança automática para {instance.nome}: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ Erro no signal de criação de cobrança para {instance.nome}: {str(e)}")


@receiver(post_save, sender=ControleFinanceiro)
def gerar_cobranca_ao_criar_controle(sender, instance, created, **kwargs):
    """
    Gera cobrança do Asaas quando um controle financeiro é criado
    """
    if created and instance.status == 'ativo':
        try:
            logger.info(f"Novo controle financeiro criado para {instance.loja.nome}. Gerando cobrança...")
            
            # Verificar se já existe cobrança para este controle
            from .models import CobrancaAsaas
            cobranca_existente = CobrancaAsaas.objects.filter(controle_financeiro=instance).exists()
            
            if cobranca_existente:
                logger.info(f"Cobrança já existe para {instance.loja.nome}")
                return
            
            # Gerar cobrança via API do Asaas
            asaas_service = AsaasService()
            
            if asaas_service.validar_configuracao():
                resultado = asaas_service.gerar_cobranca_com_pix(
                    instance, 
                    dias_vencimento=30,
                    descricao=f"Mensalidade {instance.plano.nome} - {instance.loja.nome}"
                )
                
                if resultado.get('success'):
                    cobranca_id = resultado['cobranca']['id']
                    logger.info(f"✅ Cobrança {cobranca_id} gerada para controle {instance.id}")
                else:
                    logger.error(f"❌ Erro ao gerar cobrança para controle {instance.id}")
            else:
                logger.warning(f"API Asaas não configurada para controle {instance.id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar cobrança para controle {instance.id}: {str(e)}")