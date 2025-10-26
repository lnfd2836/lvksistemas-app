from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import json

from .models import PlanoFinanceiro, ControleFinanceiro, Pagamento, NotificacaoFinanceira, ConfiguracaoBoleto, BoletoGerado
from lojas.models import Loja


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def dashboard_financeiro(request):
    """Dashboard de controle financeiro para Super Admin"""
    
    # Estatísticas gerais
    total_lojas = Loja.objects.count()
    lojas_ativas = ControleFinanceiro.objects.filter(status='ativa').count()
    lojas_vencidas = ControleFinanceiro.objects.filter(status='vencida').count()
    lojas_bloqueadas = ControleFinanceiro.objects.filter(status='bloqueada').count()
    
    # Receita
    receita_mensal = ControleFinanceiro.objects.filter(
        status='ativa',
        data_ultimo_pagamento__month=timezone.now().month
    ).aggregate(total=Sum('valor_pago'))['total'] or 0
    
    receita_pendente = ControleFinanceiro.objects.filter(
        status__in=['vencida', 'bloqueada']
    ).aggregate(total=Sum('valor_pendente'))['total'] or 0
    
    # Lojas próximas do vencimento (5 dias)
    data_limite = timezone.now() + timedelta(days=5)
    lojas_vencendo = ControleFinanceiro.objects.filter(
        data_vencimento__lte=data_limite,
        status='ativa'
    ).order_by('data_vencimento')
    
    # Pagamentos pendentes
    pagamentos_pendentes = Pagamento.objects.filter(
        status='pendente'
    ).order_by('-data_criacao')[:10]
    
    # Seção de cobranças removida - usando apenas seção Asaas
    
    # Controles financeiros recentes
    controles_recentes = ControleFinanceiro.objects.select_related(
        'loja', 'plano'
    ).order_by('-data_atualizacao')[:10]
    
    context = {
        'total_lojas': total_lojas,
        'lojas_ativas': lojas_ativas,
        'lojas_vencidas': lojas_vencidas,
        'lojas_bloqueadas': lojas_bloqueadas,
        'receita_mensal': receita_mensal,
        'receita_pendente': receita_pendente,
        'lojas_vencendo': lojas_vencendo,
        'pagamentos_pendentes': pagamentos_pendentes,

        'controles_recentes': controles_recentes,
    }
    
    return render(request, 'controle_financeiro/dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def listar_controles_financeiros(request):
    """Lista todos os controles financeiros"""
    
    # Filtros
    status_filter = request.GET.get('status', '')
    plano_filter = request.GET.get('plano', '')
    search = request.GET.get('search', '')
    
    controles = ControleFinanceiro.objects.select_related('loja', 'plano').all()
    
    if status_filter:
        controles = controles.filter(status=status_filter)
    
    if plano_filter:
        controles = controles.filter(plano_id=plano_filter)
    
    if search:
        controles = controles.filter(
            Q(loja__nome__icontains=search) |
            Q(loja__cnpj__icontains=search)
        )
    
    controles = controles.order_by('-data_vencimento')
    
    # Planos para filtro
    planos = PlanoFinanceiro.objects.filter(ativo=True)
    
    # Calcula dias de atraso para cada controle
    for controle in controles:
        if controle.dias_para_vencimento <= 0:
            controle.dias_atraso = abs(controle.dias_para_vencimento)
        else:
            controle.dias_atraso = 0
    
    context = {
        'controles': controles,
        'status_filter': status_filter,
        'plano_filter': plano_filter,
        'search': search,
        'planos': planos,
    }
    
    return render(request, 'controle_financeiro/listar.html', context)


@login_required
@user_passes_test(is_superuser)
def detalhar_controle_financeiro(request, controle_id):
    """Detalha um controle financeiro específico"""
    
    controle = get_object_or_404(ControleFinanceiro, id=controle_id)
    pagamentos = Pagamento.objects.filter(controle_financeiro=controle).order_by('-data_criacao')
    notificacoes = NotificacaoFinanceira.objects.filter(controle_financeiro=controle).order_by('-data_criacao')
    
    # Buscar cobranças do Asaas relacionadas a este controle
    from .models import CobrancaAsaas
    cobrancas_asaas = CobrancaAsaas.objects.filter(controle_financeiro=controle).order_by('-data_criacao')
    
    # Calcula dias de atraso se vencido
    dias_atraso = 0
    if controle.dias_para_vencimento <= 0:
        dias_atraso = abs(controle.dias_para_vencimento)
    
    context = {
        'controle': controle,
        'pagamentos': pagamentos,
        'notificacoes': notificacoes,
        'cobrancas_asaas': cobrancas_asaas,
        'dias_atraso': dias_atraso,
    }
    
    return render(request, 'controle_financeiro/detalhar.html', context)


@login_required
@user_passes_test(is_superuser)
def aprovar_pagamento(request, pagamento_id):
    """Aprova um pagamento"""
    
    if request.method == 'POST':
        pagamento = get_object_or_404(Pagamento, id=pagamento_id)
        observacoes = request.POST.get('observacoes', '')
        
        try:
            pagamento.aprovar(request.user, observacoes)
            messages.success(request, f'Pagamento de R$ {pagamento.valor} aprovado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao aprovar pagamento: {str(e)}')
        
        return redirect('detalhar_controle_financeiro', controle_id=pagamento.controle_financeiro.id)
    
    return redirect('dashboard_financeiro')


@login_required
@user_passes_test(is_superuser)
def rejeitar_pagamento(request, pagamento_id):
    """Rejeita um pagamento"""
    
    if request.method == 'POST':
        pagamento = get_object_or_404(Pagamento, id=pagamento_id)
        motivo = request.POST.get('motivo', '')
        
        try:
            pagamento.rejeitar(motivo, request.user)
            messages.success(request, f'Pagamento de R$ {pagamento.valor} rejeitado.')
        except Exception as e:
            messages.error(request, f'Erro ao rejeitar pagamento: {str(e)}')
        
        return redirect('detalhar_controle_financeiro', controle_id=pagamento.controle_financeiro.id)
    
    return redirect('dashboard_financeiro')


@login_required
@user_passes_test(is_superuser)
def bloquear_loja(request, controle_id):
    """Bloqueia uma loja manualmente"""
    
    if request.method == 'POST':
        controle = get_object_or_404(ControleFinanceiro, id=controle_id)
        motivo = request.POST.get('motivo', 'Bloqueio manual pelo administrador')
        
        try:
            controle.status = 'bloqueada'
            controle.bloqueada = True
            controle.motivo_bloqueio = motivo
            controle.save()
            
            messages.success(request, f'Loja {controle.loja.nome} bloqueada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao bloquear loja: {str(e)}')
        
        return redirect('detalhar_controle_financeiro', controle_id=controle_id)
    
    return redirect('dashboard_financeiro')


@login_required
@user_passes_test(is_superuser)
def desbloquear_loja(request, controle_id):
    """Desbloqueia uma loja"""
    
    if request.method == 'POST':
        controle = get_object_or_404(ControleFinanceiro, id=controle_id)
        
        try:
            controle.status = 'ativa'
            controle.bloqueada = False
            controle.motivo_bloqueio = ''
            controle.save()
            
            messages.success(request, f'Loja {controle.loja.nome} desbloqueada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao desbloquear loja: {str(e)}')
        
        return redirect('detalhar_controle_financeiro', controle_id=controle_id)
    
    return redirect('dashboard_financeiro')


@login_required
@user_passes_test(is_superuser)
def verificar_vencimentos(request):
    """Verifica e atualiza vencimentos de todas as lojas"""
    
    controles = ControleFinanceiro.objects.all()
    atualizados = 0
    
    for controle in controles:
        status_anterior = controle.status
        novo_status = controle.verificar_status()
        
        if status_anterior != novo_status:
            atualizados += 1
    
    messages.success(request, f'{atualizados} controles financeiros atualizados!')
    return redirect('dashboard_financeiro')


# Views para clientes (lojas)
@login_required
def pagamento_cliente(request):
    """Interface de pagamento para clientes"""
    
    # Busca o controle financeiro da loja do usuário
    try:
        controle = ControleFinanceiro.objects.get(loja__admin_user=request.user)
    except ControleFinanceiro.DoesNotExist:
        messages.error(request, 'Controle financeiro não encontrado para sua loja.')
        return redirect('dashboard:principal')
    
    if request.method == 'POST':
        valor = request.POST.get('valor')
        metodo = request.POST.get('metodo_pagamento')
        dados_pagamento = {
            'metodo': metodo,
            'observacoes': request.POST.get('observacoes', '')
        }
        
        try:
            valor_decimal = Decimal(valor)
            pagamento = Pagamento.objects.create(
                controle_financeiro=controle,
                valor=valor_decimal,
                metodo_pagamento=metodo,
                dados_pagamento=dados_pagamento,
                status='pendente'
            )
            
            messages.success(request, 'Pagamento registrado! Aguarde aprovação.')
            return redirect('pagamento_cliente')
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar pagamento: {str(e)}')
    
    # Pagamentos da loja
    pagamentos = Pagamento.objects.filter(controle_financeiro=controle).order_by('-data_criacao')
    
    # Calcula dias de atraso se vencido
    dias_atraso = 0
    if controle.dias_para_vencimento <= 0:
        dias_atraso = abs(controle.dias_para_vencimento)
    
    context = {
        'controle': controle,
        'pagamentos': pagamentos,
        'dias_atraso': dias_atraso,
    }
    
    return render(request, 'controle_financeiro/pagamento_cliente.html', context)


# Views para configuração de boletos
@login_required
@user_passes_test(is_superuser)
@login_required

@login_required
@user_passes_test(is_superuser)
@login_required
@user_passes_test(is_superuser)
@login_required
@user_passes_test(is_superuser)
@login_required
@user_passes_test(is_superuser)
# Views para clientes (lojas) - boletos
@login_required
@login_required
@user_passes_test(is_superuser)
@login_required
@user_passes_test(is_superuser)
def executar_rotinas_financeiras(request):
    """Executa todas as rotinas financeiras manualmente"""
    
    if request.method == 'POST':
        try:
            from .services import BoletoService, FinanceiroService
            
            # Verificar vencimentos
            financeiro_service = FinanceiroService()
            resultado_vencimentos = financeiro_service.verificar_vencimentos_automatico()
            
            # Gerar boletos automáticos
            boleto_service = BoletoService()
            resultado_boletos = boleto_service.gerar_boletos_automaticos(10)
            
            # Verificar boletos vencidos
            boletos_vencidos = boleto_service.verificar_boletos_vencidos()
            
            messages.success(
                request,
                f'Rotinas executadas com sucesso! '
                f'Vencimentos: {resultado_vencimentos["atualizados"]} atualizados. '
                f'Boletos: {resultado_boletos["boletos_gerados"]} gerados. '
                f'Boletos vencidos: {boletos_vencidos} atualizados.'
            )
            
        except Exception as e:
            messages.error(request, f'Erro ao executar rotinas financeiras: {str(e)}')
        
        return redirect('controle_financeiro:dashboard_financeiro')
    
    return redirect('controle_financeiro:dashboard_financeiro')


@login_required
@user_passes_test(is_superuser)
@login_required
@user_passes_test(is_superuser)
@login_required
@login_required
@login_required
def pdf_asaas_redirect(request, cobranca_id):
    """Redireciona para o PDF oficial do Asaas"""
    
    try:
        from .models import CobrancaAsaas
        cobranca = get_object_or_404(CobrancaAsaas, asaas_id=cobranca_id)
        
        # Verifica permissão
        if not request.user.is_superuser:
            if cobranca.controle_financeiro.loja.admin_user != request.user:
                messages.error(request, 'Você não tem permissão para visualizar este boleto.')
                return redirect('dashboard:principal')
        
        # Redirecionar para PDF oficial do Asaas
        if cobranca.bank_slip_url:
            return redirect(cobranca.bank_slip_url)
        else:
            messages.error(request, 'PDF do boleto não disponível.')
            return redirect('controle_financeiro:listar_cobrancas_asaas')
            
    except Exception as e:
        messages.error(request, f'Erro ao acessar PDF: {str(e)}')
        return redirect('controle_financeiro:listar_cobrancas_asaas')


@login_required
def pdf_asaas_direto(request, asaas_id):
    """Redireciona diretamente para o PDF do Asaas usando o ID"""
    
    # Verificar permissão básica (usuário logado)
    if not request.user.is_authenticated:
        messages.error(request, 'Você precisa estar logado para acessar este recurso.')
        return redirect('login')
    
    # Construir URL do PDF do Asaas
    pdf_url = f"https://www.asaas.com/b/pdf/{asaas_id}"
    
    # Log da ação
    logger.info(f"Redirecionamento direto para PDF Asaas: {asaas_id} por usuário {request.user.username}")
    
    return redirect(pdf_url)






# === VIEWS DE REDIRECIONAMENTO PARA ASAAS ===

@login_required
@user_passes_test(is_superuser)
def redirect_boletos_to_asaas(request):
    """Redireciona listar_boletos para listar_cobrancas_asaas"""
    messages.info(request, 'Sistema otimizado! Agora utilizamos apenas cobranças Asaas.')
    return redirect('controle_financeiro:listar_cobrancas_asaas')

@login_required
@user_passes_test(is_superuser)
def redirect_gerar_boleto_to_asaas(request, controle_id):
    """Redireciona gerar_boleto para gerar_cobranca_asaas"""
    messages.info(request, 'Sistema otimizado! Gerando cobrança via Asaas.')
    return redirect('controle_financeiro:gerar_cobranca_asaas', controle_id=controle_id)

@login_required
def redirect_boletos_cliente_to_asaas(request):
    """Redireciona boletos_cliente para dashboard com cobranças Asaas"""
    messages.info(request, 'Sistema otimizado! Visualize suas cobranças no dashboard.')
    return redirect('dashboard:dashboard')

@login_required
@user_passes_test(is_superuser)
def redirect_configurar_boletos_to_asaas(request):
    """Redireciona configurar_boletos para configurar_asaas"""
    messages.info(request, 'Sistema otimizado! Configure a integração Asaas.')
    return redirect('controle_financeiro:configurar_asaas')

@login_required
@user_passes_test(is_superuser)
def executar_rotinas_financeiras(request):
    """Executa rotinas financeiras automáticas"""
    if request.method == 'POST':
        try:
            # 1. Verificar vencimentos
            verificar_vencimentos(request)
            
            # 2. Gerar cobranças automáticas (10 dias antes do vencimento)
            resultado_cobrancas = gerar_cobrancas_automaticas_asaas()
            
            if resultado_cobrancas['geradas'] > 0:
                messages.success(
                    request, 
                    f'Rotinas executadas! {resultado_cobrancas["geradas"]} cobranças geradas, '
                    f'{resultado_cobrancas["ja_existem"]} já existiam.'
                )
            else:
                messages.success(request, 'Rotinas financeiras executadas com sucesso!')
                
        except Exception as e:
            messages.error(request, f'Erro ao executar rotinas: {e}')
    
    return redirect('controle_financeiro:dashboard_financeiro')


def gerar_cobrancas_automaticas_asaas(dias_antecedencia=10):
    """
    Gera cobranças automáticas via Asaas para lojas que vencem em X dias
    """
    from .asaas_central_service import AsaasCentralService
    from .models import CobrancaAsaas
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Data limite para gerar cobranças
        data_limite = timezone.now().date() + timedelta(days=dias_antecedencia)
        
        # Buscar controles financeiros que precisam de cobrança
        controles = ControleFinanceiro.objects.filter(
            status='ativo',
            data_vencimento__date__lte=data_limite,
            loja__status='ativa'
        ).select_related('loja', 'plano')
        
        geradas = 0
        ja_existem = 0
        erros = []
        
        asaas_service = AsaasCentralService()
        
        for controle in controles:
            try:
                # Verificar se já existe cobrança ativa para este controle
                cobranca_existente = CobrancaAsaas.objects.filter(
                    controle_financeiro=controle,
                    status__in=['PENDING', 'CONFIRMED', 'RECEIVED']
                ).first()
                
                if cobranca_existente:
                    ja_existem += 1
                    logger.info(f'Cobrança já existe para {controle.loja.nome}: {cobranca_existente.asaas_id}')
                    continue
                
                # Calcular dias para vencimento
                dias_para_vencimento = (controle.data_vencimento.date() - timezone.now().date()).days
                dias_vencimento = max(1, dias_para_vencimento)  # Mínimo 1 dia
                
                # Gerar cobrança via Asaas
                cobranca_data = asaas_service.gerar_cobranca_loja(controle, dias_vencimento)
                
                if cobranca_data:
                    # Salvar cobrança no banco local
                    CobrancaAsaas.objects.create(
                        asaas_id=cobranca_data['id'],
                        controle_financeiro=controle,
                        customer_id=cobranca_data['customer'],
                        valor=cobranca_data['value'],
                        data_vencimento=timezone.datetime.fromisoformat(cobranca_data['dueDate']).replace(tzinfo=timezone.get_current_timezone()),
                        descricao=cobranca_data['description'],
                        status=cobranca_data['status'],
                        invoice_url=cobranca_data.get('invoiceUrl', ''),
                        bank_slip_url=cobranca_data.get('bankSlipUrl', ''),
                        invoice_number=cobranca_data.get('invoiceNumber', ''),
                        external_reference=cobranca_data.get('externalReference', ''),
                        api_response=cobranca_data
                    )
                    
                    geradas += 1
                    logger.info(f'Cobrança gerada para {controle.loja.nome}: {cobranca_data["id"]}')
                else:
                    erros.append(f'Erro ao gerar cobrança para {controle.loja.nome}')
                    
            except Exception as e:
                erro_msg = f'Erro ao processar {controle.loja.nome}: {str(e)}'
                erros.append(erro_msg)
                logger.error(erro_msg)
        
        resultado = {
            'total_verificados': controles.count(),
            'geradas': geradas,
            'ja_existem': ja_existem,
            'erros': erros
        }
        
        logger.info(f'Cobranças automáticas: {geradas} geradas, {ja_existem} já existiam, {len(erros)} erros')
        return resultado
        
    except Exception as e:
        logger.error(f'Erro geral ao gerar cobranças automáticas: {str(e)}')
        return {
            'total_verificados': 0,
            'geradas': 0,
            'ja_existem': 0,
            'erros': [str(e)]
        }
