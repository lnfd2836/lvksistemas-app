"""
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
    # permite_duplicatas = models.BooleanField(default=False)
    # historico_compras = models.BooleanField(default=True)
    # notificacoes_email = models.BooleanField(default=False)
    
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



    
    # === OTIMIZAÇÕES DE PERFORMANCE ===
    
    @classmethod
    def get_cached_config(cls, loja_id):
        """Obtém configuração com cache"""
        from django.core.cache import cache
        
        cache_key = f"{cls.__name__.lower()}_{loja_id}"
        config = cache.get(cache_key)
        
        if config is None:
            try:
                config = cls.objects.select_related('loja').get(loja_id=loja_id)
                # Cache por 1 hora
                cache.set(cache_key, config, 3600)
            except cls.DoesNotExist:
                # Criar configuração padrão se não existir
                from .models import Loja
                loja = Loja.objects.get(id=loja_id)
                config = cls.objects.create(loja=loja)
                cache.set(cache_key, config, 3600)
        
        return config
    
    def save(self, *args, **kwargs):
        """Override save para limpar cache"""
        super().save(*args, **kwargs)
        # Limpar cache quando salvar
        from django.core.cache import cache
        cache_key = f"{self.__class__.__name__.lower()}_{self.loja_id}"
        cache.delete(cache_key)
    
    class Meta:
        # Adicionar índices para performance
        indexes = [
            models.Index(fields=['loja']),
            models.Index(fields=['data_atualizacao']),
        ]

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
    
    def get_periodo_padrao_display(self):
        """Retorna o nome amigável do período padrão"""
        return dict(self._meta.get_field('periodo_padrao').choices).get(self.periodo_padrao, self.periodo_padrao)
    
    def get_tema_cores_display(self):
        """Retorna o nome amigável do tema de cores"""
        return dict(self._meta.get_field('tema_cores').choices).get(self.tema_cores, self.tema_cores)
    
    def __str__(self):
        return f"Config Dashboard - {self.loja.nome}"
