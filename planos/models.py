from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class PlanoComercial(models.Model):
    """Modelo para planos comerciais das lojas"""
    
    TIPO_PLANO_CHOICES = [
        ('basico', 'Básico'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('suspenso', 'Suspenso'),
    ]
    
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Plano")
    tipo = models.CharField(max_length=20, choices=TIPO_PLANO_CHOICES, verbose_name="Tipo do Plano")
    descricao = models.TextField(verbose_name="Descrição")
    
    # Limites do plano
    max_usuarios_simultaneos = models.PositiveIntegerField(
        default=1, 
        verbose_name="Máximo de Usuários Simultâneos",
        help_text="Número máximo de usuários que podem acessar simultaneamente"
    )
    max_pdvs = models.PositiveIntegerField(
        default=1, 
        verbose_name="Máximo de PDVs",
        help_text="Número máximo de pontos de venda"
    )
    max_produtos = models.PositiveIntegerField(
        default=100, 
        verbose_name="Máximo de Produtos",
        help_text="Número máximo de produtos que podem ser cadastrados"
    )
    max_clientes = models.PositiveIntegerField(
        default=100, 
        verbose_name="Máximo de Clientes",
        help_text="Número máximo de clientes que podem ser cadastrados"
    )
    max_vendas_mes = models.PositiveIntegerField(
        default=100, 
        verbose_name="Máximo de Vendas por Mês",
        help_text="Número máximo de vendas permitidas por mês"
    )
    
    # Recursos incluídos
    backup_automatico = models.BooleanField(default=False, verbose_name="Backup Automático")
    relatorios_avancados = models.BooleanField(default=False, verbose_name="Relatórios Avançados")
    integracao_api = models.BooleanField(default=False, verbose_name="Integração API")
    suporte_prioritario = models.BooleanField(default=False, verbose_name="Suporte Prioritário")
    customizacao_avancada = models.BooleanField(default=False, verbose_name="Customização Avançada")
    
    # Preços
    preco_mensal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Preço Mensal (R$)"
    )
    preco_anual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Preço Anual (R$) - Desconto"
    )
    
    # Status e configurações
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name="Status")
    ordem_exibicao = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    destaque = models.BooleanField(default=False, verbose_name="Plano em Destaque")
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Plano Comercial"
        verbose_name_plural = "Planos Comerciais"
        ordering = ['ordem_exibicao', 'preco_mensal']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco_mensal}/mês"
    
    def calcular_desconto_anual(self):
        """Calcula o percentual de desconto do plano anual"""
        if self.preco_mensal > 0:
            preco_anual_teorico = self.preco_mensal * 12
            if self.preco_anual > 0:
                desconto = ((preco_anual_teorico - self.preco_anual) / preco_anual_teorico) * 100
                return round(desconto, 1)
        return 0
    
    def get_recursos_incluidos(self):
        """Retorna lista de recursos incluídos no plano"""
        recursos = []
        if self.backup_automatico:
            recursos.append("Backup Automático")
        if self.relatorios_avancados:
            recursos.append("Relatórios Avançados")
        if self.integracao_api:
            recursos.append("Integração API")
        if self.suporte_prioritario:
            recursos.append("Suporte Prioritário")
        if self.customizacao_avancada:
            recursos.append("Customização Avançada")
        return recursos


