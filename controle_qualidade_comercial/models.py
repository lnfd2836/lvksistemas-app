from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class CategoriaProduto(models.Model):
    """Categorias de produtos para controle de qualidade comercial"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='categorias_produtos_cqc')
    nome = models.CharField(max_length=255, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ['nome']
        unique_together = ['loja', 'nome']
    
    def __str__(self):
        return f"{self.loja.nome} - {self.nome}"


class FornecedorComercial(models.Model):
    """Fornecedores para controle de qualidade comercial"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='fornecedores_cqc')
    nome = models.CharField(max_length=255, verbose_name="Nome do Fornecedor")
    cnpj = models.CharField(max_length=18, blank=True, verbose_name="CNPJ")
    email = models.EmailField(blank=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    endereco = models.TextField(blank=True, verbose_name="Endereço")
    contato_responsavel = models.CharField(max_length=255, blank=True, verbose_name="Contato Responsável")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']
        unique_together = ['loja', 'cnpj']
    
    def __str__(self):
        return f"{self.loja.nome} - {self.nome}"


class ProdutoComercial(models.Model):
    """Produtos para controle de qualidade comercial"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='produtos_cqc')
    nome = models.CharField(max_length=255, verbose_name="Nome do Produto")
    codigo_barras = models.CharField(max_length=50, blank=True, verbose_name="Código de Barras")
    sku = models.CharField(max_length=100, blank=True, verbose_name="SKU")
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    fornecedor = models.ForeignKey(FornecedorComercial, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fornecedor")
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço de Custo")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço de Venda")
    estoque_atual = models.IntegerField(default=0, verbose_name="Estoque Atual")
    estoque_minimo = models.IntegerField(default=0, verbose_name="Estoque Mínimo")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']
        unique_together = ['loja', 'sku']
    
    def __str__(self):
        return f"{self.loja.nome} - {self.nome}"
    
    @property
    def estoque_baixo(self):
        """Verifica se o estoque está baixo"""
        return self.estoque_atual <= self.estoque_minimo


class VendaComercial(models.Model):
    """Vendas para controle de qualidade comercial"""
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='vendas_cqc')
    numero_venda = models.CharField(max_length=50, verbose_name="Número da Venda")
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vendedor")
    cliente_nome = models.CharField(max_length=255, blank=True, verbose_name="Nome do Cliente")
    cliente_cpf = models.CharField(max_length=14, blank=True, verbose_name="CPF do Cliente")
    cliente_telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone do Cliente")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desconto")
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Final")
    forma_pagamento = models.CharField(max_length=50, choices=FORMA_PAGAMENTO_CHOICES, verbose_name="Forma de Pagamento")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='concluida', verbose_name="Status")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-created_at']
        unique_together = ['loja', 'numero_venda']
    
    def __str__(self):
        return f"{self.loja.nome} - Venda {self.numero_venda}"


class ItemVenda(models.Model):
    """Itens das vendas"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venda = models.ForeignKey(VendaComercial, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(ProdutoComercial, on_delete=models.CASCADE, verbose_name="Produto")
    quantidade = models.IntegerField(verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Item de Venda"
        verbose_name_plural = "Itens de Venda"
        ordering = ['produto__nome']
    
    def __str__(self):
        return f"{self.venda.numero_venda} - {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)


class ControleQualidade(models.Model):
    """Controle de qualidade dos produtos"""
    
    STATUS_QUALIDADE_CHOICES = [
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('condicional', 'Condicional'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='controles_qualidade_cqc')
    produto = models.ForeignKey(ProdutoComercial, on_delete=models.CASCADE, verbose_name="Produto")
    lote = models.CharField(max_length=100, blank=True, verbose_name="Lote")
    data_fabricacao = models.DateField(null=True, blank=True, verbose_name="Data de Fabricação")
    data_validade = models.DateField(null=True, blank=True, verbose_name="Data de Validade")
    data_inspecao = models.DateField(verbose_name="Data de Inspeção")
    inspetor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Inspetor")
    status_qualidade = models.CharField(max_length=50, choices=STATUS_QUALIDADE_CHOICES, verbose_name="Status da Qualidade")
    
    # Critérios de qualidade (escala de 1 a 5)
    aparencia_visual = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Aparência Visual"
    )
    integridade_embalagem = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Integridade da Embalagem"
    )
    conformidade_especificacao = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Conformidade com Especificação"
    )
    
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    acoes_corretivas = models.TextField(blank=True, verbose_name="Ações Corretivas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Controle de Qualidade"
        verbose_name_plural = "Controles de Qualidade"
        ordering = ['-data_inspecao']
    
    def __str__(self):
        return f"{self.produto.nome} - {self.data_inspecao} - {self.get_status_qualidade_display()}"
    
    @property
    def nota_qualidade_geral(self):
        """Calcula a nota geral de qualidade"""
        return (self.aparencia_visual + self.integridade_embalagem + self.conformidade_especificacao) / 3


class ReclamacaoCliente(models.Model):
    """Reclamações de clientes"""
    
    TIPO_RECLAMACAO_CHOICES = [
        ('produto_defeituoso', 'Produto Defeituoso'),
        ('atendimento', 'Atendimento'),
        ('entrega', 'Entrega'),
        ('preco', 'Preço'),
        ('outros', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_andamento', 'Em Andamento'),
        ('resolvida', 'Resolvida'),
        ('fechada', 'Fechada'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='reclamacoes_cqc')
    numero_protocolo = models.CharField(max_length=50, verbose_name="Número do Protocolo")
    cliente_nome = models.CharField(max_length=255, verbose_name="Nome do Cliente")
    cliente_email = models.EmailField(blank=True, verbose_name="Email do Cliente")
    cliente_telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone do Cliente")
    produto = models.ForeignKey(ProdutoComercial, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Produto")
    venda = models.ForeignKey(VendaComercial, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Venda")
    tipo_reclamacao = models.CharField(max_length=100, choices=TIPO_RECLAMACAO_CHOICES, verbose_name="Tipo de Reclamação")
    descricao = models.TextField(verbose_name="Descrição")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='aberta', verbose_name="Status")
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media', verbose_name="Prioridade")
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsável")
    resolucao = models.TextField(blank=True, verbose_name="Resolução")
    data_resolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resolução")
    satisfacao_cliente = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Satisfação do Cliente"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Reclamação de Cliente"
        verbose_name_plural = "Reclamações de Clientes"
        ordering = ['-created_at']
        unique_together = ['loja', 'numero_protocolo']
    
    def __str__(self):
        return f"{self.loja.nome} - Protocolo {self.numero_protocolo}"
    
    def save(self, *args, **kwargs):
        if not self.numero_protocolo:
            # Gera número de protocolo único
            import random
            import string
            self.numero_protocolo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)


class MetaQualidade(models.Model):
    """Metas de qualidade"""
    
    TIPO_META_CHOICES = [
        ('aprovacao_produtos', 'Aprovação de Produtos'),
        ('satisfacao_cliente', 'Satisfação do Cliente'),
        ('reducao_reclamacoes', 'Redução de Reclamações'),
        ('tempo_resolucao', 'Tempo de Resolução'),
    ]
    
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('pausada', 'Pausada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='metas_qualidade_cqc')
    nome = models.CharField(max_length=255, verbose_name="Nome da Meta")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    tipo_meta = models.CharField(max_length=50, choices=TIPO_META_CHOICES, verbose_name="Tipo de Meta")
    valor_meta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da Meta")
    valor_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Atual")
    unidade_medida = models.CharField(max_length=20, blank=True, verbose_name="Unidade de Medida")
    periodo_inicio = models.DateField(verbose_name="Período de Início")
    periodo_fim = models.DateField(verbose_name="Período de Fim")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ativa', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Meta de Qualidade"
        verbose_name_plural = "Metas de Qualidade"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.loja.nome} - {self.nome}"
    
    @property
    def percentual_atingido(self):
        """Calcula o percentual atingido da meta"""
        if self.valor_meta > 0:
            return (self.valor_atual / self.valor_meta) * 100
        return 0
    
    @property
    def meta_atingida(self):
        """Verifica se a meta foi atingida"""
        return self.valor_atual >= self.valor_meta