"""
Views personalizadas para o Django Admin
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from lojas.models import Loja, Cliente, Produto, Venda
from planos.models import PlanoComercial, AssinaturaLoja
from usuarios.models import SessaoAtiva


@staff_member_required
def admin_index(request):
    """
    View personalizada para a página inicial do admin
    """
    
    # Estatísticas gerais
    context = {
        # Contadores principais
        'total_lojas': Loja.objects.count(),
        'total_usuarios': User.objects.filter(is_active=True).count(),
        'total_clientes': Cliente.objects.count(),
        'total_produtos': Produto.objects.count(),
        'total_planos': PlanoComercial.objects.filter(status='ativo').count(),
        'total_grupos': Group.objects.count(),
        'total_assinaturas': AssinaturaLoja.objects.filter(status='ativa').count(),
        'total_sessoes': SessaoAtiva.objects.filter(ativa=True).count(),
        
        # Vendas
        'total_vendas': Venda.objects.filter(
            data_venda__date=timezone.now().date()
        ).count(),
        'total_vendas_total': Venda.objects.count(),
        
        # Atividade recente (últimas 10 ações)
        'recent_actions': LogEntry.objects.select_related('user').order_by('-action_time')[:10],
        
        # Informações do usuário
        'user': request.user,
    }
    
    return render(request, 'admin/index.html', context)


@staff_member_required
def admin_stats_api(request):
    """
    API para estatísticas em tempo real (AJAX)
    """
    from django.http import JsonResponse
    
    stats = {
        'total_lojas': Loja.objects.count(),
        'total_usuarios': User.objects.filter(is_active=True).count(),
        'total_vendas_hoje': Venda.objects.filter(
            data_venda__date=timezone.now().date()
        ).count(),
        'total_sessoes_ativas': SessaoAtiva.objects.filter(ativa=True).count(),
        'timestamp': timezone.now().isoformat(),
    }
    
    return JsonResponse(stats)