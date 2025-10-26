from django import template
from avaliacao_qualidade.models import Professor

register = template.Library()

@register.simple_tag
def get_professores():
    """Retorna todos os professores ativos"""
    return Professor.objects.filter(ativo=True).order_by('nome')