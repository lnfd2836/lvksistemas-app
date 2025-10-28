from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, date, timedelta
import json

from crm_vendas.models import Lead, Orcamento, Proposta, Contrato, HistoricoContato
from crm_vendas.services.email_service import EmailService


@login_required
def dashboard_crm_modulo(request):
    """Dashboard principal do CRM de Vendas"""
    
    # Estatísticas gerais
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    
    stats = {
        'total_leads': Lead.objects.count(),
        'leads_qualificados': Lead.objects.filter(status='qualificado').count(),
        'orcamentos_enviados': Orcamento.objects.filter(status='enviado').count(),
        'valor_pipeline': Lead.objects.filter(
            status__in=['qualificado', 'proposta_enviada', 'negociacao']
        ).aggregate(total=Sum('valor_estimado'))['total'] or 0,
    }
    
    # Leads recentes
    leads_recentes = Lead.objects.order_by('-data_criacao')[:5]
    
    # Orçamentos pendentes
    orcamentos_pendentes = Orcamento.objects.filter(
        status__in=['enviado', 'visualizado']
    ).order_by('-data_criacao')[:5]
    
    # Atividades recentes
    atividades = HistoricoContato.objects.order_by('-data_contato')[:10]
    
    context = {
        'stats': stats,
        'leads_recentes': leads_recentes,
        'orcamentos_pendentes': orcamentos_pendentes,
        'atividades': atividades,
    }
    
    return render(request, 'crm_vendas/dashboard.html', context)


