"""
Models para configurações da Fase 2 - Operacionais
"""
from django.db import models
from django.contrib.auth.models import User
from .models import Loja
import json


class ConfiguracaoFuncionario(models.Model):
    """Configurações de gestão de funcionários por loja"""
    
    loja = models.OneToOneField(
        Loja, 
        on_delete=models.CASCADE,
        related_name='config_funcionario'
    )
    
    # Cargos personalizados
    cargos_disponiveis = models.JSONField(
        default=list,
        help_text="Lista de cargos: ['Vendedor', 'Caixa', 'Gerente']"
    )
    
    # Configurações de permissão
    niveis_permissao = models.JSONField(
        default=dict,
        help_text="Permissões por cargo"
    )
    
    # Configurações de horário
    horario_funcionamento = models.JSONField(
        default=dict,
        help_text="Horários de funcionamento por dia da semana"
    )
    
    # Configurações de comissão
    usa_comissao = models.BooleanField(default=False)
    tipos_comissao = models.JSONField(
        default=list,
        help_text="Tipos: ['percentual', 'valor_fixo', 'por_produto']"
    )
    
    # Configurações de metas
    usa_metas = models.BooleanField(default=False)
    tipos_metas = models.JSONField(
        default=list,
        help_text="Tipos: ['vendas', 'clientes', 'produtos']"
    )
    
    # Configurações de ponto
    controla_ponto = models.BooleanField(default=False)
    tolerancia_atraso = models.IntegerField(default=15, help_text="Minutos")
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Funcionário"
        verbose_name_plural = "Configurações de Funcionários"
    
    def __str__(self):
        return f"Config Funcionários - {self.loja.nome}"


class ConfiguracaoPagamento(models.Model):
    """Configurações de formas de pagamento por loja"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_pagamento'
    )
    
    # Formas de pagamento aceitas
    formas_aceitas = models.JSONField(
        default=list,
        help_text="['dinheiro', 'pix', 'cartao_debito', 'cartao_credito', 'boleto']"
    )
    
    # Configurações de parcelamento
    permite_parcelamento = models.BooleanField(default=True)
    max_parcelas = models.IntegerField(default=12)
    valor_minimo_parcelamento = models.DecimalField(
        max_digits=10, decimal_places=2, default=50.00
    )
    
    # Configurações de juros
    cobra_juros = models.BooleanField(default=False)
    taxa_juros_mensal = models.DecimalField(
        max_digits=5, decimal_places=2, default=2.50
    )
    
    # Configurações de desconto
    desconto_a_vista = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    desconto_pix = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    
    # Configurações de crediário próprio
    tem_crediario = models.BooleanField(default=False)
    limite_credito_padrao = models.DecimalField(
        max_digits=10, decimal_places=2, default=500.00
    )
    dias_vencimento_crediario = models.IntegerField(default=30)
    
    # Configurações de multa e mora
    taxa_multa = models.DecimalField(
        max_digits=5, decimal_places=2, default=2.00
    )
    taxa_mora_diaria = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.10
    )
    
    # Integrações
    integracoes_ativas = models.JSONField(
        default=dict,
        help_text="Integrações com gateways de pagamento"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Pagamento"
        verbose_name_plural = "Configurações de Pagamentos"
    
    def __str__(self):
        return f"Config Pagamentos - {self.loja.nome}"


class ConfiguracaoFornecedor(models.Model):
    """Configurações de gestão de fornecedores por loja"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_fornecedor'
    )
    
    # Campos obrigatórios para fornecedores
    campos_obrigatorios = models.JSONField(
        default=list,
        help_text="['nome', 'cnpj', 'telefone', 'email']"
    )
    
    # Configurações de avaliação
    usa_avaliacao_fornecedor = models.BooleanField(default=False)
    criterios_avaliacao = models.JSONField(
        default=list,
        help_text="['qualidade', 'preco', 'prazo', 'atendimento']"
    )
    
    # Configurações de pagamento a fornecedores
    prazos_pagamento_padrao = models.JSONField(
        default=list,
        help_text="[30, 60, 90] dias"
    )
    
    # Configurações de pedidos
    valor_minimo_pedido = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    
    # Configurações de entrega
    prazo_entrega_padrao = models.IntegerField(default=7, help_text="Dias")
    
    # Configurações de qualidade
    exige_certificacao = models.BooleanField(default=False)
    tipos_certificacao = models.JSONField(
        default=list,
        help_text="Certificações exigidas"
    )
    
    # Configurações de relatórios
    gera_relatorio_performance = models.BooleanField(default=True)
    frequencia_relatorio = models.CharField(
        max_length=20,
        default="mensal",
        choices=[
            ('semanal', 'Semanal'),
            ('mensal', 'Mensal'),
            ('trimestral', 'Trimestral')
        ]
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Fornecedor"
        verbose_name_plural = "Configurações de Fornecedores"
    
    def __str__(self):
        return f"Config Fornecedores - {self.loja.nome}"


class ConfiguracaoLogistica(models.Model):
    """Configurações de logística e entrega por loja"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_logistica'
    )
    
    # Configurações de entrega
    faz_entrega = models.BooleanField(default=False)
    raio_entrega_km = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00
    )
    
    # Configurações de taxa de entrega
    taxa_entrega_fixa = models.DecimalField(
        max_digits=10, decimal_places=2, default=5.00
    )
    taxa_por_km = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.00
    )
    valor_minimo_frete_gratis = models.DecimalField(
        max_digits=10, decimal_places=2, default=100.00
    )
    
    # Configurações de prazo
    prazo_entrega_padrao = models.IntegerField(default=1, help_text="Dias")
    prazo_entrega_expressa = models.IntegerField(default=0, help_text="Horas")
    
    # Configurações de horário de entrega
    horarios_entrega = models.JSONField(
        default=dict,
        help_text="Horários de entrega por dia da semana"
    )
    
    # Configurações de áreas de entrega
    areas_atendidas = models.JSONField(
        default=list,
        help_text="Lista de bairros/regiões atendidas"
    )
    
    # Configurações de transportadoras
    usa_transportadoras = models.BooleanField(default=False)
    transportadoras_ativas = models.JSONField(
        default=list,
        help_text="Lista de transportadoras parceiras"
    )
    
    # Configurações de embalagem
    tipos_embalagem = models.JSONField(
        default=list,
        help_text="Tipos de embalagem disponíveis"
    )
    cobra_embalagem = models.BooleanField(default=False)
    valor_embalagem = models.DecimalField(
        max_digits=5, decimal_places=2, default=2.00
    )
    
    # Configurações de rastreamento
    oferece_rastreamento = models.BooleanField(default=False)
    sistema_rastreamento = models.CharField(
        max_length=50,
        default="proprio",
        choices=[
            ('proprio', 'Sistema Próprio'),
            ('correios', 'Correios'),
            ('transportadora', 'Transportadora')
        ]
    )
    
    # Configurações de retirada
    permite_retirada_loja = models.BooleanField(default=True)
    horario_retirada = models.JSONField(
        default=dict,
        help_text="Horários para retirada na loja"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Logística"
        verbose_name_plural = "Configurações de Logística"
    
    def __str__(self):
        return f"Config Logística - {self.loja.nome}"
