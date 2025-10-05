from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import secrets
import string


class Loja(models.Model):
    """Modelo principal para representar uma loja"""
    
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('inativa', 'Inativa'),
        ('suspensa', 'Suspensa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome da Loja")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    email = models.EmailField(verbose_name="Email")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    endereco = models.TextField(verbose_name="Endereço")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado", blank=True, null=True)
    cep = models.CharField(max_length=10, verbose_name="CEP")
    
    # Configurações do banco de dados individual
    db_name = models.CharField(max_length=100, unique=True, verbose_name="Nome do Banco")
    db_host = models.CharField(max_length=100, default='localhost', verbose_name="Host do Banco")
    db_port = models.IntegerField(default=5432, verbose_name="Porta do Banco")
    
    # Status e controle
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativa')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    # Usuário administrador da loja
    admin_user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='loja_admin',
        verbose_name="Administrador"
    )
    
    # Senha provisória
    senha_provisoria = models.CharField(max_length=50, blank=True, verbose_name="Senha Provisória")
    senha_provisoria_expirada = models.BooleanField(default=False, verbose_name="Senha Expirada")
    
    # Tipo de loja (módulo)
    tipo_loja = models.ForeignKey(
        'modulos.TipoLoja', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Tipo de Loja"
    )
    
    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.db_name:
            # Gera nome único para o banco de dados
            self.db_name = f"loja_{self.cnpj.replace('.', '').replace('/', '').replace('-', '')}"
        
        if not self.senha_provisoria:
            # Gera senha provisória
            self.senha_provisoria = self.gerar_senha_provisoria()
        
        super().save(*args, **kwargs)
    
    def gerar_senha_provisoria(self):
        """Gera uma senha provisória segura"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def criar_banco_dados(self):
        """Cria o banco de dados individual para a loja"""
        # Para SQLite, não precisamos criar banco separado
        # O sistema usa o mesmo banco SQLite para todas as lojas
        # mas os dados são separados pelo campo 'loja' nas tabelas
        return True
    
    def obter_configuracao_banco(self):
        """Retorna a configuração do banco de dados da loja"""
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': self.db_name,
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': self.db_host,
            'PORT': self.db_port,
        }


class Cliente(models.Model):
    """Modelo para clientes de uma loja específica"""
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='clientes')
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="Email")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    endereco = models.TextField(verbose_name="Endereço")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    cep = models.CharField(max_length=10, verbose_name="CEP")
    
    # Controle
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = ['loja', 'cpf']
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.loja.nome}"


class Produto(models.Model):
    """Modelo para produtos de uma loja específica"""
    
    CATEGORIA_CHOICES = [
        ('eletronicos', 'Eletrônicos'),
        ('roupas', 'Roupas'),
        ('casa', 'Casa e Decoração'),
        ('esportes', 'Esportes'),
        ('livros', 'Livros'),
        ('outros', 'Outros'),
    ]
    
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    descricao = models.TextField(verbose_name="Descrição")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, verbose_name="Categoria")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    estoque = models.IntegerField(default=0, verbose_name="Estoque")
    codigo_barras = models.CharField(max_length=50, blank=True, verbose_name="Código de Barras")
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True, verbose_name="Imagem")
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.loja.nome}"


class Venda(models.Model):
    """Modelo para vendas de uma loja específica"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='vendas')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vendas')
    numero_venda = models.CharField(max_length=20, unique=True, verbose_name="Número da Venda")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desconto")
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Final")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    # Controle
    data_venda = models.DateTimeField(auto_now_add=True, verbose_name="Data da Venda")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-data_venda']
    
    def __str__(self):
        return f"Venda {self.numero_venda} - {self.loja.nome}"
    
    def save(self, *args, **kwargs):
        if not self.numero_venda:
            # Gera número único para a venda
            self.numero_venda = f"VENDA{self.loja.id.hex[:8].upper()}{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calcula valor final
        self.valor_final = self.valor_total - self.desconto
        
        super().save(*args, **kwargs)


class ItemVenda(models.Model):
    """Modelo para itens de uma venda"""
    
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='itens_venda')
    quantidade = models.IntegerField(verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    
    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"
    
    def __str__(self):
        return f"{self.produto.nome} - {self.venda.numero_venda}"
    
    def save(self, *args, **kwargs):
        # Calcula subtotal
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)


class BackupLoja(models.Model):
    """Modelo para controle de backups das lojas"""
    
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='backups')
    nome_arquivo = models.CharField(max_length=200, verbose_name="Nome do Arquivo")
    tamanho_arquivo = models.BigIntegerField(verbose_name="Tamanho do Arquivo (bytes)")
    caminho_arquivo = models.CharField(max_length=500, verbose_name="Caminho do Arquivo")
    data_backup = models.DateTimeField(auto_now_add=True, verbose_name="Data do Backup")
    sucesso = models.BooleanField(default=True, verbose_name="Backup Realizado com Sucesso")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Backup da Loja"
        verbose_name_plural = "Backups das Lojas"
        ordering = ['-data_backup']
    
    def __str__(self):
        return f"Backup {self.loja.nome} - {self.data_backup.strftime('%d/%m/%Y %H:%M')}"
