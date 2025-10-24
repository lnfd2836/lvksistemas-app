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
            descricao=plano_comercial.descricao,
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


def create_both_financial_records(loja, plano_comercial):
    """
    Creates both ControleFinanceiro and AssinaturaLoja records for a store.
    
    Args:
        loja (Loja): The store to create records for
        plano_comercial (PlanoComercial): The selected commercial plan
        
    Returns:
        tuple: (ControleFinanceiro, AssinaturaLoja) instances
    """
    from controle_financeiro.models import ControleFinanceiro
    from planos.models import AssinaturaLoja
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        with transaction.atomic():
            # Get or create corresponding PlanoFinanceiro
            plano_financeiro = get_or_create_plano_financeiro_from_comercial(plano_comercial)
            
            # Create ControleFinanceiro (usar get_or_create para evitar duplicatas)
            controle_financeiro, controle_created = ControleFinanceiro.objects.get_or_create(
                loja=loja,
                defaults={
                    'plano': plano_financeiro,
                    'status': 'ativa',
                    'valor_mensal': plano_comercial.preco_mensal,
                    'data_inicio': timezone.now(),
                    'data_vencimento': timezone.now() + timedelta(days=30)
                }
            )
            
            # Create AssinaturaLoja (usar get_or_create para evitar duplicatas)
            assinatura_loja, assinatura_created = AssinaturaLoja.objects.get_or_create(
                loja=loja,
                defaults={
                    'plano': plano_comercial,
                    'status': 'ativa',
                    'tipo_pagamento': 'mensal',
                    'data_vencimento': timezone.now() + timedelta(days=30)
                }
            )
            
            return controle_financeiro, assinatura_loja
            
    except Exception as e:
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