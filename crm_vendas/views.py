"""
Views do CRM de Vendas
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
import logging

from .models import Lead, Orcamento, ItemOrcamento, Proposta, Contrato, HistoricoContato, EmailLog, ProdutoServico, AssinaturaDigital
from .services.email_service import EmailService, EmailTrackingService
from .services.pdf_service import PDFService
from .forms import (
    LeadForm, ProdutoServicoForm, OrcamentoForm, ItemOrcamentoForm, 
    PropostaForm, ContratoForm, HistoricoContatoForm, AssinaturaDigitalForm
)
from lojas.models import Loja

logger = logging.getLogger(__name__)


@login_required
def dashboard_crm(request):
    """Dashboard principal do CRM"""
    
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
    
    # Estatísticas
    stats = {
        'total_leads': leads.count(),
        'leads_novos': leads.filter(status='novo').count(),
        'leads_qualificados': leads.filter(status='qualificado').count(),
        'orcamentos_enviados': orcamentos.filter(status='enviado').count(),
        'orcamentos_aprovados': orcamentos.filter(status='aprovado').count(),
        'propostas_enviadas': propostas.filter(status='enviada').count(),
        'contratos_ativos': contratos.filter(status='ativo').count(),
        'valor_pipeline': leads.aggregate(total=Sum('valor_estimado'))['total'] or 0,
        'valor_orcamentos': orcamentos.aggregate(total=Sum('total'))['total'] or 0,
    }
    
    # Leads recentes
    leads_recentes = leads.order_by('-data_criacao')[:5]
    
    # Orcamentos pendentes
    orcamentos_pendentes = orcamentos.filter(status__in=['enviado', 'visualizado']).order_by('-data_envio')[:5]
    
    # Atividades recentes
    atividades = HistoricoContato.objects.filter(
        lead__in=leads
    ).order_by('-data_contato')[:10]
    
    context = {
        'stats': stats,
        'leads_recentes': leads_recentes,
        'orcamentos_pendentes': orcamentos_pendentes,
        'atividades': atividades,
    }
    
    # Usar template específico para a loja Felix (sem barra superior)
    if not request.user.is_superuser:
        try:
            loja = request.user.loja_admin
            if loja and str(loja.id) == "feeac6c9-0af3-4885-9592-9c6cd196d39c":
                context['loja'] = loja
                return render(request, 'crm_vendas/dashboard_felix.html', context)
        except:
            pass
    
    return render(request, 'crm_vendas/dashboard.html', context)


@login_required
def dashboard_crm(request):
    """Dashboard principal do CRM"""
    
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
    
    # Estatísticas
    stats = {
        'total_leads': leads.count(),
        'leads_novos': leads.filter(status='novo').count(),
        'leads_qualificados': leads.filter(status='qualificado').count(),
        'orcamentos_enviados': orcamentos.filter(status='enviado').count(),
        'orcamentos_aprovados': orcamentos.filter(status='aprovado').count(),
        'propostas_enviadas': propostas.filter(status='enviada').count(),
        'contratos_ativos': contratos.filter(status='ativo').count(),
        'valor_pipeline': leads.aggregate(total=Sum('valor_estimado'))['total'] or 0,
        'valor_orcamentos': orcamentos.aggregate(total=Sum('total'))['total'] or 0,
    }
    
    # Leads recentes
    leads_recentes = leads.order_by('-data_criacao')[:5]
    
    # Orcamentos pendentes
    orcamentos_pendentes = orcamentos.filter(status__in=['enviado', 'visualizado']).order_by('-data_envio')[:5]
    
    # Atividades recentes
    atividades = HistoricoContato.objects.filter(
        lead__in=leads
    ).order_by('-data_contato')[:10]
    
    context = {
        'stats': stats,
        'leads_recentes': leads_recentes,
        'orcamentos_pendentes': orcamentos_pendentes,
        'atividades': atividades,
    }
    
    # Usar template específico para a loja Felix (sem barra superior)
    if not request.user.is_superuser:
        try:
            loja = request.user.loja_admin
            if loja and str(loja.id) == "feeac6c9-0af3-4885-9592-9c6cd196d39c":
                context['loja'] = loja
                return render(request, 'crm_vendas/dashboard_felix.html', context)
        except:
            pass
    
    return render(request, 'crm_vendas/dashboard.html', context)


@login_required
def listar_leads(request):
    """Lista todos os leads"""
    
    # Filtrar por loja
    if request.user.is_superuser:
        leads = Lead.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            leads = Lead.objects.filter(loja=loja)
        except:
            leads = Lead.objects.none()
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        leads = leads.filter(status=status_filter)
    
    origem_filter = request.GET.get('origem')
    if origem_filter:
        leads = leads.filter(origem=origem_filter)
    
    search = request.GET.get('search')
    if search:
        leads = leads.filter(
            Q(nome__icontains=search) |
            Q(email__icontains=search) |
            Q(empresa__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(leads.order_by('-data_criacao'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'origem_filter': origem_filter,
        'search': search,
        'status_choices': Lead.STATUS_CHOICES,
        'origem_choices': Lead.ORIGEM_CHOICES,
    }
    
    return render(request, 'crm_vendas/leads/listar.html', context)


@login_required
def criar_lead(request):
    """Cria um novo lead"""
    
    if request.method == 'POST':
        try:
            # Obter loja
            if request.user.is_superuser:
                loja_id = request.POST.get('loja')
                loja = get_object_or_404(Loja, id=loja_id)
            else:
                loja = request.user.loja_admin
            
            # Criar lead
            lead = Lead.objects.create(
                nome=request.POST.get('nome'),
                email=request.POST.get('email'),
                telefone=request.POST.get('telefone', ''),
                empresa=request.POST.get('empresa', ''),
                cargo=request.POST.get('cargo', ''),
                endereco=request.POST.get('endereco', ''),
                cidade=request.POST.get('cidade', ''),
                estado=request.POST.get('estado', ''),
                cep=request.POST.get('cep', ''),
                origem=request.POST.get('origem', 'site'),
                valor_estimado=request.POST.get('valor_estimado', 0),
                probabilidade=request.POST.get('probabilidade', 50),
                observacoes=request.POST.get('observacoes', ''),
                responsavel=request.user,
                loja=loja
            )
            
            messages.success(request, f'Lead {lead.nome} criado com sucesso!')
            return redirect('crm_vendas:detalhar_lead', lead_id=lead.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar lead: {str(e)}')
    
    # Buscar lojas para super admin
    lojas = Loja.objects.all() if request.user.is_superuser else None
    
    context = {
        'lojas': lojas,
        'origem_choices': Lead.ORIGEM_CHOICES,
    }
    
    return render(request, 'crm_vendas/leads/criar.html', context)


@login_required
def detalhar_lead(request, lead_id):
    """Mostra detalhes de um lead"""
    
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Verificar permissão
    if not request.user.is_superuser and lead.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para acessar este lead.')
        return redirect('crm_vendas:listar_leads')
    
    # Buscar dados relacionados
    orcamentos = lead.orcamentos.all().order_by('-data_criacao')
    propostas = lead.propostas.all().order_by('-data_criacao')
    contratos = lead.contratos.all().order_by('-data_criacao')
    historico = lead.historico_contatos.all().order_by('-data_contato')
    emails = lead.emails_enviados.all().order_by('-data_envio')
    
    context = {
        'lead': lead,
        'orcamentos': orcamentos,
        'propostas': propostas,
        'contratos': contratos,
        'historico': historico,
        'emails': emails,
        'status_choices': Lead.STATUS_CHOICES,
    }
    
    # Debug: verificar se está chegando na view correta
    logger.info(f"Renderizando detalhes do lead: {lead.nome} (ID: {lead.id})")
    
    return render(request, 'crm_vendas/leads/detalhar.html', context)


@login_required
def listar_orcamentos(request):
    """Lista orçamentos"""
    
    # Debug: verificar total de orçamentos
    total_orcamentos = Orcamento.objects.count()
    logger.info(f"Total de orçamentos na base: {total_orcamentos}")
    
    # Filtrar por loja
    if request.user.is_superuser:
        orcamentos = Orcamento.objects.all()
        logger.info(f"Usuário superuser - buscando todos os orçamentos: {orcamentos.count()}")
    else:
        try:
            loja = request.user.loja_admin
            orcamentos = Orcamento.objects.filter(loja=loja)
            logger.info(f"Usuário da loja {loja.nome} - orçamentos encontrados: {orcamentos.count()}")
        except Exception as e:
            logger.error(f"Erro ao buscar loja do usuário: {str(e)}")
            messages.error(request, 'Usuário não associado a nenhuma loja.')
            return redirect('dashboard:index')
    
    # Filtros
    status = request.GET.get('status')
    if status:
        orcamentos_antes = orcamentos.count()
        orcamentos = orcamentos.filter(status=status)
        logger.info(f"Filtro status '{status}': {orcamentos_antes} -> {orcamentos.count()}")
    
    # Debug: listar alguns orçamentos
    for orc in orcamentos[:5]:
        logger.info(f"Orçamento: {orc.numero} - {orc.titulo} - Status: {orc.status} - Loja: {orc.loja.nome}")
    
    # Paginação
    paginator = Paginator(orcamentos, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    logger.info(f"Página atual: {page_obj.number}, Total páginas: {page_obj.paginator.num_pages}, Itens na página: {len(page_obj)}")
    
    context = {
        'orcamentos': page_obj,
        'page_obj': page_obj,
        'status_filter': status,
        'total_orcamentos': total_orcamentos,  # Para debug no template
    }
    
    return render(request, 'crm_vendas/orcamentos/listar.html', context)


@login_required
def criar_orcamento(request):
    """Cria novo orçamento"""
    
    lead_id = request.GET.get('lead')
    lead = None
    if lead_id:
        lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        # Implementar criação de orçamento
        # Por enquanto, redirecionar para a versão melhorada
        return redirect('crm_vendas:criar_orcamento_melhorado')
    
    # Por enquanto, redirecionar para a versão melhorada
    if lead:
        return redirect(f"{reverse('crm_vendas:criar_orcamento_melhorado')}?lead={lead.id}")
    else:
        return redirect('crm_vendas:criar_orcamento_melhorado')


@login_required
def detalhar_orcamento(request, orcamento_id):
    """Detalha orçamento"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    # Verificar permissão
    if not request.user.is_superuser and orcamento.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para ver este orçamento.')
        return redirect('crm_vendas:listar_orcamentos')
    
    context = {
        'orcamento': orcamento,
    }
    
    return render(request, 'crm_vendas/orcamentos/detalhar.html', context)


