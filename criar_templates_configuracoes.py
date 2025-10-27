#!/usr/bin/env python
"""
Script para criar templates das configurações individuais por loja
"""

import os

def criar_template_gerenciar():
    """
    Cria o template principal para gerenciar configurações
    """
    print("🔧 Criando template de gerenciamento...")
    
    template_dir = 'templates/lojas/configuracoes'
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = f'{template_dir}/gerenciar.html'
    
    template_content = '''{% extends 'base.html' %}
{% load widget_tweaks %}

{% block title %}Configurações - {{ loja.nome }}{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-cogs me-2"></i>
                        Configurações da Loja: {{ loja.nome }}
                    </h3>
                    <div class="card-tools">
                        <a href="{% url 'lojas:detalhar_loja' loja.id %}" class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-arrow-left me-1"></i>Voltar
                        </a>
                    </div>
                </div>
                <div class="card-body">
                    <!-- Navegação por abas -->
                    <ul class="nav nav-tabs" id="configTabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="produto-tab" data-bs-toggle="tab" 
                                    data-bs-target="#produto" type="button" role="tab">
                                <i class="fas fa-box me-1"></i>Produtos
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="cliente-tab" data-bs-toggle="tab" 
                                    data-bs-target="#cliente" type="button" role="tab">
                                <i class="fas fa-users me-1"></i>Clientes
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="venda-tab" data-bs-toggle="tab" 
                                    data-bs-target="#venda" type="button" role="tab">
                                <i class="fas fa-shopping-cart me-1"></i>Vendas
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="dashboard-tab" data-bs-toggle="tab" 
                                    data-bs-target="#dashboard" type="button" role="tab">
                                <i class="fas fa-chart-bar me-1"></i>Dashboard
                            </button>
                        </li>
                    </ul>
                    
                    <!-- Conteúdo das abas -->
                    <div class="tab-content mt-3" id="configTabsContent">
                        <!-- Configurações de Produto -->
                        <div class="tab-pane fade show active" id="produto" role="tabpanel">
                            {% include 'lojas/configuracoes/produto.html' %}
                        </div>
                        
                        <!-- Configurações de Cliente -->
                        <div class="tab-pane fade" id="cliente" role="tabpanel">
                            {% include 'lojas/configuracoes/cliente.html' %}
                        </div>
                        
                        <!-- Configurações de Venda -->
                        <div class="tab-pane fade" id="venda" role="tabpanel">
                            {% include 'lojas/configuracoes/venda.html' %}
                        </div>
                        
                        <!-- Configurações de Dashboard -->
                        <div class="tab-pane fade" id="dashboard" role="tabpanel">
                            {% include 'lojas/configuracoes/dashboard.html' %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
$(document).ready(function() {
    // Salvar configurações via AJAX
    $('.config-form').on('submit', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();
        
        $.post(url, data)
            .done(function(response) {
                toastr.success('Configurações salvas com sucesso!');
            })
            .fail(function() {
                toastr.error('Erro ao salvar configurações.');
            });
    });
});
</script>
{% endblock %}'''
    
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print("✅ Template de gerenciamento criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar template: {e}")
        return False

