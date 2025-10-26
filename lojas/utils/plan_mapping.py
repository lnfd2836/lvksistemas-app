"""
Utilities for mapping between PlanoComercial and PlanoFinanceiro models.
This module handles the conversion and synchronization between the two plan systems.
"""

from django.db import transaction
from planos.models import PlanoComercial
from controle_financeiro.models import PlanoFinanceiro


def get_or_create_plano_financeiro_from_comercial(plano_comercial):
    """
    Gets or creates a PlanoFinanceiro based on a PlanoComercial.
    
    Args:
        plano_comercial (PlanoComercial): The commercial plan to map from
        
    Returns:
        PlanoFinanceiro: The corresponding financial plan
    """
    try:
        # Verificar se plano_comercial não é None
        if not plano_comercial:
            raise ValueError("PlanoComercial não pode ser None")
        
        # Verificar se tem os atributos necessários
        if not hasattr(plano_comercial, 'nome') or not plano_comercial.nome:
            raise ValueError("PlanoComercial deve ter um nome válido")
        
        # Try to find existing PlanoFinanceiro with same name and price
        plano_financeiro = PlanoFinanceiro.objects.filter(
            nome=plano_comercial.nome,
            valor_mensal=plano_comercial.preco_mensal
        ).first()
        
        if plano_financeiro:
            return plano_financeiro
        
        # Create new PlanoFinanceiro based on PlanoComercial
        plano_financeiro = PlanoFinanceiro.objects.create(
            nome=plano_comercial.nome,
            descricao=plano_comercial.descricao or f"Plano {plano_comercial.nome}",
            valor_mensal=plano_comercial.preco_mensal,
            dias_trial=30,  # Default trial period
            ativo=plano_comercial.status == 'ativo'
        )
        
        return plano_financeiro
        
    except Exception as e:
        raise Exception(f"Error creating PlanoFinanceiro from PlanoComercial: {str(e)}")


def sync_plano_financeiro_with_comercial(plano_comercial):
    """
    Synchronizes an existing PlanoFinanceiro with PlanoComercial data.
    
    Args:
        plano_comercial (PlanoComercial): The commercial plan to sync from
        
    Returns:
        PlanoFinanceiro: The updated financial plan
    """
    try:
        plano_financeiro = PlanoFinanceiro.objects.filter(
            nome=plano_comercial.nome
        ).first()
        
        if plano_financeiro:
            # Update existing PlanoFinanceiro
            plano_financeiro.descricao = plano_comercial.descricao
            plano_financeiro.valor_mensal = plano_comercial.preco_mensal
            plano_financeiro.ativo = plano_comercial.status == 'ativo'
            plano_financeiro.save()
            return plano_financeiro
        else:
            # Create new one if not found
            return get_or_create_plano_financeiro_from_comercial(plano_comercial)
            
    except Exception as e:
        raise Exception(f"Error syncing PlanoFinanceiro with PlanoComercial: {str(e)}")


