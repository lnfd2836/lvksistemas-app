from django.contrib import admin
from .models import PlanoFinanceiro, ControleFinanceiro, Pagamento, NotificacaoFinanceira, ConfiguracaoBoleto, BoletoGerado


@admin.register(PlanoFinanceiro)
class PlanoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'valor_mensal', 'dias_trial', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    ordering = ['valor_mensal']


@admin.register(ControleFinanceiro)
class ControleFinanceiroAdmin(admin.ModelAdmin):
    list_display = ['loja', 'plano', 'status', 'valor_mensal', 'data_vencimento', 'bloqueada']
    list_filter = ['status', 'bloqueada', 'plano', 'data_vencimento']
    search_fields = ['loja__nome', 'loja__cnpj']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['-data_vencimento']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('loja', 'plano', 'status')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_vencimento', 'data_bloqueio', 'data_ultimo_pagamento')
        }),
        ('Valores', {
            'fields': ('valor_mensal', 'valor_pago', 'valor_pendente')
        }),
        ('Controle de Acesso', {
            'fields': ('dias_grace_period', 'bloqueada', 'motivo_bloqueio')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'controle_financeiro', 'valor', 'status', 'metodo_pagamento', 'data_criacao']
    list_filter = ['status', 'metodo_pagamento', 'data_criacao']
    search_fields = ['controle_financeiro__loja__nome', 'id']
    readonly_fields = ['id', 'data_criacao']
    ordering = ['-data_criacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'controle_financeiro', 'valor', 'status')
        }),
        ('Dados do Pagamento', {
            'fields': ('metodo_pagamento', 'dados_pagamento')
        }),
        ('Controle', {
            'fields': ('data_pagamento', 'data_aprovacao', 'aprovado_por')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        })
    )


@admin.register(NotificacaoFinanceira)
class NotificacaoFinanceiraAdmin(admin.ModelAdmin):
    list_display = ['controle_financeiro', 'tipo', 'titulo', 'enviada', 'data_criacao']
    list_filter = ['tipo', 'enviada', 'data_criacao']
    search_fields = ['controle_financeiro__loja__nome', 'titulo']
    readonly_fields = ['data_criacao']
    ordering = ['-data_criacao']


@admin.register(ConfiguracaoBoleto)
class ConfiguracaoBoletoAdmin(admin.ModelAdmin):
    list_display = ['nome_banco', 'nome_beneficiario', 'agencia', 'conta', 'ativo']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome_banco', 'nome_beneficiario', 'cnpj_beneficiario']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
            ('Dados do Banco', {
                'fields': ('nome_banco', 'codigo_banco', 'agencia', 'conta', 'carteira', 'codigo_cedente')
            }),
        ('Dados do Beneficiário', {
            'fields': ('nome_beneficiario', 'cnpj_beneficiario', 'endereco_beneficiario')
        }),
        ('Configurações', {
            'fields': ('instrucoes', 'multa', 'juros', 'desconto')
        }),
        ('Controle', {
            'fields': ('ativo',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )


@admin.register(BoletoGerado)
class BoletoGeradoAdmin(admin.ModelAdmin):
    list_display = ['numero_boleto', 'controle_financeiro', 'valor', 'status', 'data_vencimento']
    list_filter = ['status', 'data_vencimento', 'data_criacao']
    search_fields = ['numero_boleto', 'controle_financeiro__loja__nome', 'linha_digitavel']
    readonly_fields = ['data_criacao']
    ordering = ['-data_criacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('controle_financeiro', 'configuracao', 'numero_boleto', 'status')
        }),
        ('Dados do Boleto', {
            'fields': ('linha_digitavel', 'codigo_barras')
        }),
        ('Valores e Datas', {
            'fields': ('valor', 'data_vencimento', 'data_pagamento')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        })
    )