def criar_template_produto():
    """
    Cria o template de configurações de produto
    """
    print("🔧 Criando template de configurações de produto...")
    
    template_path = 'templates/lojas/configuracoes/produto.html'
    
    template_content = '''<form method="post" action="{% url 'lojas:salvar_config_produto' loja.id %}" class="config-form">
    {% csrf_token %}
    
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title">Campos Obrigatórios</h5>
                </div>
                <div class="card-body">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="campos_obrigatorios" 
                               value="nome" id="campo_nome" 
                               {% if 'nome' in config_produto.campos_obrigatorios %}checked{% endif %}>
                        <label class="form-check-label" for="campo_nome">Nome do Produto</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="campos_obrigatorios" 
                               value="preco" id="campo_preco"
                               {% if 'preco' in config_produto.campos_obrigatorios %}checked{% endif %}>
                        <label class="form-check-label" for="campo_preco">Preço</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="campos_obrigatorios" 
                               value="categoria" id="campo_categoria"
                               {% if 'categoria' in config_produto.campos_obrigatorios %}checked{% endif %}>
                        <label class="form-check-label" for="campo_categoria">Categoria</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="campos_obrigatorios" 
                               value="codigo" id="campo_codigo"
                               {% if 'codigo' in config_produto.campos_obrigatorios %}checked{% endif %}>
                        <label class="form-check-label" for="campo_codigo">Código</label>
                    </div>
                </div>
            </div>
            
            <div class="card mt-3">
                <div class="card-header">
                    <h5 class="card-title">Configurações de Preço</h5>
                </div>
                <div class="card-body">
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" name="permite_preco_zero" 
                               id="permite_preco_zero" {% if config_produto.permite_preco_zero %}checked{% endif %}>
                        <label class="form-check-label" for="permite_preco_zero">
                            Permitir preço zero
                        </label>
                    </div>
                    
                    <div class="mb-3">
                        <label for="preco_minimo" class="form-label">Preço Mínimo</label>
                        <input type="number" class="form-control" name="preco_minimo" 
                               id="preco_minimo" step="0.01" 
                               value="{{ config_produto.preco_minimo|default:'' }}">
                    </div>
                    
                    <div class="mb-3">
                        <label for="preco_maximo" class="form-label">Preço Máximo</label>
                        <input type="number" class="form-control" name="preco_maximo" 
                               id="preco_maximo" step="0.01"
                               value="{{ config_produto.preco_maximo|default:'' }}">
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title">Configurações de Estoque</h5>
                </div>
                <div class="card-body">
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" name="controla_estoque" 
                               id="controla_estoque" {% if config_produto.controla_estoque %}checked{% endif %}>
                        <label class="form-check-label" for="controla_estoque">
                            Controlar estoque
                        </label>
                    </div>
                    
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" name="alerta_estoque_baixo" 
                               id="alerta_estoque_baixo" {% if config_produto.alerta_estoque_baixo %}checked{% endif %}>
                        <label class="form-check-label" for="alerta_estoque_baixo">
                            Alertar estoque baixo
                        </label>
                    </div>
                    
                    <div class="mb-3">
                        <label for="estoque_minimo_padrao" class="form-label">Estoque Mínimo Padrão</label>
                        <input type="number" class="form-control" name="estoque_minimo_padrao" 
                               id="estoque_minimo_padrao" 
                               value="{{ config_produto.estoque_minimo_padrao }}">
                    </div>
                </div>
            </div>
            
            <div class="card mt-3">
                <div class="card-header">
                    <h5 class="card-title">Configurações de Código</h5>
                </div>
                <div class="card-body">
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" name="gera_codigo_automatico" 
                               id="gera_codigo_automatico" {% if config_produto.gera_codigo_automatico %}checked{% endif %}>
                        <label class="form-check-label" for="gera_codigo_automatico">
                            Gerar código automaticamente
                        </label>
                    </div>
                    
                    <div class="mb-3">
                        <label for="prefixo_codigo" class="form-label">Prefixo do Código</label>
                        <input type="text" class="form-control" name="prefixo_codigo" 
                               id="prefixo_codigo" maxlength="10"
                               value="{{ config_produto.prefixo_codigo }}">
                        <div class="form-text">Ex: PROD, ITEM, etc.</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-3">
        <div class="col-12">
            <button type="submit" class="btn btn-primary">
                <i class="fas fa-save me-1"></i>Salvar Configurações de Produto
            </button>
        </div>
    </div>
</form>'''
    
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print("✅ Template de configurações de produto criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar template: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 CRIANDO TEMPLATES DE CONFIGURAÇÕES")
    print("=" * 60)
    
    success_count = 0
    total_tasks = 2
    
    # 1. Template principal
    if criar_template_gerenciar():
        success_count += 1
    
    # 2. Template de produto
    if criar_template_produto():
        success_count += 1
    
    print("=" * 60)
    print(f"📊 RESULTADO: {success_count}/{total_tasks} templates criados")
    
    if success_count == total_tasks:
        print("✅ Templates básicos criados com sucesso!")
        print("📋 Ainda faltam criar:")
        print("- Template de configurações de cliente")
        print("- Template de configurações de venda") 
        print("- Template de configurações de dashboard")
    
    print("=" * 60)

if __name__ == '__main__':
    main()