from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import PlanoComercial, AssinaturaLoja, HistoricoUso
from lojas.models import Loja


def is_superuser(user):
    return user.is_superuser


def teste_planos(request):
    """Teste simples para verificar se o app planos está funcionando"""
    return render(request, 'planos/teste.html')


@login_required
@user_passes_test(is_superuser)
def listar_planos(request):
    """Lista todos os planos comerciais"""
    from lojas.models import Loja
    
    planos = PlanoComercial.objects.all().order_by('ordem_exibicao', 'preco_mensal')
    lojas = Loja.objects.filter(status='ativa').order_by('nome')
    
    context = {
        'planos': planos,
        'lojas': lojas,
        'titulo': 'Planos Comerciais',
    }
    return render(request, 'planos/listar.html', context)


@login_required
@user_passes_test(is_superuser)
def criar_plano(request):
    """Cria um novo plano comercial"""
    if request.method == 'POST':
        # Processar dados do formulário
        nome = request.POST.get('nome')
        tipo = request.POST.get('tipo')
        descricao = request.POST.get('descricao')
        
        # Limites
        max_usuarios = int(request.POST.get('max_usuarios_simultaneos', 1))
        max_pdvs = int(request.POST.get('max_pdvs', 1))
        max_produtos = int(request.POST.get('max_produtos', 100))
        max_clientes = int(request.POST.get('max_clientes', 100))
        max_vendas = int(request.POST.get('max_vendas_mes', 100))
        
        # Recursos
        backup_automatico = request.POST.get('backup_automatico') == 'on'
        relatorios_avancados = request.POST.get('relatorios_avancados') == 'on'
        integracao_api = request.POST.get('integracao_api') == 'on'
        suporte_prioritario = request.POST.get('suporte_prioritario') == 'on'
        customizacao_avancada = request.POST.get('customizacao_avancada') == 'on'
        
        # Preços
        preco_mensal = Decimal(request.POST.get('preco_mensal', '0.00'))
        preco_anual = Decimal(request.POST.get('preco_anual', '0.00'))
        
        # Configurações
        status = request.POST.get('status', 'ativo')
        ordem_exibicao = int(request.POST.get('ordem_exibicao', 0))
        destaque = request.POST.get('destaque') == 'on'
        
        try:
            with transaction.atomic():
                plano = PlanoComercial.objects.create(
                    nome=nome,
                    tipo=tipo,
                    descricao=descricao,
                    max_usuarios_simultaneos=max_usuarios,
                    max_pdvs=max_pdvs,
                    max_produtos=max_produtos,
                    max_clientes=max_clientes,
                    max_vendas_mes=max_vendas,
                    backup_automatico=backup_automatico,
                    relatorios_avancados=relatorios_avancados,
                    integracao_api=integracao_api,
                    suporte_prioritario=suporte_prioritario,
                    customizacao_avancada=customizacao_avancada,
                    preco_mensal=preco_mensal,
                    preco_anual=preco_anual,
                    status=status,
                    ordem_exibicao=ordem_exibicao,
                    destaque=destaque
                )
                
                messages.success(request, f'Plano "{plano.nome}" criado com sucesso!')
                return redirect('listar_planos')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar plano: {str(e)}')
    
    context = {
        'titulo': 'Novo Plano Comercial',
        'tipos_plano': PlanoComercial.TIPO_PLANO_CHOICES,
        'status_choices': PlanoComercial.STATUS_CHOICES,
    }
    return render(request, 'planos/criar.html', context)


@login_required
@user_passes_test(is_superuser)
def editar_plano(request, plano_id):
    """Edita um plano comercial"""
    plano = get_object_or_404(PlanoComercial, id=plano_id)
    
    if request.method == 'POST':
        # Processar dados do formulário
        plano.nome = request.POST.get('nome')
        plano.tipo = request.POST.get('tipo')
        plano.descricao = request.POST.get('descricao')
        
        # Limites
        plano.max_usuarios_simultaneos = int(request.POST.get('max_usuarios_simultaneos', 1))
        plano.max_pdvs = int(request.POST.get('max_pdvs', 1))
        plano.max_produtos = int(request.POST.get('max_produtos', 100))
        plano.max_clientes = int(request.POST.get('max_clientes', 100))
        plano.max_vendas_mes = int(request.POST.get('max_vendas_mes', 100))
        
        # Recursos
        plano.backup_automatico = request.POST.get('backup_automatico') == 'on'
        plano.relatorios_avancados = request.POST.get('relatorios_avancados') == 'on'
        plano.integracao_api = request.POST.get('integracao_api') == 'on'
        plano.suporte_prioritario = request.POST.get('suporte_prioritario') == 'on'
        plano.customizacao_avancada = request.POST.get('customizacao_avancada') == 'on'
        
        # Preços
        plano.preco_mensal = Decimal(request.POST.get('preco_mensal', '0.00'))
        plano.preco_anual = Decimal(request.POST.get('preco_anual', '0.00'))
        
        # Configurações
        plano.status = request.POST.get('status', 'ativo')
        plano.ordem_exibicao = int(request.POST.get('ordem_exibicao', 0))
        plano.destaque = request.POST.get('destaque') == 'on'
        
        try:
            plano.save()
            messages.success(request, f'Plano "{plano.nome}" atualizado com sucesso!')
            return redirect('listar_planos')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar plano: {str(e)}')
    
    context = {
        'plano': plano,
        'titulo': f'Editar Plano: {plano.nome}',
        'tipos_plano': PlanoComercial.TIPO_PLANO_CHOICES,
        'status_choices': PlanoComercial.STATUS_CHOICES,
    }
    return render(request, 'planos/editar.html', context)


