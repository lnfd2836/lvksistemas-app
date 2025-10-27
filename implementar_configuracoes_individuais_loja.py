#!/usr/bin/env python
"""
Script para implementar configurações individuais por loja
- Configurações de Produto por loja
- Configurações de Cliente por loja  
- Configurações de Venda por loja
- Dashboard personalizado por loja
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def criar_models_configuracoes():
    """
    Cria os models para configurações individuais por loja
    """
    print("🔧 Criando models de configurações por loja...")
    
    models_path = 'lojas/models_configuracoes.py'
    
    models_content = '''"""
Models para configurações individuais por loja
"""
from django.db import models
from django.contrib.auth.models import User
from .models import Loja
import json


class ConfiguracaoProduto(models.Model):
    """Configurações específicas de produtos para cada loja"""
    
    loja = models.OneToOneField(
        Loja, 
        on_delete=models.CASCADE,
        related_name='config_produto'
    )
    
    # Campos obrigatórios
    campos_obrigatorios = models.JSONField(
        default=list,
        help_text="Lista de campos obrigatórios: ['nome', 'preco', 'categoria']"
    )
    
    # Categorias personalizadas
    categorias_personalizadas = models.JSONField(
        default=list,
        help_text="Categorias específicas desta loja"
    )
    
    # Configurações de preço
    permite_preco_zero = models.BooleanField(default=False)
    preco_minimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_maximo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Configurações de estoque
    controla_estoque = models.BooleanField(default=True)
    estoque_minimo_padrao = models.IntegerField(default=0)
    alerta_estoque_baixo = models.BooleanField(default=True)
    
    # Configurações de código
    gera_codigo_automatico = models.BooleanField(default=True)
    prefixo_codigo = models.CharField(max_length=10, blank=True)
    formato_codigo = models.CharField(
        max_length=50, 
        default="AUTO",
        help_text="AUTO, MANUAL, ou padrão personalizado"
    )
    
    # Campos personalizados
    campos_personalizados = models.JSONField(
        default=dict,
        help_text="Campos extras específicos desta loja"
    )
    
    # Configurações de exibição
    campos_listagem = models.JSONField(
        default=list,
        help_text="Campos a exibir na listagem de produtos"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Produto"
        verbose_name_plural = "Configurações de Produtos"
    
    def __str__(self):
        return f"Config Produtos - {self.loja.nome}"


class ConfiguracaoCliente(models.Model):
    """Configurações específicas de clientes para cada loja"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_cliente'
    )
    
    # Campos obrigatórios
    campos_obrigatorios = models.JSONField(
        default=list,
        help_text="Lista de campos obrigatórios: ['nome', 'telefone', 'email']"
    )
    
    # Configurações de documento
    exige_cpf_cnpj = models.BooleanField(default=False)
    valida_cpf_cnpj = models.BooleanField(default=True)
    permite_cpf_duplicado = models.BooleanField(default=False)
    
    # Configurações de contato
    exige_telefone = models.BooleanField(default=True)
    exige_email = models.BooleanField(default=False)
    exige_endereco = models.BooleanField(default=False)
    
    # Configurações de cadastro
    permite_auto_cadastro = models.BooleanField(default=True)
    aprova_automaticamente = models.BooleanField(default=True)
    
    # Campos personalizados
    campos_personalizados = models.JSONField(
        default=dict,
        help_text="Campos extras específicos desta loja"
    )
    
    # Configurações de segmentação
    usa_segmentacao = models.BooleanField(default=False)
    segmentos_disponiveis = models.JSONField(
        default=list,
        help_text="Segmentos de clientes: ['VIP', 'Regular', 'Novo']"
    )
    
    # Configurações de exibição
    campos_listagem = models.JSONField(
        default=list,
        help_text="Campos a exibir na listagem de clientes"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Cliente"
        verbose_name_plural = "Configurações de Clientes"
    
    def __str__(self):
        return f"Config Clientes - {self.loja.nome}"


class ConfiguracaoVenda(models.Model):
    """Configurações específicas de vendas para cada loja"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_venda'
    )
    
    # Configurações de numeração
    numeracao_automatica = models.BooleanField(default=True)
    prefixo_numero = models.CharField(max_length=10, blank=True)
    proximo_numero = models.IntegerField(default=1)
    
    # Configurações de desconto
    permite_desconto = models.BooleanField(default=True)
    desconto_maximo_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=10.00,
        help_text="Desconto máximo em %"
    )
    desconto_maximo_valor = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Desconto máximo em valor"
    )
    
    # Formas de pagamento
    formas_pagamento_disponiveis = models.JSONField(
        default=list,
        help_text="Formas de pagamento aceitas"
    )
    
    # Configurações de estoque
    baixa_estoque_automatica = models.BooleanField(default=True)
    permite_venda_sem_estoque = models.BooleanField(default=False)
    
    # Configurações de cliente
    exige_cliente = models.BooleanField(default=False)
    permite_cliente_generico = models.BooleanField(default=True)
    
    # Configurações de impressão
    imprime_automaticamente = models.BooleanField(default=False)
    modelo_impressao = models.CharField(
        max_length=50,
        default="padrao",
        choices=[
            ('padrao', 'Padrão'),
            ('termica', 'Térmica'),
            ('a4', 'A4'),
            ('personalizado', 'Personalizado')
        ]
    )
    
    # Campos personalizados
    campos_personalizados = models.JSONField(
        default=dict,
        help_text="Campos extras específicos desta loja"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Venda"
        verbose_name_plural = "Configurações de Vendas"
    
    def __str__(self):
        return f"Config Vendas - {self.loja.nome}"


class ConfiguracaoDashboard(models.Model):
    """Configurações do dashboard para cada loja"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_dashboard'
    )
    
    # Widgets habilitados
    widgets_habilitados = models.JSONField(
        default=list,
        help_text="Lista de widgets a exibir no dashboard"
    )
    
    # Layout do dashboard
    layout_colunas = models.IntegerField(
        default=3,
        choices=[(1, '1 Coluna'), (2, '2 Colunas'), (3, '3 Colunas'), (4, '4 Colunas')]
    )
    
    # Configurações de período
    periodo_padrao = models.CharField(
        max_length=20,
        default="mes_atual",
        choices=[
            ('hoje', 'Hoje'),
            ('semana_atual', 'Semana Atual'),
            ('mes_atual', 'Mês Atual'),
            ('trimestre_atual', 'Trimestre Atual'),
            ('ano_atual', 'Ano Atual'),
            ('personalizado', 'Personalizado')
        ]
    )
    
    # Métricas principais
    metricas_principais = models.JSONField(
        default=list,
        help_text="Métricas a destacar: ['vendas', 'clientes', 'produtos']"
    )
    
    # Gráficos habilitados
    graficos_habilitados = models.JSONField(
        default=list,
        help_text="Tipos de gráficos a exibir"
    )
    
    # Configurações de cores
    tema_cores = models.CharField(
        max_length=20,
        default="padrao",
        choices=[
            ('padrao', 'Padrão'),
            ('azul', 'Azul'),
            ('verde', 'Verde'),
            ('roxo', 'Roxo'),
            ('laranja', 'Laranja'),
            ('personalizado', 'Personalizado')
        ]
    )
    
    # Configurações personalizadas
    configuracoes_personalizadas = models.JSONField(
        default=dict,
        help_text="Configurações específicas desta loja"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Dashboard"
        verbose_name_plural = "Configurações de Dashboard"
    
    def __str__(self):
        return f"Config Dashboard - {self.loja.nome}"
'''
    
    try:
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(models_content)
        print("✅ Models de configurações criados")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar models: {e}")
        return False

def criar_admin_configuracoes():
    """
    Cria o admin para as configurações
    """
    print("🔧 Criando admin para configurações...")
    
    admin_path = 'lojas/admin_configuracoes.py'
    
    admin_content = '''"""
Admin para configurações individuais por loja
"""
from django.contrib import admin
from .models_configuracoes import (
    ConfiguracaoProduto, ConfiguracaoCliente, 
    ConfiguracaoVenda, ConfiguracaoDashboard
)


@admin.register(ConfiguracaoProduto)
class ConfiguracaoProdutoAdmin(admin.ModelAdmin):
    list_display = ['loja', 'controla_estoque', 'gera_codigo_automatico', 'data_atualizacao']
    list_filter = ['controla_estoque', 'gera_codigo_automatico', 'permite_preco_zero']
    search_fields = ['loja__nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Loja', {
            'fields': ('loja',)
        }),
        ('Campos Obrigatórios', {
            'fields': ('campos_obrigatorios', 'categorias_personalizadas')
        }),
        ('Configurações de Preço', {
            'fields': ('permite_preco_zero', 'preco_minimo', 'preco_maximo')
        }),
        ('Configurações de Estoque', {
            'fields': ('controla_estoque', 'estoque_minimo_padrao', 'alerta_estoque_baixo')
        }),
        ('Configurações de Código', {
            'fields': ('gera_codigo_automatico', 'prefixo_codigo', 'formato_codigo')
        }),
        ('Personalização', {
            'fields': ('campos_personalizados', 'campos_listagem')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )


@admin.register(ConfiguracaoCliente)
class ConfiguracaoClienteAdmin(admin.ModelAdmin):
    list_display = ['loja', 'exige_cpf_cnpj', 'exige_telefone', 'exige_email', 'data_atualizacao']
    list_filter = ['exige_cpf_cnpj', 'exige_telefone', 'exige_email', 'usa_segmentacao']
    search_fields = ['loja__nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']


@admin.register(ConfiguracaoVenda)
class ConfiguracaoVendaAdmin(admin.ModelAdmin):
    list_display = ['loja', 'numeracao_automatica', 'permite_desconto', 'exige_cliente', 'data_atualizacao']
    list_filter = ['numeracao_automatica', 'permite_desconto', 'exige_cliente', 'baixa_estoque_automatica']
    search_fields = ['loja__nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']


@admin.register(ConfiguracaoDashboard)
class ConfiguracaoDashboardAdmin(admin.ModelAdmin):
    list_display = ['loja', 'layout_colunas', 'periodo_padrao', 'tema_cores', 'data_atualizacao']
    list_filter = ['layout_colunas', 'periodo_padrao', 'tema_cores']
    search_fields = ['loja__nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']
'''
    
    try:
        with open(admin_path, 'w', encoding='utf-8') as f:
            f.write(admin_content)
        print("✅ Admin de configurações criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        return False

def criar_views_configuracoes():
    """
    Cria views para gerenciar configurações
    """
    print("🔧 Criando views para configurações...")
    
    views_path = 'lojas/views_configuracoes.py'
    
    views_content = '''"""
Views para gerenciar configurações individuais por loja
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import Loja
from .models_configuracoes import (
    ConfiguracaoProduto, ConfiguracaoCliente,
    ConfiguracaoVenda, ConfiguracaoDashboard
)


@login_required
def gerenciar_configuracoes_loja(request, loja_id):
    """View principal para gerenciar todas as configurações de uma loja"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    # Verificar permissão
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'loja_admin') and str(request.user.loja_admin.id) == str(loja_id))):
        messages.error(request, 'Você não tem permissão para acessar esta loja.')
        return redirect('lojas:listar_lojas')
    
    # Buscar ou criar configurações
    config_produto, _ = ConfiguracaoProduto.objects.get_or_create(loja=loja)
    config_cliente, _ = ConfiguracaoCliente.objects.get_or_create(loja=loja)
    config_venda, _ = ConfiguracaoVenda.objects.get_or_create(loja=loja)
    config_dashboard, _ = ConfiguracaoDashboard.objects.get_or_create(loja=loja)
    
    context = {
        'loja': loja,
        'config_produto': config_produto,
        'config_cliente': config_cliente,
        'config_venda': config_venda,
        'config_dashboard': config_dashboard,
    }
    
    return render(request, 'lojas/configuracoes/gerenciar.html', context)


