from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


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