def create_both_financial_records(loja, plano_comercial, dia_vencimento=None):
    """
    Creates both ControleFinanceiro and AssinaturaLoja records for a store.
    
    Args:
        loja (Loja): The store to create records for
        plano_comercial (PlanoComercial): The selected commercial plan
        dia_vencimento (int): Dia do mês para vencimento (1-28, opcional)
        
    Returns:
        tuple: (ControleFinanceiro, AssinaturaLoja) instances
    """
    from controle_financeiro.models import ControleFinanceiro
    from planos.models import AssinaturaLoja
    from django.utils import timezone
    from datetime import timedelta, datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        with transaction.atomic():
            # Validar plano_comercial
            if not plano_comercial:
                raise ValueError("É obrigatório selecionar um plano comercial")
            
            logger.info(f"Criando registros financeiros para loja {loja.nome} com plano {plano_comercial.nome}")
            
            # Get or create corresponding PlanoFinanceiro
            plano_financeiro = get_or_create_plano_financeiro_from_comercial(plano_comercial)
            
            # Calcular data de vencimento
            data_atual = timezone.now()
            if dia_vencimento and 1 <= dia_vencimento <= 28:
                # Usar o dia específico escolhido pelo cliente
                try:
                    data_vencimento = data_atual.replace(day=dia_vencimento)
                    # Se o dia já passou neste mês, usar o próximo mês
                    if data_vencimento <= data_atual:
                        if data_vencimento.month == 12:
                            data_vencimento = data_vencimento.replace(year=data_vencimento.year + 1, month=1)
                        else:
                            data_vencimento = data_vencimento.replace(month=data_vencimento.month + 1)
                except ValueError:
                    # Se o dia não existe no mês (ex: 31 em fevereiro), usar o último dia do mês
                    data_vencimento = data_atual + timedelta(days=30)
            else:
                # Usar 30 dias a partir de hoje como padrão
                data_vencimento = data_atual + timedelta(days=30)
            
            # Create ControleFinanceiro (usar get_or_create para evitar duplicatas)
            controle_financeiro, controle_created = ControleFinanceiro.objects.get_or_create(
                loja=loja,
                defaults={
                    'plano': plano_financeiro,
                    'status': 'ativa',
                    'valor_mensal': plano_comercial.preco_mensal,
                    'data_inicio': data_atual,
                    'data_vencimento': data_vencimento,
                    'dia_vencimento': dia_vencimento or data_vencimento.day
                }
            )
            
            if not controle_created:
                logger.info(f"ControleFinanceiro já existia para loja {loja.nome}")
            
            # Create AssinaturaLoja (usar get_or_create para evitar duplicatas)
            assinatura_loja, assinatura_created = AssinaturaLoja.objects.get_or_create(
                loja=loja,
                defaults={
                    'plano': plano_comercial,
                    'status': 'ativa',
                    'tipo_pagamento': 'mensal',
                    'data_vencimento': data_vencimento
                }
            )
            
            if not assinatura_created:
                logger.info(f"AssinaturaLoja já existia para loja {loja.nome}")
            
            logger.info(f"Registros financeiros criados com sucesso para {loja.nome}")
            return controle_financeiro, assinatura_loja
            
    except Exception as e:
        logger.error(f"Erro ao criar registros financeiros para {loja.nome}: {str(e)}")
        raise Exception(f"Error creating financial records: {str(e)}")


def fix_inconsistent_store_data(loja):
    """
    Fixes inconsistent store data by creating missing AssinaturaLoja based on existing ControleFinanceiro.
    
    Args:
        loja (Loja): The store to fix
        
    Returns:
        AssinaturaLoja: The created subscription record
    """
    from controle_financeiro.models import ControleFinanceiro
    from planos.models import AssinaturaLoja, PlanoComercial
    from django.utils import timezone
    
    try:
        # Check if store has ControleFinanceiro but no AssinaturaLoja
        controle = ControleFinanceiro.objects.filter(loja=loja).first()
        assinatura = AssinaturaLoja.objects.filter(loja=loja).first()
        
        if controle and not assinatura:
            # Find or create matching PlanoComercial
            plano_comercial = PlanoComercial.objects.filter(
                nome=controle.plano.nome,
                preco_mensal=controle.valor_mensal
            ).first()
            
            if not plano_comercial:
                # Create PlanoComercial based on PlanoFinanceiro
                plano_comercial = PlanoComercial.objects.create(
                    nome=controle.plano.nome,
                    tipo='basico',  # Default type
                    descricao=controle.plano.descricao,
                    preco_mensal=controle.valor_mensal,
                    status='ativo'
                )
            
            # Create AssinaturaLoja (usar get_or_create para evitar duplicatas)
            assinatura, assinatura_created = AssinaturaLoja.objects.get_or_create(
                loja=loja,
                defaults={
                    'plano': plano_comercial,
                    'status': controle.status,
                    'tipo_pagamento': 'mensal',
                    'data_vencimento': controle.data_vencimento
                }
            )
            
            return assinatura
        
        return assinatura
        
    except Exception as e:
        raise Exception(f"Error fixing inconsistent store data: {str(e)}")


def get_available_commercial_plans():
    """
    Gets all available commercial plans for store creation.
    
    Returns:
        QuerySet: Active PlanoComercial instances ordered by price
    """
    return PlanoComercial.objects.filter(
        status='ativo'
    ).order_by('ordem_exibicao', 'preco_mensal')


def validate_plan_selection(plano_id):
    """
    Validates that a plan selection is valid for store creation.
    
    Args:
        plano_id (int): The ID of the selected plan
        
    Returns:
        PlanoComercial: The validated plan instance
        
    Raises:
        ValueError: If plan is invalid or not available
    """
    try:
        plano = PlanoComercial.objects.get(
            id=plano_id,
            status='ativo'
        )
        return plano
    except PlanoComercial.DoesNotExist:
        raise ValueError("Selected plan is not available or does not exist")