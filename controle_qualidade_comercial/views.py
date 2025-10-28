from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    ProdutoComercial, VendaComercial, ControleQualidade, 
    ReclamacaoCliente, MetaQualidade, CategoriaProduto, FornecedorComercial
)
from lojas.models import Loja


@login_required
def dashboard_controle_qualidade(request):
    """Dashboard principal do controle de qualidade comercial"""
    
    # Verificar se o usuário tem acesso a uma loja de controle de qualidade
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado. Esta loja não é do tipo Dashboard Comercial e Qualidade.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Usuário não está associado a uma loja de Dashboard Comercial e Qualidade.')
        return redirect('dashboard:index')
    
    # Métricas gerais
    total_produtos = ProdutoComercial.objects.filter(loja=loja, ativo=True).count()
    
    # Vendas do mês
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    vendas_mes = VendaComercial.objects.filter(
        loja=loja, 
        created_at__gte=inicio_mes,
        status='concluida'
    ).aggregate(
        total=Count('id'),
        valor_total=Sum('valor_final')
    )
    
    # Produtos com estoque baixo
    estoque_baixo = ProdutoComercial.objects.filter(
        loja=loja, 
        ativo=True,
        estoque_atual__lte=F('estoque_minimo')
    ).count()
    
    # Reclamações abertas
    reclamacoes_abertas = ReclamacaoCliente.objects.filter(
        loja=loja,
        status__in=['aberta', 'em_andamento']
    ).count()
    
    # Taxa de aprovação de qualidade (últimos 30 dias)
    data_limite = timezone.now() - timedelta(days=30)
    qualidade_stats = ControleQualidade.objects.filter(
        loja=loja,
        data_inspecao__gte=data_limite
    ).aggregate(
        total=Count('id'),
        aprovados=Count('id', filter=Q(status_qualidade='aprovado'))
    )
    
    taxa_aprovacao = 0
    if qualidade_stats['total'] > 0:
        taxa_aprovacao = (qualidade_stats['aprovados'] / qualidade_stats['total']) * 100
    
    context = {
        'loja': loja,
        'total_produtos': total_produtos,
        'vendas_mes': vendas_mes,
        'estoque_baixo': estoque_baixo,
        'reclamacoes_abertas': reclamacoes_abertas,
        'taxa_aprovacao': round(taxa_aprovacao, 1),
        'total_inspecoes': qualidade_stats['total'],
    }
    
    return render(request, 'controle_qualidade_comercial/dashboard.html', context)


@login_required
def api_metricas(request):
    """API para métricas do dashboard"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    # Métricas gerais
    total_produtos = ProdutoComercial.objects.filter(loja=loja, ativo=True).count()
    
    # Vendas do mês
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    vendas_mes = VendaComercial.objects.filter(
        loja=loja, 
        created_at__gte=inicio_mes,
        status='concluida'
    ).aggregate(
        total=Count('id'),
        valor_total=Sum('valor_final')
    )
    
    # Produtos com estoque baixo
    estoque_baixo = ProdutoComercial.objects.filter(
        loja=loja, 
        ativo=True,
        estoque_atual__lte=F('estoque_minimo')
    ).count()
    
    # Reclamações abertas
    reclamacoes_abertas = ReclamacaoCliente.objects.filter(
        loja=loja,
        status__in=['aberta', 'em_andamento']
    ).count()
    
    # Taxa de aprovação de qualidade (últimos 30 dias)
    data_limite = timezone.now() - timedelta(days=30)
    qualidade_stats = ControleQualidade.objects.filter(
        loja=loja,
        data_inspecao__gte=data_limite
    ).aggregate(
        total=Count('id'),
        aprovados=Count('id', filter=Q(status_qualidade='aprovado'))
    )
    
    taxa_aprovacao = 0
    if qualidade_stats['total'] > 0:
        taxa_aprovacao = (qualidade_stats['aprovados'] / qualidade_stats['total']) * 100
    
    return JsonResponse({
        'produtos': {
            'total': total_produtos,
            'estoque_baixo': estoque_baixo
        },
        'vendas': {
            'total_mes': vendas_mes['total'] or 0,
            'valor_total_mes': float(vendas_mes['valor_total'] or 0)
        },
        'qualidade': {
            'taxa_aprovacao': round(taxa_aprovacao, 1),
            'total_inspecoes': qualidade_stats['total']
        },
        'reclamacoes': {
            'abertas': reclamacoes_abertas
        }
    })


@login_required
def api_vendas_diarias(request):
    """API para gráfico de vendas diárias (últimos 7 dias)"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    # Últimos 7 dias
    data_limite = timezone.now() - timedelta(days=7)
    
    vendas_diarias = VendaComercial.objects.filter(
        loja=loja,
        created_at__gte=data_limite,
        status='concluida'
    ).extra(
        select={'data': 'DATE(created_at)'}
    ).values('data').annotate(
        total_vendas=Count('id'),
        valor_total=Sum('valor_final')
    ).order_by('data')
    
    # Converter para formato JSON serializável
    resultado = []
    for venda in vendas_diarias:
        resultado.append({
            'data': venda['data'].strftime('%Y-%m-%d'),
            'total_vendas': venda['total_vendas'],
            'valor_total': float(venda['valor_total'] or 0)
        })
    
    return JsonResponse(resultado, safe=False)


@login_required
def api_top_produtos(request):
    """API para top produtos mais vendidos"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    # Últimos 30 dias
    data_limite = timezone.now() - timedelta(days=30)
    
    from .models import ItemVenda
    
    top_produtos = ItemVenda.objects.filter(
        venda__loja=loja,
        venda__created_at__gte=data_limite,
        venda__status='concluida'
    ).values(
        'produto__nome',
        'produto__sku'
    ).annotate(
        total_vendido=Sum('quantidade'),
        valor_total=Sum('subtotal')
    ).order_by('-total_vendido')[:10]
    
    # Converter para formato JSON serializável
    resultado = []
    for produto in top_produtos:
        resultado.append({
            'nome': produto['produto__nome'],
            'sku': produto['produto__sku'],
            'total_vendido': produto['total_vendido'],
            'valor_total': float(produto['valor_total'] or 0)
        })
    
    return JsonResponse(resultado, safe=False)


@login_required
def api_reclamacoes_tipo(request):
    """API para distribuição de reclamações por tipo"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    # Últimos 30 dias
    data_limite = timezone.now() - timedelta(days=30)
    
    reclamacoes_tipo = ReclamacaoCliente.objects.filter(
        loja=loja,
        created_at__gte=data_limite
    ).values('tipo_reclamacao').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Converter para formato JSON serializável
    resultado = []
    for reclamacao in reclamacoes_tipo:
        resultado.append({
            'tipo_reclamacao': reclamacao['tipo_reclamacao'],
            'total': reclamacao['total']
        })
    
    return JsonResponse(resultado, safe=False)


