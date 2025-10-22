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
    
    # Boletos gerados recentemente
    boletos_recentes = BoletoGerado.objects.select_related(
        'controle_financeiro__loja', 'configuracao'
    ).order_by('-data_criacao')[:10]
    
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
        'boletos_recentes': boletos_recentes,
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
    
    # Calcula dias de atraso se vencido
    dias_atraso = 0
    if controle.dias_para_vencimento <= 0:
        dias_atraso = abs(controle.dias_para_vencimento)
    
    context = {
        'controle': controle,
        'pagamentos': pagamentos,
        'notificacoes': notificacoes,
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
def configurar_boletos(request):
    """Configuração de boletos para Super Admin"""
    
    form_errors = False
    form_success = False
    show_form = request.GET.get('show_form', 'false') == 'true'
    
    if request.method == 'POST':
        try:
            # Cria ou atualiza configuração
            config_id = request.POST.get('config_id')
            if config_id:
                config = get_object_or_404(ConfiguracaoBoleto, id=config_id)
            else:
                config = ConfiguracaoBoleto()
            
            # Validação básica dos campos obrigatórios
            required_fields = ['nome_banco', 'codigo_banco', 'agencia', 'conta', 'carteira', 
                             'nome_beneficiario', 'cnpj_beneficiario', 'endereco_beneficiario']
            
            for field in required_fields:
                if not request.POST.get(field, '').strip():
                    messages.error(request, f'O campo {field.replace("_", " ").title()} é obrigatório.')
                    form_errors = True
            
            if not form_errors:
                config.nome_banco = request.POST.get('nome_banco')
                config.codigo_banco = request.POST.get('codigo_banco')
                config.agencia = request.POST.get('agencia')
                config.conta = request.POST.get('conta')
                config.carteira = request.POST.get('carteira')
                config.codigo_cedente = request.POST.get('codigo_cedente', '')
                config.convenio = request.POST.get("convenio", "") or None
                config.nome_beneficiario = request.POST.get('nome_beneficiario')
                config.cnpj_beneficiario = request.POST.get('cnpj_beneficiario')
                config.endereco_beneficiario = request.POST.get('endereco_beneficiario')
                config.instrucoes = request.POST.get('instrucoes', '')
                
                try:
                    config.multa = Decimal(request.POST.get('multa', 2.00))
                    config.juros = Decimal(request.POST.get('juros', 1.00))
                    config.desconto = Decimal(request.POST.get('desconto', 0.00))
                except (ValueError, TypeError):
                    messages.error(request, 'Valores de multa, juros e desconto devem ser números válidos.')
                    form_errors = True
                
                if not form_errors:
                    config.ativo = 'ativo' in request.POST
                    
                    # Se está ativando esta configuração, desativa todas as outras
                    if config.ativo:
                        ConfiguracaoBoleto.objects.exclude(id=config.id).update(ativo=False)
                    
                    config.save()
                    messages.success(request, 'Configuração de boleto salva com sucesso!')
                    form_success = True
                    
                    # Redireciona para esconder o formulário após sucesso
                    return redirect('controle_financeiro:configurar_boletos')
        
        except Exception as e:
            messages.error(request, f'Erro ao salvar configuração: {str(e)}')
            form_errors = True
    
    # Busca configurações existentes
    configuracoes = ConfiguracaoBoleto.objects.all().order_by('-data_criacao')
    
    # Determina o estado inicial do formulário
    # Mostra o formulário se:
    # 1. Não há configurações existentes
    # 2. Há erros de validação
    # 3. Foi explicitamente solicitado via parâmetro show_form
    should_show_form = (
        not configuracoes.exists() or 
        form_errors or 
        show_form
    )
    
    # Busca a configuração ativa para exibir no resumo
    configuracao_ativa = configuracoes.filter(ativo=True).first()
    
    context = {
        'configuracoes': configuracoes,
        'configuracao_ativa': configuracao_ativa,
        'show_form': should_show_form,
        'form_errors': form_errors,
        'form_success': form_success,
        'has_configurations': configuracoes.exists(),
    }
    
    return render(request, 'controle_financeiro/configurar_boletos.html', context)


@login_required

@login_required
@user_passes_test(is_superuser)
def editar_configuracao_boleto(request, config_id):
    """Edita uma configuração de boleto"""
    
    config = get_object_or_404(ConfiguracaoBoleto, id=config_id)
    form_errors = False
    
    if request.method == 'POST':
        try:
            # Validação básica dos campos obrigatórios
            required_fields = ['nome_banco', 'codigo_banco', 'agencia', 'conta', 'carteira', 
                             'nome_beneficiario', 'cnpj_beneficiario', 'endereco_beneficiario']
            
            for field in required_fields:
                if not request.POST.get(field, '').strip():
                    messages.error(request, f'O campo {field.replace("_", " ").title()} é obrigatório.')
                    form_errors = True
            
            if not form_errors:
                config.nome_banco = request.POST.get('nome_banco')
                config.codigo_banco = request.POST.get('codigo_banco')
                config.agencia = request.POST.get('agencia')
                config.conta = request.POST.get('conta')
                config.carteira = request.POST.get('carteira')
                config.codigo_cedente = request.POST.get('codigo_cedente', '')
                config.nome_beneficiario = request.POST.get('nome_beneficiario')
                config.cnpj_beneficiario = request.POST.get('cnpj_beneficiario')
                config.endereco_beneficiario = request.POST.get('endereco_beneficiario')
                config.instrucoes = request.POST.get('instrucoes', '')
                
                try:
                    config.multa = Decimal(request.POST.get('multa', 2.00))
                    config.juros = Decimal(request.POST.get('juros', 1.00))
                    config.desconto = Decimal(request.POST.get('desconto', 0.00))
                except (ValueError, TypeError):
                    messages.error(request, 'Valores de multa, juros e desconto devem ser números válidos.')
                    form_errors = True
                
                if not form_errors:
                    config.ativo = 'ativo' in request.POST
                    
                    # Se está ativando esta configuração, desativa todas as outras
                    if config.ativo:
                        ConfiguracaoBoleto.objects.exclude(id=config.id).update(ativo=False)
                    
                    config.save()
                    messages.success(request, 'Configuração de boleto atualizada com sucesso!')
                    return redirect('controle_financeiro:configurar_boletos')
        
        except Exception as e:
            messages.error(request, f'Erro ao atualizar configuração: {str(e)}')
            form_errors = True
    
    context = {
        'config': config,
        'form_errors': form_errors,
        'editing': True,
    }
    
    return render(request, 'controle_financeiro/editar_configuracao_boleto.html', context)


@login_required
@user_passes_test(is_superuser)
def gerar_boleto(request, controle_id):
    """Gera um boleto SEMPRE via API do Asaas"""
    
    controle = get_object_or_404(ControleFinanceiro, id=controle_id)
    
    if request.method == 'POST':
        try:
            # SEMPRE usar API do Asaas - não mais boletos locais
            from .asaas_service import AsaasService
            
            asaas_service = AsaasService()
            
            # Validar configuração da API
            if not asaas_service.validar_configuracao():
                messages.error(request, 
                    '❌ API do Asaas não está configurada corretamente. '
                    'Verifique as configurações de API Key e conectividade.'
                )
                return redirect('controle_financeiro:gerar_boleto', controle_id=controle_id)
            
            # Gerar cobrança via API do Asaas
            resultado = asaas_service.gerar_cobranca_com_pix(controle, dias_vencimento=30)
            
            if resultado.get('success'):
                messages.success(request, 
                    f'✅ Cobrança Asaas {resultado["cobranca"]["id"]} gerada com sucesso! '
                    'Boleto e PIX disponíveis.'
                )
                
                # Redirecionar para visualizar a cobrança criada
                from .models import CobrancaAsaas
                cobranca = CobrancaAsaas.objects.filter(
                    controle_financeiro=controle
                ).order_by('-data_criacao').first()
                
                if cobranca:
                    return redirect('controle_financeiro:visualizar_cobranca_asaas', cobranca_id=cobranca.id)
                else:
                    return redirect('controle_financeiro:listar_cobrancas_asaas')
            else:
                error_msg = resultado.get('error', 'Erro desconhecido')
                messages.error(request, f'❌ Erro ao gerar cobrança via API Asaas: {error_msg}')
                return redirect('controle_financeiro:gerar_boleto', controle_id=controle_id)
                
        except Exception as e:
            messages.error(request, f'❌ Erro interno ao gerar cobrança: {str(e)}')
            return redirect('controle_financeiro:gerar_boleto', controle_id=controle_id)
    
    # Lista configurações ativas - priorizar Asaas
    configuracoes = ConfiguracaoBoleto.objects.filter(ativo=True)
    
    # Debug: garantir que o Asaas apareça
    if not configuracoes.exists():
        # Se não há configurações ativas, ativar o Asaas
        config_asaas = ConfiguracaoBoleto.objects.filter(codigo_banco="461").first()
        if config_asaas:
            config_asaas.ativo = True
            config_asaas.save()
            configuracoes = ConfiguracaoBoleto.objects.filter(ativo=True)
    
    # Logs removidos para produção
    
    context = {
        'controle': controle,
        'configuracoes': configuracoes,
    }
    
    return render(request, 'controle_financeiro/gerar_boleto.html', context)


@login_required
@user_passes_test(is_superuser)
def listar_boletos(request):
    """Lista todos os boletos gerados"""
    
    # Filtros
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    boletos = BoletoGerado.objects.select_related('controle_financeiro__loja', 'configuracao').all()
    
    if status_filter:
        boletos = boletos.filter(status=status_filter)
    
    if search:
        boletos = boletos.filter(
            Q(numero_boleto__icontains=search) |
            Q(controle_financeiro__loja__nome__icontains=search) |
            Q(linha_digitavel__icontains=search)
        )
    
    boletos = boletos.order_by('-data_criacao')
    
    # Calcula dias de atraso para cada boleto
    for boleto in boletos:
        if boleto.dias_para_vencimento <= 0:
            boleto.dias_atraso = abs(boleto.dias_para_vencimento)
        else:
            boleto.dias_atraso = 0
    
    context = {
        'boletos': boletos,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'controle_financeiro/listar_boletos.html', context)


@login_required
@user_passes_test(is_superuser)
def marcar_boleto_pago(request, boleto_id):
    """Marca um boleto como pago"""
    
    if request.method == 'POST':
        boleto = get_object_or_404(BoletoGerado, id=boleto_id)
        
        try:
            boleto.marcar_como_pago()
            messages.success(
                request, 
                f'✅ Boleto {boleto.numero_boleto} da loja {boleto.controle_financeiro.loja.nome} '
                f'foi marcado como pago! Valor: R$ {boleto.valor}'
            )
        except Exception as e:
            messages.error(request, f'❌ Erro ao marcar boleto como pago: {str(e)}')
        
        # Redireciona de volta para a página de origem se especificada
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        
        return redirect('controle_financeiro:listar_boletos')
    
    return redirect('controle_financeiro:listar_boletos')


# Views para clientes (lojas) - boletos
@login_required
def boletos_cliente(request):
    """Interface de boletos para clientes"""
    
    # Busca o controle financeiro da loja do usuário
    try:
        controle = ControleFinanceiro.objects.get(loja__admin_user=request.user)
    except ControleFinanceiro.DoesNotExist:
        messages.error(request, 'Controle financeiro não encontrado para sua loja.')
        return redirect('dashboard:principal')
    
    # Boletos da loja
    boletos = BoletoGerado.objects.filter(controle_financeiro=controle).order_by('-data_criacao')
    
    # Calcula dias de atraso se vencido
    dias_atraso = 0
    if controle.dias_para_vencimento <= 0:
        dias_atraso = abs(controle.dias_para_vencimento)
    
    context = {
        'controle': controle,
        'boletos': boletos,
        'dias_atraso': dias_atraso,
    }
    
    return render(request, 'controle_financeiro/boletos_cliente.html', context)


@login_required
@user_passes_test(is_superuser)
def gerar_boletos_automaticos(request):
    """Gera cobranças automaticamente via API do Asaas para lojas que vencem em 10 dias"""
    
    if request.method == 'POST':
        try:
            from .asaas_service import AsaasService
            from .models import CobrancaAsaas
            from datetime import timedelta
            
            dias_antecedencia = int(request.POST.get('dias_antecedencia', 10))
            
            # Buscar controles que vencem nos próximos X dias e não têm cobrança
            data_limite = timezone.now() + timedelta(days=dias_antecedencia)
            
            controles_sem_cobranca = ControleFinanceiro.objects.filter(
                data_vencimento__lte=data_limite,
                status__in=['ativo', 'vencida']
            ).exclude(
                id__in=CobrancaAsaas.objects.values_list('controle_financeiro_id', flat=True)
            )
            
            asaas_service = AsaasService()
            
            # Verificar se API está funcionando
            if not asaas_service.validar_configuracao():
                messages.error(request, '❌ API do Asaas não está configurada. Verifique as configurações.')
                return redirect('controle_financeiro:dashboard_financeiro')
            
            cobrancas_geradas = 0
            erros = []
            
            for controle in controles_sem_cobranca:
                try:
                    resultado = asaas_service.gerar_cobranca_com_pix(
                        controle, 
                        dias_vencimento=30,
                        descricao=f"Mensalidade automática - {controle.loja.nome}"
                    )
                    
                    if resultado.get('success'):
                        cobrancas_geradas += 1
                        logger.info(f"Cobrança automática gerada para {controle.loja.nome}")
                    else:
                        error_msg = resultado.get('error', 'Erro desconhecido')
                        erros.append({'loja': controle.loja.nome, 'erro': error_msg})
                        
                except Exception as e:
                    erros.append({'loja': controle.loja.nome, 'erro': str(e)})
            
            messages.success(
                request, 
                f'✅ Processo concluído! {cobrancas_geradas} cobranças Asaas geradas automaticamente.'
            )
            
            if erros:
                for erro in erros:
                    messages.warning(request, f'⚠️ Erro na loja {erro["loja"]}: {erro["erro"]}')
            
        except Exception as e:
            messages.error(request, f'❌ Erro ao gerar cobranças automáticas: {str(e)}')
        
        return redirect('controle_financeiro:dashboard_financeiro')
    
    return redirect('controle_financeiro:dashboard_financeiro')


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
def criar_boleto_manual(request):
    """Cria um boleto manualmente"""
    
    if request.method == 'POST':
        try:
            controle_id = request.POST.get('controle_id')
            valor = request.POST.get('valor')
            dias_vencimento = int(request.POST.get('dias_vencimento', 30))
            observacoes = request.POST.get('observacoes', '')
            
            # Busca o controle financeiro
            controle = get_object_or_404(ControleFinanceiro, id=controle_id)
            
            # Busca configuração ativa
            configuracao = ConfiguracaoBoleto.objects.filter(ativo=True).first()
            if not configuracao:
                messages.error(request, 'Nenhuma configuração de boleto ativa encontrada!')
                return redirect('controle_financeiro:dashboard_financeiro')
            
            # Gera o boleto
            from .services import BoletoService
            boleto_service = BoletoService()
            
            # Se não informou valor, usa o valor mensal da loja
            if not valor:
                valor = controle.valor_mensal
            else:
                valor = Decimal(valor)
            
            boleto = boleto_service.gerar_boleto(controle, configuracao, dias_vencimento)
            
            # Atualiza valor se diferente do padrão
            if valor != controle.valor_mensal:
                boleto.valor = valor
                boleto.save()
            
            # Adiciona observações se fornecidas
            if observacoes:
                boleto.observacoes = observacoes
                boleto.save()
            
            messages.success(
                request, 
                f'Boleto {boleto.numero_boleto} criado com sucesso para {controle.loja.nome}! '
                f'Valor: R$ {boleto.valor} - Vence em: {boleto.data_vencimento.strftime("%d/%m/%Y")}'
            )
            
        except Exception as e:
            messages.error(request, f'Erro ao criar boleto: {str(e)}')
        
        return redirect('controle_financeiro:dashboard_financeiro')
    
    return redirect('controle_financeiro:dashboard_financeiro')


@login_required
@user_passes_test(is_superuser)
def excluir_boleto(request, boleto_id):
    """Exclui um boleto"""
    
    if request.method == 'POST':
        try:
            boleto = get_object_or_404(BoletoGerado, id=boleto_id)
            
            # Verifica se o boleto pode ser excluído
            if boleto.status == 'pago':
                messages.error(request, 'Não é possível excluir um boleto que já foi pago!')
                return redirect('controle_financeiro:dashboard_financeiro')
            
            loja_nome = boleto.controle_financeiro.loja.nome
            numero_boleto = boleto.numero_boleto
            
            boleto.delete()
            
            messages.success(
                request, 
                f'Boleto {numero_boleto} da loja {loja_nome} foi excluído com sucesso!'
            )
            
        except Exception as e:
            messages.error(request, f'Erro ao excluir boleto: {str(e)}')
        
        return redirect('controle_financeiro:dashboard_financeiro')
    
    # Se não for POST, mostra confirmação
    boleto = get_object_or_404(BoletoGerado, id=boleto_id)
    
    context = {
        'boleto': boleto,
    }
    
    return render(request, 'controle_financeiro/confirmar_exclusao_boleto.html', context)


@login_required
def detalhar_boleto(request, boleto_id):
    """Exibe os detalhes completos de um boleto"""
    
    boleto = get_object_or_404(BoletoGerado, id=boleto_id)
    
    # Verifica se o usuário tem permissão para ver este boleto
    if not request.user.is_superuser:
        # Se não for superuser, verifica se é o dono da loja
        if boleto.controle_financeiro.loja.admin_user != request.user:
            messages.error(request, 'Você não tem permissão para visualizar este boleto.')
            return redirect('dashboard:principal')
    
    context = {
        'boleto': boleto,
    }
    
    return render(request, 'controle_financeiro/boleto_detalhes.html', context)


@login_required
def imprimir_boleto_pdf(request, boleto_id):
    """Gera PDF do boleto para impressão"""
    
    boleto = get_object_or_404(BoletoGerado, id=boleto_id)
    
    # Verifica se o usuário tem permissão para ver este boleto
    if not request.user.is_superuser:
        # Se não for superuser, verifica se é o dono da loja
        if boleto.controle_financeiro.loja.admin_user != request.user:
            messages.error(request, 'Você não tem permissão para visualizar este boleto.')
            return redirect('dashboard:principal')
    
    try:
        # Verificar se existe cobrança do Asaas associada
        try:
            from .models import CobrancaAsaas
            
            # Tentar buscar por controle financeiro
            cobranca_asaas = CobrancaAsaas.objects.filter(
                controle_financeiro=boleto.controle_financeiro
            ).first()
            
            # Se não encontrou, tentar buscar pela loja (caso mais recente)
            if not cobranca_asaas:
                cobranca_asaas = CobrancaAsaas.objects.filter(
                    controle_financeiro__loja=boleto.controle_financeiro.loja
                ).order_by('-data_criacao').first()
            
            # Se existe cobrança do Asaas e tem URL do PDF, redirecionar
            if cobranca_asaas and cobranca_asaas.bank_slip_url:
                return redirect(cobranca_asaas.bank_slip_url)
            
            # Se é um boleto do Asaas mas não tem cobrança salva
            if boleto.configuracao.codigo_banco == "461":  # Asaas
                # Verificar se há ID do Asaas nas observações ou outros campos
                observacoes = getattr(boleto, 'observacoes', '') or ''
                
                # Procurar padrão de ID do Asaas nas observações
                import re
                asaas_id_match = re.search(r'pay_[a-zA-Z0-9]+|[a-zA-Z0-9]{16,20}', observacoes)
                
                if asaas_id_match:
                    asaas_id = asaas_id_match.group()
                    pdf_url = f"https://www.asaas.com/b/pdf/{asaas_id}"
                    logger.info(f"ID Asaas extraído das observações: {asaas_id}")
                    return redirect(pdf_url)
                
                # Se não encontrou ID nas observações, mostrar mensagem explicativa
                messages.warning(request, 
                    'Este boleto foi criado localmente. Para usar o PDF oficial do Asaas, '
                    'gere uma nova cobrança através do sistema de Cobranças Asaas.'
                )
                
                # Redirecionar para a página de geração de cobranças do Asaas
                return redirect('controle_financeiro:gerar_cobranca_asaas', controle_id=boleto.controle_financeiro.id)
                
        except Exception as e:
            # Log do erro mas continuar com PDF local
            logger.warning(f"Erro ao buscar cobrança Asaas: {str(e)}")
            pass
        
        # NUNCA MAIS GERAR PDF LOCAL - sempre redirecionar para Asaas
        if boleto.configuracao.codigo_banco == "461":  # Asaas
            messages.warning(request, 
                '⚠️ Este é um boleto antigo. O sistema agora usa apenas cobranças oficiais do Asaas. '
                'Clique no botão abaixo para gerar uma nova cobrança oficial.'
            )
            return redirect('controle_financeiro:gerar_cobranca_asaas', controle_id=boleto.controle_financeiro.id)
        else:
            # Para outros bancos (se houver), manter PDF local
            from .pdf_service import BoletoPDFService
            
            pdf_service = BoletoPDFService()
            return pdf_service.gerar_pdf_boleto(boleto)
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF do boleto: {str(e)}')
        return redirect('controle_financeiro:detalhar_boleto', boleto_id=boleto_id)


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



