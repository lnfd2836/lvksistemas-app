"""
Views para gerenciar configurações individuais por loja
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import DatabaseError, ProgrammingError
import json
import logging

from .models import Loja
from .models_configuracoes import (
    ConfiguracaoProduto, ConfiguracaoCliente,
    ConfiguracaoVenda, ConfiguracaoDashboard
)

logger = logging.getLogger(__name__)


@login_required
def gerenciar_configuracoes_loja(request, loja_id):
    """View principal para gerenciar todas as configurações de uma loja"""
    
    try:
        loja = get_object_or_404(Loja, id=loja_id)
    except Exception as e:
        logger.error(f"Erro ao buscar loja {loja_id}: {str(e)}")
        messages.error(request, 'Loja não encontrada.')
        return redirect('lojas:listar_lojas')
    
    # Verificar permissão
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'loja_admin') and str(request.user.loja_admin.id) == str(loja_id))):
        messages.error(request, 'Você não tem permissão para acessar esta loja.')
        return redirect('lojas:listar_lojas')
    
    # Para simplificar, vamos usar o banco padrão por enquanto
    # TODO: Implementar isolamento completo de banco posteriormente
    
    # Buscar ou criar configurações (com tratamento de erro para tabelas ausentes)
    config_produto = None
    config_cliente = None
    config_venda = None
    config_dashboard = None
    
    try:
        config_produto, _ = ConfiguracaoProduto.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoProduto não existe para loja {loja.nome}: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar ConfiguracaoProduto para loja {loja.nome}: {str(e)}")
    
    try:
        config_cliente, _ = ConfiguracaoCliente.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoCliente não existe para loja {loja.nome}: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar ConfiguracaoCliente para loja {loja.nome}: {str(e)}")
    
    try:
        config_venda, _ = ConfiguracaoVenda.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoVenda não existe para loja {loja.nome}: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar ConfiguracaoVenda para loja {loja.nome}: {str(e)}")
    
    try:
        config_dashboard, _ = ConfiguracaoDashboard.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoDashboard não existe para loja {loja.nome}: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar ConfiguracaoDashboard para loja {loja.nome}: {str(e)}")
    
    context = {
        'loja': loja,
        'config_produto': config_produto,
        'config_cliente': config_cliente,
        'config_venda': config_venda,
        'config_dashboard': config_dashboard,
    }
    
    try:
        return render(request, 'lojas/configuracoes/gerenciar.html', context)
    except Exception as e:
        logger.error(f"Erro ao renderizar template de configurações: {str(e)}")
        # Fallback para template mais simples se o específico não existir
        try:
            return render(request, 'lojas/configuracoes.html', context)
        except Exception:
            messages.error(request, 'Página de configurações não disponível no momento.')
            return redirect('lojas:detalhar_loja', loja_id=loja_id)


@login_required
@require_http_methods(["POST"])
def salvar_configuracao_produto(request, loja_id):
    """Salva configurações de produto"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    try:
        config, _ = ConfiguracaoProduto.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoProduto não existe para loja {loja.nome}: {str(e)}")
        messages.error(request, 'As configurações de produto não estão disponíveis no momento.')
        return redirect('lojas:configuracoes', loja_id=loja_id)
    
    try:
        # Atualizar configurações
        config.campos_obrigatorios = request.POST.getlist('campos_obrigatorios')
        config.categorias_personalizadas = request.POST.get('categorias_personalizadas', '').split(',')
        config.permite_preco_zero = request.POST.get('permite_preco_zero') == 'on'
        config.controla_estoque = request.POST.get('controla_estoque') == 'on'
        config.gera_codigo_automatico = request.POST.get('gera_codigo_automatico') == 'on'
        config.prefixo_codigo = request.POST.get('prefixo_codigo', '')
        
        # Campos numéricos
        preco_minimo = request.POST.get('preco_minimo')
        if preco_minimo:
            config.preco_minimo = float(preco_minimo)
        
        preco_maximo = request.POST.get('preco_maximo')
        if preco_maximo:
            config.preco_maximo = float(preco_maximo)
        
        estoque_minimo = request.POST.get('estoque_minimo_padrao')
        if estoque_minimo:
            config.estoque_minimo_padrao = int(estoque_minimo)
        
        config.save()
        
        messages.success(request, 'Configurações de produto salvas com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao salvar configurações: {str(e)}')
    
    return redirect('lojas:configuracoes', loja_id=loja_id)


