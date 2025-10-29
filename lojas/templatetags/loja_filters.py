"""
Template filters customizados para lojas com tratamento de erros
"""
from django import template
from django.db import DatabaseError, ProgrammingError

register = template.Library()


@register.filter
def safe_get_tipo_loja(loja):
    """
    Obtém tipo_loja de forma segura, retornando None se houver erro de banco
    """
    if not loja:
        return None
    
    try:
        return loja.tipo_loja
    except (DatabaseError, ProgrammingError, AttributeError):
        return None
    except Exception:
        # Outros erros também retornam None
        return None


@register.filter
def has_tipo_loja(loja):
    """
    Verifica se loja tem tipo_loja de forma segura (sem fazer query)
    """
    if not loja:
        return False
    
    try:
        # Verifica se o campo tipo_loja_id está presente e não é None
        tipo_loja_id = getattr(loja, 'tipo_loja_id', None)
        if tipo_loja_id is None:
            return False
        
        # Se tem ID, tenta acessar o objeto mas trata erro
        tipo_loja = safe_get_tipo_loja(loja)
        return tipo_loja is not None
    except Exception:
        return False


@register.filter
def safe_count_related(loja, related_name):
    """
    Conta objetos relacionados de forma segura, retornando 0 se houver erro
    """
    if not loja:
        return 0
    
    try:
        related_manager = getattr(loja, related_name, None)
        if related_manager is None:
            return 0
        return related_manager.count()
    except (DatabaseError, ProgrammingError, AttributeError):
        return 0
    except Exception:
        return 0