@login_required
def editar_orcamento(request, orcamento_id):
    """Edita orçamento"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    # Verificar permissão
    if not request.user.is_superuser and orcamento.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para editar este orçamento.')
        return redirect('crm_vendas:listar_orcamentos')
    
    # Redirecionar para a versão melhorada
    return redirect('crm_vendas:editar_orcamento_itens', orcamento_id=orcamento_id)


@login_required
def listar_propostas(request):
    """Lista propostas"""
    
    # Filtrar por loja
    if request.user.is_superuser:
        propostas = Proposta.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            propostas = Proposta.objects.filter(loja=loja)
        except:
            messages.error(request, 'Usuário não associado a nenhuma loja.')
            return redirect('dashboard:index')
    
    # Paginação
    paginator = Paginator(propostas, 20)
    page = request.GET.get('page')
    propostas = paginator.get_page(page)
    
    context = {
        'propostas': propostas,
    }
    
    return render(request, 'crm_vendas/propostas/listar.html', context)


@login_required
def criar_proposta(request):
    """Cria nova proposta"""
    
    lead_id = request.GET.get('lead')
    lead = None
    if lead_id:
        lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        form = PropostaForm(request.POST)
        if form.is_valid():
            try:
                proposta = form.save(commit=False)
                
                # Definir loja
                if request.user.is_superuser:
                    loja = Loja.objects.first()  # Temporário
                else:
                    loja = request.user.loja_admin
                
                proposta.loja = loja
                proposta.responsavel = request.user
                proposta.save()
                
                messages.success(request, f'Proposta "{proposta.numero}" criada com sucesso!')
                return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
                
            except Exception as e:
                logger.error(f"Erro ao criar proposta: {str(e)}")
                messages.error(request, 'Erro ao criar proposta. Tente novamente.')
    else:
        initial = {}
        if lead:
            initial['lead'] = lead
        form = PropostaForm(initial=initial)
    
    context = {
        'form': form,
        'lead': lead,
        'titulo': 'Nova Proposta'
    }
    
    return render(request, 'crm_vendas/propostas/form.html', context)


@login_required
def detalhar_proposta(request, proposta_id):
    """Detalha proposta"""
    
    proposta = get_object_or_404(Proposta, id=proposta_id)
    
    # Verificar permissão
    if not request.user.is_superuser and proposta.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para ver esta proposta.')
        return redirect('crm_vendas:listar_propostas')
    
    context = {
        'proposta': proposta,
    }
    
    return render(request, 'crm_vendas/propostas/detalhar.html', context)


@login_required
def listar_contratos(request):
    """Lista contratos"""
    
    # Filtrar por loja
    if request.user.is_superuser:
        contratos = Contrato.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            contratos = Contrato.objects.filter(loja=loja)
        except:
            messages.error(request, 'Usuário não associado a nenhuma loja.')
            return redirect('dashboard:index')
    
    # Paginação
    paginator = Paginator(contratos, 20)
    page = request.GET.get('page')
    contratos = paginator.get_page(page)
    
    context = {
        'contratos': contratos,
    }
    
    return render(request, 'crm_vendas/contratos/listar.html', context)


@login_required
def criar_contrato(request):
    """Cria novo contrato"""
    
    lead_id = request.GET.get('lead')
    lead = None
    if lead_id:
        lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            try:
                contrato = form.save(commit=False)
                
                # Definir loja
                if request.user.is_superuser:
                    loja = Loja.objects.first()  # Temporário
                else:
                    loja = request.user.loja_admin
                
                contrato.loja = loja
                contrato.responsavel = request.user
                contrato.save()
                
                messages.success(request, f'Contrato "{contrato.numero}" criado com sucesso!')
                return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato.id)
                
            except Exception as e:
                logger.error(f"Erro ao criar contrato: {str(e)}")
                messages.error(request, 'Erro ao criar contrato. Tente novamente.')
    else:
        initial = {}
        if lead:
            initial['lead'] = lead
        form = ContratoForm(initial=initial)
    
    context = {
        'form': form,
        'lead': lead,
        'titulo': 'Novo Contrato'
    }
    
    return render(request, 'crm_vendas/contratos/form.html', context)


@login_required
def detalhar_contrato(request, contrato_id):
    """Detalha contrato"""
    
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Verificar permissão
    if not request.user.is_superuser and contrato.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para ver este contrato.')
        return redirect('crm_vendas:listar_contratos')
    
    context = {
        'contrato': contrato,
    }
    
    return render(request, 'crm_vendas/contratos/detalhar.html', context)


@login_required
def gerar_pdf_orcamento(request, orcamento_id):
    """Gera PDF do orçamento"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    # Verificar permissão
    if not request.user.is_superuser and orcamento.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para este orçamento.')
        return redirect('crm_vendas:listar_orcamentos')
    
    try:
        # Usar o serviço de PDF
        pdf_content = PDFService.gerar_orcamento(orcamento)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{orcamento.numero}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF do orçamento {orcamento_id}: {str(e)}")
        messages.error(request, 'Erro ao gerar PDF. Tente novamente.')
        return redirect('crm_vendas:detalhar_orcamento', orcamento_id=orcamento_id)


@login_required
def configuracoes_crm(request):
    """Configurações do CRM"""
    
    context = {
        'titulo': 'Configurações do CRM'
    }
    
    return render(request, 'crm_vendas/configuracoes.html', context)


@login_required
def relatorios_crm(request):
    """Relatórios do CRM"""
    
    # Redirecionar para a versão melhorada
    return redirect('crm_vendas:relatorios_vendas')


@login_required
def relatorio_funil_vendas(request):
    """Relatório do funil de vendas"""
    
    # Filtrar por loja
    if request.user.is_superuser:
        leads = Lead.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            leads = Lead.objects.filter(loja=loja)
        except:
            messages.error(request, 'Usuário não associado a nenhuma loja.')
            return redirect('dashboard:index')
    
    # Estatísticas do funil
    funil = {}
    for status, label in Lead.STATUS_CHOICES:
        funil[status] = {
            'label': label,
            'count': leads.filter(status=status).count(),
            'valor': leads.filter(status=status).aggregate(total=Sum('valor_estimado'))['total'] or 0
        }
    
    context = {
        'funil': funil,
    }
    
    return render(request, 'crm_vendas/funil.html', context)


@login_required
def relatorio_performance(request):
    """Relatório de performance"""
    
    # Redirecionar para relatórios de vendas
    return redirect('crm_vendas:relatorios_vendas')


@login_required
@require_http_methods(["POST"])
def enviar_orcamento(request, orcamento_id):
    """Envia orçamento por email"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    # Verificar permissão
    if not request.user.is_superuser and orcamento.loja != request.user.loja_admin:
        return JsonResponse({'success': False, 'error': 'Sem permissão'})
    
    try:
        # Enviar email
        sucesso = EmailService.enviar_orcamento(orcamento)
        
        if sucesso:
            return JsonResponse({
                'success': True,
                'message': f'Orçamento {orcamento.numero} enviado com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erro ao enviar email'
            })
            
    except Exception as e:
        logger.error(f"Erro ao enviar orçamento {orcamento_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def gerar_pdf_orcamento(request, orcamento_id):
    """Gera e retorna PDF do orçamento"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    # Verificar permissão
    if not request.user.is_superuser and orcamento.loja != request.user.loja_admin:
        messages.error(request, 'Sem permissão')
        return redirect('crm_vendas:listar_orcamentos')
    
    try:
        pdf_content = PDFService.gerar_orcamento_pdf(orcamento)
        
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Orcamento_{orcamento.numero}.pdf"'
            return response
        else:
            messages.error(request, 'Erro ao gerar PDF')
            return redirect('crm_vendas:detalhar_orcamento', orcamento_id=orcamento_id)
            
    except Exception as e:
        logger.error(f"Erro ao gerar PDF do orçamento {orcamento_id}: {e}")
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect('crm_vendas:detalhar_orcamento', orcamento_id=orcamento_id)


@csrf_exempt
def visualizar_orcamento_publico(request, orcamento_id):
    """Visualização pública do orçamento (para clientes)"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    # Registrar visualização
    if not orcamento.data_visualizacao:
        orcamento.data_visualizacao = timezone.now()
        orcamento.status = 'visualizado'
        orcamento.save()
    
    context = {
        'orcamento': orcamento,
        'itens': orcamento.itens.all(),
        'is_public_view': True,
    }
    
    return render(request, 'crm_vendas/publico/orcamento.html', context)


@csrf_exempt
def aprovar_orcamento_publico(request, orcamento_id):
    """Aprovação pública do orçamento (para clientes)"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao', 'aprovar')
        
        if acao == 'aprovar':
            # Aprovar orçamento
            orcamento.status = 'aprovado'
            orcamento.data_resposta = timezone.now()
            orcamento.save()
            
            # Atualizar lead
            orcamento.lead.status = 'fechado_ganho'
            orcamento.lead.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=orcamento.lead,
                tipo='email',
                assunto='Orçamento Aprovado',
                descricao=f'Cliente aprovou o orçamento {orcamento.numero}',
                resultado='Orçamento aprovado pelo cliente',
                data_contato=timezone.now()
            )
            
            messages.success(request, 'Orçamento aprovado com sucesso! Entraremos em contato em breve.')
            
        elif acao == 'rejeitar':
            # Rejeitar orçamento
            orcamento.status = 'rejeitado'
            orcamento.data_resposta = timezone.now()
            orcamento.save()
            
            # Atualizar lead
            orcamento.lead.status = 'fechado_perdido'
            orcamento.lead.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=orcamento.lead,
                tipo='email',
                assunto='Orçamento Rejeitado',
                descricao=f'Cliente rejeitou o orçamento {orcamento.numero}',
                resultado='Orçamento rejeitado pelo cliente',
                data_contato=timezone.now()
            )
            
            messages.info(request, 'Orçamento rejeitado. Agradecemos seu interesse.')
    
    context = {
        'orcamento': orcamento,
        'aprovado': orcamento.status == 'aprovado',
    }
    
    return render(request, 'crm_vendas/publico/aprovacao.html', context)


def track_email_abertura(request, orcamento_id):
    """Tracking de abertura de email (pixel invisível)"""
    
    try:
        # Buscar email log pelo orçamento
        email_log = EmailLog.objects.filter(orcamento_id=orcamento_id).first()
        
        if email_log:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            EmailTrackingService.registrar_abertura(email_log.token_rastreamento, ip_address)
    
    except Exception as e:
        logger.error(f"Erro no tracking de email: {e}")
    
    # Retornar pixel transparente 1x1
    from django.http import HttpResponse
    import base64
    
    # Pixel transparente em base64
    pixel_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
    
    response = HttpResponse(pixel_data, content_type='image/png')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


# Views básicas para outras funcionalidades

