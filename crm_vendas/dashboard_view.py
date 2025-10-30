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
        # Filtrar por loja se não for super admin
        if request.user.is_superuser:
            leads = Lead.objects.all()
            orcamentos = Orcamento.objects.all()
            propostas = Proposta.objects.all()
            contratos = Contrato.objects.all()
        else:
            # Buscar loja do usuário
            try:
                loja = request.user.loja_admin
            except:
                loja = None
            
            if not loja:
                messages.error(request, 'Usuário não associado a nenhuma loja.')
                return redirect('dashboard:index')
            
            leads = Lead.objects.filter(loja=loja)
            orcamentos = Orcamento.objects.filter(loja=loja)
            propostas = Proposta.objects.filter(loja=loja)
            contratos = Contrato.objects.filter(loja=loja)
        
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
        
        # Leads recentes
        leads_recentes = leads.order_by('-data_criacao')[:5]
        
        # Orcamentos recentes
        orcamentos_pendentes = orcamentos.order_by('-data_criacao')[:5]
        
        # Atividades recentes
        atividades = []
        try:
            atividades = HistoricoContato.objects.filter(
                lead__in=leads
            ).order_by('-data_contato')[:10]
        except:
            pass
        
        context = {
            'stats': stats,
            'leads_recentes': leads_recentes,
            'orcamentos_pendentes': orcamentos_pendentes,
            'atividades': atividades,
        }
        
        return render(request, 'crm_vendas/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Erro no dashboard CRM: {str(e)}")
        messages.error(request, 'Erro ao carregar dashboard. Tente novamente.')
        return redirect('dashboard:index')