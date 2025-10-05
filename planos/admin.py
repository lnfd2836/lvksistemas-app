from django.contrib import admin
from .models import PlanoComercial, AssinaturaLoja, HistoricoUso


@admin.register(PlanoComercial)
class PlanoComercialAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo', 'preco_mensal', 'preco_anual', 
        'max_usuarios_simultaneos', 'max_pdvs', 'status', 'destaque'
    ]
    list_filter = ['tipo', 'status', 'destaque']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem_exibicao', 'preco_mensal']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo', 'descricao', 'status', 'destaque', 'ordem_exibicao')
        }),
        ('Limites do Plano', {
            'fields': (
                'max_usuarios_simultaneos', 'max_pdvs', 'max_produtos', 
                'max_clientes', 'max_vendas_mes'
            )
        }),
        ('Recursos Incluídos', {
            'fields': (
                'backup_automatico', 'relatorios_avancados', 'integracao_api',
                'suporte_prioritario', 'customizacao_avancada'
            )
        }),
        ('Preços', {
            'fields': ('preco_mensal', 'preco_anual')
        }),
    )


@admin.register(AssinaturaLoja)
class AssinaturaLojaAdmin(admin.ModelAdmin):
    list_display = [
        'loja', 'plano', 'status', 'tipo_pagamento', 
        'data_inicio', 'data_vencimento', 'usuarios_online', 'pdvs_ativos'
    ]
    list_filter = ['status', 'tipo_pagamento', 'plano']
    search_fields = ['loja__nome', 'loja__cnpj']
    readonly_fields = ['data_inicio', 'data_atualizacao']
    
    fieldsets = (
        ('Assinatura', {
            'fields': ('loja', 'plano', 'status', 'tipo_pagamento')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_vencimento', 'data_cancelamento')
        }),
        ('Uso Atual', {
            'fields': (
                'usuarios_online', 'pdvs_ativos', 'vendas_mes_atual',
                'limite_usuarios_atingido', 'limite_pdvs_atingido', 'limite_vendas_atingido'
            )
        }),
    )


@admin.register(HistoricoUso)
class HistoricoUsoAdmin(admin.ModelAdmin):
    list_display = [
        'assinatura', 'tipo_evento', 'usuarios_online', 
        'pdvs_ativos', 'vendas_mes', 'data_evento'
    ]
    list_filter = ['tipo_evento', 'data_evento']
    search_fields = ['assinatura__loja__nome', 'descricao']
    readonly_fields = ['data_evento']
    ordering = ['-data_evento']




