"""
Views otimizadas para configurações com cache e lazy loading
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import json
import logging

from .models import Loja
from .services.configuracao_service import ConfiguracaoService, ConfiguracaoTipoLojaService

logger = logging.getLogger(__name__)


@login_required
def gerenciar_configuracoes_otimizado(request, loja_id):
    """
    View principal otimizada para gerenciar configurações
    """
    loja = get_object_or_404(Loja, id=loja_id)
    
    # Verificar permissão
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'loja_admin') and str(request.user.loja_admin.id) == str(loja_id))):
        messages.error(request, 'Você não tem permissão para acessar esta loja.')
        return redirect('lojas:listar_lojas')
    
    # Usar service para obter configurações com cache
    configs = ConfiguracaoService.get_all_configs(str(loja_id))
    
    # Obter configurações específicas do tipo de loja
    tipo_loja = loja.tipo_loja.nome if loja.tipo_loja else 'padrao'
    config_tipo = ConfiguracaoTipoLojaService.get_config_by_type(str(loja_id), tipo_loja)
    
    context = {
        'loja': loja,
        'configs': configs,
        'config_tipo': config_tipo,
        'tipo_loja': tipo_loja,
        'performance_info': {
            'cache_hit': bool(cache.get(f"all_configs_{loja_id}")),
            'load_time': 'otimizado'
        }
    }
    
    return render(request, 'lojas/configuracoes/gerenciar_otimizado.html', context)


@login_required
@require_http_methods(["POST"])
def salvar_configuracao_ajax(request, loja_id):
    """
    Salva configuração via AJAX com otimização
    """
    try:
        config_type = request.POST.get('config_type')
        
        if not config_type:
            return JsonResponse({'success': False, 'error': 'Tipo de configuração não especificado'})
        
        # Preparar dados baseado no tipo
        data = {}
        
        if config_type == 'produto':
            data = {
                'campos_obrigatorios': request.POST.getlist('campos_obrigatorios'),
                'permite_preco_zero': request.POST.get('permite_preco_zero') == 'on',
                'controla_estoque': request.POST.get('controla_estoque') == 'on',
                'gera_codigo_automatico': request.POST.get('gera_codigo_automatico') == 'on',
                'prefixo_codigo': request.POST.get('prefixo_codigo', ''),
            }
            
            # Campos numéricos com validação
            try:
                if request.POST.get('preco_minimo'):
                    data['preco_minimo'] = float(request.POST.get('preco_minimo'))
                if request.POST.get('preco_maximo'):
                    data['preco_maximo'] = float(request.POST.get('preco_maximo'))
                if request.POST.get('estoque_minimo_padrao'):
                    data['estoque_minimo_padrao'] = int(request.POST.get('estoque_minimo_padrao'))
            except (ValueError, TypeError) as e:
                return JsonResponse({'success': False, 'error': f'Valor numérico inválido: {e}'})
        
        elif config_type == 'cliente':
            data = {
                'campos_obrigatorios': request.POST.getlist('campos_obrigatorios'),
                'exige_cpf_cnpj': request.POST.get('exige_cpf_cnpj') == 'on',
                'valida_cpf_cnpj': request.POST.get('valida_cpf_cnpj') == 'on',
                'exige_telefone': request.POST.get('exige_telefone') == 'on',
                'exige_email': request.POST.get('exige_email') == 'on',
                'usa_segmentacao': request.POST.get('usa_segmentacao') == 'on',
            }
        
        elif config_type == 'venda':
            data = {
                'numeracao_automatica': request.POST.get('numeracao_automatica') == 'on',
                'prefixo_numero': request.POST.get('prefixo_numero', ''),
                'permite_desconto': request.POST.get('permite_desconto') == 'on',
                'exige_cliente': request.POST.get('exige_cliente') == 'on',
                'baixa_estoque_automatica': request.POST.get('baixa_estoque_automatica') == 'on',
                'formas_pagamento_disponiveis': request.POST.getlist('formas_pagamento'),
            }
        
        elif config_type == 'dashboard':
            data = {
                'widgets_habilitados': request.POST.getlist('widgets_habilitados'),
                'layout_colunas': int(request.POST.get('layout_colunas', 3)),
                'periodo_padrao': request.POST.get('periodo_padrao', 'mes_atual'),
                'tema_cores': request.POST.get('tema_cores', 'padrao'),
                'metricas_principais': request.POST.getlist('metricas_principais'),
            }
        
        # Usar service para salvar com cache
        success = ConfiguracaoService.update_config(str(loja_id), config_type, data)
        
        if success:
            logger.info(f"Configuração {config_type} salva para loja {loja_id}")
            return JsonResponse({
                'success': True, 
                'message': f'Configurações de {config_type} salvas com sucesso!',
                'cache_cleared': True
            })
        else:
            return JsonResponse({'success': False, 'error': 'Erro ao salvar configurações'})
    
    except Exception as e:
        logger.error(f"Erro ao salvar configuração: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_config_summary(request, loja_id):
    """
    Retorna resumo das configurações (endpoint leve)
    """
    try:
        summary = ConfiguracaoService.get_config_summary(str(loja_id))
        return JsonResponse({'success': True, 'data': summary})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def warm_cache_configs(request, loja_id):
    """
    Pré-carrega cache das configurações (para admins)
    """
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Acesso negado'})
    
    try:
        ConfiguracaoService.warm_cache(str(loja_id))
        return JsonResponse({'success': True, 'message': 'Cache pré-carregado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@cache_page(60 * 15)  # Cache por 15 minutos
def get_default_configs_by_type(request, tipo_loja):
    """
    Retorna configurações padrão por tipo de loja (cached)
    """
    try:
        config = ConfiguracaoTipoLojaService._get_default_config_by_type(tipo_loja)
        return JsonResponse({'success': True, 'data': config})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
