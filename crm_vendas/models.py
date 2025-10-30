"""
Models para sistema CRM de vendas com orçamentos, propostas e contratos
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class ProdutoServico(models.Model):
    """Produtos e Serviços para orçamentos, propostas e contratos"""
    
    TIPO_CHOICES = [
        ('produto', 'Produto'),
        ('servico', 'Serviço'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='produtos_servicos')
    
    # Dados básicos
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='servico')
    codigo = models.CharField(max_length=50, blank=True, help_text="Código interno do produto/serviço")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    
    # Valores
    preco_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unidade = models.CharField(max_length=20, default='un', help_text="Unidade de medida (un, h, kg, m², etc.)")
    
    # Controle
    ativo = models.BooleanField(default=True)
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produto/Serviço"
        verbose_name_plural = "Produtos/Serviços"
        ordering = ['nome']
        unique_together = ['loja', 'codigo']
        indexes = [
            models.Index(fields=['loja', 'ativo']),
            models.Index(fields=['tipo', 'categoria']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Lead(models.Model):
    """Leads/Prospects do CRM"""
    
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('contatado', 'Contatado'),
        ('qualificado', 'Qualificado'),
        ('proposta_enviada', 'Proposta Enviada'),
        ('negociacao', 'Negociação'),
        ('fechado_ganho', 'Fechado - Ganho'),
        ('fechado_perdido', 'Fechado - Perdido'),
        ('inativo', 'Inativo'),
    ]
    
    ORIGEM_CHOICES = [
        ('site', 'Site'),
        ('telefone', 'Telefone'),
        ('email', 'Email'),
        ('indicacao', 'Indicação'),
        ('redes_sociais', 'Redes Sociais'),
        ('evento', 'Evento'),
        ('publicidade', 'Publicidade'),
        ('outros', 'Outros'),
    ]
    
    TIPO_PESSOA_CHOICES = [
        ('fisica', 'Pessoa Física'),
        ('juridica', 'Pessoa Jurídica'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tipo de pessoa
    tipo_pessoa = models.CharField(max_length=10, choices=TIPO_PESSOA_CHOICES, default='fisica')
    
    # Dados básicos - Pessoa Física
    nome = models.CharField(max_length=200, help_text="Nome completo para PF ou Razão Social para PJ")
    cpf = models.CharField(max_length=14, blank=True, help_text="CPF para Pessoa Física")
    rg = models.CharField(max_length=20, blank=True, help_text="RG para Pessoa Física")
    
    # Dados básicos - Pessoa Jurídica
    cnpj = models.CharField(max_length=18, blank=True, help_text="CNPJ para Pessoa Jurídica")
    inscricao_estadual = models.CharField(max_length=20, blank=True, help_text="Inscrição Estadual")
    inscricao_municipal = models.CharField(max_length=20, blank=True, help_text="Inscrição Municipal")
    nome_fantasia = models.CharField(max_length=200, blank=True, help_text="Nome Fantasia para PJ")
    
    # Contato
    email = models.EmailField(validators=[EmailValidator()])
    telefone = models.CharField(max_length=20, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    
    # Dados profissionais/empresariais
    empresa = models.CharField(max_length=200, blank=True, help_text="Empresa onde trabalha (para PF)")
    cargo = models.CharField(max_length=100, blank=True, help_text="Cargo na empresa (para PF)")
    ramo_atividade = models.CharField(max_length=200, blank=True, help_text="Ramo de atividade da empresa")
    
    # Endereço
    endereco = models.TextField(blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=10, blank=True)
    
    # Controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo')
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='site')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dados comerciais
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    probabilidade = models.IntegerField(default=50, help_text="Probabilidade de fechamento (%)")
    
    # Interesse e necessidades do cliente
    interesse_principal = models.TextField(blank=True, help_text="Principal interesse/necessidade do cliente")
    observacoes = models.TextField(blank=True, help_text="Observações gerais sobre o lead")
    observacoes_interesse = models.TextField(blank=True, help_text="Detalhes específicos do interesse do cliente")
    tags = models.JSONField(default=list, blank=True)
    
    # Qualificação
    orcamento_disponivel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Orçamento disponível informado pelo cliente")
    prazo_decisao = models.CharField(max_length=100, blank=True, help_text="Prazo para tomada de decisão")
    decisor = models.BooleanField(default=True, help_text="É o decisor da compra?")
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_ultimo_contato = models.DateTimeField(null=True, blank=True)
    data_proximo_contato = models.DateTimeField(null=True, blank=True)
    
    # Loja associada
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='leads')
    
    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['loja', 'status']),
            models.Index(fields=['responsavel']),
            models.Index(fields=['data_proximo_contato']),
        ]
    
    def __str__(self):
        return f"{self.nome} - {self.empresa} ({self.get_status_display()})"
    
    @property
    def valor_ponderado(self):
        """Valor ponderado pela probabilidade"""
        return self.valor_estimado * (self.probabilidade / 100)


class Orcamento(models.Model):
    """Orçamentos enviados para leads/clientes"""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviado', 'Enviado'),
        ('visualizado', 'Visualizado'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('expirado', 'Expirado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='orcamentos')
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Dados do orçamento
    numero = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    
    # Valores
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impostos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Condições
    condicoes_pagamento = models.TextField(default="À vista")
    prazo_entrega = models.CharField(max_length=100, default="A combinar")
    validade_dias = models.IntegerField(default=30)
    
    # Controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    
    # Template e personalização
    template_usado = models.CharField(max_length=50, default='padrao')
    cores_personalizadas = models.JSONField(default=dict, blank=True)
    logo_personalizado = models.ImageField(upload_to='orcamentos/logos/', blank=True)
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_visualizacao = models.DateTimeField(null=True, blank=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)
    
    # Email
    email_enviado = models.BooleanField(default=False)
    email_assunto = models.CharField(max_length=200, blank=True)
    email_corpo = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['loja', 'status']),
            models.Index(fields=['lead']),
            models.Index(fields=['data_expiracao']),
        ]
    
    def __str__(self):
        return f"Orçamento {self.numero} - {self.lead.nome}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.gerar_numero()
        
        # Calcular data de expiração
        if not self.data_expiracao and self.validade_dias:
            self.data_expiracao = timezone.now() + timezone.timedelta(days=self.validade_dias)
        
        super().save(*args, **kwargs)
    
    def gerar_numero(self):
        """Gera número único do orçamento"""
        from datetime import datetime
        ano = datetime.now().year
        mes = datetime.now().month
        
        # Contar orçamentos do mês
        count = Orcamento.objects.filter(
            loja=self.loja,
            data_criacao__year=ano,
            data_criacao__month=mes
        ).count() + 1
        
        return f"ORC-{ano}{mes:02d}-{count:04d}"
    
    @property
    def esta_expirado(self):
        """Verifica se o orçamento está expirado"""
        return self.data_expiracao and timezone.now() > self.data_expiracao
    
    def atualizar_totais(self):
        """Atualiza os totais do orçamento baseado nos itens"""
        subtotal = sum(item.valor_total for item in self.itens.all())
        self.subtotal = subtotal
        self.total = subtotal - self.desconto + self.impostos
        self.save()


class ItemOrcamento(models.Model):
    """Itens do orçamento"""
    
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    produto_servico = models.ForeignKey(ProdutoServico, on_delete=models.SET_NULL, null=True, blank=True, help_text="Produto/Serviço cadastrado")
    
    # Dados do item (podem ser preenchidos automaticamente do produto/serviço)
    descricao = models.CharField(max_length=500)
    detalhes = models.TextField(blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unidade = models.CharField(max_length=20, default='un')
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Desconto específico do item
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Desconto em %")
    desconto_valor = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Desconto em valor")
    
    # Ordem
    ordem = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Item do Orçamento"
        verbose_name_plural = "Itens do Orçamento"
        ordering = ['ordem', 'id']
    
    def save(self, *args, **kwargs):
        # Se produto/serviço foi selecionado, preencher dados automaticamente
        if self.produto_servico and not self.descricao:
            self.descricao = self.produto_servico.nome
            self.unidade = self.produto_servico.unidade
            if not self.valor_unitario:
                self.valor_unitario = self.produto_servico.preco_base
        
        # Calcular valor total com descontos
        valor_bruto = self.quantidade * self.valor_unitario
        desconto_total = self.desconto_valor + (valor_bruto * self.desconto_percentual / 100)
        self.valor_total = valor_bruto - desconto_total
        
        super().save(*args, **kwargs)
        
        # Atualizar totais do orçamento
        self.orcamento.atualizar_totais()
    
    def __str__(self):
        return f"{self.descricao} - {self.quantidade} {self.unidade}"


class Proposta(models.Model):
    """Propostas comerciais mais elaboradas"""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviada', 'Enviada'),
        ('em_analise', 'Em Análise'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('expirada', 'Expirada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='propostas')
    orcamento = models.ForeignKey(Orcamento, on_delete=models.SET_NULL, null=True, blank=True)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Dados da proposta
    numero = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=200)
    resumo_executivo = models.TextField()
    objetivos = models.TextField()
    metodologia = models.TextField(blank=True)
    cronograma = models.TextField(blank=True)
    investimento = models.TextField()
    
    # Valores
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Condições
    condicoes_comerciais = models.TextField()
    prazo_validade = models.IntegerField(default=30)
    
    # Controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    
    # Template
    template_usado = models.CharField(max_length=50, default='executivo')
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Proposta"
        verbose_name_plural = "Propostas"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Proposta {self.numero} - {self.lead.nome}"


class Contrato(models.Model):
    """Contratos gerados a partir de propostas aprovadas"""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviado', 'Enviado'),
        ('assinado_cliente', 'Assinado pelo Cliente'),
        ('assinado_empresa', 'Assinado pela Empresa'),
        ('ativo', 'Ativo'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='contratos')
    proposta = models.ForeignKey(Proposta, on_delete=models.SET_NULL, null=True, blank=True)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Dados do contrato
    numero = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=200)
    objeto = models.TextField()
    clausulas = models.TextField()
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Prazos
    data_inicio = models.DateField()
    data_fim = models.DateField()
    prazo_meses = models.IntegerField(default=12)
    
    # Condições
    forma_pagamento = models.TextField()
    condicoes_especiais = models.TextField(blank=True)
    
    # Controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    
    # Assinaturas
    assinado_cliente_em = models.DateTimeField(null=True, blank=True)
    assinado_empresa_em = models.DateTimeField(null=True, blank=True)
    
    # Arquivos
    arquivo_pdf = models.FileField(upload_to='contratos/pdfs/', blank=True)
    arquivo_assinado = models.FileField(upload_to='contratos/assinados/', blank=True)
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Contrato {self.numero} - {self.lead.nome}"


class HistoricoContato(models.Model):
    """Histórico de contatos com leads"""
    
    TIPO_CHOICES = [
        ('telefone', 'Telefone'),
        ('email', 'Email'),
        ('reuniao', 'Reunião'),
        ('whatsapp', 'WhatsApp'),
        ('visita', 'Visita'),
        ('evento', 'Evento'),
        ('outros', 'Outros'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='historico_contatos')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    assunto = models.CharField(max_length=200)
    descricao = models.TextField()
    
    # Resultado
    resultado = models.TextField(blank=True)
    proximo_passo = models.TextField(blank=True)
    data_proximo_contato = models.DateTimeField(null=True, blank=True)
    
    # Anexos
    anexos = models.JSONField(default=list, blank=True)
    
    data_contato = models.DateTimeField(default=timezone.now)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Histórico de Contato"
        verbose_name_plural = "Histórico de Contatos"
        ordering = ['-data_contato']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.assunto}"


class EmailLog(models.Model):
    """Log de emails enviados"""
    
    STATUS_CHOICES = [
        ('enviando', 'Enviando'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('aberto', 'Aberto'),
        ('clicado', 'Clicado'),
        ('erro', 'Erro'),
    ]
    
    # Relacionamentos
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='emails_enviados')
    orcamento = models.ForeignKey(Orcamento, on_delete=models.SET_NULL, null=True, blank=True)
    proposta = models.ForeignKey(Proposta, on_delete=models.SET_NULL, null=True, blank=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dados do email
    destinatario = models.EmailField()
    assunto = models.CharField(max_length=200)
    corpo = models.TextField()
    anexos = models.JSONField(default=list, blank=True)
    
    # Controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enviando')
    tentativas = models.IntegerField(default=0)
    erro_mensagem = models.TextField(blank=True)
    
    # Tracking
    token_rastreamento = models.UUIDField(default=uuid.uuid4, unique=True)
    data_abertura = models.DateTimeField(null=True, blank=True)
    data_clique = models.DateTimeField(null=True, blank=True)
    ip_abertura = models.GenericIPAddressField(null=True, blank=True)
    
    # Datas
    data_envio = models.DateTimeField(auto_now_add=True)
    data_entrega = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Log de Email"
        verbose_name_plural = "Logs de Emails"
        ordering = ['-data_envio']
    
    def __str__(self):
        return f"Email para {self.destinatario} - {self.assunto}"


class AssinaturaDigital(models.Model):
    """Controle de assinaturas digitais de documentos"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('enviado', 'Enviado para Assinatura'),
        ('visualizado', 'Visualizado'),
        ('assinado', 'Assinado'),
        ('rejeitado', 'Rejeitado'),
        ('expirado', 'Expirado'),
    ]
    
    TIPO_DOCUMENTO_CHOICES = [
        ('orcamento', 'Orçamento'),
        ('proposta', 'Proposta'),
        ('contrato', 'Contrato'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='assinaturas')
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, null=True, blank=True)
    proposta = models.ForeignKey(Proposta, on_delete=models.CASCADE, null=True, blank=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, null=True, blank=True)
    
    # Dados da assinatura
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    # Signatários
    nome_signatario = models.CharField(max_length=200)
    email_signatario = models.EmailField()
    cpf_signatario = models.CharField(max_length=14, blank=True)
    
    # Controle de acesso
    token_acesso = models.UUIDField(default=uuid.uuid4, unique=True)
    ip_assinatura = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Arquivos
    documento_original = models.FileField(upload_to='assinaturas/originais/', blank=True)
    documento_assinado = models.FileField(upload_to='assinaturas/assinados/', blank=True)
    
    # Dados da assinatura
    hash_documento = models.CharField(max_length=64, blank=True, help_text="Hash SHA-256 do documento")
    certificado_digital = models.TextField(blank=True, help_text="Dados do certificado usado na assinatura")
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_visualizacao = models.DateTimeField(null=True, blank=True)
    data_assinatura = models.DateTimeField(null=True, blank=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)
    
    # Observações
    observacoes = models.TextField(blank=True)
    motivo_rejeicao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Assinatura Digital"
        verbose_name_plural = "Assinaturas Digitais"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['lead', 'status']),
            models.Index(fields=['token_acesso']),
            models.Index(fields=['data_expiracao']),
        ]
    
    def __str__(self):
        return f"Assinatura {self.get_tipo_documento_display()} - {self.nome_signatario}"
    
    @property
    def esta_expirado(self):
        """Verifica se a assinatura está expirada"""
        return self.data_expiracao and timezone.now() > self.data_expiracao
    
    def gerar_url_assinatura(self):
        """Gera URL para assinatura do documento"""
        from django.urls import reverse
        return reverse('crm_vendas:assinar_documento', kwargs={'token': self.token_acesso})