@login_required
def listar_propostas(request):
    """Lista propostas com filtros e paginação"""
    try:
        # Obter loja do usuário
        if request.user.is_superuser:
            propostas = Proposta.objects.all()
        else:
            loja = request.user.loja_admin
            propostas = Proposta.objects.filter(loja=loja)
        
        # Filtros
        status_filter = request.GET.get('status')
        lead_filter = request.GET.get('lead')
        search = request.GET.get('search')
        
        if status_filter:
            propostas = propostas.filter(status=status_filter)
        
        if lead_filter:
            propostas = propostas.filter(lead__nome__icontains=lead_filter)
        
        if search:
            propostas = propostas.filter(
                Q(numero__icontains=search) |
                Q(titulo__icontains=search) |
                Q(lead__nome__icontains=search)
            )
        
        # Ordenação
        propostas = propostas.select_related('lead', 'loja').order_by('-data_criacao')
        
        # Paginação
        paginator = Paginator(propostas, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Estatísticas
        stats = {
            'total': propostas.count(),
            'rascunho': propostas.filter(status='rascunho').count(),
            'enviada': propostas.filter(status='enviada').count(),
            'aprovada': propostas.filter(status='aprovada').count(),
            'rejeitada': propostas.filter(status='rejeitada').count(),
        }
        
        context = {
            'page_obj': page_obj,
            'stats': stats,
            'status_choices': Proposta.STATUS_CHOICES,
            'current_filters': {
                'status': status_filter,
                'lead': lead_filter,
                'search': search,
            }
        }
        
        return render(request, 'crm_vendas/propostas/listar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao listar propostas: {str(e)}")
        messages.error(request, 'Erro ao carregar propostas.')
        return redirect('crm_vendas:dashboard')

@login_required
def listar_contratos(request):
    """Lista contratos"""
    return render(request, 'crm_vendas/contratos/listar.html')

@login_required
def relatorios_crm(request):
    """Relatórios do CRM"""
    # Filtrar por loja se não for super admin
    if request.user.is_superuser:
        leads = Lead.objects.all()
        orcamentos = Orcamento.objects.all()
        propostas = Proposta.objects.all()
        contratos = Contrato.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            leads = Lead.objects.filter(loja=loja)
            orcamentos = Orcamento.objects.filter(loja=loja)
            propostas = Proposta.objects.filter(loja=loja)
            contratos = Contrato.objects.filter(loja=loja)
        except:
            leads = Lead.objects.none()
            orcamentos = Orcamento.objects.none()
            propostas = Proposta.objects.none()
            contratos = Contrato.objects.none()
    
    context = {
        'total_leads': leads.count(),
        'total_orcamentos': orcamentos.count(),
        'total_propostas': propostas.count(),
        'total_contratos': contratos.count(),
    }
    
    # Tentar usar template de relatórios, se não existir, usar o template básico
    from django.template import loader
    from django.template.exceptions import TemplateDoesNotExist
    
    try:
        loader.get_template('crm_vendas/relatorios/index.html')
        template_name = 'crm_vendas/relatorios/index.html'
    except TemplateDoesNotExist:
        template_name = 'crm_vendas/relatorios.html'
    
    return render(request, template_name, context)

# Placeholder views (implementar conforme necessário)
@login_required
def criar_orcamento(request):
    """Cria um novo orçamento"""
    
    # Obter loja
    if not request.user.is_superuser:
        try:
            loja = request.user.loja_admin
            if not loja:
                messages.error(request, 'Usuário não está associado a nenhuma loja.')
                return redirect('dashboard:principal')
        except AttributeError:
            messages.error(request, 'Usuário não tem permissão para acessar o CRM.')
            return redirect('dashboard:principal')
    else:
        loja = None
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            lead_id = request.POST.get('lead_id')
            titulo = request.POST.get('titulo')
            descricao = request.POST.get('descricao', '')
            condicoes_pagamento = request.POST.get('condicoes_pagamento', 'À vista')
            validade_dias = int(request.POST.get('validade_dias', 30))
            observacoes = request.POST.get('observacoes', '')
            
            # Buscar lead
            lead = get_object_or_404(Lead, id=lead_id)
            
            # Verificar permissão
            if not request.user.is_superuser and lead.loja != loja:
                messages.error(request, 'Você não tem permissão para criar orçamento para este lead.')
                return redirect('crm_vendas:criar_orcamento')
            
            # Criar orçamento
            orcamento = Orcamento.objects.create(
                lead=lead,
                loja=lead.loja,
                responsavel=request.user,
                titulo=titulo,
                descricao=descricao,
                condicoes_pagamento=condicoes_pagamento,
                validade_dias=validade_dias,
                status='rascunho'
            )
            
            # Processar itens
            subtotal = 0
            itens_data = {}
            
            # Agrupar dados dos itens
            for key, value in request.POST.items():
                if key.startswith('itens[') and '][' in key:
                    # Extrair índice e campo (ex: itens[0][descricao])
                    parts = key.replace('itens[', '').replace(']', '').split('[')
                    if len(parts) == 2:
                        index, field = parts
                        if index not in itens_data:
                            itens_data[index] = {}
                        itens_data[index][field] = value
            
            # Criar itens do orçamento
            for index, item_data in itens_data.items():
                if 'descricao' in item_data and item_data['descricao'].strip():
                    quantidade = float(item_data.get('quantidade', 1))
                    valor_unitario = float(item_data.get('valor_unitario', 0))
                    valor_total = quantidade * valor_unitario
                    
                    ItemOrcamento.objects.create(
                        orcamento=orcamento,
                        descricao=item_data['descricao'].strip(),
                        detalhes=item_data.get('detalhes', '').strip(),
                        quantidade=quantidade,
                        valor_unitario=valor_unitario,
                        valor_total=valor_total,
                        ordem=int(index)
                    )
                    
                    subtotal += valor_total
            
            # Atualizar totais do orçamento
            orcamento.subtotal = subtotal
            orcamento.total = subtotal  # Por enquanto sem desconto/impostos
            orcamento.save()
            
            # Atualizar status do lead
            if lead.status == 'novo' or lead.status == 'contatado':
                lead.status = 'proposta_enviada'
                lead.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=lead,
                usuario=request.user,
                tipo='outros',
                assunto='Orçamento Criado',
                descricao=f'Orçamento {orcamento.numero} criado com {orcamento.itens.count()} itens',
                resultado=f'Valor total: R$ {orcamento.total:,.2f}',
                data_contato=timezone.now()
            )
            
            messages.success(request, f'Orçamento {orcamento.numero} criado com sucesso!')
            return redirect('crm_vendas:detalhar_orcamento', orcamento_id=orcamento.id)
            
        except Exception as e:
            logger.error(f"Erro ao criar orçamento: {str(e)}")
            messages.error(request, f'Erro ao criar orçamento: {str(e)}')
    
    # Buscar leads disponíveis
    if loja:
        leads = Lead.objects.filter(loja=loja).exclude(status__in=['fechado_ganho', 'fechado_perdido'])
    else:
        leads = Lead.objects.exclude(status__in=['fechado_ganho', 'fechado_perdido'])
    
    context = {
        'loja': loja,
        'leads': leads,
        'lojas': Loja.objects.all() if request.user.is_superuser else None,
    }
    return render(request, 'crm_vendas/orcamentos/criar.html', context)

@login_required
def detalhar_orcamento(request, orcamento_id): 
    """Detalhes de um orçamento"""
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    context = {'orcamento': orcamento}
    return render(request, 'crm_vendas/orcamentos/detalhar.html', context)

@login_required
def editar_orcamento(request, orcamento_id): 
    """Edita um orçamento"""
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    context = {'orcamento': orcamento}
    return render(request, 'crm_vendas/orcamentos/editar.html', context)

@login_required
def criar_proposta(request):
    """Cria uma nova proposta"""
    try:
        # Obter loja do usuário
        if request.user.is_superuser:
            loja = None
        else:
            loja = request.user.loja_admin
        
        if request.method == 'POST':
            form = PropostaForm(request.POST, user=request.user)
            
            if form.is_valid():
                proposta = form.save(commit=False)
                
                # Definir loja
                if loja:
                    proposta.loja = loja
                else:
                    proposta.loja = proposta.lead.loja
                
                # Definir responsável
                proposta.responsavel = request.user
                
                # Pré-preencher dados do orçamento base se selecionado
                if proposta.orcamento_base:
                    orcamento = proposta.orcamento_base
                    if not proposta.titulo:
                        proposta.titulo = f"Proposta baseada no {orcamento.titulo}"
                    if not proposta.valor_total:
                        proposta.valor_total = orcamento.total
                
                proposta.save()
                
                # Registrar no histórico do lead
                HistoricoContato.objects.create(
                    lead=proposta.lead,
                    usuario=request.user,
                    tipo='outros',
                    assunto=f'Proposta {proposta.numero} criada',
                    descricao=f'Nova proposta comercial criada: {proposta.titulo}',
                    resultado=f'Valor: R$ {proposta.valor_total:,.2f}',
                    data_contato=timezone.now()
                )
                
                messages.success(request, f'Proposta {proposta.numero} criada com sucesso!')
                return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
            else:
                messages.error(request, 'Erro ao criar proposta. Verifique os dados informados.')
        else:
            # Pré-preencher com orçamento se fornecido
            orcamento_id = request.GET.get('orcamento')
            initial_data = {}
            
            if orcamento_id:
                try:
                    orcamento = Orcamento.objects.get(id=orcamento_id)
                    if not loja or orcamento.loja == loja:
                        initial_data = {
                            'lead': orcamento.lead,
                            'orcamento_base': orcamento,
                            'titulo': f"Proposta baseada no {orcamento.titulo}",
                            'valor_total': orcamento.total,
                        }
                except Orcamento.DoesNotExist:
                    pass
            
            form = PropostaForm(initial=initial_data, user=request.user)
        
        context = {
            'form': form,
            'title': 'Nova Proposta Comercial',
        }
        
        return render(request, 'crm_vendas/propostas/criar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao criar proposta: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_propostas')
                responsavel=request.user,
                titulo=titulo,
                resumo_executivo=descricao,
                objetivos=f"Serviços: {len(servicos_data)} itens",
                metodologia=prazo_execucao,
                investimento=condicoes_pagamento,
                valor_total=valor_total,
                condicoes_comerciais=observacoes,
                prazo_validade=prazo_validade,
                status='rascunho'
            )
            
            # Atualizar status do lead
            if lead.status in ['novo', 'contatado', 'qualificado']:
                lead.status = 'proposta_enviada'
                lead.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=lead,
                usuario=request.user,
                tipo='outros',
                assunto='Proposta Criada',
                descricao=f'Proposta {proposta.numero} criada com {len(servicos_data)} serviços',
                resultado=f'Valor total: R$ {proposta.valor_total:,.2f}',
                data_contato=timezone.now()
            )
            
            messages.success(request, f'Proposta {proposta.numero} criada com sucesso!')
            return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
            
        except Exception as e:
            logger.error(f"Erro ao criar proposta: {str(e)}")
            messages.error(request, f'Erro ao criar proposta: {str(e)}')
    
    # Buscar leads disponíveis
    if loja:
        leads = Lead.objects.filter(loja=loja).exclude(status__in=['fechado_ganho', 'fechado_perdido'])
    else:
        leads = Lead.objects.exclude(status__in=['fechado_ganho', 'fechado_perdido'])
    
    context = {
        'loja': loja,
        'leads': leads,
        'lojas': Loja.objects.all() if request.user.is_superuser else None,
    }
    return render(request, 'crm_vendas/propostas/criar.html', context)