@login_required
def api_evolucao_qualidade(request):
    """API para evolução da qualidade (últimos 6 meses)"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    # Últimos 6 meses
    data_limite = timezone.now() - timedelta(days=180)
    
    evolucao_qualidade = ControleQualidade.objects.filter(
        loja=loja,
        data_inspecao__gte=data_limite
    ).extra(
        select={'mes': "DATE_TRUNC('month', data_inspecao)"}
    ).values('mes').annotate(
        total_inspecoes=Count('id'),
        aprovados=Count('id', filter=Q(status_qualidade='aprovado'))
    ).order_by('mes')
    
    # Converter para formato JSON serializável
    resultado = []
    for item in evolucao_qualidade:
        taxa_aprovacao = 0
        if item['total_inspecoes'] > 0:
            taxa_aprovacao = (item['aprovados'] / item['total_inspecoes']) * 100
        
        resultado.append({
            'mes': item['mes'].strftime('%Y-%m-%d'),
            'total_inspecoes': item['total_inspecoes'],
            'aprovados': item['aprovados'],
            'taxa_aprovacao': round(taxa_aprovacao, 1)
        })
    
    return JsonResponse(resultado, safe=False)


# =============================================================================
# VIEWS CRUD - PRODUTOS
# =============================================================================

@login_required
def listar_produtos(request):
    """Lista todos os produtos da loja"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    produtos = ProdutoComercial.objects.filter(loja=loja).select_related('categoria', 'fornecedor').order_by('nome')
    
    context = {
        'loja': loja,
        'produtos': produtos,
        'total_produtos': produtos.count(),
        'produtos_ativos': produtos.filter(ativo=True).count(),
        'produtos_estoque_baixo': produtos.filter(estoque_atual__lte=F('estoque_minimo')).count(),
    }
    
    return render(request, 'controle_qualidade_comercial/produtos/listar.html', context)


@login_required
def criar_produto(request):
    """Cria um novo produto"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            produto = ProdutoComercial.objects.create(
                loja=loja,
                nome=request.POST.get('nome'),
                sku=request.POST.get('sku'),
                codigo_barras=request.POST.get('codigo_barras', ''),
                categoria_id=request.POST.get('categoria') if request.POST.get('categoria') else None,
                fornecedor_id=request.POST.get('fornecedor') if request.POST.get('fornecedor') else None,
                preco_custo=request.POST.get('preco_custo') or 0,
                preco_venda=request.POST.get('preco_venda') or 0,
                estoque_atual=request.POST.get('estoque_atual') or 0,
                estoque_minimo=request.POST.get('estoque_minimo') or 0,
                descricao=request.POST.get('descricao', ''),
                ativo=request.POST.get('ativo') == 'on'
            )
            
            messages.success(request, f'Produto "{produto.nome}" criado com sucesso!')
            return redirect('controle_qualidade_comercial:listar_produtos')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar produto: {str(e)}')
    
    # Buscar categorias e fornecedores para o formulário
    categorias = CategoriaProduto.objects.filter(loja=loja, ativo=True)
    fornecedores = FornecedorComercial.objects.filter(loja=loja, ativo=True)
    
    context = {
        'loja': loja,
        'categorias': categorias,
        'fornecedores': fornecedores,
    }
    
    return render(request, 'controle_qualidade_comercial/produtos/criar.html', context)


@login_required
def editar_produto(request, produto_id):
    """Edita um produto existente"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    produto = get_object_or_404(ProdutoComercial, id=produto_id, loja=loja)
    
    if request.method == 'POST':
        try:
            produto.nome = request.POST.get('nome')
            produto.sku = request.POST.get('sku')
            produto.codigo_barras = request.POST.get('codigo_barras', '')
            produto.categoria_id = request.POST.get('categoria') if request.POST.get('categoria') else None
            produto.fornecedor_id = request.POST.get('fornecedor') if request.POST.get('fornecedor') else None
            produto.preco_custo = request.POST.get('preco_custo') or 0
            produto.preco_venda = request.POST.get('preco_venda') or 0
            produto.estoque_atual = request.POST.get('estoque_atual') or 0
            produto.estoque_minimo = request.POST.get('estoque_minimo') or 0
            produto.descricao = request.POST.get('descricao', '')
            produto.ativo = request.POST.get('ativo') == 'on'
            produto.save()
            
            messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso!')
            return redirect('controle_qualidade_comercial:listar_produtos')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar produto: {str(e)}')
    
    # Buscar categorias e fornecedores para o formulário
    categorias = CategoriaProduto.objects.filter(loja=loja, ativo=True)
    fornecedores = FornecedorComercial.objects.filter(loja=loja, ativo=True)
    
    context = {
        'loja': loja,
        'produto': produto,
        'categorias': categorias,
        'fornecedores': fornecedores,
    }
    
    return render(request, 'controle_qualidade_comercial/produtos/editar.html', context)


