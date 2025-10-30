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
    """Dashboard principal do CRM - redireciona para dashboard da loja"""
    
    # Redirecionar para o dashboard principal da loja onde o CRM está integrado
    messages.info(request, 'O CRM agora está integrado no dashboard principal da loja.')
    return redirect('dashboard:loja')