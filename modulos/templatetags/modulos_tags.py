"""
Template tags para módulos
"""
from django import template
from django.db import DatabaseError, ProgrammingError
import logging

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def count_servicos_ativos():
    """
    Conta o número de serviços ativos (placeholder - retorna 0 por enquanto)
    """
    # Por enquanto retorna 0 já que não temos sistema de serviços
    return 0


@register.simple_tag
def count_protocolos_ativos():
    """
    Conta o número de protocolos de emagrecimento ativos (placeholder)
    """
    return 0


@register.simple_tag
def count_agendamentos_hoje():
    """
    Conta o número de agendamentos para hoje (placeholder)
    """
    return 0


@register.simple_tag
def count_pacotes_ativos():
    """
    Conta o número de pacotes de tratamento ativos (placeholder)
    """
    return 0


@register.simple_tag
def get_modulos_loja(loja):
    """
    Obtém os módulos disponíveis para uma loja
    """
    try:
        if not loja or not hasattr(loja, 'tipo_loja') or not loja.tipo_loja:
            return []
        
        from modulos.models import ModuloLoja
        return ModuloLoja.objects.filter(
            tipo_loja=loja.tipo_loja,
            ativo=True
        ).order_by('ordem')
    except (DatabaseError, ProgrammingError, ImportError) as e:
        logger.warning(f"Erro ao obter módulos da loja: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Erro inesperado ao obter módulos: {str(e)}")
        return []


@register.simple_tag
def has_modulo_estetica(loja):
    """
    Verifica se a loja tem o módulo de estética ativo
    """
    try:
        if not loja or not hasattr(loja, 'tipo_loja') or not loja.tipo_loja:
            return False
        
        return loja.tipo_loja.nome == 'clinica_estetica'
    except Exception as e:
        logger.error(f"Erro ao verificar módulo de estética: {str(e)}")
        return False


@register.simple_tag
def has_modulo_crm(loja):
    """
    Verifica se a loja tem o módulo de CRM ativo
    """
    try:
        if not loja or not hasattr(loja, 'tipo_loja') or not loja.tipo_loja:
            return False
        
        return loja.tipo_loja.nome == 'crm_vendas'
    except Exception as e:
        logger.error(f"Erro ao verificar módulo de CRM: {str(e)}")
        return False


@register.filter
def get_item(dictionary, key):
    """
    Obtém um item de um dicionário usando uma chave
    """
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None


@register.filter
def multiply(value, arg):
    """
    Multiplica dois valores
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """
    Calcula a porcentagem de um valor em relação ao total
    """
    try:
        if not total or total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0