class AssinaturaLoja(models.Model):
    """Modelo para assinaturas das lojas aos planos"""
    
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('suspensa', 'Suspensa'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    ]
    
    TIPO_PAGAMENTO_CHOICES = [
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]
    
    loja = models.OneToOneField('lojas.Loja', on_delete=models.CASCADE, verbose_name="Loja")
    plano = models.ForeignKey(PlanoComercial, on_delete=models.PROTECT, verbose_name="Plano")
    
    # Status da assinatura
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa', verbose_name="Status")
    tipo_pagamento = models.CharField(max_length=20, choices=TIPO_PAGAMENTO_CHOICES, default='mensal', verbose_name="Tipo de Pagamento")
    
    # Datas
    data_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Início")
    data_vencimento = models.DateTimeField(verbose_name="Data de Vencimento")
    data_cancelamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Cancelamento")
    
    # Controle de uso atual
    usuarios_online = models.PositiveIntegerField(default=0, verbose_name="Usuários Online Atualmente")
    pdvs_ativos = models.PositiveIntegerField(default=0, verbose_name="PDVs Ativos Atualmente")
    vendas_mes_atual = models.PositiveIntegerField(default=0, verbose_name="Vendas no Mês Atual")
    
    # Configurações
    limite_usuarios_atingido = models.BooleanField(default=False, verbose_name="Limite de Usuários Atingido")
    limite_pdvs_atingido = models.BooleanField(default=False, verbose_name="Limite de PDVs Atingido")
    limite_vendas_atingido = models.BooleanField(default=False, verbose_name="Limite de Vendas Atingido")
    
    # Datas de controle
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Assinatura da Loja"
        verbose_name_plural = "Assinaturas das Lojas"
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.loja.nome} - {self.plano.nome}"
    
    def verificar_limites(self):
        """Verifica se os limites do plano foram atingidos"""
        self.limite_usuarios_atingido = self.usuarios_online >= self.plano.max_usuarios_simultaneos
        self.limite_pdvs_atingido = self.pdvs_ativos >= self.plano.max_pdvs
        self.limite_vendas_atingido = self.vendas_mes_atual >= self.plano.max_vendas_mes
        self.save()
        return {
            'usuarios': self.limite_usuarios_atingido,
            'pdvs': self.limite_pdvs_atingido,
            'vendas': self.limite_vendas_atingido
        }
    
    def pode_adicionar_usuario(self):
        """Verifica se pode adicionar mais um usuário online"""
        return self.usuarios_online < self.plano.max_usuarios_simultaneos
    
    def pode_adicionar_pdv(self):
        """Verifica se pode adicionar mais um PDV"""
        return self.pdvs_ativos < self.plano.max_pdvs
    
    def pode_realizar_venda(self):
        """Verifica se pode realizar mais uma venda no mês"""
        return self.vendas_mes_atual < self.plano.max_vendas_mes
    
    def is_vencida(self):
        """Verifica se a assinatura está vencida"""
        from django.utils import timezone
        return timezone.now() > self.data_vencimento
    
    def dias_para_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        from django.utils import timezone
        delta = self.data_vencimento - timezone.now()
        return delta.days if delta.days > 0 else 0


class HistoricoUso(models.Model):
    """Modelo para histórico de uso das lojas"""
    
    TIPO_EVENTO_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('pdv_aberto', 'PDV Aberto'),
        ('pdv_fechado', 'PDV Fechado'),
        ('venda_realizada', 'Venda Realizada'),
        ('limite_atingido', 'Limite Atingido'),
    ]
    
    assinatura = models.ForeignKey(AssinaturaLoja, on_delete=models.CASCADE, verbose_name="Assinatura")
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de Evento")
    descricao = models.TextField(verbose_name="Descrição")
    
    # Dados do evento
    usuarios_online = models.PositiveIntegerField(default=0, verbose_name="Usuários Online")
    pdvs_ativos = models.PositiveIntegerField(default=0, verbose_name="PDVs Ativos")
    vendas_mes = models.PositiveIntegerField(default=0, verbose_name="Vendas no Mês")
    
    # Metadados
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Endereço IP")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")
    data_evento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Evento")
    
    class Meta:
        verbose_name = "Histórico de Uso"
        verbose_name_plural = "Históricos de Uso"
        ordering = ['-data_evento']
    
    def __str__(self):
        return f"{self.assinatura.loja.nome} - {self.get_tipo_evento_display()} - {self.data_evento.strftime('%d/%m/%Y %H:%M')}"