@login_required
@require_http_methods(["POST"])
def salvar_configuracao_produto(request, loja_id):
    """Salva configurações de produto"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    config, _ = ConfiguracaoProduto.objects.get_or_create(loja=loja)
    
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
    config, _ = ConfiguracaoCliente.objects.get_or_create(loja=loja)
    
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
    config, _ = ConfiguracaoVenda.objects.get_or_create(loja=loja)
    
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
    config, _ = ConfiguracaoDashboard.objects.get_or_create(loja=loja)
    
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
    config, _ = ConfiguracaoDashboard.objects.get_or_create(loja=loja)
    
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
'''
    
    try:
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(views_content)
        print("✅ Views de configurações criadas")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar views: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 IMPLEMENTANDO CONFIGURAÇÕES INDIVIDUAIS POR LOJA")
    print("=" * 60)
    
    success_count = 0
    total_tasks = 3
    
    # 1. Criar models
    if criar_models_configuracoes():
        success_count += 1
    
    # 2. Criar admin
    if criar_admin_configuracoes():
        success_count += 1
    
    # 3. Criar views
    if criar_views_configuracoes():
        success_count += 1
    
    print("=" * 60)
    print(f"📊 RESULTADO: {success_count}/{total_tasks} tarefas concluídas")
    
    if success_count == total_tasks:
        print("🎉 IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Executar migrações: python manage.py makemigrations")
        print("2. Aplicar migrações: python manage.py migrate")
        print("3. Criar templates de configuração")
        print("4. Adicionar URLs")
        print("5. Testar funcionalidades")
    else:
        print("⚠️ ALGUMAS TAREFAS FALHARAM")
    
    print("=" * 60)

if __name__ == '__main__':
    main()