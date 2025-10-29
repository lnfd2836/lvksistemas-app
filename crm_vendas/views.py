"""
Views do CRM de Vendas
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
import logging

from .models import Lead, Orcamento, ItemOrcamento, Proposta, Contrato, HistoricoContato, EmailLog
from .services.email_service import EmailService, EmailTrackingService
from .services.pdf_service import PDFService
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
    
    return render(request, 'crm_vendas/leads/detalhar.html', context)


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
def listar_orcamentos(request):
    """Lista orçamentos"""
    return render(request, 'crm_vendas/orcamentos/listar.html')

@login_required
def listar_propostas(request):
    """Lista propostas"""
    return render(request, 'crm_vendas/propostas/listar.html')

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
        except:
            loja = None
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
    # Implementação básica - renderizar formulário
    if not request.user.is_superuser:
        try:
            loja = request.user.loja_admin
        except:
            loja = None
    else:
        loja = None
    
    context = {
        'loja': loja,
        'lojas': Loja.objects.all() if request.user.is_superuser else None,
    }
    return render(request, 'crm_vendas/propostas/criar.html', context)

@login_required
def detalhar_proposta(request, proposta_id): 
    """Detalhes de uma proposta"""
    proposta = get_object_or_404(Proposta, id=proposta_id)
    context = {'proposta': proposta}
    return render(request, 'crm_vendas/propostas/detalhar.html', context)

@login_required
def enviar_proposta(request, proposta_id): 
    """Envia uma proposta por email"""
    proposta = get_object_or_404(Proposta, id=proposta_id)
    messages.info(request, 'Funcionalidade de envio de proposta em desenvolvimento.')
    return redirect('crm_vendas:detalhar_proposta', proposta_id=proposta_id)

@login_required
def criar_contrato(request):
    """Cria um novo contrato"""
    # Implementação básica - renderizar formulário
    if not request.user.is_superuser:
        try:
            loja = request.user.loja_admin
        except:
            loja = None
    else:
        loja = None
    
    context = {
        'loja': loja,
        'lojas': Loja.objects.all() if request.user.is_superuser else None,
    }
    return render(request, 'crm_vendas/contratos/criar.html', context)

@login_required
def detalhar_contrato(request, contrato_id): 
    """Detalhes de um contrato"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    context = {'contrato': contrato}
    return render(request, 'crm_vendas/contratos/detalhar.html', context)

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
    messages.info(request, 'Funcionalidade de registro de contato em desenvolvimento.')
    return redirect('crm_vendas:detalhar_lead', lead_id=lead_id)
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