@login_required
@user_passes_test(is_superuser)
def detalhar_plano(request, plano_id):
    """Detalha um plano comercial"""
    plano = get_object_or_404(PlanoComercial, id=plano_id)
    assinaturas = AssinaturaLoja.objects.filter(plano=plano).order_by('-data_inicio')
    
    context = {
        'plano': plano,
        'assinaturas': assinaturas,
        'titulo': f'Detalhes do Plano: {plano.nome}',
    }
    return render(request, 'planos/detalhar.html', context)


@login_required
@user_passes_test(is_superuser)
def assinar_plano(request, loja_id, plano_id):
    """Assina uma loja a um plano"""
    loja = get_object_or_404(Loja, id=loja_id)
    plano = get_object_or_404(PlanoComercial, id=plano_id)
    
    if request.method == 'POST':
        tipo_pagamento = request.POST.get('tipo_pagamento', 'mensal')
        
        try:
            with transaction.atomic():
                # Cancela assinatura anterior se existir
                assinatura_anterior = AssinaturaLoja.objects.filter(loja=loja).first()
                if assinatura_anterior:
                    assinatura_anterior.status = 'cancelada'
                    assinatura_anterior.data_cancelamento = timezone.now()
                    assinatura_anterior.save()
                
                # Calcula data de vencimento
                if tipo_pagamento == 'anual':
                    data_vencimento = timezone.now() + timedelta(days=365)
                else:
                    data_vencimento = timezone.now() + timedelta(days=30)
                
                # Cria nova assinatura
                assinatura = AssinaturaLoja.objects.create(
                    loja=loja,
                    plano=plano,
                    tipo_pagamento=tipo_pagamento,
                    data_vencimento=data_vencimento
                )
                
                # Registra no histórico
                HistoricoUso.objects.create(
                    assinatura=assinatura,
                    tipo_evento='login',
                    descricao=f'Assinatura do plano {plano.nome} ativada',
                    usuarios_online=0,
                    pdvs_ativos=0,
                    vendas_mes=0
                )
                
                messages.success(request, f'Loja "{loja.nome}" assinada ao plano "{plano.nome}" com sucesso!')
                return redirect('planos:detalhar_plano', plano_id=plano.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao assinar plano: {str(e)}')
    
    context = {
        'loja': loja,
        'plano': plano,
        'titulo': f'Assinar Plano: {plano.nome}',
        'tipos_pagamento': AssinaturaLoja.TIPO_PAGAMENTO_CHOICES,
    }
    return render(request, 'planos/assinar.html', context)


@login_required
@user_passes_test(is_superuser)
def estatisticas_planos(request):
    """Estatísticas dos planos comerciais"""
    total_planos = PlanoComercial.objects.count()
    planos_ativos = PlanoComercial.objects.filter(status='ativo').count()
    total_assinaturas = AssinaturaLoja.objects.count()
    assinaturas_ativas = AssinaturaLoja.objects.filter(status='ativa').count()
    
    # Estatísticas por plano
    planos_stats = []
    for plano in PlanoComercial.objects.filter(status='ativo'):
        assinaturas_plano = AssinaturaLoja.objects.filter(plano=plano, status='ativa').count()
        planos_stats.append({
            'plano': plano,
            'assinaturas': assinaturas_plano,
            'receita_mensal': assinaturas_plano * plano.preco_mensal,
            'receita_anual': assinaturas_plano * plano.preco_anual,
        })
    
    context = {
        'total_planos': total_planos,
        'planos_ativos': planos_ativos,
        'total_assinaturas': total_assinaturas,
        'assinaturas_ativas': assinaturas_ativas,
        'planos_stats': planos_stats,
        'titulo': 'Estatísticas dos Planos',
    }
    return render(request, 'planos/estatisticas.html', context)


@login_required
@user_passes_test(is_superuser)
def controle_acesso_ajax(request):
    """API para controle de acesso em tempo real"""
    if request.method == 'GET':
        loja_id = request.GET.get('loja_id')
        
        if loja_id:
            try:
                assinatura = AssinaturaLoja.objects.get(loja_id=loja_id, status='ativa')
                
                # Atualiza contadores (simulado)
                assinatura.usuarios_online = int(request.GET.get('usuarios_online', 0))
                assinatura.pdvs_ativos = int(request.GET.get('pdvs_ativos', 0))
                assinatura.vendas_mes_atual = int(request.GET.get('vendas_mes', 0))
                assinatura.save()
                
                # Verifica limites
                limites = assinatura.verificar_limites()
                
                return JsonResponse({
                    'success': True,
                    'assinatura': {
                        'id': assinatura.id,
                        'plano': assinatura.plano.nome,
                        'usuarios_online': assinatura.usuarios_online,
                        'max_usuarios': assinatura.plano.max_usuarios_simultaneos,
                        'pdvs_ativos': assinatura.pdvs_ativos,
                        'max_pdvs': assinatura.plano.max_pdvs,
                        'vendas_mes': assinatura.vendas_mes_atual,
                        'max_vendas': assinatura.plano.max_vendas_mes,
                        'limites_atingidos': limites,
                        'pode_adicionar_usuario': assinatura.pode_adicionar_usuario(),
                        'pode_adicionar_pdv': assinatura.pode_adicionar_pdv(),
                        'pode_realizar_venda': assinatura.pode_realizar_venda(),
                    }
                })
                
            except AssinaturaLoja.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Loja não possui assinatura ativa'
                })
        
        return JsonResponse({
            'success': False,
            'error': 'ID da loja não fornecido'
        })
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})
