"""
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