@login_required
def detalhar_produto(request, produto_id):
    """Detalha um produto específico"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    produto = get_object_or_404(ProdutoComercial, id=produto_id, loja=loja)
    
    # Histórico de vendas do produto (últimas 10)
    vendas_produto = ItemVenda.objects.filter(
        produto=produto,
        venda__loja=loja
    ).select_related('venda').order_by('-venda__created_at')[:10]
    
    # Controles de qualidade do produto (últimos 5)
    controles_qualidade = ControleQualidade.objects.filter(
        produto=produto,
        loja=loja
    ).order_by('-data_inspecao')[:5]
    
    context = {
        'loja': loja,
        'produto': produto,
        'vendas_produto': vendas_produto,
        'controles_qualidade': controles_qualidade,
    }
    
    return render(request, 'controle_qualidade_comercial/produtos/detalhar.html', context)


@login_required
def excluir_produto(request, produto_id):
    """Exclui um produto"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    produto = get_object_or_404(ProdutoComercial, id=produto_id, loja=loja)
    
    if request.method == 'POST':
        try:
            nome_produto = produto.nome
            produto.delete()
            messages.success(request, f'Produto "{nome_produto}" excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir produto: {str(e)}')
    
    return redirect('controle_qualidade_comercial:listar_produtos')


# =============================================================================
# VIEWS CRUD - VENDAS
# =============================================================================