@login_required
def detalhar_proposta(request, proposta_id): 
    """Detalhes de uma proposta"""
    try:
        proposta = get_object_or_404(Proposta, id=proposta_id)
        
        # Verificar permissão
        if not request.user.is_superuser and proposta.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para visualizar esta proposta.')
            return redirect('crm_vendas:listar_propostas')
        
        # Buscar histórico de contatos relacionados
        historico = HistoricoContato.objects.filter(lead=proposta.lead).order_by('-data_contato')[:10]
        
        # Verificar se pode editar (apenas rascunho)
        pode_editar = proposta.status == 'rascunho'
        
        # Verificar se pode enviar
        pode_enviar = proposta.status in ['rascunho', 'rejeitada']
        
        context = {
            'proposta': proposta,
            'historico': historico,
            'pode_editar': pode_editar,
            'pode_enviar': pode_enviar,
        }
        
        return render(request, 'crm_vendas/propostas/detalhar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao detalhar proposta: {str(e)}")
        messages.error(request, 'Erro ao carregar proposta.')
        return redirect('crm_vendas:listar_propostas')

@login_required
def editar_proposta(request, proposta_id):
    """Edita uma proposta"""
    try:
        proposta = get_object_or_404(Proposta, id=proposta_id)
        
        # Verificar permissão
        if not request.user.is_superuser and proposta.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para editar esta proposta.')
            return redirect('crm_vendas:listar_propostas')
        
        # Verificar se pode editar
        if proposta.status not in ['rascunho', 'rejeitada']:
            messages.error(request, 'Esta proposta não pode ser editada.')
            return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
        
        if request.method == 'POST':
            form = PropostaForm(request.POST, instance=proposta, user=request.user)
            
            if form.is_valid():
                proposta = form.save()
                
                # Registrar no histórico
                HistoricoContato.objects.create(
                    lead=proposta.lead,
                    usuario=request.user,
                    tipo='outros',
                    assunto=f'Proposta {proposta.numero} editada',
                    descricao=f'Proposta comercial atualizada: {proposta.titulo}',
                    resultado=f'Valor: R$ {proposta.valor_total:,.2f}',
                    data_contato=timezone.now()
                )
                
                messages.success(request, 'Proposta atualizada com sucesso!')
                return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
            else:
                messages.error(request, 'Erro ao atualizar proposta. Verifique os dados informados.')
        else:
            form = PropostaForm(instance=proposta, user=request.user)
        
        context = {
            'form': form,
            'proposta': proposta,
            'title': f'Editar Proposta {proposta.numero}',
        }
        
        return render(request, 'crm_vendas/propostas/editar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao editar proposta: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_propostas')

@login_required
def enviar_proposta(request, proposta_id): 
    """Envia uma proposta por email"""
    try:
        proposta = get_object_or_404(Proposta, id=proposta_id)
        
        # Verificar permissão
        if not request.user.is_superuser and proposta.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para enviar esta proposta.')
            return redirect('crm_vendas:listar_propostas')
        
        # Verificar se pode enviar
        if proposta.status not in ['rascunho', 'rejeitada']:
            messages.error(request, 'Esta proposta não pode ser enviada.')
            return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
        
        # Enviar por email
        success = EmailService.enviar_proposta(proposta)
        
        if success:
            # Atualizar status
            proposta.status = 'enviada'
            proposta.data_envio = timezone.now()
            proposta.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=proposta.lead,
                usuario=request.user,
                tipo='email',
                assunto=f'Proposta {proposta.numero} enviada',
                descricao=f'Proposta comercial enviada por email para {proposta.lead.email}',
                resultado='Email enviado com sucesso',
                data_contato=timezone.now()
            )
            
            messages.success(request, 'Proposta enviada com sucesso!')
        else:
            messages.error(request, 'Erro ao enviar proposta por email.')
        
        return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
        
    except Exception as e:
        logger.error(f"Erro ao enviar proposta: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_propostas')

@login_required
def gerar_pdf_proposta(request, proposta_id):
    """Gera PDF da proposta"""
    try:
        proposta = get_object_or_404(Proposta, id=proposta_id)
        
        # Verificar permissão
        if not request.user.is_superuser and proposta.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para acessar esta proposta.')
            return redirect('crm_vendas:listar_propostas')
        
        # Gerar PDF
        pdf_content = PDFService.gerar_proposta_pdf(proposta)
        
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Proposta_{proposta.numero}.pdf"'
            return response
        else:
            messages.error(request, 'Erro ao gerar PDF da proposta.')
            return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta.id)
            
    except Exception as e:
        logger.error(f"Erro ao gerar PDF da proposta: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_propostas')

@login_required
def criar_contrato(request):
    """Cria um novo contrato"""
    try:
        # Obter loja do usuário
        if request.user.is_superuser:
            loja = None
        else:
            loja = request.user.loja_admin
        
        if request.method == 'POST':
            form = ContratoForm(request.POST, user=request.user)
            
            if form.is_valid():
                contrato = form.save(commit=False)
                
                # Definir loja
                if loja:
                    contrato.loja = loja
                else:
                    contrato.loja = contrato.lead.loja
                
                # Definir responsável
                contrato.responsavel = request.user
                
                # Pré-preencher dados da proposta base se selecionada
                if contrato.proposta_base:
                    proposta = contrato.proposta_base
                    if not contrato.titulo:
                        contrato.titulo = f"Contrato baseado na {proposta.titulo}"
                    if not contrato.valor_total:
                        contrato.valor_total = proposta.valor_total
                    if not contrato.objeto:
                        contrato.objeto = proposta.resumo_executivo
                
                contrato.save()
                
                # Atualizar status do lead
                if contrato.lead.status != 'fechado_ganho':
                    contrato.lead.status = 'fechado_ganho'
                    contrato.lead.save()
                
                # Registrar no histórico do lead
                HistoricoContato.objects.create(
                    lead=contrato.lead,
                    usuario=request.user,
                    tipo='outros',
                    assunto=f'Contrato {contrato.numero} criado',
                    descricao=f'Novo contrato criado: {contrato.titulo}',
                    resultado=f'Valor: R$ {contrato.valor_total:,.2f}',
                    data_contato=timezone.now()
                )
                
                messages.success(request, f'Contrato {contrato.numero} criado com sucesso!')
                return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato.id)
            else:
                messages.error(request, 'Erro ao criar contrato. Verifique os dados informados.')
        else:
            # Pré-preencher com proposta se fornecida
            proposta_id = request.GET.get('proposta')
            initial_data = {}
            
            if proposta_id:
                try:
                    proposta = Proposta.objects.get(id=proposta_id)
                    if not loja or proposta.loja == loja:
                        initial_data = {
                            'lead': proposta.lead,
                            'proposta_base': proposta,
                            'titulo': f"Contrato baseado na {proposta.titulo}",
                            'valor_total': proposta.valor_total,
                            'objeto': proposta.resumo_executivo,
                        }
                except Proposta.DoesNotExist:
                    pass
            
            form = ContratoForm(initial=initial_data, user=request.user)
        
        context = {
            'form': form,
            'title': 'Novo Contrato',
        }
        
        return render(request, 'crm_vendas/contratos/criar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao criar contrato: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_contratos')

