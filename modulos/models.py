from django.db import models
from django.utils import timezone
import uuid


class TipoLoja(models.Model):
    """Modelo para tipos de loja (conveniência, roupas, tintas, etc.)"""
    
    TIPO_CHOICES = [
        ('conveniencia', 'Loja de Conveniência'),
        ('roupas', 'Loja de Roupas'),
        ('tintas', 'Loja de Tintas'),
        ('supermercado', 'Supermercado'),
        ('lanchonete', 'Lanchonete'),
        ('farmacia', 'Farmácia'),
        ('eletronicos', 'Eletrônicos'),
        ('casa_construcao', 'Casa e Construção'),
        ('livraria', 'Livraria'),
        ('outros', 'Outros'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=50, choices=TIPO_CHOICES, unique=True, verbose_name="Nome do Tipo")
    descricao = models.TextField(verbose_name="Descrição")
    icone = models.CharField(max_length=50, default='fas fa-store', verbose_name="Ícone")
    cor_primaria = models.CharField(max_length=7, default='#007bff', verbose_name="Cor Primária")
    cor_secundaria = models.CharField(max_length=7, default='#6c757d', verbose_name="Cor Secundária")
    
    # Configurações específicas do tipo
    tem_categoria_produto = models.BooleanField(default=True, verbose_name="Tem Categoria de Produto")
    tem_marca_produto = models.BooleanField(default=True, verbose_name="Tem Marca de Produto")
    tem_tamanho_produto = models.BooleanField(default=False, verbose_name="Tem Tamanho de Produto")
    tem_cor_produto = models.BooleanField(default=False, verbose_name="Tem Cor de Produto")
    tem_peso_produto = models.BooleanField(default=False, verbose_name="Tem Peso de Produto")
    tem_volume_produto = models.BooleanField(default=False, verbose_name="Tem Volume de Produto")
    tem_data_validade = models.BooleanField(default=False, verbose_name="Tem Data de Validade")
    tem_codigo_barras = models.BooleanField(default=True, verbose_name="Tem Código de Barras")
    tem_estoque_minimo = models.BooleanField(default=True, verbose_name="Tem Estoque Mínimo")
    
    # Campos específicos para clientes
    tem_data_nascimento_cliente = models.BooleanField(default=True, verbose_name="Cliente: Data de Nascimento")
    tem_sexo_cliente = models.BooleanField(default=True, verbose_name="Cliente: Sexo")
    tem_cpf_cliente = models.BooleanField(default=True, verbose_name="Cliente: CPF")
    tem_rg_cliente = models.BooleanField(default=False, verbose_name="Cliente: RG")
    tem_cnpj_cliente = models.BooleanField(default=False, verbose_name="Cliente: CNPJ")
    
    # Campos específicos para vendas
    tem_desconto_venda = models.BooleanField(default=True, verbose_name="Venda: Desconto")
    tem_taxa_entrega = models.BooleanField(default=False, verbose_name="Venda: Taxa de Entrega")
    tem_mesa_venda = models.BooleanField(default=False, verbose_name="Venda: Mesa")
    tem_garcom_venda = models.BooleanField(default=False, verbose_name="Venda: Garçom")
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Tipo de Loja"
        verbose_name_plural = "Tipos de Loja"
        ordering = ['nome']
    
    def __str__(self):
        return self.get_nome_display()
    
    def get_configuracoes(self):
        """Retorna as configurações do tipo de loja"""
        return {
            'categoria_produto': self.tem_categoria_produto,
            'marca_produto': self.tem_marca_produto,
            'tamanho_produto': self.tem_tamanho_produto,
            'cor_produto': self.tem_cor_produto,
            'peso_produto': self.tem_peso_produto,
            'volume_produto': self.tem_volume_produto,
            'data_validade': self.tem_data_validade,
            'codigo_barras': self.tem_codigo_barras,
            'estoque_minimo': self.tem_estoque_minimo,
            'data_nascimento_cliente': self.tem_data_nascimento_cliente,
            'sexo_cliente': self.tem_sexo_cliente,
            'cpf_cliente': self.tem_cpf_cliente,
            'rg_cliente': self.tem_rg_cliente,
            'cnpj_cliente': self.tem_cnpj_cliente,
            'desconto_venda': self.tem_desconto_venda,
            'taxa_entrega': self.tem_taxa_entrega,
            'mesa_venda': self.tem_mesa_venda,
            'garcom_venda': self.tem_garcom_venda,
        }


class ModuloLoja(models.Model):
    """Modelo para módulos específicos de cada tipo de loja"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_loja = models.ForeignKey(TipoLoja, on_delete=models.CASCADE, related_name='modulos')
    nome = models.CharField(max_length=100, verbose_name="Nome do Módulo")
    descricao = models.TextField(verbose_name="Descrição")
    icone = models.CharField(max_length=50, default='fas fa-cog', verbose_name="Ícone")
    url = models.CharField(max_length=200, verbose_name="URL do Módulo")
    ordem = models.IntegerField(default=0, verbose_name="Ordem de Exibição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Módulo de Loja"
        verbose_name_plural = "Módulos de Loja"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return f"{self.tipo_loja.get_nome_display()} - {self.nome}"


class CampoPersonalizado(models.Model):
    """Modelo para campos personalizados de produtos por tipo de loja"""
    
    TIPO_CAMPO_CHOICES = [
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('decimal', 'Decimal'),
        ('data', 'Data'),
        ('hora', 'Hora'),
        ('boolean', 'Sim/Não'),
        ('escolha', 'Escolha Única'),
        ('multipla_escolha', 'Múltipla Escolha'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_loja = models.ForeignKey(TipoLoja, on_delete=models.CASCADE, related_name='campos_personalizados')
    nome = models.CharField(max_length=100, verbose_name="Nome do Campo")
    slug = models.SlugField(max_length=100, verbose_name="Slug do Campo")
    tipo_campo = models.CharField(max_length=20, choices=TIPO_CAMPO_CHOICES, verbose_name="Tipo do Campo")
    obrigatorio = models.BooleanField(default=False, verbose_name="Obrigatório")
    opcoes = models.TextField(blank=True, null=True, verbose_name="Opções (uma por linha)")
    ordem = models.IntegerField(default=0, verbose_name="Ordem de Exibição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Campo Personalizado"
        verbose_name_plural = "Campos Personalizados"
        ordering = ['ordem', 'nome']
        unique_together = ['tipo_loja', 'slug']
    
    def __str__(self):
        return f"{self.tipo_loja.get_nome_display()} - {self.nome}"
    
    def get_opcoes_list(self):
        """Retorna as opções como lista"""
        if self.opcoes:
            return [opcao.strip() for opcao in self.opcoes.split('\n') if opcao.strip()]
        return []


class ValorCampoPersonalizado(models.Model):
    """Modelo para armazenar valores dos campos personalizados"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campo = models.ForeignKey(CampoPersonalizado, on_delete=models.CASCADE, related_name='valores')
    produto = models.ForeignKey('lojas.Produto', on_delete=models.CASCADE, related_name='campos_personalizados')
    valor = models.TextField(verbose_name="Valor")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Valor Campo Personalizado"
        verbose_name_plural = "Valores Campos Personalizados"
        unique_together = ['campo', 'produto']
    
    def __str__(self):
        return f"{self.produto.nome} - {self.campo.nome}: {self.valor}"