@login_required
def listar_leads_modulo(request):
    """Lista leads do CRM"""
    
    leads = Lead.objects.all()
    
    # Filtros
    status = request.GET.get('status')
    if status:
        leads = leads.filter(status=status)
    
    origem = request.GET.get('origem')
    if origem:
        leads = leads.filter(origem=origem)
    
    busca = request.GET.get('busca')
    if busca:
        leads = leads.filter(
            Q(nome__icontains=busca) |
            Q(email__icontains=busca) |
            Q(empresa__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(leads.order_by('-data_criacao'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Lead.STATUS_CHOICES,
        'origem_choices': Lead.ORIGEM_CHOICES,
    }
    
    return render(request, 'crm_vendas/leads/listar.html', context)


@login_required
def criar_lead_modulo(request):
    """Cria novo lead"""
    
    if request.method == 'POST':
        try:
            lead = Lead.objects.create(
                nome=request.POST.get('nome'),
                email=request.POST.get('email'),
                telefone=request.POST.get('telefone'),
                empresa=request.POST.get('empresa'),
                cargo=request.POST.get('cargo'),
                origem=request.POST.get('origem'),
                valor_estimado=request.POST.get('valor_estimado') or 0,
                observacoes=request.POST.get('observacoes'),
                responsavel=request.user,
            )
            
            messages.success(request, f'Lead {lead.nome} criado com sucesso!')
            return redirect('modulos_crm:detalhar_lead', lead_id=lead.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar lead: {e}')
    
    context = {
        'origem_choices': Lead.ORIGEM_CHOICES,
    }
    
    return render(request, 'crm_vendas/leads/criar.html', context)


@login_required
def detalhar_lead_modulo(request, lead_id):
    """Detalha um lead específico"""
    
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Histórico de contatos
    historico = HistoricoContato.objects.filter(lead=lead).order_by('-data_contato')
    
    # Orçamentos do lead
    orcamentos = Orcamento.objects.filter(lead=lead).order_by('-data_criacao')
    
    context = {
        'lead': lead,
        'historico': historico,
        'orcamentos': orcamentos,
    }
    
    return render(request, 'crm_vendas/detalhar_lead.html', context)


@login_required
def listar_orcamentos_modulo(request):
    """Lista orçamentos do CRM"""
    
    orcamentos = Orcamento.objects.all()
    
    # Filtros
    status = request.GET.get('status')
    if status:
        orcamentos = orcamentos.filter(status=status)
    
    # Paginação
    paginator = Paginator(orcamentos.order_by('-data_criacao'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Orcamento.STATUS_CHOICES,
    }
    
    return render(request, 'crm_vendas/orcamentos/listar.html', context)


@login_required
def criar_orcamento_modulo(request):
    """Cria novo orçamento"""
    
    if request.method == 'POST':
        try:
            lead_id = request.POST.get('lead_id')
            lead = get_object_or_404(Lead, id=lead_id)
            
            orcamento = Orcamento.objects.create(
                lead=lead,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao'),
                valor_total=request.POST.get('valor_total'),
                validade_dias=request.POST.get('validade_dias', 30),
                observacoes=request.POST.get('observacoes'),
                criado_por=request.user,
            )
            
            messages.success(request, f'Orçamento {orcamento.numero} criado com sucesso!')
            return redirect('modulos_crm:detalhar_orcamento', orcamento_id=orcamento.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar orçamento: {e}')
    
    # Buscar leads para o formulário
    leads = Lead.objects.filter(status__in=['novo', 'qualificado', 'interessado'])
    
    context = {
        'leads': leads,
    }
    
    return render(request, 'crm_vendas/orcamentos/criar.html', context)


@login_required
def enviar_orcamento_modulo(request, orcamento_id):
    """Envia orçamento por email"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    if request.method == 'POST':
        try:
            email_service = EmailService()
            sucesso = email_service.enviar_orcamento(orcamento)
            
            if sucesso:
                orcamento.status = 'enviado'
                orcamento.data_envio = timezone.now()
                orcamento.save()
                
                messages.success(request, 'Orçamento enviado com sucesso!')
            else:
                messages.error(request, 'Erro ao enviar orçamento')
                
        except Exception as e:
            messages.error(request, f'Erro ao enviar orçamento: {e}')
    
    return redirect('modulos_crm:listar_orcamentos')


@login_required
def listar_propostas_modulo(request):
    """Lista propostas do CRM"""
    
    propostas = Proposta.objects.all().order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(propostas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'crm_vendas/propostas/listar.html', context)


@login_required
def criar_proposta_modulo(request):
    """Cria nova proposta"""
    
    if request.method == 'POST':
        try:
            lead_id = request.POST.get('lead_id')
            lead = get_object_or_404(Lead, id=lead_id)
            
            proposta = Proposta.objects.create(
                lead=lead,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao'),
                valor_proposto=request.POST.get('valor_proposto'),
                prazo_execucao=request.POST.get('prazo_execucao'),
                condicoes_pagamento=request.POST.get('condicoes_pagamento'),
                observacoes=request.POST.get('observacoes'),
                criado_por=request.user,
            )
            
            messages.success(request, f'Proposta {proposta.numero} criada com sucesso!')
            return redirect('modulos_crm:listar_propostas')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar proposta: {e}')
    
    # Buscar leads para o formulário
    leads = Lead.objects.filter(status__in=['qualificado', 'interessado', 'negociacao'])
    
    context = {
        'leads': leads,
    }
    
    return render(request, 'crm_vendas/propostas/criar.html', context)


@login_required
def listar_contratos_modulo(request):
    """Lista contratos do CRM"""
    
    contratos = Contrato.objects.all().order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(contratos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'crm_vendas/contratos/listar.html', context)


@login_required
def criar_contrato_modulo(request):
    """Cria novo contrato"""
    
    if request.method == 'POST':
        try:
            lead_id = request.POST.get('lead_id')
            lead = get_object_or_404(Lead, id=lead_id)
            
            contrato = Contrato.objects.create(
                lead=lead,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao'),
                valor_contrato=request.POST.get('valor_contrato'),
                data_inicio=request.POST.get('data_inicio'),
                data_fim=request.POST.get('data_fim'),
                condicoes=request.POST.get('condicoes'),
                observacoes=request.POST.get('observacoes'),
                criado_por=request.user,
            )
            
            messages.success(request, f'Contrato {contrato.numero} criado com sucesso!')
            return redirect('modulos_crm:listar_contratos')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar contrato: {e}')
    
    # Buscar leads para o formulário
    leads = Lead.objects.filter(status__in=['negociacao', 'proposta_aceita'])
    
    context = {
        'leads': leads,
    }
    
    return render(request, 'crm_vendas/contratos/criar.html', context)


@login_required
def relatorios_crm_modulo(request):
    """Relatórios do CRM"""
    
    # Estatísticas por período
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    inicio_ano = hoje.replace(month=1, day=1)
    
    # Leads por status
    leads_por_status = {}
    for status, nome in Lead.STATUS_CHOICES:
        leads_por_status[nome] = Lead.objects.filter(status=status).count()
    
    # Conversão por mês
    conversao_mes = Lead.objects.filter(
        data_criacao__gte=inicio_mes,
        status='fechado_ganho'
    ).count()
    
    total_leads_mes = Lead.objects.filter(data_criacao__gte=inicio_mes).count()
    taxa_conversao = (conversao_mes / total_leads_mes * 100) if total_leads_mes > 0 else 0
    
    context = {
        'leads_por_status': leads_por_status,
        'conversao_mes': conversao_mes,
        'total_leads_mes': total_leads_mes,
        'taxa_conversao': round(taxa_conversao, 2),
    }
    
    return render(request, 'crm_vendas/relatorios.html', context)


@login_required
def relatorio_funil_modulo(request):
    """Relatório do funil de vendas"""
    
    # Dados do funil
    funil = {
        'leads_novos': Lead.objects.filter(status='novo').count(),
        'leads_qualificados': Lead.objects.filter(status='qualificado').count(),
        'leads_interessados': Lead.objects.filter(status='interessado').count(),
        'em_negociacao': Lead.objects.filter(status='negociacao').count(),
        'fechados_ganhos': Lead.objects.filter(status='fechado_ganho').count(),
        'fechados_perdidos': Lead.objects.filter(status='fechado_perdido').count(),
    }
    
    context = {
        'funil': funil,
    }
    
    return render(request, 'crm_vendas/funil.html', context)


@login_required
def configuracoes_crm_modulo(request):
    """Configurações do CRM"""
    
    if request.method == 'POST':
        # Implementar salvamento de configurações
        messages.success(request, 'Configurações salvas com sucesso!')
    
    context = {}
    
    return render(request, 'crm_vendas/configuracoes.html', context)