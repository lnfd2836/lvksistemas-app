"""
Signals do CRM de Vendas
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Lead, Orcamento, ItemOrcamento, Proposta, Contrato, HistoricoContato
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lead)
def lead_criado(sender, instance, created, **kwargs):
    """Signal executado quando um lead é criado"""
    if created:
        logger.info(f"Novo lead criado: {instance.nome} - {instance.email}")
        
        # Criar histórico inicial
        HistoricoContato.objects.create(
            lead=instance,
            tipo='outros',
            assunto='Lead Criado',
            descricao=f'Lead {instance.nome} foi criado no sistema',
            resultado='Lead adicionado ao pipeline',
            data_contato=timezone.now()
        )


@receiver(pre_save, sender=Lead)
def lead_status_alterado(sender, instance, **kwargs):
    """Signal executado antes de salvar um lead (para detectar mudança de status)"""
    if instance.pk:  # Se não é um novo lead
        try:
            lead_anterior = Lead.objects.get(pk=instance.pk)
            if lead_anterior.status != instance.status:
                logger.info(f"Status do lead {instance.nome} alterado de {lead_anterior.status} para {instance.status}")
                
                # Criar histórico da mudança de status
                HistoricoContato.objects.create(
                    lead=instance,
                    tipo='outros',
                    assunto='Status Alterado',
                    descricao=f'Status alterado de {lead_anterior.get_status_display()} para {instance.get_status_display()}',
                    resultado=f'Lead movido para {instance.get_status_display()}',
                    data_contato=timezone.now()
                )
        except Lead.DoesNotExist:
            pass


@receiver(post_save, sender=Orcamento)
def orcamento_criado(sender, instance, created, **kwargs):
    """Signal executado quando um orçamento é criado"""
    if created:
        logger.info(f"Novo orçamento criado: {instance.numero} para {instance.lead.nome}")
        
        # Atualizar status do lead
        if instance.lead.status in ['novo', 'contatado', 'qualificado']:
            instance.lead.status = 'proposta_enviada'
            instance.lead.save()
        
        # Criar histórico
        HistoricoContato.objects.create(
            lead=instance.lead,
            tipo='email',
            assunto='Orçamento Criado',
            descricao=f'Orçamento {instance.numero} foi criado',
            resultado='Orçamento preparado para envio',
            data_contato=timezone.now()
        )


@receiver(post_save, sender=ItemOrcamento)
def item_orcamento_salvo(sender, instance, **kwargs):
    """Signal executado quando um item de orçamento é salvo"""
    # Atualizar totais do orçamento
    orcamento = instance.orcamento
    
    # Calcular subtotal
    subtotal = sum(item.valor_total for item in orcamento.itens.all())
    
    # Calcular total (subtotal - desconto + impostos)
    total = subtotal - orcamento.desconto + orcamento.impostos
    
    # Atualizar orçamento
    Orcamento.objects.filter(id=orcamento.id).update(
        subtotal=subtotal,
        total=total
    )


@receiver(post_save, sender=Proposta)
def proposta_criada(sender, instance, created, **kwargs):
    """Signal executado quando uma proposta é criada"""
    if created:
        logger.info(f"Nova proposta criada: {instance.numero} para {instance.lead.nome}")
        
        # Atualizar status do lead
        if instance.lead.status != 'negociacao':
            instance.lead.status = 'negociacao'
            instance.lead.save()


@receiver(post_save, sender=Contrato)
def contrato_criado(sender, instance, created, **kwargs):
    """Signal executado quando um contrato é criado"""
    if created:
        logger.info(f"Novo contrato criado: {instance.numero} para {instance.lead.nome}")
        
        # Atualizar status do lead para fechado ganho
        instance.lead.status = 'fechado_ganho'
        instance.lead.save()
        
        # Criar histórico
        HistoricoContato.objects.create(
            lead=instance.lead,
            tipo='reuniao',
            assunto='Contrato Criado',
            descricao=f'Contrato {instance.numero} foi criado e está pronto para assinatura',
            resultado='Negócio fechado - contrato gerado',
            data_contato=timezone.now()
        )


@receiver(pre_save, sender=Orcamento)
def orcamento_status_alterado(sender, instance, **kwargs):
    """Signal executado antes de salvar um orçamento"""
    if instance.pk:
        try:
            orcamento_anterior = Orcamento.objects.get(pk=instance.pk)
            if orcamento_anterior.status != instance.status:
                logger.info(f"Status do orçamento {instance.numero} alterado para {instance.status}")
                
                # Criar histórico baseado no novo status
                if instance.status == 'enviado':
                    assunto = 'Orçamento Enviado'
                    descricao = f'Orçamento {instance.numero} foi enviado por email'
                    resultado = 'Aguardando resposta do cliente'
                elif instance.status == 'visualizado':
                    assunto = 'Orçamento Visualizado'
                    descricao = f'Cliente visualizou o orçamento {instance.numero}'
                    resultado = 'Cliente demonstrou interesse'
                elif instance.status == 'aprovado':
                    assunto = 'Orçamento Aprovado'
                    descricao = f'Cliente aprovou o orçamento {instance.numero}'
                    resultado = 'Orçamento aprovado - preparar contrato'
                    # Atualizar lead
                    instance.lead.status = 'fechado_ganho'
                    instance.lead.save()
                elif instance.status == 'rejeitado':
                    assunto = 'Orçamento Rejeitado'
                    descricao = f'Cliente rejeitou o orçamento {instance.numero}'
                    resultado = 'Orçamento rejeitado - analisar motivos'
                else:
                    assunto = 'Status do Orçamento Alterado'
                    descricao = f'Status do orçamento {instance.numero} alterado para {instance.get_status_display()}'
                    resultado = f'Orçamento em {instance.get_status_display()}'
                
                HistoricoContato.objects.create(
                    lead=instance.lead,
                    tipo='email',
                    assunto=assunto,
                    descricao=descricao,
                    resultado=resultado,
                    data_contato=timezone.now()
                )
        except Orcamento.DoesNotExist:
            pass