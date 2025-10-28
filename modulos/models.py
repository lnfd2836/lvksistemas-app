from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class TipoLoja(models.Model):
    """Modelo simplificado para categorização de tipos de loja"""
    
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
        ('clinica_estetica', 'Clínica de Estética'),
        ('avaliacao_fatesa', 'Avaliação Educacional - FATESA'),
        ('dashboard_comercial', 'Dashboard Comercial e Qualidade'),
        ('crm_vendas', 'CRM de Vendas'),
        ('outros', 'Outros'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=50, choices=TIPO_CHOICES, unique=True, verbose_name="Nome do Tipo")
    descricao = models.TextField(verbose_name="Descrição")
    icone = models.CharField(max_length=50, default='fas fa-store', verbose_name="Ícone")
    cor_primaria = models.CharField(max_length=7, default='#007bff', verbose_name="Cor Primária")
    cor_secundaria = models.CharField(max_length=7, default='#6c757d', verbose_name="Cor Secundária")
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Tipo de Loja"
        verbose_name_plural = "Tipos de Loja"
        ordering = ['nome']
    
    def __str__(self):
        return self.get_nome_display()
    
    @property
    def nome_display(self):
        """Retorna o nome amigável do tipo"""
        return self.get_nome_display()


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


class ConfiguracaoTipoLoja(models.Model):
    """Configurações padrão para cada tipo de loja"""
    
    CATEGORIA_CONFIG_CHOICES = [
        ('produto', 'Configurações de Produto'),
        ('cliente', 'Configurações de Cliente'),
        ('venda', 'Configurações de Venda'),
        ('dashboard', 'Configurações de Dashboard'),
        ('sistema', 'Configurações de Sistema'),
    ]
    
    TIPO_VALOR_CHOICES = [
        ('boolean', 'Sim/Não'),
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('decimal', 'Decimal'),
        ('lista', 'Lista de Opções'),
        ('json', 'JSON'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_loja = models.ForeignKey(TipoLoja, on_delete=models.CASCADE, related_name='configuracoes_padrao')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CONFIG_CHOICES, verbose_name="Categoria")
    chave = models.CharField(max_length=100, verbose_name="Chave da Configuração")
    nome_exibicao = models.CharField(max_length=200, verbose_name="Nome para Exibição")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    tipo_valor = models.CharField(max_length=20, choices=TIPO_VALOR_CHOICES, verbose_name="Tipo do Valor")
    valor_padrao = models.TextField(blank=True, verbose_name="Valor Padrão")
    opcoes_disponiveis = models.TextField(blank=True, verbose_name="Opções Disponíveis (uma por linha)")
    obrigatorio = models.BooleanField(default=False, verbose_name="Obrigatório")
    editavel_loja = models.BooleanField(default=True, verbose_name="Loja pode editar")
    ordem = models.IntegerField(default=0, verbose_name="Ordem de Exibição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Configuração Padrão do Tipo de Loja"
        verbose_name_plural = "Configurações Padrão dos Tipos de Loja"
        ordering = ['categoria', 'ordem', 'nome_exibicao']
        unique_together = ['tipo_loja', 'chave']
    
    def __str__(self):
        return f"{self.tipo_loja.get_nome_display()} - {self.nome_exibicao}"
    
    def get_opcoes_list(self):
        """Retorna as opções disponíveis como lista"""
        if self.opcoes_disponiveis:
            return [opcao.strip() for opcao in self.opcoes_disponiveis.split('\n') if opcao.strip()]
        return []
    
    def get_valor_formatado(self):
        """Retorna o valor padrão formatado conforme o tipo"""
        if self.tipo_valor == 'boolean':
            return self.valor_padrao.lower() in ['true', '1', 'sim', 'yes']
        elif self.tipo_valor in ['numero', 'decimal']:
            try:
                return float(self.valor_padrao) if self.valor_padrao else 0
            except ValueError:
                return 0
        elif self.tipo_valor == 'json':
            try:
                import json
                return json.loads(self.valor_padrao) if self.valor_padrao else {}
            except json.JSONDecodeError:
                return {}
        else:
            return self.valor_padrao


class ConfiguracaoLoja(models.Model):
    """Configurações específicas de cada loja (baseadas no tipo de loja)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.ForeignKey('lojas.Loja', on_delete=models.CASCADE, related_name='configuracoes_especificas')
    configuracao_tipo = models.ForeignKey(ConfiguracaoTipoLoja, on_delete=models.CASCADE, verbose_name="Configuração do Tipo")
    valor_personalizado = models.TextField(blank=True, verbose_name="Valor Personalizado")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Configuração da Loja"
        verbose_name_plural = "Configurações das Lojas"
        unique_together = ['loja', 'configuracao_tipo']
    
    def __str__(self):
        return f"{self.loja.nome} - {self.configuracao_tipo.nome_exibicao}"
    
    def get_valor_efetivo(self):
        """Retorna o valor efetivo (personalizado ou padrão)"""
        if self.valor_personalizado:
            # Aplicar formatação conforme o tipo
            if self.configuracao_tipo.tipo_valor == 'boolean':
                return self.valor_personalizado.lower() in ['true', '1', 'sim', 'yes']
            elif self.configuracao_tipo.tipo_valor in ['numero', 'decimal']:
                try:
                    return float(self.valor_personalizado)
                except ValueError:
                    return self.configuracao_tipo.get_valor_formatado()
            elif self.configuracao_tipo.tipo_valor == 'json':
                try:
                    import json
                    return json.loads(self.valor_personalizado)
                except json.JSONDecodeError:
                    return self.configuracao_tipo.get_valor_formatado()
            else:
                return self.valor_personalizado
        else:
            return self.configuracao_tipo.get_valor_formatado()


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


# =============================================================================
# MODELOS ESPECÍFICOS PARA CLÍNICA DE ESTÉTICA
# =============================================================================

class ServicoEstetica(models.Model):
    """Modelo para serviços oferecidos pela clínica de estética"""
    
    CATEGORIA_CHOICES = [
        ('facial', 'Tratamento Facial'),
        ('corporal', 'Tratamento Corporal'),
        ('injetavel', 'Procedimentos Injetáveis'),
        ('laser', 'Tratamentos a Laser'),
        ('depilacao', 'Depilação'),
        ('manicure', 'Manicure e Pedicure'),
        ('massagem', 'Massagens'),
        ('outros', 'Outros'),
    ]
    
    DURACAO_CHOICES = [
        (15, '15 minutos'),
        (30, '30 minutos'),
        (45, '45 minutos'),
        (60, '1 hora'),
        (90, '1h30'),
        (120, '2 horas'),
        (180, '3 horas'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome do Serviço")
    descricao = models.TextField(verbose_name="Descrição")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, verbose_name="Categoria")
    duracao_minutos = models.IntegerField(choices=DURACAO_CHOICES, verbose_name="Duração")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço Promocional")
    
    # Configurações específicas
    requer_consulta_medica = models.BooleanField(default=False, verbose_name="Requer Consulta Médica")
    idade_minima = models.IntegerField(default=16, verbose_name="Idade Mínima")
    contraindicacoes = models.TextField(blank=True, verbose_name="Contraindicações")
    cuidados_pos_procedimento = models.TextField(blank=True, verbose_name="Cuidados Pós-Procedimento")
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Serviço de Estética"
        verbose_name_plural = "Serviços de Estética"
        ordering = ['categoria', 'nome']
    
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.nome}"


class ProtocoloEmagrecimento(models.Model):
    """Modelo para protocolos de emagrecimento"""
    
    TIPO_PROTOCOLO_CHOICES = [
        ('drenagem', 'Drenagem Linfática'),
        ('criolipolise', 'Criolipólise'),
        ('radiofrequencia', 'Radiofrequência'),
        ('ultrassom', 'Ultrassom'),
        ('massagem_modeladora', 'Massagem Modeladora'),
        ('bandagem', 'Bandagem Redutora'),
        ('combinado', 'Protocolo Combinado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome do Protocolo")
    descricao = models.TextField(verbose_name="Descrição")
    tipo_protocolo = models.CharField(max_length=20, choices=TIPO_PROTOCOLO_CHOICES, verbose_name="Tipo de Protocolo")
    
    # Configurações do protocolo
    numero_sessoes = models.IntegerField(verbose_name="Número de Sessões")
    intervalo_dias = models.IntegerField(default=7, verbose_name="Intervalo entre Sessões (dias)")
    duracao_sessao_minutos = models.IntegerField(verbose_name="Duração da Sessão (minutos)")
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Total")
    preco_sessao = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço por Sessão")
    
    # Indicações e contraindicações
    indicacoes = models.TextField(verbose_name="Indicações")
    contraindicacoes = models.TextField(verbose_name="Contraindicações")
    resultados_esperados = models.TextField(verbose_name="Resultados Esperados")
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Protocolo de Emagrecimento"
        verbose_name_plural = "Protocolos de Emagrecimento"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    """Modelo para agendamentos de clientes"""
    
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
        ('faltou', 'Cliente Faltou'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey('lojas.Cliente', on_delete=models.CASCADE, related_name='agendamentos', verbose_name="Cliente")
    servico = models.ForeignKey(ServicoEstetica, on_delete=models.CASCADE, related_name='agendamentos', verbose_name="Serviço")
    protocolo = models.ForeignKey(ProtocoloEmagrecimento, on_delete=models.SET_NULL, null=True, blank=True, related_name='agendamentos', verbose_name="Protocolo")
    
    # Data e hora
    data_agendamento = models.DateField(verbose_name="Data do Agendamento")
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    hora_fim = models.TimeField(verbose_name="Hora de Fim")
    
    # Profissional responsável
    profissional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agendamentos_profissional', verbose_name="Profissional")
    
    # Status e observações
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado', verbose_name="Status")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    observacoes_pos_procedimento = models.TextField(blank=True, verbose_name="Observações Pós-Procedimento")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['data_agendamento', 'hora_inicio']
    
    def __str__(self):
        return f"{self.cliente.nome} - {self.servico.nome} - {self.data_agendamento} {self.hora_inicio}"


class Retorno(models.Model):
    """Modelo para retornos de clientes"""
    
    TIPO_RETORNO_CHOICES = [
        ('avaliacao', 'Avaliação'),
        ('manutencao', 'Manutenção'),
        ('complementar', 'Tratamento Complementar'),
        ('emergencia', 'Emergência'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agendamento_original = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='retornos', verbose_name="Agendamento Original")
    tipo_retorno = models.CharField(max_length=20, choices=TIPO_RETORNO_CHOICES, verbose_name="Tipo de Retorno")
    
    # Data do retorno
    data_retorno = models.DateField(verbose_name="Data do Retorno")
    hora_retorno = models.TimeField(verbose_name="Hora do Retorno")
    
    # Observações
    motivo_retorno = models.TextField(verbose_name="Motivo do Retorno")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Retorno"
        verbose_name_plural = "Retornos"
        ordering = ['data_retorno', 'hora_retorno']
    
    def __str__(self):
        return f"Retorno - {self.agendamento_original.cliente.nome} - {self.data_retorno}"


class FichaAnamnese(models.Model):
    """Modelo para ficha de anamnese do cliente"""
    
    TIPO_PELE_CHOICES = [
        ('normal', 'Normal'),
        ('oleosa', 'Oleosa'),
        ('seca', 'Seca'),
        ('mista', 'Mista'),
        ('sensivel', 'Sensível'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.OneToOneField('lojas.Cliente', on_delete=models.CASCADE, related_name='ficha_anamnese', verbose_name="Cliente")
    
    # Dados da pele
    tipo_pele = models.CharField(max_length=20, choices=TIPO_PELE_CHOICES, verbose_name="Tipo de Pele")
    alergias = models.TextField(blank=True, verbose_name="Alergias Conhecidas")
    medicamentos_uso = models.TextField(blank=True, verbose_name="Medicamentos em Uso")
    tratamentos_anteriores = models.TextField(blank=True, verbose_name="Tratamentos Anteriores")
    
    # Histórico médico
    problemas_circulatorios = models.BooleanField(default=False, verbose_name="Problemas Circulatórios")
    diabetes = models.BooleanField(default=False, verbose_name="Diabetes")
    hipertensao = models.BooleanField(default=False, verbose_name="Hipertensão")
    gravidez = models.BooleanField(default=False, verbose_name="Gravidez")
    amamentacao = models.BooleanField(default=False, verbose_name="Amamentação")
    
    # Objetivos
    objetivos_tratamento = models.TextField(verbose_name="Objetivos do Tratamento")
    expectativas = models.TextField(blank=True, verbose_name="Expectativas")
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Ficha de Anamnese"
        verbose_name_plural = "Fichas de Anamnese"
    
    def __str__(self):
        return f"Anamnese - {self.cliente.nome}"


class EvolucaoTratamento(models.Model):
    """Modelo para evolução do tratamento do cliente"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey('lojas.Cliente', on_delete=models.CASCADE, related_name='evolucoes', verbose_name="Cliente")
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='evolucoes', verbose_name="Agendamento")
    
    # Dados da evolução
    peso_inicial = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso Inicial (kg)")
    peso_atual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso Atual (kg)")
    medidas_corporais = models.TextField(blank=True, verbose_name="Medidas Corporais")
    fotos_antes = models.TextField(blank=True, verbose_name="Fotos Antes (URLs)")
    fotos_depois = models.TextField(blank=True, verbose_name="Fotos Depois (URLs)")
    
    # Observações
    observacoes_profissional = models.TextField(verbose_name="Observações do Profissional")
    observacoes_cliente = models.TextField(blank=True, verbose_name="Observações do Cliente")
    proximos_passos = models.TextField(blank=True, verbose_name="Próximos Passos")
    
    # Controle
    data_evolucao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Evolução")
    
    class Meta:
        verbose_name = "Evolução do Tratamento"
        verbose_name_plural = "Evoluções do Tratamento"
        ordering = ['-data_evolucao']
    
    def __str__(self):
        return f"Evolução - {self.cliente.nome} - {self.data_evolucao.strftime('%d/%m/%Y')}"


class PacoteTratamento(models.Model):
    """Modelo para pacotes de tratamento"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome do Pacote")
    descricao = models.TextField(verbose_name="Descrição")
    
    # Serviços incluídos
    servicos = models.ManyToManyField(ServicoEstetica, related_name='pacotes', verbose_name="Serviços Incluídos")
    protocolo = models.ForeignKey(ProtocoloEmagrecimento, on_delete=models.SET_NULL, null=True, blank=True, related_name='pacotes', verbose_name="Protocolo")
    
    # Configurações
    numero_sessoes = models.IntegerField(verbose_name="Número de Sessões")
    validade_dias = models.IntegerField(default=90, verbose_name="Validade (dias)")
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Total")
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Desconto (%)")
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Pacote de Tratamento"
        verbose_name_plural = "Pacotes de Tratamento"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    @property
    def preco_com_desconto(self):
        """Calcula o preço com desconto aplicado"""
        if self.desconto_percentual > 0:
            desconto = self.preco_total * (self.desconto_percentual / 100)
            return self.preco_total - desconto
        return self.preco_total
