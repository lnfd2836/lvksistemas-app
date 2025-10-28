from django.contrib import admin
from .models import (
    TipoLoja, ModuloLoja, CampoPersonalizado, ValorCampoPersonalizado,
    ServicoEstetica, ProtocoloEmagrecimento, Agendamento, Retorno,
    FichaAnamnese, EvolucaoTratamento, PacoteTratamento
)


@admin.register(TipoLoja)
class TipoLojaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_criacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Aparência', {
            'fields': ('icone', 'cor_primaria', 'cor_secundaria'),
            'description': 'Configure a aparência visual do tipo de loja'
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Editando
            readonly.append('nome')  # Não permitir alterar o nome após criação
        return readonly


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


# =============================================================================
# ADMIN PARA MODELOS DE CLÍNICA DE ESTÉTICA
# =============================================================================

@admin.register(ServicoEstetica)
class ServicoEsteticaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'duracao_minutos', 'preco', 'preco_promocional', 'ativo']
    list_filter = ['categoria', 'requer_consulta_medica', 'ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    ordering = ['categoria', 'nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'categoria', 'ativo')
        }),
        ('Configurações', {
            'fields': ('duracao_minutos', 'preco', 'preco_promocional')
        }),
        ('Requisitos', {
            'fields': ('requer_consulta_medica', 'idade_minima', 'contraindicacoes', 'cuidados_pos_procedimento')
        })
    )


@admin.register(ProtocoloEmagrecimento)
class ProtocoloEmagrecimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo_protocolo', 'numero_sessoes', 'preco_total', 'ativo']
    list_filter = ['tipo_protocolo', 'ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'tipo_protocolo', 'ativo')
        }),
        ('Configurações do Protocolo', {
            'fields': ('numero_sessoes', 'intervalo_dias', 'duracao_sessao_minutos', 'preco_total', 'preco_sessao')
        }),
        ('Informações Médicas', {
            'fields': ('indicacoes', 'contraindicacoes', 'resultados_esperados')
        })
    )


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'servico', 'data_agendamento', 'hora_inicio', 'profissional', 'status']
    list_filter = ['status', 'data_agendamento', 'profissional', 'servico__categoria']
    search_fields = ['cliente__nome', 'servico__nome', 'observacoes']
    ordering = ['-data_agendamento', '-hora_inicio']
    date_hierarchy = 'data_agendamento'
    
    fieldsets = (
        ('Informações do Agendamento', {
            'fields': ('cliente', 'servico', 'protocolo', 'data_agendamento', 'hora_inicio', 'hora_fim')
        }),
        ('Profissional e Status', {
            'fields': ('profissional', 'status')
        }),
        ('Observações', {
            'fields': ('observacoes', 'observacoes_pos_procedimento')
        })
    )


@admin.register(Retorno)
class RetornoAdmin(admin.ModelAdmin):
    list_display = ['agendamento_original', 'tipo_retorno', 'data_retorno', 'hora_retorno']
    list_filter = ['tipo_retorno', 'data_retorno', 'data_criacao']
    search_fields = ['agendamento_original__cliente__nome', 'motivo_retorno']
    ordering = ['-data_retorno', '-hora_retorno']
    date_hierarchy = 'data_retorno'


@admin.register(FichaAnamnese)
class FichaAnamneseAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_pele', 'problemas_circulatorios', 'diabetes', 'hipertensao', 'gravidez']
    list_filter = ['tipo_pele', 'problemas_circulatorios', 'diabetes', 'hipertensao', 'gravidez', 'amamentacao']
    search_fields = ['cliente__nome', 'alergias', 'medicamentos_uso']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações do Cliente', {
            'fields': ('cliente',)
        }),
        ('Dados da Pele', {
            'fields': ('tipo_pele', 'alergias', 'medicamentos_uso', 'tratamentos_anteriores')
        }),
        ('Histórico Médico', {
            'fields': ('problemas_circulatorios', 'diabetes', 'hipertensao', 'gravidez', 'amamentacao')
        }),
        ('Objetivos', {
            'fields': ('objetivos_tratamento', 'expectativas')
        })
    )


@admin.register(EvolucaoTratamento)
class EvolucaoTratamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'agendamento', 'peso_inicial', 'peso_atual', 'data_evolucao']
    list_filter = ['data_evolucao', 'agendamento__servico__categoria']
    search_fields = ['cliente__nome', 'observacoes_profissional']
    ordering = ['-data_evolucao']
    date_hierarchy = 'data_evolucao'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('cliente', 'agendamento', 'data_evolucao')
        }),
        ('Dados Corporais', {
            'fields': ('peso_inicial', 'peso_atual', 'medidas_corporais')
        }),
        ('Documentação', {
            'fields': ('fotos_antes', 'fotos_depois')
        }),
        ('Observações', {
            'fields': ('observacoes_profissional', 'observacoes_cliente', 'proximos_passos')
        })
    )


@admin.register(PacoteTratamento)
class PacoteTratamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'numero_sessoes', 'preco_total', 'desconto_percentual', 'ativo']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    filter_horizontal = ['servicos']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Configurações', {
            'fields': ('servicos', 'protocolo', 'numero_sessoes', 'validade_dias')
        }),
        ('Preços', {
            'fields': ('preco_total', 'desconto_percentual')
        })
    )
