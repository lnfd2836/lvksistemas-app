from django.contrib import admin
from .models import TipoLoja, ModuloLoja, CampoPersonalizado, ValorCampoPersonalizado


@admin.register(TipoLoja)
class TipoLojaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_criacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'icone', 'cor_primaria', 'cor_secundaria'),
            'classes': ('wide',)
        }),
        ('Configurações de Produto', {
            'fields': (
                ('tem_categoria_produto', 'tem_marca_produto', 'tem_tamanho_produto'),
                ('tem_cor_produto', 'tem_peso_produto', 'tem_volume_produto'),
                ('tem_data_validade', 'tem_codigo_barras', 'tem_estoque_minimo')
            ),
            'classes': ('wide', 'collapse'),
            'description': 'Configure quais campos de produto estarão disponíveis para este tipo de loja'
        }),
        ('Configurações de Cliente', {
            'fields': (
                ('tem_data_nascimento_cliente', 'tem_sexo_cliente', 'tem_cpf_cliente'),
                ('tem_rg_cliente', 'tem_cnpj_cliente')
            ),
            'classes': ('wide', 'collapse'),
            'description': 'Configure quais campos de cliente estarão disponíveis para este tipo de loja'
        }),
        ('Configurações de Venda', {
            'fields': (
                ('tem_desconto_venda', 'tem_taxa_entrega'),
                ('tem_mesa_venda', 'tem_garcom_venda')
            ),
            'classes': ('wide', 'collapse'),
            'description': 'Configure quais funcionalidades de venda estarão disponíveis para este tipo de loja'
        }),
        ('Status', {
            'fields': ('ativo',),
            'classes': ('wide',)
        })
    )


@admin.register(ModuloLoja)
class ModuloLojaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo_loja', 'url', 'ordem', 'ativo']
    list_filter = ['tipo_loja', 'ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['tipo_loja', 'ordem']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'tipo_loja', 'icone')
        }),
        ('Configurações de Navegação', {
            'fields': ('url', 'ordem', 'ativo'),
            'description': 'Configure como este módulo aparecerá no dashboard da loja'
        })
    )


@admin.register(CampoPersonalizado)
class CampoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo_loja', 'tipo_campo', 'obrigatorio', 'ordem', 'ativo']
    list_filter = ['tipo_loja', 'tipo_campo', 'obrigatorio', 'ativo']
    search_fields = ['nome', 'slug']
    ordering = ['tipo_loja', 'ordem']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'tipo_loja', 'descricao')
        }),
        ('Configurações do Campo', {
            'fields': ('tipo_campo', 'obrigatorio', 'opcoes', 'placeholder', 'ajuda_texto'),
            'description': 'Configure as propriedades do campo personalizado'
        }),
        ('Exibição', {
            'fields': ('ordem', 'ativo'),
            'description': 'Configure como este campo será exibido nos formulários'
        })
    )


@admin.register(ValorCampoPersonalizado)
class ValorCampoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'campo', 'valor', 'data_atualizacao']
    list_filter = ['campo__tipo_loja', 'data_criacao']
    search_fields = ['produto__nome', 'campo__nome', 'valor']
    readonly_fields = ['data_criacao', 'data_atualizacao']