@login_required
@require_http_methods(["POST"])
def salvar_configuracao_cliente(request, loja_id):
    """Salva configurações de cliente"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    try:
        config, _ = ConfiguracaoCliente.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoCliente não existe para loja {loja.nome}: {str(e)}")
        messages.error(request, 'As configurações de cliente não estão disponíveis no momento.')
        return redirect('lojas:configuracoes', loja_id=loja_id)
    
    try:
        config.campos_obrigatorios = request.POST.getlist('campos_obrigatorios')
        config.exige_cpf_cnpj = request.POST.get('exige_cpf_cnpj') == 'on'
        config.valida_cpf_cnpj = request.POST.get('valida_cpf_cnpj') == 'on'
        config.exige_telefone = request.POST.get('exige_telefone') == 'on'
        config.exige_email = request.POST.get('exige_email') == 'on'
        config.exige_endereco = request.POST.get('exige_endereco') == 'on'
        config.usa_segmentacao = request.POST.get('usa_segmentacao') == 'on'
        
        segmentos = request.POST.get('segmentos_disponiveis', '')
        if segmentos:
            config.segmentos_disponiveis = segmentos.split(',')
        
        config.save()
        
        messages.success(request, 'Configurações de cliente salvas com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao salvar configurações: {str(e)}')
    
    return redirect('lojas:configuracoes', loja_id=loja_id)


@login_required
@require_http_methods(["POST"])
def salvar_configuracao_venda(request, loja_id):
    """Salva configurações de venda"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    try:
        config, _ = ConfiguracaoVenda.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoVenda não existe para loja {loja.nome}: {str(e)}")
        messages.error(request, 'As configurações de venda não estão disponíveis no momento.')
        return redirect('lojas:configuracoes', loja_id=loja_id)
    
    try:
        config.numeracao_automatica = request.POST.get('numeracao_automatica') == 'on'
        config.prefixo_numero = request.POST.get('prefixo_numero', '')
        config.permite_desconto = request.POST.get('permite_desconto') == 'on'
        config.exige_cliente = request.POST.get('exige_cliente') == 'on'
        config.baixa_estoque_automatica = request.POST.get('baixa_estoque_automatica') == 'on'
        
        # Campos numéricos
        desconto_max = request.POST.get('desconto_maximo_percentual')
        if desconto_max:
            config.desconto_maximo_percentual = float(desconto_max)
        
        # Formas de pagamento
        formas_pagamento = request.POST.getlist('formas_pagamento')
        config.formas_pagamento_disponiveis = formas_pagamento
        
        config.save()
        
        messages.success(request, 'Configurações de venda salvas com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao salvar configurações: {str(e)}')
    
    return redirect('lojas:configuracoes', loja_id=loja_id)


@login_required
@require_http_methods(["POST"])
def salvar_configuracao_dashboard(request, loja_id):
    """Salva configurações de dashboard"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    try:
        config, _ = ConfiguracaoDashboard.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoDashboard não existe para loja {loja.nome}: {str(e)}")
        messages.error(request, 'As configurações de dashboard não estão disponíveis no momento.')
        return redirect('lojas:configuracoes', loja_id=loja_id)
    
    try:
        config.widgets_habilitados = request.POST.getlist('widgets_habilitados')
        config.layout_colunas = int(request.POST.get('layout_colunas', 3))
        config.periodo_padrao = request.POST.get('periodo_padrao', 'mes_atual')
        config.tema_cores = request.POST.get('tema_cores', 'padrao')
        config.metricas_principais = request.POST.getlist('metricas_principais')
        config.graficos_habilitados = request.POST.getlist('graficos_habilitados')
        
        config.save()
        
        messages.success(request, 'Configurações de dashboard salvas com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao salvar configurações: {str(e)}')
    
    return redirect('lojas:configuracoes', loja_id=loja_id)


@login_required
def preview_dashboard(request, loja_id):
    """Preview do dashboard com as configurações atuais"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    try:
        config, _ = ConfiguracaoDashboard.objects.get_or_create(loja=loja)
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela ConfiguracaoDashboard não existe para loja {loja.nome}: {str(e)}")
        messages.error(request, 'As configurações de dashboard não estão disponíveis no momento.')
        return redirect('lojas:configuracoes', loja_id=loja_id)
    
    # Dados simulados para preview
    dados_preview = {
        'vendas_hoje': 1250.00,
        'vendas_mes': 35000.00,
        'clientes_novos': 15,
        'produtos_cadastrados': 120,
    }
    
    context = {
        'loja': loja,
        'config': config,
        'dados': dados_preview,
        'is_preview': True,
    }
    
    return render(request, 'lojas/configuracoes/preview_dashboard.html', context)
