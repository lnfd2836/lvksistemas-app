"""
Admin para CRM de Vendas
"""
from django.contrib import admin
from .models import Lead, Orcamento, ItemOrcamento, Proposta, Contrato, HistoricoContato, EmailLog


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['nome', 'empresa', 'email', 'status', 'responsavel', 'valor_estimado', 'data_criacao']
    list_filter = ['status', 'origem', 'loja', 'responsavel']
    search_fields = ['nome', 'email', 'empresa']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Dados Básicos', {
            'fields': ('nome', 'email', 'telefone', 'empresa', 'cargo')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep'),
            'classes': ('collapse',)
        }),
        ('Controle Comercial', {
            'fields': ('status', 'origem', 'responsavel', 'loja')
        }),
        ('Dados Comerciais', {
            'fields': ('valor_estimado', 'probabilidade')
        }),
        ('Observações', {
            'fields': ('observacoes', 'tags')
        }),
        ('Datas', {
            'fields': ('data_ultimo_contato', 'data_proximo_contato', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )


class ItemOrcamentoInline(admin.TabularInline):
    model = ItemOrcamento
    extra = 1


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'titulo', 'lead', 'total', 'status', 'data_criacao']
    list_filter = ['status', 'loja', 'responsavel']
    search_fields = ['numero', 'titulo', 'lead__nome']
    readonly_fields = ['numero', 'data_criacao', 'data_atualizacao']
    inlines = [ItemOrcamentoInline]


@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'titulo', 'lead', 'valor_total', 'status', 'data_criacao']
    list_filter = ['status', 'loja']
    search_fields = ['numero', 'titulo', 'lead__nome']


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'titulo', 'lead', 'valor_total', 'status', 'data_inicio', 'data_fim']
    list_filter = ['status', 'loja']
    search_fields = ['numero', 'titulo', 'lead__nome']


@admin.register(HistoricoContato)
class HistoricoContatoAdmin(admin.ModelAdmin):
    list_display = ['lead', 'tipo', 'assunto', 'usuario', 'data_contato']
    list_filter = ['tipo', 'data_contato']
    search_fields = ['lead__nome', 'assunto']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['destinatario', 'assunto', 'status', 'data_envio', 'data_abertura']
    list_filter = ['status', 'data_envio']
    search_fields = ['destinatario', 'assunto']
    readonly_fields = ['token_rastreamento', 'data_envio']