@login_required
def detalhar_contrato(request, contrato_id): 
    """Detalhes de um contrato"""
    try:
        contrato = get_object_or_404(Contrato, id=contrato_id)
        
        # Verificar permissão
        if not request.user.is_superuser and contrato.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para visualizar este contrato.')
            return redirect('crm_vendas:listar_contratos')
        
        # Buscar histórico de contatos relacionados
        historico = HistoricoContato.objects.filter(lead=contrato.lead).order_by('-data_contato')[:10]
        
        # Verificar se pode editar (apenas rascunho)
        pode_editar = contrato.status == 'rascunho'
        
        # Verificar se pode enviar
        pode_enviar = contrato.status == 'rascunho'
        
        # Verificar status das assinaturas
        assinado_cliente = contrato.assinado_cliente_em is not None
        assinado_empresa = contrato.assinado_empresa_em is not None
        
        context = {
            'contrato': contrato,
            'historico': historico,
            'pode_editar': pode_editar,
            'pode_enviar': pode_enviar,
            'assinado_cliente': assinado_cliente,
            'assinado_empresa': assinado_empresa,
        }
        
        return render(request, 'crm_vendas/contratos/detalhar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao detalhar contrato: {str(e)}")
        messages.error(request, 'Erro ao carregar contrato.')
        return redirect('crm_vendas:listar_contratos')

@login_required
def enviar_contrato(request, contrato_id): 
    """Envia um contrato por email"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    messages.info(request, 'Funcionalidade de envio de contrato em desenvolvimento.')
    return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato_id)

@login_required
def editar_lead(request, lead_id): 
    """Edita um lead"""
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Verificar permissão
    if not request.user.is_superuser and hasattr(request.user, 'loja_admin'):
        if lead.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para editar este lead.')
            return redirect('crm_vendas:listar_leads')
    
    if request.method == 'POST':
        try:
            # Atualizar dados do lead
            lead.nome = request.POST.get('nome', lead.nome)
            lead.email = request.POST.get('email', lead.email)
            lead.telefone = request.POST.get('telefone', lead.telefone)
            lead.empresa = request.POST.get('empresa', lead.empresa)
            lead.cargo = request.POST.get('cargo', lead.cargo)
            lead.endereco = request.POST.get('endereco', lead.endereco)
            lead.cidade = request.POST.get('cidade', lead.cidade)
            lead.estado = request.POST.get('estado', lead.estado)
            lead.cep = request.POST.get('cep', lead.cep)
            lead.status = request.POST.get('status', lead.status)
            lead.origem = request.POST.get('origem', lead.origem)
            lead.valor_estimado = request.POST.get('valor_estimado', lead.valor_estimado) or 0
            lead.probabilidade = request.POST.get('probabilidade', lead.probabilidade) or 50
            lead.observacoes = request.POST.get('observacoes', lead.observacoes)
            
            # Responsável (apenas super admin pode alterar)
            if request.user.is_superuser:
                responsavel_id = request.POST.get('responsavel')
                if responsavel_id:
                    lead.responsavel_id = responsavel_id
            
            lead.save()
            
            messages.success(request, f'Lead "{lead.nome}" atualizado com sucesso!')
            return redirect('crm_vendas:detalhar_lead', lead_id=lead_id)
            
        except Exception as e:
            logger.error(f"Erro ao editar lead {lead_id}: {str(e)}")
            messages.error(request, 'Erro ao atualizar lead. Verifique os dados informados.')
    
    # Buscar usuários para o campo responsável (apenas super admin)
    usuarios = []
    if request.user.is_superuser:
        usuarios = User.objects.filter(is_active=True).order_by('first_name', 'username')
    
    context = {
        'lead': lead,
        'usuarios': usuarios,
        'status_choices': Lead.STATUS_CHOICES,
        'origem_choices': Lead.ORIGEM_CHOICES,
    }
    
    return render(request, 'crm_vendas/leads/editar.html', context)


@login_required
def excluir_lead(request, lead_id):
    """Exclui um lead"""
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Verificar permissão
    if not request.user.is_superuser and hasattr(request.user, 'loja_admin'):
        if lead.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para excluir este lead.')
            return redirect('crm_vendas:listar_leads')
    
    if request.method == 'POST':
        try:
            nome_lead = lead.nome
            lead.delete()
            messages.success(request, f'Lead "{nome_lead}" excluído com sucesso!')
            return redirect('crm_vendas:listar_leads')
        except Exception as e:
            logger.error(f"Erro ao excluir lead {lead_id}: {str(e)}")
            messages.error(request, 'Erro ao excluir lead. Tente novamente.')
            return redirect('crm_vendas:detalhar_lead', lead_id=lead_id)
    
    context = {
        'lead': lead,
    }
    
    return render(request, 'crm_vendas/leads/excluir.html', context)


@login_required
def registrar_contato(request, lead_id): 
    """Registra um novo contato com um lead"""
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Verificar permissão
    if not request.user.is_superuser and lead.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para registrar contatos neste lead.')
        return redirect('crm_vendas:listar_leads')
    
    if request.method == 'POST':
        form = HistoricoContatoForm(request.POST)
        if form.is_valid():
            try:
                contato = form.save(commit=False)
                contato.lead = lead
                contato.usuario = request.user
                contato.save()
                
                # Atualizar data do último contato no lead
                lead.data_ultimo_contato = timezone.now()
                
                # Se foi definida uma data para próximo contato, atualizar no lead
                if contato.data_proximo_contato:
                    lead.data_proximo_contato = contato.data_proximo_contato
                
                lead.save()
                
                messages.success(request, f'Contato registrado com sucesso! Tipo: {contato.get_tipo_display()}')
                return redirect('crm_vendas:detalhar_lead', lead_id=lead.id)
                
            except Exception as e:
                logger.error(f"Erro ao registrar contato para lead {lead_id}: {str(e)}")
                messages.error(request, f'Erro ao registrar contato: {str(e)}')
        else:
            # Exibir erros de validação
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = HistoricoContatoForm()
    
    context = {
        'form': form,
        'lead': lead,
        'titulo': f'Registrar Contato - {lead.nome}'
    }
    
    return render(request, 'crm_vendas/leads/registrar_contato.html', context)
@csrf_exempt
def visualizar_proposta_publico(request, proposta_id):
    """Visualização pública da proposta (para clientes)"""
    
    proposta = get_object_or_404(Proposta, id=proposta_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'aprovar':
            proposta.status = 'aprovada'
            proposta.data_resposta = timezone.now()
            proposta.save()
            
            # Atualizar lead
            proposta.lead.status = 'proposta_aceita'
            proposta.lead.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=proposta.lead,
                tipo='email',
                assunto='Proposta Aceita',
                descricao=f'Cliente aceitou a proposta {proposta.numero}',
                resultado='Proposta aceita pelo cliente',
                data_contato=timezone.now()
            )
            
            messages.success(request, 'Proposta aceita com sucesso! Entraremos em contato para elaborar o contrato.')
            
        elif acao == 'rejeitar':
            proposta.status = 'rejeitada'
            proposta.data_resposta = timezone.now()
            proposta.save()
            
            # Atualizar lead
            proposta.lead.status = 'fechado_perdido'
            proposta.lead.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=proposta.lead,
                tipo='email',
                assunto='Proposta Rejeitada',
                descricao=f'Cliente rejeitou a proposta {proposta.numero}',
                resultado='Proposta rejeitada pelo cliente',
                data_contato=timezone.now()
            )
            
            messages.info(request, 'Proposta rejeitada. Agradecemos seu interesse.')
            
        elif acao == 'revisar':
            proposta.status = 'em_analise'
            proposta.save()
            
            observacoes = request.POST.get('observacoes_revisao', '')
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=proposta.lead,
                tipo='email',
                assunto='Solicitação de Revisão',
                descricao=f'Cliente solicitou revisão da proposta {proposta.numero}',
                resultado=f'Revisão solicitada: {observacoes}',
                data_contato=timezone.now()
            )
            
            messages.info(request, 'Solicitação de revisão enviada. Entraremos em contato em breve.')
    
    context = {
        'proposta': proposta,
    }
    
    return render(request, 'crm_vendas/publico/proposta.html', context)
@csrf_exempt
def assinar_contrato_publico(request, contrato_id):
    """Assinatura digital pública do contrato (para clientes)"""
    
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    if request.method == 'POST':
        # Verificar se já foi assinado
        if contrato.assinado_cliente_em:
            messages.warning(request, 'Este contrato já foi assinado por você.')
        else:
            # Registrar assinatura do cliente
            contrato.assinado_cliente_em = timezone.now()
            contrato.status = 'assinado_cliente'
            contrato.save()
            
            # Atualizar lead
            contrato.lead.status = 'fechado_ganho'
            contrato.lead.save()
            
            # Registrar no histórico
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'N/A'))
            user_agent = request.META.get('HTTP_USER_AGENT', 'N/A')
            
            HistoricoContato.objects.create(
                lead=contrato.lead,
                tipo='outros',
                assunto='Contrato Assinado Digitalmente',
                descricao=f'Cliente assinou digitalmente o contrato {contrato.numero}',
                resultado=f'Assinatura digital realizada. IP: {ip_address}',
                data_contato=timezone.now()
            )
            
            messages.success(request, 'Contrato assinado digitalmente com sucesso!')
            
            # Se a empresa já assinou, ativar o contrato
            if contrato.assinado_empresa_em:
                contrato.status = 'ativo'
                contrato.save()
                
                messages.success(request, 'Contrato está agora ativo! Todas as partes assinaram.')
    
    context = {
        'contrato': contrato,
    }
    
    return render(request, 'crm_vendas/publico/contrato.html', context)
def track_email_clique(request, token): 
    """Track de cliques em emails"""
    # TODO: Implementar tracking de cliques
    return redirect('crm_vendas:dashboard')


@login_required
def relatorio_funil_vendas(request):
    """Relatório do funil de vendas"""
    # Filtrar por loja se não for super admin
    if request.user.is_superuser:
        leads = Lead.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            leads = Lead.objects.filter(loja=loja)
        except:
            leads = Lead.objects.none()
    
    # Contar leads por status para o funil
    funil_data = {
        'leads_novos': leads.filter(status='novo').count(),
        'leads_qualificados': leads.filter(status='qualificado').count(),
        'leads_interessados': leads.filter(status='proposta_enviada').count(),
        'em_negociacao': leads.filter(status='negociacao').count(),
        'fechados_ganhos': leads.filter(status='fechado_ganho').count(),
        'fechados_perdidos': leads.filter(status='fechado_perdido').count(),
    }
    
    context = {
        'funil': funil_data,
    }
    
    return render(request, 'crm_vendas/funil.html', context)
    # Verificar permissão
    if not request.user.is_superuser and not hasattr(request.user, 'loja_admin'):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('crm_vendas:dashboard')
    
    # Determinar loja
    loja = None
    if request.user.is_superuser:
        # Super admin pode ver todas as lojas ou uma específica
        loja_id = request.GET.get('loja')
        if loja_id:
            try:
                loja = Loja.objects.get(id=loja_id)
            except Loja.DoesNotExist:
                pass
    else:
        loja = request.user.loja_admin
    
    # Filtrar leads por loja se especificada
    leads_query = Lead.objects.all()
    if loja:
        leads_query = leads_query.filter(loja=loja)
    
    # Estatísticas do funil
    stats = {
        'total_leads': leads_query.count(),
        'novos': leads_query.filter(status='novo').count(),
        'qualificados': leads_query.filter(status='qualificado').count(),
        'proposta_enviada': leads_query.filter(status='proposta_enviada').count(),
        'negociacao': leads_query.filter(status='negociacao').count(),
        'fechado_ganho': leads_query.filter(status='fechado_ganho').count(),
        'fechado_perdido': leads_query.filter(status='fechado_perdido').count(),
    }
    
    # Calcular taxas de conversão
    conversao = {}
    if stats['total_leads'] > 0:
        conversao['qualificacao'] = (stats['qualificados'] / stats['total_leads']) * 100
        conversao['proposta'] = (stats['proposta_enviada'] / stats['total_leads']) * 100
        conversao['fechamento'] = (stats['fechado_ganho'] / stats['total_leads']) * 100
    
    context = {
        'loja': loja,
        'stats': stats,
        'conversao': conversao,
        'leads_recentes': leads_query.order_by('-data_criacao')[:10],
    }
    
    return render(request, 'crm_vendas/funil.html', context)


@login_required
def relatorio_performance(request):
    """Relatório de performance de vendas"""
    
    # Verificar permissão
    if not request.user.is_superuser and not hasattr(request.user, 'loja_admin'):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('crm_vendas:dashboard')
    
    # Determinar loja
    loja = None
    if request.user.is_superuser:
        loja_id = request.GET.get('loja')
        if loja_id:
            try:
                loja = Loja.objects.get(id=loja_id)
            except Loja.DoesNotExist:
                pass
    else:
        loja = request.user.loja_admin
    
    context = {
        'loja': loja,
        'em_desenvolvimento': True,
    }
    
    return render(request, 'crm_vendas/relatorios.html', context)


@login_required
def configuracoes_crm(request):
    """Configurações do CRM"""
    # Verificar permissão
    if not request.user.is_superuser and not hasattr(request.user, 'loja_admin'):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('crm_vendas:dashboard')
    
    # Determinar loja
    loja = None
    if request.user.is_superuser:
        loja_id = request.GET.get('loja')
        if loja_id:
            try:
                loja = Loja.objects.get(id=loja_id)
            except Loja.DoesNotExist:
                pass
    else:
        loja = request.user.loja_admin
    
    context = {
        'loja': loja,
        'em_desenvolvimento': True,
    }
    
    return render(request, 'crm_vendas/configuracoes.html', context)

# ============================================================================
# NOVAS VIEWS PARA FLUXO COMPLETO DO CRM
# ============================================================================

@login_required
def criar_lead_melhorado(request):
    """Cria novo lead com campos melhorados"""
    
    if request.method == 'POST':
        form = LeadForm(request.POST)
        
        # Debug: log dos dados recebidos
        logger.info(f"POST data recebido: {request.POST}")
        
        if form.is_valid():
            try:
                lead = form.save(commit=False)
                
                # Definir loja
                if request.user.is_superuser:
                    # Super admin pode escolher a loja (implementar seleção)
                    loja = Loja.objects.first()  # Temporário
                else:
                    try:
                        loja = request.user.loja_admin
                    except:
                        loja = Loja.objects.first()  # Fallback
                
                if not loja:
                    messages.error(request, 'Erro: Nenhuma loja encontrada para associar ao lead.')
                    logger.error("Nenhuma loja encontrada para criar lead")
                else:
                    lead.loja = loja
                    lead.responsavel = request.user
                    lead.save()
                    
                    logger.info(f"Lead criado com sucesso: {lead.nome} (ID: {lead.id})")
                    messages.success(request, f'Lead "{lead.nome}" criado com sucesso!')
                    return redirect('crm_vendas:detalhar_lead', lead_id=lead.id)
                
            except Exception as e:
                logger.error(f"Erro ao criar lead: {str(e)}")
                messages.error(request, f'Erro ao criar lead: {str(e)}')
        else:
            # Debug: log dos erros de validação
            logger.error(f"Erros de validação do formulário: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'titulo': 'Novo Lead'
    }
    
    return render(request, 'crm_vendas/leads/form_melhorado.html', context)


# ============================================================================
# PRODUTOS E SERVIÇOS
# ============================================================================

@login_required
def listar_produtos_servicos(request):
    """Lista produtos e serviços"""
    
    # Filtrar por loja
    if request.user.is_superuser:
        produtos_servicos = ProdutoServico.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            produtos_servicos = ProdutoServico.objects.filter(loja=loja)
        except:
            messages.error(request, 'Usuário não associado a nenhuma loja.')
            return redirect('dashboard:index')
    
    # Filtros
    tipo = request.GET.get('tipo')
    categoria = request.GET.get('categoria')
    ativo = request.GET.get('ativo')
    busca = request.GET.get('busca')
    
    if tipo:
        produtos_servicos = produtos_servicos.filter(tipo=tipo)
    if categoria:
        produtos_servicos = produtos_servicos.filter(categoria__icontains=categoria)
    if ativo:
        produtos_servicos = produtos_servicos.filter(ativo=ativo == 'true')
    if busca:
        produtos_servicos = produtos_servicos.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca) |
            Q(codigo__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(produtos_servicos, 20)
    page = request.GET.get('page')
    produtos_servicos = paginator.get_page(page)
    
    # Categorias para filtro
    categorias = ProdutoServico.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'produtos_servicos': produtos_servicos,
        'categorias': categorias,
        'filtros': {
            'tipo': tipo,
            'categoria': categoria,
            'ativo': ativo,
            'busca': busca,
        }
    }
    
    return render(request, 'crm_vendas/produtos_servicos/listar.html', context)


@login_required
def criar_produto_servico(request):
    """Cria novo produto/serviço"""
    
    if request.method == 'POST':
        form = ProdutoServicoForm(request.POST)
        if form.is_valid():
            try:
                produto_servico = form.save(commit=False)
                
                # Definir loja
                if request.user.is_superuser:
                    # Super admin pode escolher a loja (implementar seleção)
                    loja = Loja.objects.first()  # Temporário
                else:
                    loja = request.user.loja_admin
                
                produto_servico.loja = loja
                produto_servico.save()
                
                messages.success(request, f'Produto/Serviço "{produto_servico.nome}" criado com sucesso!')
                return redirect('crm_vendas:listar_produtos_servicos')
                
            except Exception as e:
                logger.error(f"Erro ao criar produto/serviço: {str(e)}")
                messages.error(request, 'Erro ao criar produto/serviço. Tente novamente.')
    else:
        form = ProdutoServicoForm()
    
    context = {
        'form': form,
        'titulo': 'Novo Produto/Serviço'
    }
    
    return render(request, 'crm_vendas/produtos_servicos/form.html', context)


@login_required
def editar_produto_servico(request, produto_id):
    """Edita produto/serviço"""
    
    produto_servico = get_object_or_404(ProdutoServico, id=produto_id)
    
    # Verificar permissão
    if not request.user.is_superuser and produto_servico.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para editar este produto/serviço.')
        return redirect('crm_vendas:listar_produtos_servicos')
    
    if request.method == 'POST':
        form = ProdutoServicoForm(request.POST, instance=produto_servico)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Produto/Serviço "{produto_servico.nome}" atualizado com sucesso!')
                return redirect('crm_vendas:listar_produtos_servicos')
                
            except Exception as e:
                logger.error(f"Erro ao atualizar produto/serviço {produto_id}: {str(e)}")
                messages.error(request, 'Erro ao atualizar produto/serviço. Tente novamente.')
    else:
        form = ProdutoServicoForm(instance=produto_servico)
    
    context = {
        'form': form,
        'produto_servico': produto_servico,
        'titulo': f'Editar {produto_servico.nome}'
    }
    
    return render(request, 'crm_vendas/produtos_servicos/form.html', context)


# ============================================================================
# LEADS MELHORADOS
# ============================================================================




# ============================================================================
# ORÇAMENTOS MELHORADOS
# ============================================================================

@login_required
def criar_orcamento_melhorado(request):
    """Cria orçamento com produtos/serviços"""
    
    lead_id = request.GET.get('lead')
    lead = None
    if lead_id:
        lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            try:
                orcamento = form.save(commit=False)
                
                # Definir loja
                if request.user.is_superuser:
                    loja = Loja.objects.first()  # Temporário
                else:
                    loja = request.user.loja_admin
                
                orcamento.loja = loja
                orcamento.responsavel = request.user
                orcamento.save()
                
                messages.success(request, f'Orçamento "{orcamento.numero}" criado com sucesso!')
                return redirect('crm_vendas:editar_orcamento_itens', orcamento_id=orcamento.id)
                
            except Exception as e:
                logger.error(f"Erro ao criar orçamento: {str(e)}")
                messages.error(request, 'Erro ao criar orçamento. Tente novamente.')
    else:
        initial = {}
        if lead:
            initial['lead'] = lead
        form = OrcamentoForm(initial=initial)
    
    context = {
        'form': form,
        'lead': lead,
        'titulo': 'Novo Orçamento'
    }
    
    return render(request, 'crm_vendas/orcamentos/form_melhorado.html', context)


@login_required
def editar_orcamento_itens(request, orcamento_id):
    """Edita itens do orçamento"""
    
    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    
    # Verificar permissão
    if not request.user.is_superuser and orcamento.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para editar este orçamento.')
        return redirect('crm_vendas:listar_orcamentos')
    
    # Produtos/serviços disponíveis
    produtos_servicos = ProdutoServico.objects.filter(loja=orcamento.loja, ativo=True)
    
    if request.method == 'POST':
        # Processar adição de item
        if 'adicionar_item' in request.POST:
            form_item = ItemOrcamentoForm(request.POST)
            if form_item.is_valid():
                item = form_item.save(commit=False)
                item.orcamento = orcamento
                item.save()
                messages.success(request, 'Item adicionado com sucesso!')
                return redirect('crm_vendas:editar_orcamento_itens', orcamento_id=orcamento_id)
        
        # Processar remoção de item
        elif 'remover_item' in request.POST:
            item_id = request.POST.get('item_id')
            try:
                item = ItemOrcamento.objects.get(id=item_id, orcamento=orcamento)
                item.delete()
                messages.success(request, 'Item removido com sucesso!')
            except ItemOrcamento.DoesNotExist:
                messages.error(request, 'Item não encontrado.')
            return redirect('crm_vendas:editar_orcamento_itens', orcamento_id=orcamento_id)
    
    form_item = ItemOrcamentoForm()
    
    context = {
        'orcamento': orcamento,
        'form_item': form_item,
        'produtos_servicos': produtos_servicos,
        'titulo': f'Editar Itens - {orcamento.numero}'
    }
    
    return render(request, 'crm_vendas/orcamentos/editar_itens.html', context)


# ============================================================================
# ASSINATURA DIGITAL
# ============================================================================

@login_required
def solicitar_assinatura(request, tipo_documento, documento_id):
    """Solicita assinatura digital de documento"""
    
    # Buscar documento
    documento = None
    if tipo_documento == 'orcamento':
        documento = get_object_or_404(Orcamento, id=documento_id)
    elif tipo_documento == 'proposta':
        documento = get_object_or_404(Proposta, id=documento_id)
    elif tipo_documento == 'contrato':
        documento = get_object_or_404(Contrato, id=documento_id)
    else:
        messages.error(request, 'Tipo de documento inválido.')
        return redirect('crm_vendas:dashboard')
    
    # Verificar permissão
    if not request.user.is_superuser and documento.loja != request.user.loja_admin:
        messages.error(request, 'Você não tem permissão para este documento.')
        return redirect('crm_vendas:dashboard')
    
    if request.method == 'POST':
        form = AssinaturaDigitalForm(request.POST)
        if form.is_valid():
            try:
                assinatura = form.save(commit=False)
                assinatura.lead = documento.lead
                assinatura.tipo_documento = tipo_documento
                
                # Associar documento específico
                if tipo_documento == 'orcamento':
                    assinatura.orcamento = documento
                elif tipo_documento == 'proposta':
                    assinatura.proposta = documento
                elif tipo_documento == 'contrato':
                    assinatura.contrato = documento
                
                # Definir data de expiração (30 dias)
                assinatura.data_expiracao = timezone.now() + timezone.timedelta(days=30)
                assinatura.save()
                
                # Enviar email com link de assinatura
                from .services.email_service import EmailService
                
                logger.info(f"Tentando enviar email de assinatura para {assinatura.email_signatario}")
                sucesso_email = EmailService.enviar_solicitacao_assinatura(assinatura)
                
                if sucesso_email:
                    messages.success(request, f'Solicitação de assinatura enviada para {assinatura.email_signatario}!')
                    logger.info(f"Email de assinatura enviado com sucesso para {assinatura.email_signatario}")
                else:
                    messages.warning(request, 'Solicitação criada, mas houve erro no envio do email. Verifique as configurações de email.')
                    logger.error(f"Falha no envio do email de assinatura para {assinatura.email_signatario}")
                
                return redirect('crm_vendas:detalhar_lead', lead_id=documento.lead.id)
                
            except Exception as e:
                logger.error(f"Erro ao solicitar assinatura: {str(e)}")
                messages.error(request, 'Erro ao solicitar assinatura. Tente novamente.')
    else:
        # Preencher dados do lead
        initial = {
            'nome_signatario': documento.lead.nome,
            'email_signatario': documento.lead.email,
            'cpf_signatario': documento.lead.cpf,
        }
        form = AssinaturaDigitalForm(initial=initial)
    
    context = {
        'form': form,
        'documento': documento,
        'tipo_documento': tipo_documento,
        'titulo': f'Solicitar Assinatura - {documento}'
    }
    
    return render(request, 'crm_vendas/assinaturas/solicitar.html', context)


@csrf_exempt
def assinar_documento_publico(request, token):
    """Página pública para assinatura de documento"""
    
    logger.info(f"Tentativa de acesso à assinatura pública com token: {token}")
    
    try:
        assinatura = get_object_or_404(AssinaturaDigital, token_acesso=token)
        logger.info(f"Assinatura encontrada: {assinatura.id} - Status: {assinatura.status}")
    except Exception as e:
        logger.error(f"Erro ao buscar assinatura com token {token}: {str(e)}")
        raise
    
    # Verificar se não expirou
    if assinatura.esta_expirado:
        return render(request, 'crm_vendas/assinaturas/expirado.html', {'assinatura': assinatura})
    
    # Marcar como visualizado
    if not assinatura.data_visualizacao:
        assinatura.data_visualizacao = timezone.now()
        assinatura.status = 'visualizado'
        assinatura.save()
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'assinar':
            # Processar assinatura
            assinatura.status = 'assinado'
            assinatura.data_assinatura = timezone.now()
            assinatura.ip_assinatura = request.META.get('REMOTE_ADDR')
            assinatura.user_agent = request.META.get('HTTP_USER_AGENT', '')
            assinatura.save()
            
            # Atualizar status do documento
            if assinatura.orcamento:
                assinatura.orcamento.status = 'aprovado'
                assinatura.orcamento.data_resposta = timezone.now()
                assinatura.orcamento.save()
            elif assinatura.proposta:
                assinatura.proposta.status = 'aprovada'
                assinatura.proposta.data_resposta = timezone.now()
                assinatura.proposta.save()
            elif assinatura.contrato:
                assinatura.contrato.status = 'assinado_cliente'
                assinatura.contrato.assinado_cliente_em = timezone.now()
                assinatura.contrato.save()
            
            return render(request, 'crm_vendas/assinaturas/sucesso.html', {'assinatura': assinatura})
        
        elif acao == 'rejeitar':
            motivo = request.POST.get('motivo_rejeicao', '')
            assinatura.status = 'rejeitado'
            assinatura.motivo_rejeicao = motivo
            assinatura.data_assinatura = timezone.now()
            assinatura.save()
            
            # Atualizar status do documento
            if assinatura.orcamento:
                assinatura.orcamento.status = 'rejeitado'
                assinatura.orcamento.save()
            elif assinatura.proposta:
                assinatura.proposta.status = 'rejeitada'
                assinatura.proposta.save()
            
            return render(request, 'crm_vendas/assinaturas/rejeitado.html', {'assinatura': assinatura})
    
    context = {
        'assinatura': assinatura,
    }
    
    return render(request, 'crm_vendas/assinaturas/assinar.html', context)


# ============================================================================
# RELATÓRIOS
# ============================================================================

@login_required
def relatorios_vendas(request):
    """Relatórios de vendas"""
    
    # Filtrar por loja
    if request.user.is_superuser:
        leads = Lead.objects.all()
        orcamentos = Orcamento.objects.all()
        propostas = Proposta.objects.all()
        contratos = Contrato.objects.all()
    else:
        try:
            loja = request.user.loja_admin
            leads = Lead.objects.filter(loja=loja)
            orcamentos = Orcamento.objects.filter(loja=loja)
            propostas = Proposta.objects.filter(loja=loja)
            contratos = Contrato.objects.filter(loja=loja)
        except:
            messages.error(request, 'Usuário não associado a nenhuma loja.')
            return redirect('dashboard:index')
    
    # Período
    periodo = request.GET.get('periodo', '30')  # últimos 30 dias
    data_inicio = timezone.now() - timezone.timedelta(days=int(periodo))
    
    # Estatísticas do período
    stats = {
        'leads_criados': leads.filter(data_criacao__gte=data_inicio).count(),
        'leads_convertidos': leads.filter(status='fechado_ganho', data_atualizacao__gte=data_inicio).count(),
        'orcamentos_enviados': orcamentos.filter(data_envio__gte=data_inicio).count(),
        'orcamentos_aprovados': orcamentos.filter(status='aprovado', data_resposta__gte=data_inicio).count(),
        'propostas_enviadas': propostas.filter(data_envio__gte=data_inicio).count(),
        'propostas_aprovadas': propostas.filter(status='aprovada', data_resposta__gte=data_inicio).count(),
        'contratos_assinados': contratos.filter(status__in=['assinado_cliente', 'ativo'], assinado_cliente_em__gte=data_inicio).count(),
        'valor_total_vendas': contratos.filter(status__in=['assinado_cliente', 'ativo'], assinado_cliente_em__gte=data_inicio).aggregate(total=Sum('valor_total'))['total'] or 0,
    }
    
    # Taxa de conversão
    if stats['leads_criados'] > 0:
        stats['taxa_conversao'] = (stats['leads_convertidos'] / stats['leads_criados']) * 100
    else:
        stats['taxa_conversao'] = 0
    
    # Leads por status
    leads_por_status = leads.values('status').annotate(count=Count('id')).order_by('-count')
    
    # Origem dos leads
    leads_por_origem = leads.filter(data_criacao__gte=data_inicio).values('origem').annotate(count=Count('id')).order_by('-count')
    
    # Top produtos/serviços
    top_produtos = ItemOrcamento.objects.filter(
        orcamento__data_criacao__gte=data_inicio,
        orcamento__status='aprovado'
    ).values('descricao').annotate(
        quantidade_total=Sum('quantidade'),
        valor_total=Sum('valor_total')
    ).order_by('-valor_total')[:10]
    
    context = {
        'stats': stats,
        'leads_por_status': leads_por_status,
        'leads_por_origem': leads_por_origem,
        'top_produtos': top_produtos,
        'periodo': periodo,
    }
    
    return render(request, 'crm_vendas/relatorios/vendas.html', context)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required
def api_produto_servico_detalhes(request, produto_id):
    """API para buscar detalhes de produto/serviço"""
    
    try:
        produto = get_object_or_404(ProdutoServico, id=produto_id)
        
        # Verificar permissão
        if not request.user.is_superuser and produto.loja != request.user.loja_admin:
            return JsonResponse({'error': 'Sem permissão'}, status=403)
        
        data = {
            'id': str(produto.id),
            'nome': produto.nome,
            'descricao': produto.descricao,
            'preco_base': float(produto.preco_base),
            'unidade': produto.unidade,
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def assinar_documento_publico(request, token):
    """
    View pública para assinatura digital de documentos
    """
    try:
        # Buscar assinatura pelo token
        assinatura = get_object_or_404(AssinaturaDigital, token_acesso=token)
        
        # Verificar se o token ainda é válido
        if assinatura.data_expiracao and assinatura.data_expiracao < timezone.now():
            return render(request, 'crm_vendas/assinatura_expirada.html', {
                'assinatura': assinatura
            })
        
        # Verificar se já foi assinado
        if assinatura.status == 'assinado':
            return render(request, 'crm_vendas/documento_ja_assinado.html', {
                'assinatura': assinatura
            })
        
        if request.method == 'POST':
            # Processar assinatura
            assinatura.status = 'assinado'
            assinatura.data_assinatura = timezone.now()
            assinatura.ip_assinatura = request.META.get('REMOTE_ADDR')
            assinatura.user_agent = request.META.get('HTTP_USER_AGENT', '')
            assinatura.save()
            
            # Atualizar documento baseado no tipo de signatário
            if assinatura.tipo_signatario == 'cliente':
                if assinatura.orcamento:
                    assinatura.orcamento.status = 'aprovado'
                    assinatura.orcamento.data_resposta = timezone.now()
                    assinatura.orcamento.save()
                    # Solicitar automaticamente assinatura da empresa
                    _solicitar_assinatura_empresa_automatica(assinatura.orcamento, 'orcamento')
                elif assinatura.proposta:
                    assinatura.proposta.status = 'aprovada'
                    assinatura.proposta.data_resposta = timezone.now()
                    assinatura.proposta.save()
                    # Solicitar automaticamente assinatura da empresa
                    _solicitar_assinatura_empresa_automatica(assinatura.proposta, 'proposta')
                elif assinatura.contrato:
                    assinatura.contrato.status = 'assinado_cliente'
                    assinatura.contrato.assinado_cliente_em = timezone.now()
                    assinatura.contrato.save()
                    # Solicitar automaticamente assinatura da empresa
                    _solicitar_assinatura_empresa_automatica(assinatura.contrato, 'contrato')
            
            elif assinatura.tipo_signatario == 'empresa':
                if assinatura.orcamento:
                    # Enviar documento final com ambas assinaturas
                    _enviar_documento_final_assinado(assinatura.orcamento, 'orcamento')
                elif assinatura.proposta:
                    # Enviar documento final com ambas assinaturas
                    _enviar_documento_final_assinado(assinatura.proposta, 'proposta')
                elif assinatura.contrato:
                    assinatura.contrato.assinado_empresa_em = timezone.now()
                    # Se cliente já assinou, ativar contrato
                    if assinatura.contrato.assinado_cliente_em:
                        assinatura.contrato.status = 'ativo'
                    else:
                        assinatura.contrato.status = 'assinado_empresa'
                    assinatura.contrato.save()
                    # Enviar documento final com ambas assinaturas
                    _enviar_documento_final_assinado(assinatura.contrato, 'contrato')
            
            # Log da assinatura
            logger.info(f"Documento assinado digitalmente: {assinatura.tipo_documento} por {assinatura.nome_signatario} ({assinatura.tipo_signatario})")
            
            return render(request, 'crm_vendas/assinatura_concluida.html', {
                'assinatura': assinatura
            })
        
        # Exibir formulário de assinatura
        return render(request, 'crm_vendas/assinar_documento.html', {
            'assinatura': assinatura
        })
        
    except Exception as e:
        logger.error(f"Erro na assinatura digital: {str(e)}")
        return render(request, 'crm_vendas/erro_assinatura.html', {
            'erro': 'Erro interno do servidor'
        })


def solicitar_assinatura_empresa(request, tipo_documento, documento_id):
    """
    View para solicitar assinatura da empresa após cliente ter assinado
    """
    try:
        # Verificar se o usuário tem permissão
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Buscar o documento baseado no tipo
        documento = None
        if tipo_documento == 'orcamento':
            documento = get_object_or_404(Orcamento, id=documento_id)
        elif tipo_documento == 'proposta':
            documento = get_object_or_404(Proposta, id=documento_id)
        elif tipo_documento == 'contrato':
            documento = get_object_or_404(Contrato, id=documento_id)
        else:
            messages.error(request, 'Tipo de documento inválido.')
            return redirect('crm_vendas:dashboard')
        
        # Verificar permissão
        if not request.user.is_superuser and documento.loja != request.user.loja_admin:
            messages.error(request, 'Sem permissão para acessar este documento.')
            return redirect('crm_vendas:dashboard')
        
        # Verificar se cliente já assinou (para contratos)
        if tipo_documento == 'contrato' and not documento.assinado_cliente_em:
            messages.error(request, 'O cliente deve assinar primeiro antes da empresa.')
            return redirect('crm_vendas:dashboard')
        
        if request.method == 'POST':
            form = AssinaturaDigitalForm(request.POST)
            if form.is_valid():
                assinatura = form.save(commit=False)
                assinatura.tipo_documento = tipo_documento
                assinatura.tipo_signatario = 'empresa'
                assinatura.lead = documento.lead if hasattr(documento, 'lead') else None
                
                # Associar o documento correto baseado no tipo
                if tipo_documento == 'orcamento':
                    assinatura.orcamento = documento
                elif tipo_documento == 'proposta':
                    assinatura.proposta = documento
                elif tipo_documento == 'contrato':
                    assinatura.contrato = documento
                
                assinatura.save()
                
                # Enviar email de solicitação
                try:
                    EmailService.enviar_solicitacao_assinatura(assinatura)
                    messages.success(request, 'Solicitação de assinatura da empresa enviada com sucesso!')
                except Exception as e:
                    logger.error(f"Erro ao enviar email de assinatura da empresa: {str(e)}")
                    messages.warning(request, 'Assinatura criada, mas houve erro no envio do email.')
                
                return redirect('crm_vendas:dashboard')
        else:
            # Pré-preencher com dados da empresa/loja
            initial = {
                'nome_signatario': documento.loja.nome,
                'email_signatario': documento.loja.email,
                'cpf_signatario': documento.loja.cnpj,  # ou CPF do responsável se houver
            }
            form = AssinaturaDigitalForm(initial=initial)
        
        return render(request, 'crm_vendas/solicitar_assinatura_empresa.html', {
            'form': form,
            'documento': documento,
            'tipo_documento': tipo_documento
        })
        
    except Exception as e:
        logger.error(f"Erro ao solicitar assinatura da empresa: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:dashboard')


def solicitar_assinatura(request, tipo_documento, documento_id):
    """
    View para solicitar assinatura digital de um documento (cliente)
    """
    try:
        # Verificar se o usuário tem permissão
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Buscar o documento baseado no tipo
        documento = None
        if tipo_documento == 'orcamento':
            documento = get_object_or_404(Orcamento, id=documento_id)
        elif tipo_documento == 'proposta':
            documento = get_object_or_404(Proposta, id=documento_id)
        elif tipo_documento == 'contrato':
            documento = get_object_or_404(Contrato, id=documento_id)
        else:
            messages.error(request, 'Tipo de documento inválido.')
            return redirect('crm_vendas:dashboard')
        
        # Verificar permissão
        if not request.user.is_superuser and documento.loja != request.user.loja_admin:
            messages.error(request, 'Sem permissão para acessar este documento.')
            return redirect('crm_vendas:dashboard')
        
        if request.method == 'POST':
            form = AssinaturaDigitalForm(request.POST)
            if form.is_valid():
                assinatura = form.save(commit=False)
                assinatura.tipo_documento = tipo_documento
                assinatura.lead = documento.lead if hasattr(documento, 'lead') else None
                
                # Associar o documento correto baseado no tipo
                if tipo_documento == 'orcamento':
                    assinatura.orcamento = documento
                elif tipo_documento == 'proposta':
                    assinatura.proposta = documento
                elif tipo_documento == 'contrato':
                    assinatura.contrato = documento
                
                assinatura.save()
                
                # Enviar email de solicitação
                try:
                    EmailService.enviar_solicitacao_assinatura(assinatura)
                    messages.success(request, 'Solicitação de assinatura enviada com sucesso!')
                except Exception as e:
                    logger.error(f"Erro ao enviar email de assinatura: {str(e)}")
                    messages.warning(request, 'Assinatura criada, mas houve erro no envio do email.')
                
                return redirect('crm_vendas:dashboard')
        else:
            form = AssinaturaDigitalForm()
        
        return render(request, 'crm_vendas/solicitar_assinatura.html', {
            'form': form,
            'documento': documento,
            'tipo_documento': tipo_documento
        })
        
    except Exception as e:
        logger.error(f"Erro ao solicitar assinatura: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:dashboard')

# ============================================================================
# FUNÇÕES AUXILIARES PARA AUTOMAÇÃO DE ASSINATURAS
# ============================================================================

def _solicitar_assinatura_empresa_automatica(documento, tipo_documento):
    """
    Solicita automaticamente assinatura da empresa após cliente assinar
    """
    from .services.assinatura_validator import AssinaturaDataValidator
    from django.db import IntegrityError
    
    try:
        # Verificar se já existe assinatura da empresa para este documento
        if AssinaturaDataValidator.check_company_signature_exists(documento, tipo_documento):
            logger.info(f"Assinatura da empresa já existe para {tipo_documento} {documento.numero}")
            return
        
        # Validar e sanitizar dados da empresa
        validated_data = AssinaturaDataValidator.validate_and_sanitize_company_data(
            documento.loja, documento, tipo_documento
        )
        
        # Criar solicitação de assinatura para a empresa
        try:
            assinatura = AssinaturaDigital.objects.create(**validated_data)
            logger.info(f"Assinatura da empresa criada com sucesso para {tipo_documento} {documento.numero}")
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao criar assinatura da empresa: {str(e)}")
            raise ValueError("Dados inválidos para criação de assinatura da empresa")
        
        # Enviar email automaticamente com retry
        try:
            success = EmailService.enviar_solicitacao_assinatura_com_retry(assinatura, max_retries=3)
            if success:
                logger.info(f"Email de assinatura da empresa enviado com sucesso para {tipo_documento} {documento.numero}")
            else:
                logger.error(f"Falha no envio de email após múltiplas tentativas para {tipo_documento} {documento.numero}")
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar email automático de assinatura da empresa: {str(e)}")
            # Marcar assinatura para reenvio posterior
            assinatura.status = 'pendente_reenvio'
            assinatura.save()
            
    except ValueError as e:
        logger.error(f"Erro de validação na assinatura automática da empresa: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao solicitar assinatura automática da empresa: {str(e)}")


def _enviar_documento_final_assinado(documento, tipo_documento):
    """
    Envia documento final com ambas assinaturas por email
    """
    try:
        # Verificar se ambas as assinaturas estão completas
        if not _verificar_documento_totalmente_assinado(documento, tipo_documento):
            logger.warning(f"Documento {tipo_documento} {documento.numero} não está totalmente assinado")
            return False
        
        # Preparar dados do email
        if tipo_documento == 'orcamento':
            assunto = f"Orçamento {documento.numero} - Aprovado e Assinado"
            template = 'crm_vendas/emails/orcamento_final_assinado.html'
        elif tipo_documento == 'proposta':
            assunto = f"Proposta {documento.numero} - Aprovada e Assinada"
            template = 'crm_vendas/emails/proposta_final_assinada.html'
        elif tipo_documento == 'contrato':
            assunto = f"Contrato {documento.numero} - Ativo e Assinado"
            template = 'crm_vendas/emails/contrato_final_assinado.html'
        else:
            logger.error(f"Tipo de documento inválido: {tipo_documento}")
            return False
        
        # Obter informações das assinaturas
        assinaturas_info = _obter_informacoes_assinaturas(documento, tipo_documento)
        
        # Contexto do email
        context = {
            'documento': documento,
            'lead': documento.lead,
            'loja': documento.loja,
            'tipo_documento': tipo_documento,
            'data_envio': timezone.now(),
            'assinatura_cliente': assinaturas_info.get('cliente'),
            'assinatura_empresa': assinaturas_info.get('empresa'),
            'data_conclusao': assinaturas_info.get('data_conclusao'),
        }
        
        # Renderizar email
        from django.template.loader import render_to_string
        
        # Debug: Log das variáveis do contexto
        logger.info(f"Contexto do email: assinatura_cliente={context.get('assinatura_cliente')}, assinatura_empresa={context.get('assinatura_empresa')}, data_conclusao={context.get('data_conclusao')}")
        
        html_content = render_to_string(template, context)
        text_content = f"Documento {documento.numero} foi assinado por ambas as partes em {assinaturas_info.get('data_conclusao')}."
        
        # Preparar destinatários
        destinatarios = []
        if documento.lead.email:
            destinatarios.append(documento.lead.email)
        if documento.loja.email and documento.loja.email != documento.lead.email:
            destinatarios.append(documento.loja.email)
        
        if not destinatarios:
            logger.error(f"Nenhum destinatário válido para envio do documento final: {tipo_documento} {documento.numero}")
            return False
        
        # Enviar email
        from django.core.mail import EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=assunto,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
            reply_to=[documento.loja.email] if documento.loja.email else None
        )
        email.attach_alternative(html_content, "text/html")
        
        # Anexar PDF do documento final
        try:
            pdf_content = _gerar_pdf_documento_final(documento, tipo_documento)
            if pdf_content:
                filename = f"{tipo_documento.title()}_{documento.numero}_Final_Assinado.pdf"
                email.attach(filename, pdf_content, "application/pdf")
        except Exception as e:
            logger.warning(f"Erro ao anexar PDF do documento final: {str(e)}")
        
        email.send()
        
        logger.info(f"Documento final enviado por email para {len(destinatarios)} destinatários: {tipo_documento} {documento.numero}")
        
        # Registrar no histórico para cada destinatário
        from .models import HistoricoContato
        for destinatario in destinatarios:
            HistoricoContato.objects.create(
                lead=documento.lead,
                tipo='email',
                assunto=assunto,
                descricao=f'Documento final {tipo_documento} {documento.numero} enviado com ambas assinaturas para {destinatario}',
                resultado='Email enviado com sucesso',
                data_contato=timezone.now()
            )
        
        # Atualizar status do documento se necessário
        _atualizar_status_documento_final(documento, tipo_documento)
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar documento final assinado: {str(e)}")
        return False


def _verificar_documento_totalmente_assinado(documento, tipo_documento):
    """
    Verifica se o documento possui assinaturas de cliente e empresa
    """
    try:
        from .models import AssinaturaDigital
        
        filter_kwargs = {
            'status': 'assinado',
            'tipo_documento': tipo_documento,
            tipo_documento: documento
        }
        
        # Verificar assinatura do cliente
        assinatura_cliente = AssinaturaDigital.objects.filter(
            tipo_signatario='cliente',
            **filter_kwargs
        ).exists()
        
        # Verificar assinatura da empresa
        assinatura_empresa = AssinaturaDigital.objects.filter(
            tipo_signatario='empresa',
            **filter_kwargs
        ).exists()
        
        return assinatura_cliente and assinatura_empresa
        
    except Exception as e:
        logger.error(f"Erro ao verificar assinaturas do documento: {str(e)}")
        return False


def _obter_informacoes_assinaturas(documento, tipo_documento):
    """
    Obtém informações detalhadas das assinaturas do documento
    """
    try:
        from .models import AssinaturaDigital
        
        filter_kwargs = {
            'status': 'assinado',
            'tipo_documento': tipo_documento,
            tipo_documento: documento
        }
        
        # Obter assinatura do cliente
        assinatura_cliente = AssinaturaDigital.objects.filter(
            tipo_signatario='cliente',
            **filter_kwargs
        ).first()
        
        # Obter assinatura da empresa
        assinatura_empresa = AssinaturaDigital.objects.filter(
            tipo_signatario='empresa',
            **filter_kwargs
        ).first()
        
        # Determinar data de conclusão (última assinatura)
        data_conclusao = None
        if assinatura_cliente and assinatura_empresa:
            data_conclusao = max(
                assinatura_cliente.data_assinatura,
                assinatura_empresa.data_assinatura
            )
        
        return {
            'cliente': assinatura_cliente,
            'empresa': assinatura_empresa,
            'data_conclusao': data_conclusao
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter informações das assinaturas: {str(e)}")
        return {}


def _gerar_pdf_documento_final(documento, tipo_documento):
    """
    Gera PDF do documento final com assinaturas
    """
    try:
        from .services.pdf_service import PDFService
        
        if tipo_documento == 'orcamento':
            return PDFService.gerar_orcamento_pdf(documento)
        elif tipo_documento == 'proposta':
            return PDFService.gerar_proposta_pdf(documento)
        elif tipo_documento == 'contrato':
            return PDFService.gerar_contrato_pdf(documento)
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF do documento final: {str(e)}")
        return None


def _atualizar_status_documento_final(documento, tipo_documento):
    """
    Atualiza o status do documento para refletir conclusão das assinaturas
    """
    try:
        if tipo_documento == 'orcamento':
            documento.status = 'assinado'
        elif tipo_documento == 'proposta':
            documento.status = 'assinada'
        elif tipo_documento == 'contrato':
            documento.status = 'ativo'
        
        documento.save()
        logger.info(f"Status do {tipo_documento} {documento.numero} atualizado para conclusão das assinaturas")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar status do documento final: {str(e)}")
@lo
gin_required
def listar_contratos(request):
    """Lista contratos com filtros e paginação"""
    try:
        # Obter loja do usuário
        if request.user.is_superuser:
            contratos = Contrato.objects.all()
        else:
            loja = request.user.loja_admin
            contratos = Contrato.objects.filter(loja=loja)
        
        # Filtros
        status_filter = request.GET.get('status')
        lead_filter = request.GET.get('lead')
        search = request.GET.get('search')
        
        if status_filter:
            contratos = contratos.filter(status=status_filter)
        
        if lead_filter:
            contratos = contratos.filter(lead__nome__icontains=lead_filter)
        
        if search:
            contratos = contratos.filter(
                Q(numero__icontains=search) |
                Q(titulo__icontains=search) |
                Q(lead__nome__icontains=search)
            )
        
        # Ordenação
        contratos = contratos.select_related('lead', 'loja').order_by('-data_criacao')
        
        # Paginação
        paginator = Paginator(contratos, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Estatísticas
        stats = {
            'total': contratos.count(),
            'rascunho': contratos.filter(status='rascunho').count(),
            'enviado': contratos.filter(status='enviado').count(),
            'ativo': contratos.filter(status='ativo').count(),
            'finalizado': contratos.filter(status='finalizado').count(),
        }
        
        context = {
            'page_obj': page_obj,
            'stats': stats,
            'status_choices': Contrato.STATUS_CHOICES,
            'current_filters': {
                'status': status_filter,
                'lead': lead_filter,
                'search': search,
            }
        }
        
        return render(request, 'crm_vendas/contratos/listar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao listar contratos: {str(e)}")
        messages.error(request, 'Erro ao carregar contratos.')
        return redirect('crm_vendas:dashboard')

@login_required
def editar_contrato(request, contrato_id):
    """Edita um contrato"""
    try:
        contrato = get_object_or_404(Contrato, id=contrato_id)
        
        # Verificar permissão
        if not request.user.is_superuser and contrato.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para editar este contrato.')
            return redirect('crm_vendas:listar_contratos')
        
        # Verificar se pode editar
        if contrato.status != 'rascunho':
            messages.error(request, 'Este contrato não pode ser editado.')
            return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato.id)
        
        if request.method == 'POST':
            form = ContratoForm(request.POST, instance=contrato, user=request.user)
            
            if form.is_valid():
                contrato = form.save()
                
                # Registrar no histórico
                HistoricoContato.objects.create(
                    lead=contrato.lead,
                    usuario=request.user,
                    tipo='outros',
                    assunto=f'Contrato {contrato.numero} editado',
                    descricao=f'Contrato atualizado: {contrato.titulo}',
                    resultado=f'Valor: R$ {contrato.valor_total:,.2f}',
                    data_contato=timezone.now()
                )
                
                messages.success(request, 'Contrato atualizado com sucesso!')
                return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato.id)
            else:
                messages.error(request, 'Erro ao atualizar contrato. Verifique os dados informados.')
        else:
            form = ContratoForm(instance=contrato, user=request.user)
        
        context = {
            'form': form,
            'contrato': contrato,
            'title': f'Editar Contrato {contrato.numero}',
        }
        
        return render(request, 'crm_vendas/contratos/editar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao editar contrato: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_contratos')

@login_required
def enviar_contrato(request, contrato_id):
    """Envia um contrato por email"""
    try:
        contrato = get_object_or_404(Contrato, id=contrato_id)
        
        # Verificar permissão
        if not request.user.is_superuser and contrato.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para enviar este contrato.')
            return redirect('crm_vendas:listar_contratos')
        
        # Verificar se pode enviar
        if contrato.status != 'rascunho':
            messages.error(request, 'Este contrato não pode ser enviado.')
            return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato.id)
        
        # Enviar por email
        success = EmailService.enviar_contrato(contrato)
        
        if success:
            # Atualizar status
            contrato.status = 'enviado'
            contrato.save()
            
            # Registrar no histórico
            HistoricoContato.objects.create(
                lead=contrato.lead,
                usuario=request.user,
                tipo='email',
                assunto=f'Contrato {contrato.numero} enviado',
                descricao=f'Contrato enviado por email para {contrato.lead.email}',
                resultado='Email enviado com sucesso',
                data_contato=timezone.now()
            )
            
            messages.success(request, 'Contrato enviado com sucesso!')
        else:
            messages.error(request, 'Erro ao enviar contrato por email.')
        
        return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato.id)
        
    except Exception as e:
        logger.error(f"Erro ao enviar contrato: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_contratos')

@login_required
def gerar_pdf_contrato(request, contrato_id):
    """Gera PDF do contrato"""
    try:
        contrato = get_object_or_404(Contrato, id=contrato_id)
        
        # Verificar permissão
        if not request.user.is_superuser and contrato.loja != request.user.loja_admin:
            messages.error(request, 'Você não tem permissão para acessar este contrato.')
            return redirect('crm_vendas:listar_contratos')
        
        # Gerar PDF
        pdf_content = PDFService.gerar_contrato_pdf(contrato)
        
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Contrato_{contrato.numero}.pdf"'
            return response
        else:
            messages.error(request, 'Erro ao gerar PDF do contrato.')
            return redirect('crm_vendas:detalhar_contrato', contrato_id=contrato.id)
            
    except Exception as e:
        logger.error(f"Erro ao gerar PDF do contrato: {str(e)}")
        messages.error(request, 'Erro interno do servidor.')
        return redirect('crm_vendas:listar_contratos')