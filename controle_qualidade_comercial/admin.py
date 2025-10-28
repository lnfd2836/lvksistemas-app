from django.contrib import admin
from .models import (
    CategoriaProduto, FornecedorComercial, ProdutoComercial, 
    VendaComercial, ItemVenda, ControleQualidade, 
    ReclamacaoCliente, MetaQualidade
)


@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'loja', 'ativo', 'created_at']
    list_filter = ['loja', 'ativo', 'created_at']
    search_fields = ['nome', 'loja__nome']
    ordering = ['loja', 'nome']


@admin.register(FornecedorComercial)
class FornecedorComercialAdmin(admin.ModelAdmin):
    list_display = ['nome', 'loja', 'cnpj', 'email', 'ativo', 'created_at']
    list_filter = ['loja', 'ativo', 'created_at']
    search_fields = ['nome', 'cnpj', 'email', 'loja__nome']
    ordering = ['loja', 'nome']


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(ProdutoComercial)
class ProdutoComercialAdmin(admin.ModelAdmin):
    list_display = ['nome', 'loja', 'sku', 'categoria', 'fornecedor', 'estoque_atual', 'estoque_minimo', 'ativo']
    list_filter = ['loja', 'categoria', 'fornecedor', 'ativo', 'created_at']
    search_fields = ['nome', 'sku', 'codigo_barras', 'loja__nome']
    ordering = ['loja', 'nome']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('loja', 'categoria', 'fornecedor')


@admin.register(VendaComercial)
class VendaComercialAdmin(admin.ModelAdmin):
    list_display = ['numero_venda', 'loja', 'cliente_nome', 'valor_final', 'forma_pagamento', 'status', 'created_at']
    list_filter = ['loja', 'forma_pagamento', 'status', 'created_at']
    search_fields = ['numero_venda', 'cliente_nome', 'cliente_cpf', 'loja__nome']
    ordering = ['loja', '-created_at']
    inlines = [ItemVendaInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('loja', 'vendedor')


@admin.register(ControleQualidade)
class ControleQualidadeAdmin(admin.ModelAdmin):
    list_display = ['produto', 'loja', 'data_inspecao', 'status_qualidade', 'nota_qualidade_geral', 'inspetor']
    list_filter = ['loja', 'status_qualidade', 'data_inspecao', 'inspetor']
    search_fields = ['produto__nome', 'lote', 'loja__nome']
    ordering = ['loja', '-data_inspecao']
    date_hierarchy = 'data_inspecao'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('loja', 'produto', 'inspetor')


@admin.register(ReclamacaoCliente)
class ReclamacaoClienteAdmin(admin.ModelAdmin):
    list_display = ['numero_protocolo', 'loja', 'cliente_nome', 'tipo_reclamacao', 'status', 'prioridade', 'created_at']
    list_filter = ['loja', 'tipo_reclamacao', 'status', 'prioridade', 'created_at']
    search_fields = ['numero_protocolo', 'cliente_nome', 'cliente_email', 'loja__nome']
    ordering = ['loja', '-created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('loja', 'produto', 'venda', 'responsavel')


@admin.register(MetaQualidade)
class MetaQualidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'loja', 'tipo_meta', 'valor_meta', 'valor_atual', 'percentual_atingido', 'status']
    list_filter = ['loja', 'tipo_meta', 'status', 'created_at']
    search_fields = ['nome', 'loja__nome']
    ordering = ['loja', '-created_at']
    
    def percentual_atingido(self, obj):
        return f"{obj.percentual_atingido:.1f}%"
    percentual_atingido.short_description = "% Atingido"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('loja')