"""
Models para configurações específicas por tipo de loja
"""
from django.db import models
from .models import Loja
import json


class ConfiguracaoLanchonete(models.Model):
    """Configurações específicas para lanchonetes/restaurantes"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_lanchonete'
    )
    
    # Configurações de cardápio
    categorias_cardapio = models.JSONField(
        default=list,
        help_text="['Lanches', 'Bebidas', 'Sobremesas', 'Porções']"
    )
    
    # Configurações de mesas
    numero_mesas = models.IntegerField(default=10)
    capacidade_maxima_mesa = models.IntegerField(default=6)
    usa_reservas = models.BooleanField(default=False)
    tempo_limite_mesa = models.IntegerField(default=120, help_text="Minutos")
    
    # Configurações de comandas
    usa_comandas = models.BooleanField(default=True)
    numeracao_comandas = models.CharField(
        max_length=20,
        default="sequencial",
        choices=[
            ('sequencial', 'Sequencial'),
            ('por_mesa', 'Por Mesa'),
            ('personalizada', 'Personalizada')
        ]
    )
    
    # Configurações de delivery
    faz_delivery = models.BooleanField(default=False)
    tempo_preparo_medio = models.IntegerField(default=30, help_text="Minutos")
    valor_minimo_delivery = models.DecimalField(max_digits=10, decimal_places=2, default=20.00)
    
    # Configurações de ingredientes
    controla_ingredientes = models.BooleanField(default=True)
    alerta_ingrediente_acabando = models.BooleanField(default=True)
    
    # Configurações de receitas
    usa_fichas_tecnicas = models.BooleanField(default=False)
    calcula_custo_receita = models.BooleanField(default=False)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Lanchonete"
        verbose_name_plural = "Configurações de Lanchonetes"
    
    def __str__(self):
        return f"Config Lanchonete - {self.loja.nome}"


class ConfiguracaoClinicaEstetica(models.Model):
    """Configurações específicas para clínicas de estética"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_clinica'
    )
    
    # Configurações de procedimentos
    tipos_procedimentos = models.JSONField(
        default=list,
        help_text="['Limpeza de Pele', 'Massagem', 'Depilação']"
    )
    
    # Configurações de agendamento
    intervalo_agendamento = models.IntegerField(default=30, help_text="Minutos")
    antecedencia_minima = models.IntegerField(default=24, help_text="Horas")
    permite_reagendamento = models.BooleanField(default=True)
    
    # Configurações de profissionais
    especialidades_profissionais = models.JSONField(
        default=list,
        help_text="Especialidades dos profissionais"
    )
    
    # Configurações de equipamentos
    controla_equipamentos = models.BooleanField(default=True)
    agenda_manutencao = models.BooleanField(default=True)
    
    # Configurações de anamnese
    usa_anamnese = models.BooleanField(default=True)
    campos_anamnese = models.JSONField(
        default=list,
        help_text="Campos do formulário de anamnese"
    )
    
    # Configurações de produtos
    vende_produtos = models.BooleanField(default=True)
    tipos_produtos = models.JSONField(
        default=list,
        help_text="['Cosméticos', 'Suplementos', 'Acessórios']"
    )
    
    # Configurações de follow-up
    faz_followup = models.BooleanField(default=True)
    dias_followup = models.IntegerField(default=7)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Clínica de Estética"
        verbose_name_plural = "Configurações de Clínicas de Estética"
    
    def __str__(self):
        return f"Config Clínica - {self.loja.nome}"


class ConfiguracaoLojaRoupas(models.Model):
    """Configurações específicas para lojas de roupas"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_roupas'
    )
    
    # Configurações de tamanhos
    grades_tamanho = models.JSONField(
        default=dict,
        help_text="Grades de tamanho por categoria"
    )
    
    # Configurações de cores
    cores_disponiveis = models.JSONField(
        default=list,
        help_text="Paleta de cores da loja"
    )
    
    # Configurações de coleções
    usa_colecoes = models.BooleanField(default=True)
    tipos_colecoes = models.JSONField(
        default=list,
        help_text="['Verão', 'Inverno', 'Primavera', 'Outono']"
    )
    
    # Configurações de provador
    numero_provadores = models.IntegerField(default=3)
    tempo_limite_provador = models.IntegerField(default=15, help_text="Minutos")
    
    # Configurações de etiquetas
    tipo_etiqueta = models.CharField(
        max_length=20,
        default="codigo_barras",
        choices=[
            ('codigo_barras', 'Código de Barras'),
            ('qr_code', 'QR Code'),
            ('rfid', 'RFID')
        ]
    )
    
    # Configurações de trocas e devoluções
    prazo_troca = models.IntegerField(default=30, help_text="Dias")
    permite_devolucao = models.BooleanField(default=True)
    prazo_devolucao = models.IntegerField(default=7, help_text="Dias")
    
    # Configurações de promoções
    tipos_promocoes = models.JSONField(
        default=list,
        help_text="['Liquidação', 'Black Friday', 'Queima de Estoque']"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Loja de Roupas"
        verbose_name_plural = "Configurações de Lojas de Roupas"
    
    def __str__(self):
        return f"Config Roupas - {self.loja.nome}"


class ConfiguracaoSupermercado(models.Model):
    """Configurações específicas para supermercados"""
    
    loja = models.OneToOneField(
        Loja,
        on_delete=models.CASCADE,
        related_name='config_supermercado'
    )
    
    # Configurações de seções
    secoes_loja = models.JSONField(
        default=list,
        help_text="['Açougue', 'Padaria', 'Hortifruti', 'Frios']"
    )
    
    # Configurações de validade
    controla_validade = models.BooleanField(default=True)
    dias_alerta_vencimento = models.IntegerField(default=3)
    desconto_produtos_vencendo = models.DecimalField(
        max_digits=5, decimal_places=2, default=20.00
    )
    
    # Configurações de pesagem
    produtos_por_peso = models.BooleanField(default=True)
    balancas_integradas = models.BooleanField(default=False)
    
    # Configurações de promoções
    promocoes_semanais = models.BooleanField(default=True)
    dia_promocao = models.CharField(
        max_length=20,
        default="quarta",
        choices=[
            ('segunda', 'Segunda-feira'),
            ('terca', 'Terça-feira'),
            ('quarta', 'Quarta-feira'),
            ('quinta', 'Quinta-feira'),
            ('sexta', 'Sexta-feira'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo')
        ]
    )
    
    # Configurações de sacolas
    cobra_sacola = models.BooleanField(default=True)
    valor_sacola = models.DecimalField(max_digits=5, decimal_places=2, default=0.10)
    tipos_sacola = models.JSONField(
        default=list,
        help_text="['Plástica', 'Papel', 'Ecológica']"
    )
    
    # Configurações de código de barras
    sistema_codigo_barras = models.CharField(
        max_length=20,
        default="ean13",
        choices=[
            ('ean13', 'EAN-13'),
            ('ean8', 'EAN-8'),
            ('code128', 'Code 128')
        ]
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Supermercado"
        verbose_name_plural = "Configurações de Supermercados"
    
    def __str__(self):
        return f"Config Supermercado - {self.loja.nome}"
