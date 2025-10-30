"""
View dashboard_crm simplificada para resolver erro 500
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Lead, Orcamento, Proposta, Contrato, HistoricoContato
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard_crm_simples(request):
    """Dashboard principal do CRM - versão simplificada"""
    
    try:
        # Estatísticas básicas sem filtro por loja (temporário)
        leads = Lead.objects.all()
        orcamentos = Orcamento.objects.all()
        propostas = Proposta.objects.all()
        contratos = Contrato.objects.all()
        
        # Estatísticas básicas
        stats = {
            'total_leads': leads.count(),
            'leads_novos': leads.filter(status='novo').count(),
            'leads_qualificados': leads.filter(status='qualificado').count(),
            'orcamentos_enviados': orcamentos.count(),
            'orcamentos_aprovados': orcamentos.filter(status='aprovado').count(),
            'propostas_enviadas': propostas.count(),
            'contratos_ativos': contratos.filter(status='ativo').count(),
            'valor_pipeline': 0,
            'valor_orcamentos': 0,
        }
        
        # Dados recentes
        leads_recentes = leads.order_by('-data_criacao')[:5]
        orcamentos_pendentes = orcamentos.order_by('-data_criacao')[:5]
        atividades = []
        
        context = {
            'stats': stats,
            'leads_recentes': leads_recentes,
            'orcamentos_pendentes': orcamentos_pendentes,
            'atividades': atividades,
        }
        
        return render(request, 'crm_vendas/dashboard_simples.html', context)
        
    except Exception as e:
        logger.error(f"Erro no dashboard CRM: {str(e)}")
        # Em caso de erro, retornar uma página básica
        context = {
            'stats': {
                'total_leads': 0,
                'leads_novos': 0,
                'leads_qualificados': 0,
                'orcamentos_enviados': 0,
                'orcamentos_aprovados': 0,
                'propostas_enviadas': 0,
                'contratos_ativos': 0,
                'valor_pipeline': 0,
                'valor_orcamentos': 0,
            },
            'leads_recentes': [],
            'orcamentos_pendentes': [],
            'atividades': [],
            'erro': True,
        }
        return render(request, 'crm_vendas/dashboard_simples.html', context)