@login_required
def listar_vendas(request):
    """Lista todas as vendas da loja"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    vendas = VendaComercial.objects.filter(loja=loja).select_related('vendedor').order_by('-created_at')
    
    # Filtros
    status_filtro = request.GET.get('status')
    if status_filtro:
        vendas = vendas.filter(status=status_filtro)
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    if data_inicio:
        vendas = vendas.filter(created_at__date__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(created_at__date__lte=data_fim)
    
    context = {
        'loja': loja,
        'vendas': vendas,
        'status_filtro': status_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    
    return render(request, 'controle_qualidade_comercial/vendas/listar.html', context)


@login_required
def criar_venda(request):
    """Cria uma nova venda"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            # Gerar número da venda
            import random
            import string
            numero_venda = ''.join(random.choices(string.digits, k=8))
            
            venda = VendaComercial.objects.create(
                loja=loja,
                numero_venda=numero_venda,
                vendedor=request.user,
                cliente_nome=request.POST.get('cliente_nome', ''),
                cliente_cpf=request.POST.get('cliente_cpf', ''),
                cliente_telefone=request.POST.get('cliente_telefone', ''),
                valor_total=request.POST.get('valor_total') or 0,
                desconto=request.POST.get('desconto') or 0,
                valor_final=request.POST.get('valor_final') or 0,
                forma_pagamento=request.POST.get('forma_pagamento'),
                status=request.POST.get('status', 'concluida'),
                observacoes=request.POST.get('observacoes', '')
            )
            
            messages.success(request, f'Venda "{venda.numero_venda}" criada com sucesso!')
            return redirect('controle_qualidade_comercial:detalhar_venda', venda_id=venda.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar venda: {str(e)}')
    
    produtos = ProdutoComercial.objects.filter(loja=loja, ativo=True)
    
    context = {
        'loja': loja,
        'produtos': produtos,
    }
    
    return render(request, 'controle_qualidade_comercial/vendas/criar.html', context)


@login_required
def detalhar_venda(request, venda_id):
    """Detalha uma venda específica"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    venda = get_object_or_404(VendaComercial, id=venda_id, loja=loja)
    itens = venda.itens.select_related('produto').all()
    
    context = {
        'loja': loja,
        'venda': venda,
        'itens': itens,
    }
    
    return render(request, 'controle_qualidade_comercial/vendas/detalhar.html', context)


@login_required
def editar_venda(request, venda_id):
    """Edita uma venda existente"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    venda = get_object_or_404(VendaComercial, id=venda_id, loja=loja)
    
    if request.method == 'POST':
        try:
            venda.cliente_nome = request.POST.get('cliente_nome', '')
            venda.cliente_cpf = request.POST.get('cliente_cpf', '')
            venda.cliente_telefone = request.POST.get('cliente_telefone', '')
            venda.valor_total = request.POST.get('valor_total') or 0
            venda.desconto = request.POST.get('desconto') or 0
            venda.valor_final = request.POST.get('valor_final') or 0
            venda.forma_pagamento = request.POST.get('forma_pagamento')
            venda.status = request.POST.get('status')
            venda.observacoes = request.POST.get('observacoes', '')
            venda.save()
            
            messages.success(request, f'Venda "{venda.numero_venda}" atualizada com sucesso!')
            return redirect('controle_qualidade_comercial:detalhar_venda', venda_id=venda.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar venda: {str(e)}')
    
    context = {
        'loja': loja,
        'venda': venda,
    }
    
    return render(request, 'controle_qualidade_comercial/vendas/editar.html', context)


@login_required
def adicionar_item_venda(request, venda_id):
    """Adiciona item a uma venda"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    venda = get_object_or_404(VendaComercial, id=venda_id, loja=loja)
    
    if request.method == 'POST':
        try:
            produto_id = request.POST.get('produto_id')
            quantidade = int(request.POST.get('quantidade', 1))
            preco_unitario = float(request.POST.get('preco_unitario', 0))
            
            produto = get_object_or_404(ProdutoComercial, id=produto_id, loja=loja)
            
            item = ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco_unitario
            )
            
            # Atualizar totais da venda
            itens = venda.itens.all()
            valor_total = sum(item.subtotal for item in itens)
            venda.valor_total = valor_total
            venda.valor_final = valor_total - venda.desconto
            venda.save()
            
            return JsonResponse({
                'success': True,
                'item_id': str(item.id),
                'subtotal': float(item.subtotal),
                'valor_total': float(venda.valor_total),
                'valor_final': float(venda.valor_final)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


# =============================================================================
# VIEWS CRUD - CONTROLE DE QUALIDADE
# =============================================================================

@login_required
def listar_controle_qualidade(request):
    """Lista todas as inspeções de qualidade"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    inspecoes = ControleQualidade.objects.filter(loja=loja).select_related('produto', 'inspetor').order_by('-data_inspecao')
    
    # Filtros
    status_filtro = request.GET.get('status')
    if status_filtro:
        inspecoes = inspecoes.filter(status_qualidade=status_filtro)
    
    produto_filtro = request.GET.get('produto')
    if produto_filtro:
        inspecoes = inspecoes.filter(produto_id=produto_filtro)
    
    context = {
        'loja': loja,
        'inspecoes': inspecoes,
        'produtos': ProdutoComercial.objects.filter(loja=loja, ativo=True),
        'status_filtro': status_filtro,
        'produto_filtro': produto_filtro,
    }
    
    return render(request, 'controle_qualidade_comercial/qualidade/listar.html', context)


@login_required
def criar_inspecao_qualidade(request):
    """Cria uma nova inspeção de qualidade"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            inspecao = ControleQualidade.objects.create(
                loja=loja,
                produto_id=request.POST.get('produto'),
                lote=request.POST.get('lote', ''),
                data_fabricacao=request.POST.get('data_fabricacao') or None,
                data_validade=request.POST.get('data_validade') or None,
                data_inspecao=request.POST.get('data_inspecao'),
                inspetor=request.user,
                status_qualidade=request.POST.get('status_qualidade'),
                aparencia_visual=request.POST.get('aparencia_visual'),
                integridade_embalagem=request.POST.get('integridade_embalagem'),
                conformidade_especificacao=request.POST.get('conformidade_especificacao'),
                observacoes=request.POST.get('observacoes', ''),
                acoes_corretivas=request.POST.get('acoes_corretivas', '')
            )
            
            messages.success(request, f'Inspeção de qualidade criada com sucesso!')
            return redirect('controle_qualidade_comercial:listar_controle_qualidade')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar inspeção: {str(e)}')
    
    produtos = ProdutoComercial.objects.filter(loja=loja, ativo=True)
    
    context = {
        'loja': loja,
        'produtos': produtos,
    }
    
    return render(request, 'controle_qualidade_comercial/qualidade/criar.html', context)


@login_required
def detalhar_inspecao_qualidade(request, inspecao_id):
    """Detalha uma inspeção de qualidade específica"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    inspecao = get_object_or_404(ControleQualidade, id=inspecao_id, loja=loja)
    
    context = {
        'loja': loja,
        'inspecao': inspecao,
    }
    
    return render(request, 'controle_qualidade_comercial/qualidade/detalhar.html', context)


@login_required
def editar_inspecao_qualidade(request, inspecao_id):
    """Edita uma inspeção de qualidade existente"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    inspecao = get_object_or_404(ControleQualidade, id=inspecao_id, loja=loja)
    
    if request.method == 'POST':
        try:
            inspecao.produto_id = request.POST.get('produto')
            inspecao.lote = request.POST.get('lote', '')
            inspecao.data_fabricacao = request.POST.get('data_fabricacao') or None
            inspecao.data_validade = request.POST.get('data_validade') or None
            inspecao.data_inspecao = request.POST.get('data_inspecao')
            inspecao.status_qualidade = request.POST.get('status_qualidade')
            inspecao.aparencia_visual = request.POST.get('aparencia_visual')
            inspecao.integridade_embalagem = request.POST.get('integridade_embalagem')
            inspecao.conformidade_especificacao = request.POST.get('conformidade_especificacao')
            inspecao.observacoes = request.POST.get('observacoes', '')
            inspecao.acoes_corretivas = request.POST.get('acoes_corretivas', '')
            inspecao.save()
            
            messages.success(request, f'Inspeção de qualidade atualizada com sucesso!')
            return redirect('controle_qualidade_comercial:detalhar_inspecao_qualidade', inspecao_id=inspecao.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar inspeção: {str(e)}')
    
    produtos = ProdutoComercial.objects.filter(loja=loja, ativo=True)
    
    context = {
        'loja': loja,
        'inspecao': inspecao,
        'produtos': produtos,
    }
    
    return render(request, 'controle_qualidade_comercial/qualidade/editar.html', context)


@login_required
def excluir_inspecao_qualidade(request, inspecao_id):
    """Exclui uma inspeção de qualidade"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    inspecao = get_object_or_404(ControleQualidade, id=inspecao_id, loja=loja)
    
    if request.method == 'POST':
        try:
            inspecao.delete()
            messages.success(request, f'Inspeção de qualidade excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir inspeção: {str(e)}')
    
    return redirect('controle_qualidade_comercial:listar_controle_qualidade')


# =============================================================================
# VIEWS CRUD - RECLAMAÇÕES
# =============================================================================

@login_required
def listar_reclamacoes(request):
    """Lista todas as reclamações"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    reclamacoes = ReclamacaoCliente.objects.filter(loja=loja).select_related('produto', 'venda', 'responsavel').order_by('-created_at')
    
    # Filtros
    status_filtro = request.GET.get('status')
    if status_filtro:
        reclamacoes = reclamacoes.filter(status=status_filtro)
    
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        reclamacoes = reclamacoes.filter(tipo_reclamacao=tipo_filtro)
    
    context = {
        'loja': loja,
        'reclamacoes': reclamacoes,
        'status_filtro': status_filtro,
        'tipo_filtro': tipo_filtro,
    }
    
    return render(request, 'controle_qualidade_comercial/reclamacoes/listar.html', context)


@login_required
def criar_reclamacao(request):
    """Cria uma nova reclamação"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            reclamacao = ReclamacaoCliente.objects.create(
                loja=loja,
                cliente_nome=request.POST.get('cliente_nome'),
                cliente_email=request.POST.get('cliente_email', ''),
                cliente_telefone=request.POST.get('cliente_telefone', ''),
                produto_id=request.POST.get('produto') if request.POST.get('produto') else None,
                venda_id=request.POST.get('venda') if request.POST.get('venda') else None,
                tipo_reclamacao=request.POST.get('tipo_reclamacao'),
                descricao=request.POST.get('descricao'),
                prioridade=request.POST.get('prioridade', 'media'),
                responsavel=request.user
            )
            
            messages.success(request, f'Reclamação "{reclamacao.numero_protocolo}" criada com sucesso!')
            return redirect('controle_qualidade_comercial:listar_reclamacoes')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar reclamação: {str(e)}')
    
    produtos = ProdutoComercial.objects.filter(loja=loja, ativo=True)
    vendas_recentes = VendaComercial.objects.filter(loja=loja).order_by('-created_at')[:50]
    
    context = {
        'loja': loja,
        'produtos': produtos,
        'vendas_recentes': vendas_recentes,
    }
    
    return render(request, 'controle_qualidade_comercial/reclamacoes/criar.html', context)


@login_required
def detalhar_reclamacao(request, reclamacao_id):
    """Detalha uma reclamação específica"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    reclamacao = get_object_or_404(ReclamacaoCliente, id=reclamacao_id, loja=loja)
    
    context = {
        'loja': loja,
        'reclamacao': reclamacao,
    }
    
    return render(request, 'controle_qualidade_comercial/reclamacoes/detalhar.html', context)


@login_required
def editar_reclamacao(request, reclamacao_id):
    """Edita uma reclamação existente"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    reclamacao = get_object_or_404(ReclamacaoCliente, id=reclamacao_id, loja=loja)
    
    if request.method == 'POST':
        try:
            reclamacao.cliente_nome = request.POST.get('cliente_nome')
            reclamacao.cliente_email = request.POST.get('cliente_email', '')
            reclamacao.cliente_telefone = request.POST.get('cliente_telefone', '')
            reclamacao.produto_id = request.POST.get('produto') if request.POST.get('produto') else None
            reclamacao.venda_id = request.POST.get('venda') if request.POST.get('venda') else None
            reclamacao.tipo_reclamacao = request.POST.get('tipo_reclamacao')
            reclamacao.descricao = request.POST.get('descricao')
            reclamacao.prioridade = request.POST.get('prioridade', 'media')
            reclamacao.save()
            
            messages.success(request, f'Reclamação "{reclamacao.numero_protocolo}" atualizada com sucesso!')
            return redirect('controle_qualidade_comercial:detalhar_reclamacao', reclamacao_id=reclamacao.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar reclamação: {str(e)}')
    
    produtos = ProdutoComercial.objects.filter(loja=loja, ativo=True)
    vendas_recentes = VendaComercial.objects.filter(loja=loja).order_by('-created_at')[:50]
    
    context = {
        'loja': loja,
        'reclamacao': reclamacao,
        'produtos': produtos,
        'vendas_recentes': vendas_recentes,
    }
    
    return render(request, 'controle_qualidade_comercial/reclamacoes/editar.html', context)


@login_required
def atualizar_reclamacao(request, reclamacao_id):
    """Atualiza status de uma reclamação"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    reclamacao = get_object_or_404(ReclamacaoCliente, id=reclamacao_id, loja=loja)
    
    if request.method == 'POST':
        try:
            reclamacao.status = request.POST.get('status')
            reclamacao.resolucao = request.POST.get('resolucao', '')
            reclamacao.satisfacao_cliente = request.POST.get('satisfacao_cliente') or None
            
            if reclamacao.status == 'resolvida' and not reclamacao.data_resolucao:
                reclamacao.data_resolucao = timezone.now()
            
            reclamacao.save()
            
            messages.success(request, f'Reclamação "{reclamacao.numero_protocolo}" atualizada com sucesso!')
            return redirect('controle_qualidade_comercial:listar_reclamacoes')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar reclamação: {str(e)}')
    
    context = {
        'loja': loja,
        'reclamacao': reclamacao,
    }
    
    return render(request, 'controle_qualidade_comercial/reclamacoes/atualizar.html', context)


@login_required
def excluir_reclamacao(request, reclamacao_id):
    """Exclui uma reclamação"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    reclamacao = get_object_or_404(ReclamacaoCliente, id=reclamacao_id, loja=loja)
    
    if request.method == 'POST':
        try:
            protocolo = reclamacao.numero_protocolo
            reclamacao.delete()
            messages.success(request, f'Reclamação "{protocolo}" excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir reclamação: {str(e)}')
    
    return redirect('controle_qualidade_comercial:listar_reclamacoes')


# =============================================================================
# VIEWS CRUD - METAS DE QUALIDADE
# =============================================================================

@login_required
def listar_metas(request):
    """Lista todas as metas de qualidade"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    metas = MetaQualidade.objects.filter(loja=loja).order_by('-created_at')
    
    context = {
        'loja': loja,
        'metas': metas,
    }
    
    return render(request, 'controle_qualidade_comercial/metas/listar.html', context)


@login_required
def criar_meta(request):
    """Cria uma nova meta de qualidade"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            meta = MetaQualidade.objects.create(
                loja=loja,
                nome=request.POST.get('nome'),
                descricao=request.POST.get('descricao', ''),
                tipo_meta=request.POST.get('tipo_meta'),
                valor_meta=request.POST.get('valor_meta'),
                unidade_medida=request.POST.get('unidade_medida', ''),
                periodo_inicio=request.POST.get('periodo_inicio'),
                periodo_fim=request.POST.get('periodo_fim')
            )
            
            messages.success(request, f'Meta "{meta.nome}" criada com sucesso!')
            return redirect('controle_qualidade_comercial:listar_metas')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar meta: {str(e)}')
    
    context = {
        'loja': loja,
    }
    
    return render(request, 'controle_qualidade_comercial/metas/criar.html', context)


@login_required
def detalhar_meta(request, meta_id):
    """Detalha uma meta de qualidade específica"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    meta = get_object_or_404(MetaQualidade, id=meta_id, loja=loja)
    
    context = {
        'loja': loja,
        'meta': meta,
    }
    
    return render(request, 'controle_qualidade_comercial/metas/detalhar.html', context)


@login_required
def editar_meta(request, meta_id):
    """Edita uma meta de qualidade existente"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    meta = get_object_or_404(MetaQualidade, id=meta_id, loja=loja)
    
    if request.method == 'POST':
        try:
            meta.nome = request.POST.get('nome')
            meta.descricao = request.POST.get('descricao', '')
            meta.tipo_meta = request.POST.get('tipo_meta')
            meta.valor_meta = request.POST.get('valor_meta')
            meta.valor_atual = request.POST.get('valor_atual', meta.valor_atual)
            meta.unidade_medida = request.POST.get('unidade_medida', '')
            meta.periodo_inicio = request.POST.get('periodo_inicio')
            meta.periodo_fim = request.POST.get('periodo_fim')
            meta.status = request.POST.get('status', meta.status)
            meta.save()
            
            messages.success(request, f'Meta "{meta.nome}" atualizada com sucesso!')
            return redirect('controle_qualidade_comercial:detalhar_meta', meta_id=meta.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar meta: {str(e)}')
    
    context = {
        'loja': loja,
        'meta': meta,
    }
    
    return render(request, 'controle_qualidade_comercial/metas/editar.html', context)


@login_required
def excluir_meta(request, meta_id):
    """Exclui uma meta de qualidade"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    meta = get_object_or_404(MetaQualidade, id=meta_id, loja=loja)
    
    if request.method == 'POST':
        try:
            nome_meta = meta.nome
            meta.delete()
            messages.success(request, f'Meta "{nome_meta}" excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir meta: {str(e)}')
    
    return redirect('controle_qualidade_comercial:listar_metas')


@login_required
def atualizar_progresso_meta(request, meta_id):
    """Atualiza o progresso de uma meta"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    meta = get_object_or_404(MetaQualidade, id=meta_id, loja=loja)
    
    if request.method == 'POST':
        try:
            valor_atual = float(request.POST.get('valor_atual', 0))
            meta.valor_atual = valor_atual
            
            # Verificar se a meta foi atingida
            if meta.meta_atingida and meta.status == 'ativa':
                meta.status = 'concluida'
            
            meta.save()
            
            return JsonResponse({
                'success': True,
                'valor_atual': float(meta.valor_atual),
                'percentual_atingido': meta.percentual_atingido,
                'meta_atingida': meta.meta_atingida,
                'status': meta.status
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


# =============================================================================
# VIEWS CRUD - CATEGORIAS
# =============================================================================

@login_required
def listar_categorias(request):
    """Lista todas as categorias de produtos"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    categorias = CategoriaProduto.objects.filter(loja=loja).order_by('nome')
    
    context = {
        'loja': loja,
        'categorias': categorias,
    }
    
    return render(request, 'controle_qualidade_comercial/categorias/listar.html', context)


@login_required
def criar_categoria(request):
    """Cria uma nova categoria de produto"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            categoria = CategoriaProduto.objects.create(
                loja=loja,
                nome=request.POST.get('nome'),
                descricao=request.POST.get('descricao', ''),
                ativo=request.POST.get('ativo') == 'on'
            )
            
            messages.success(request, f'Categoria "{categoria.nome}" criada com sucesso!')
            return redirect('controle_qualidade_comercial:listar_categorias')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar categoria: {str(e)}')
    
    context = {
        'loja': loja,
    }
    
    return render(request, 'controle_qualidade_comercial/categorias/criar.html', context)


@login_required
def editar_categoria(request, categoria_id):
    """Edita uma categoria existente"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    categoria = get_object_or_404(CategoriaProduto, id=categoria_id, loja=loja)
    
    if request.method == 'POST':
        try:
            categoria.nome = request.POST.get('nome')
            categoria.descricao = request.POST.get('descricao', '')
            categoria.ativo = request.POST.get('ativo') == 'on'
            categoria.save()
            
            messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
            return redirect('controle_qualidade_comercial:listar_categorias')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar categoria: {str(e)}')
    
    context = {
        'loja': loja,
        'categoria': categoria,
    }
    
    return render(request, 'controle_qualidade_comercial/categorias/editar.html', context)


@login_required
def excluir_categoria(request, categoria_id):
    """Exclui uma categoria"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    categoria = get_object_or_404(CategoriaProduto, id=categoria_id, loja=loja)
    
    if request.method == 'POST':
        try:
            nome_categoria = categoria.nome
            categoria.delete()
            messages.success(request, f'Categoria "{nome_categoria}" excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir categoria: {str(e)}')
    
    return redirect('controle_qualidade_comercial:listar_categorias')


# =============================================================================
# VIEWS CRUD - FORNECEDORES
# =============================================================================

@login_required
def listar_fornecedores(request):
    """Lista todos os fornecedores"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    fornecedores = FornecedorComercial.objects.filter(loja=loja).order_by('nome')
    
    context = {
        'loja': loja,
        'fornecedores': fornecedores,
    }
    
    return render(request, 'controle_qualidade_comercial/fornecedores/listar.html', context)


@login_required
def criar_fornecedor(request):
    """Cria um novo fornecedor"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            fornecedor = FornecedorComercial.objects.create(
                loja=loja,
                nome=request.POST.get('nome'),
                cnpj=request.POST.get('cnpj', ''),
                email=request.POST.get('email', ''),
                telefone=request.POST.get('telefone', ''),
                endereco=request.POST.get('endereco', ''),
                contato_responsavel=request.POST.get('contato_responsavel', ''),
                ativo=request.POST.get('ativo') == 'on'
            )
            
            messages.success(request, f'Fornecedor "{fornecedor.nome}" criado com sucesso!')
            return redirect('controle_qualidade_comercial:listar_fornecedores')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar fornecedor: {str(e)}')
    
    context = {
        'loja': loja,
    }
    
    return render(request, 'controle_qualidade_comercial/fornecedores/criar.html', context)


@login_required
def editar_fornecedor(request, fornecedor_id):
    """Edita um fornecedor existente"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    fornecedor = get_object_or_404(FornecedorComercial, id=fornecedor_id, loja=loja)
    
    if request.method == 'POST':
        try:
            fornecedor.nome = request.POST.get('nome')
            fornecedor.cnpj = request.POST.get('cnpj', '')
            fornecedor.email = request.POST.get('email', '')
            fornecedor.telefone = request.POST.get('telefone', '')
            fornecedor.endereco = request.POST.get('endereco', '')
            fornecedor.contato_responsavel = request.POST.get('contato_responsavel', '')
            fornecedor.ativo = request.POST.get('ativo') == 'on'
            fornecedor.save()
            
            messages.success(request, f'Fornecedor "{fornecedor.nome}" atualizado com sucesso!')
            return redirect('controle_qualidade_comercial:listar_fornecedores')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar fornecedor: {str(e)}')
    
    context = {
        'loja': loja,
        'fornecedor': fornecedor,
    }
    
    return render(request, 'controle_qualidade_comercial/fornecedores/editar.html', context)


@login_required
def excluir_fornecedor(request, fornecedor_id):
    """Exclui um fornecedor"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    fornecedor = get_object_or_404(FornecedorComercial, id=fornecedor_id, loja=loja)
    
    if request.method == 'POST':
        try:
            nome_fornecedor = fornecedor.nome
            fornecedor.delete()
            messages.success(request, f'Fornecedor "{nome_fornecedor}" excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir fornecedor: {str(e)}')
    
    return redirect('controle_qualidade_comercial:listar_fornecedores')


# =============================================================================
# VIEWS DE RELATÓRIOS
# =============================================================================

@login_required
def relatorios_dashboard(request):
    """Dashboard de relatórios"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    context = {
        'loja': loja,
    }
    
    return render(request, 'controle_qualidade_comercial/relatorios/dashboard.html', context)


@login_required
def api_relatorio_vendas(request):
    """API para relatório de vendas"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    # Parâmetros de filtro
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    vendas = VendaComercial.objects.filter(loja=loja, status='concluida')
    
    if data_inicio:
        vendas = vendas.filter(created_at__date__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(created_at__date__lte=data_fim)
    
    # Estatísticas
    stats = vendas.aggregate(
        total_vendas=Count('id'),
        valor_total=Sum('valor_final'),
        ticket_medio=Avg('valor_final')
    )
    
    # Vendas por dia
    vendas_por_dia = vendas.extra(
        select={'data': 'DATE(created_at)'}
    ).values('data').annotate(
        total=Count('id'),
        valor=Sum('valor_final')
    ).order_by('data')
    
    return JsonResponse({
        'estatisticas': {
            'total_vendas': stats['total_vendas'] or 0,
            'valor_total': float(stats['valor_total'] or 0),
            'ticket_medio': float(stats['ticket_medio'] or 0)
        },
        'vendas_por_dia': list(vendas_por_dia)
    })


@login_required
def api_relatorio_qualidade(request):
    """API para relatório de qualidade"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    # Parâmetros de filtro
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    inspecoes = ControleQualidade.objects.filter(loja=loja)
    
    if data_inicio:
        inspecoes = inspecoes.filter(data_inspecao__gte=data_inicio)
    if data_fim:
        inspecoes = inspecoes.filter(data_inspecao__lte=data_fim)
    
    # Estatísticas
    stats = inspecoes.aggregate(
        total_inspecoes=Count('id'),
        aprovados=Count('id', filter=Q(status_qualidade='aprovado')),
        reprovados=Count('id', filter=Q(status_qualidade='reprovado')),
        condicionais=Count('id', filter=Q(status_qualidade='condicional')),
        nota_media_aparencia=Avg('aparencia_visual'),
        nota_media_embalagem=Avg('integridade_embalagem'),
        nota_media_conformidade=Avg('conformidade_especificacao')
    )
    
    # Taxa de aprovação
    taxa_aprovacao = 0
    if stats['total_inspecoes'] > 0:
        taxa_aprovacao = (stats['aprovados'] / stats['total_inspecoes']) * 100
    
    return JsonResponse({
        'estatisticas': {
            'total_inspecoes': stats['total_inspecoes'] or 0,
            'aprovados': stats['aprovados'] or 0,
            'reprovados': stats['reprovados'] or 0,
            'condicionais': stats['condicionais'] or 0,
            'taxa_aprovacao': round(taxa_aprovacao, 1),
            'nota_media_aparencia': round(float(stats['nota_media_aparencia'] or 0), 1),
            'nota_media_embalagem': round(float(stats['nota_media_embalagem'] or 0), 1),
            'nota_media_conformidade': round(float(stats['nota_media_conformidade'] or 0), 1)
        }
    })


# =============================================================================
# VIEWS ADICIONAIS E UTILITÁRIAS
# =============================================================================

@login_required
def buscar_produtos_ajax(request):
    """Busca produtos via AJAX para autocomplete"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    termo = request.GET.get('q', '')
    
    if len(termo) < 2:
        return JsonResponse({'produtos': []})
    
    produtos = ProdutoComercial.objects.filter(
        loja=loja,
        ativo=True,
        nome__icontains=termo
    ).values('id', 'nome', 'sku', 'preco_venda')[:10]
    
    return JsonResponse({'produtos': list(produtos)})


@login_required
def buscar_vendas_ajax(request):
    """Busca vendas via AJAX para autocomplete"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    termo = request.GET.get('q', '')
    
    if len(termo) < 2:
        return JsonResponse({'vendas': []})
    
    vendas = VendaComercial.objects.filter(
        loja=loja,
        numero_venda__icontains=termo
    ).values('id', 'numero_venda', 'cliente_nome', 'valor_final')[:10]
    
    return JsonResponse({'vendas': list(vendas)})


@login_required
def estatisticas_gerais(request):
    """Página com estatísticas gerais do sistema"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    # Estatísticas de produtos
    produtos_stats = {
        'total': ProdutoComercial.objects.filter(loja=loja).count(),
        'ativos': ProdutoComercial.objects.filter(loja=loja, ativo=True).count(),
        'estoque_baixo': ProdutoComercial.objects.filter(
            loja=loja, 
            ativo=True,
            estoque_atual__lte=F('estoque_minimo')
        ).count(),
    }
    
    # Estatísticas de vendas (último mês)
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    vendas_stats = VendaComercial.objects.filter(
        loja=loja,
        created_at__gte=inicio_mes,
        status='concluida'
    ).aggregate(
        total_vendas=Count('id'),
        valor_total=Sum('valor_final'),
        ticket_medio=Avg('valor_final')
    )
    
    # Estatísticas de qualidade (último mês)
    qualidade_stats = ControleQualidade.objects.filter(
        loja=loja,
        data_inspecao__gte=inicio_mes.date()
    ).aggregate(
        total_inspecoes=Count('id'),
        aprovados=Count('id', filter=Q(status_qualidade='aprovado')),
        reprovados=Count('id', filter=Q(status_qualidade='reprovado')),
        nota_media=Avg('aparencia_visual')
    )
    
    # Estatísticas de reclamações (último mês)
    reclamacoes_stats = ReclamacaoCliente.objects.filter(
        loja=loja,
        created_at__gte=inicio_mes
    ).aggregate(
        total_reclamacoes=Count('id'),
        abertas=Count('id', filter=Q(status='aberta')),
        resolvidas=Count('id', filter=Q(status='resolvida')),
        satisfacao_media=Avg('satisfacao_cliente')
    )
    
    context = {
        'loja': loja,
        'produtos_stats': produtos_stats,
        'vendas_stats': vendas_stats,
        'qualidade_stats': qualidade_stats,
        'reclamacoes_stats': reclamacoes_stats,
    }
    
    return render(request, 'controle_qualidade_comercial/estatisticas.html', context)


@login_required
def exportar_dados(request):
    """Exporta dados do sistema em CSV"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    tipo_export = request.GET.get('tipo', 'produtos')
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{tipo_export}_{loja.nome}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if tipo_export == 'produtos':
        writer.writerow(['Nome', 'SKU', 'Categoria', 'Fornecedor', 'Preço Custo', 'Preço Venda', 'Estoque Atual', 'Estoque Mínimo', 'Ativo'])
        
        produtos = ProdutoComercial.objects.filter(loja=loja).select_related('categoria', 'fornecedor')
        for produto in produtos:
            writer.writerow([
                produto.nome,
                produto.sku,
                produto.categoria.nome if produto.categoria else '',
                produto.fornecedor.nome if produto.fornecedor else '',
                produto.preco_custo,
                produto.preco_venda,
                produto.estoque_atual,
                produto.estoque_minimo,
                'Sim' if produto.ativo else 'Não'
            ])
    
    elif tipo_export == 'vendas':
        writer.writerow(['Número Venda', 'Data', 'Cliente', 'Vendedor', 'Valor Total', 'Desconto', 'Valor Final', 'Forma Pagamento', 'Status'])
        
        vendas = VendaComercial.objects.filter(loja=loja).select_related('vendedor')
        for venda in vendas:
            writer.writerow([
                venda.numero_venda,
                venda.created_at.strftime('%d/%m/%Y %H:%M'),
                venda.cliente_nome,
                venda.vendedor.get_full_name() if venda.vendedor else '',
                venda.valor_total,
                venda.desconto,
                venda.valor_final,
                venda.get_forma_pagamento_display(),
                venda.get_status_display()
            ])
    
    elif tipo_export == 'qualidade':
        writer.writerow(['Produto', 'Data Inspeção', 'Inspetor', 'Status', 'Aparência', 'Embalagem', 'Conformidade', 'Nota Geral'])
        
        inspecoes = ControleQualidade.objects.filter(loja=loja).select_related('produto', 'inspetor')
        for inspecao in inspecoes:
            writer.writerow([
                inspecao.produto.nome,
                inspecao.data_inspecao.strftime('%d/%m/%Y'),
                inspecao.inspetor.get_full_name() if inspecao.inspetor else '',
                inspecao.get_status_qualidade_display(),
                inspecao.aparencia_visual,
                inspecao.integridade_embalagem,
                inspecao.conformidade_especificacao,
                round(inspecao.nota_qualidade_geral, 1)
            ])
    
    elif tipo_export == 'reclamacoes':
        writer.writerow(['Protocolo', 'Data', 'Cliente', 'Tipo', 'Produto', 'Status', 'Prioridade', 'Satisfação'])
        
        reclamacoes = ReclamacaoCliente.objects.filter(loja=loja).select_related('produto')
        for reclamacao in reclamacoes:
            writer.writerow([
                reclamacao.numero_protocolo,
                reclamacao.created_at.strftime('%d/%m/%Y %H:%M'),
                reclamacao.cliente_nome,
                reclamacao.get_tipo_reclamacao_display(),
                reclamacao.produto.nome if reclamacao.produto else '',
                reclamacao.get_status_display(),
                reclamacao.get_prioridade_display(),
                reclamacao.satisfacao_cliente or ''
            ])
    
    return response


@login_required
def configuracoes_sistema(request):
    """Página de configurações do sistema"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard:index')
    except:
        messages.error(request, 'Loja não encontrada.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Aqui você pode implementar salvamento de configurações
        messages.success(request, 'Configurações salvas com sucesso!')
        return redirect('controle_qualidade_comercial:configuracoes_sistema')
    
    context = {
        'loja': loja,
    }
    
    return render(request, 'controle_qualidade_comercial/configuracoes.html', context)


@login_required
def backup_dados(request):
    """Gera backup dos dados do sistema"""
    
    try:
        loja = request.user.loja_admin
        if loja.tipo_loja.nome != 'dashboard_comercial':
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    except:
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    
    if request.method == 'POST':
        try:
            import json
            from django.core import serializers
            
            # Coletar todos os dados da loja
            dados_backup = {
                'loja_info': {
                    'nome': loja.nome,
                    'data_backup': timezone.now().isoformat()
                },
                'produtos': list(ProdutoComercial.objects.filter(loja=loja).values()),
                'categorias': list(CategoriaProduto.objects.filter(loja=loja).values()),
                'fornecedores': list(FornecedorComercial.objects.filter(loja=loja).values()),
                'vendas': list(VendaComercial.objects.filter(loja=loja).values()),
                'controle_qualidade': list(ControleQualidade.objects.filter(loja=loja).values()),
                'reclamacoes': list(ReclamacaoCliente.objects.filter(loja=loja).values()),
                'metas': list(MetaQualidade.objects.filter(loja=loja).values()),
            }
            
            # Converter UUIDs e datas para string
            def converter_dados(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, 'hex'):
                    return str(obj)
                return obj
            
            backup_json = json.dumps(dados_backup, default=converter_dados, indent=2)
            
            response = HttpResponse(backup_json, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="backup_{loja.nome}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            return response
            
        except Exception as e:
            return JsonResponse({'error': f'Erro ao gerar backup: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)