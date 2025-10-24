from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import secrets
import string


class PerfilUsuario(models.Model):
    """Perfil de usuário para o sistema FATESA"""
    
    TIPO_PERFIL_CHOICES = [
        ('diretoria', 'Diretoria'),
        ('coordenacao', 'Coordenação'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='perfil_fatesa',
        verbose_name="Usuário"
    )
    tipo_perfil = models.CharField(
        max_length=20, 
        choices=TIPO_PERFIL_CHOICES,
        verbose_name="Tipo de Perfil"
    )
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Campos específicos para coordenadores
    cursos_coordenados = models.ManyToManyField(
        'Curso', 
        blank=True, 
        related_name='coordenadores_perfil',
        verbose_name="Cursos Coordenados"
    )
    
    # Campos específicos para professores
    especialidade = models.CharField(
        max_length=300, 
        blank=True, 
        null=True, 
        verbose_name="Especialidade"
    )
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuário"
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.get_tipo_perfil_display()})"
    
    def save(self, *args, **kwargs):
        # Criar o usuário se não existir
        if not self.user_id:
            raise ValidationError("Usuário é obrigatório")
        
        super().save(*args, **kwargs)
        
        # Adicionar aos grupos apropriados
        self.configurar_grupos()
    
    def configurar_grupos(self):
        """Configura os grupos do usuário baseado no tipo de perfil"""
        # Remove de todos os grupos FATESA
        grupos_fatesa = ['FATESA_Diretoria', 'FATESA_Coordenacao', 'FATESA_Professor', 'FATESA_Secretaria']
        for grupo_nome in grupos_fatesa:
            try:
                grupo = Group.objects.get(name=grupo_nome)
                self.user.groups.remove(grupo)
            except Group.DoesNotExist:
                pass
        
        # Adiciona ao grupo apropriado
        grupo_nome = f'FATESA_{self.tipo_perfil.title()}'
        if self.tipo_perfil == 'coordenacao':
            grupo_nome = 'FATESA_Coordenacao'
        
        grupo, created = Group.objects.get_or_create(name=grupo_nome)
        self.user.groups.add(grupo)
    
    def pode_acessar_dashboard_diretoria(self):
        """Verifica se pode acessar dashboard da diretoria"""
        return self.tipo_perfil == 'diretoria'
    
    def pode_acessar_dashboard_coordenacao(self):
        """Verifica se pode acessar dashboard de coordenação"""
        return self.tipo_perfil in ['diretoria', 'coordenacao']
    
    def pode_acessar_dashboard_professor(self):
        """Verifica se pode acessar dashboard do professor"""
        return self.tipo_perfil in ['diretoria', 'coordenacao', 'professor']
    
    def pode_criar_avaliacoes(self):
        """Verifica se pode criar avaliações"""
        return self.tipo_perfil in ['diretoria', 'secretaria']
    
    def pode_gerenciar_usuarios(self):
        """Verifica se pode gerenciar usuários"""
        return self.tipo_perfil == 'diretoria'


class Curso(models.Model):
    """Modelo para os cursos da FATESA"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=500, verbose_name="Nome do Curso")
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código do Curso")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Coordenador(models.Model):
    """Modelo para coordenadores dos cursos"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome do Coordenador")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='coordenador_fatesa',
        verbose_name="Usuário do Sistema"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Coordenador"
        verbose_name_plural = "Coordenadores"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Professor(models.Model):
    """Modelo para professores dos cursos"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome do Professor")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    especialidade = models.CharField(max_length=300, blank=True, null=True, verbose_name="Especialidade")
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='professor_fatesa',
        verbose_name="Usuário do Sistema"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class AvaliacaoConfig(models.Model):
    """Configuração de uma avaliação - criada pela secretaria"""
    
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name="Curso")
    coordenador = models.ForeignKey(Coordenador, on_delete=models.CASCADE, verbose_name="Coordenador")
    professores = models.ManyToManyField(Professor, verbose_name="Professores")
    turma = models.CharField(max_length=200, verbose_name="Turma/Data")
    
    # Link único para avaliação
    link_token = models.CharField(max_length=100, unique=True, verbose_name="Token do Link")
    
    # Controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Criado por", null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Finalização")
    
    # Estatísticas
    total_avaliacoes = models.IntegerField(default=0, verbose_name="Total de Avaliações Recebidas")
    
    class Meta:
        verbose_name = "Configuração de Avaliação"
        verbose_name_plural = "Configurações de Avaliação"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.curso.nome} - {self.turma}"
    
    def save(self, *args, **kwargs):
        if not self.link_token:
            self.link_token = self.gerar_token_unico()
        super().save(*args, **kwargs)
    
    def gerar_token_unico(self):
        """Gera um token único para o link de avaliação"""
        while True:
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            if not AvaliacaoConfig.objects.filter(link_token=token).exists():
                return token
    
    def get_link_avaliacao(self):
        """Retorna o link completo para avaliação"""
        from django.urls import reverse
        return reverse('avaliacao_qualidade:formulario_aluno', kwargs={'token': self.link_token})
    
    def finalizar(self):
        """Finaliza a avaliação"""
        self.status = 'finalizada'
        self.data_finalizacao = timezone.now()
        self.save()


class AvaliacaoResposta(models.Model):
    """Resposta de um aluno para uma avaliação"""
    
    ORIGEM_CHOICES = [
        ('indicacao', 'Indicação de ex-alunos/amigos'),
        ('site', 'Site da FATESA'),
        ('email_marketing', 'E-mail marketing'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('google', 'Google'),
        ('congressos', 'Congressos ou eventos'),
        ('telemarketing', 'Telemarketing'),
        ('material_impresso', 'Material impresso'),
        ('anuncios', 'Anúncios em revistas ou jornais'),
        ('outros', 'Outros'),
    ]
    
    MOTIVO_ESCOLHA_CHOICES = [
        ('influencia_amigos', 'Influência de amigos'),
        ('tradicao', 'Tradição'),
        ('propaganda', 'Propaganda'),
        ('qualidade_ensino', 'Qualidade do ensino'),
        ('preco_competitivo', 'Preço competitivo'),
        ('estrutura', 'Estrutura'),
        ('outros', 'Outros'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avaliacao_config = models.ForeignKey(
        AvaliacaoConfig, 
        on_delete=models.CASCADE, 
        related_name='respostas',
        verbose_name="Configuração da Avaliação"
    )
    
    # === SEÇÃO 1 - AVALIAÇÃO DO PROFESSOR ===
    # Notas de 0 a 10
    nota_relacionamento_professor = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Relacionamento professor-aluno"
    )
    nota_didatica_professor = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Didática dos professores"
    )
    nota_dominio_assunto = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Domínio do assunto pelos professores"
    )
    
    # Questão Sim/Não
    professor_respeita_horarios = models.BooleanField(
        verbose_name="O professor respeita os horários e fica disponível para dúvidas após as aulas?"
    )
    
    # === SEÇÃO 2 - ORIGEM DO ALUNO ===
    origem_conhecimento = models.CharField(
        max_length=50,
        choices=ORIGEM_CHOICES,
        verbose_name="Como você ficou sabendo da FATESA?"
    )
    
    # === SEÇÃO 3 - MOTIVO DA ESCOLHA ===
    motivo_escolha = models.CharField(
        max_length=50,
        choices=MOTIVO_ESCOLHA_CHOICES,
        verbose_name="O que motivou sua decisão de escolher a FATESA?"
    )
    
    # === SEÇÃO 4 - SATISFAÇÃO COM O CURSO ===
    nota_conteudo_teorico = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Satisfação com o conteúdo teórico"
    )
    nota_atividade_pratica = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Satisfação com a atividade prática"
    )
    
    # === SEÇÃO 5 - AVALIAÇÃO DA ADMINISTRAÇÃO ===
    nota_portaria = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Portaria"
    )
    nota_atendimento_aluno = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Atendimento ao aluno"
    )
    nota_secretaria = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Secretaria"
    )
    nota_recepcao_paciente = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Recepção Paciente"
    )
    nota_biblioteca = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Biblioteca"
    )
    nota_setor_comercial = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Setor Comercial"
    )
    nota_limpeza = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Limpeza"
    )
    nota_cantina = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        verbose_name="Cantina"
    )
    
    # === SEÇÃO 6 - COMENTÁRIOS FINAIS ===
    comentarios_adicionais = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Comentários adicionais"
    )
    sugestoes_melhorias = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Sugestões de melhorias"
    )
    
    # Dados opcionais do aluno
    nome_aluno = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Nome do aluno"
    )
    contato_aluno = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Contato do aluno"
    )
    
    # Controle
    ip_address = models.GenericIPAddressField(verbose_name="IP do Aluno")
    user_agent = models.TextField(verbose_name="User Agent")
    data_resposta = models.DateTimeField(auto_now_add=True, verbose_name="Data da Resposta")
    
    class Meta:
        verbose_name = "Resposta de Avaliação"
        verbose_name_plural = "Respostas de Avaliação"
        ordering = ['-data_resposta']
    
    def __str__(self):
        nome = self.nome_aluno or "Anônimo"
        return f"{nome} - {self.avaliacao_config.curso.nome} - {self.data_resposta.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Incrementa contador na configuração
        if not self.pk:  # Apenas para novas respostas
            self.avaliacao_config.total_avaliacoes += 1
            self.avaliacao_config.save()
        super().save(*args, **kwargs)
    
    def get_media_professor(self):
        """Calcula a média das notas do professor"""
        notas = [
            self.nota_relacionamento_professor,
            self.nota_didatica_professor,
            self.nota_dominio_assunto
        ]
        return sum(notas) / len(notas)
    
    def get_media_curso(self):
        """Calcula a média das notas do curso"""
        notas = [
            self.nota_conteudo_teorico,
            self.nota_atividade_pratica
        ]
        return sum(notas) / len(notas)
    
    def get_media_administracao(self):
        """Calcula a média das notas da administração"""
        notas = [
            self.nota_portaria,
            self.nota_atendimento_aluno,
            self.nota_secretaria,
            self.nota_recepcao_paciente,
            self.nota_biblioteca,
            self.nota_setor_comercial,
            self.nota_limpeza,
            self.nota_cantina
        ]
        return sum(notas) / len(notas)
    
    def get_media_geral(self):
        """Calcula a média geral de todas as notas"""
        todas_notas = [
            self.nota_relacionamento_professor,
            self.nota_didatica_professor,
            self.nota_dominio_assunto,
            self.nota_conteudo_teorico,
            self.nota_atividade_pratica,
            self.nota_portaria,
            self.nota_atendimento_aluno,
            self.nota_secretaria,
            self.nota_recepcao_paciente,
            self.nota_biblioteca,
            self.nota_setor_comercial,
            self.nota_limpeza,
            self.nota_cantina
        ]
        return sum(todas_notas) / len(todas_notas)


class RelatorioEstatisticas(models.Model):
    """Cache de estatísticas para relatórios"""
    
    TIPO_CHOICES = [
        ('curso', 'Por Curso'),
        ('professor', 'Por Professor'),
        ('coordenador', 'Por Coordenador'),
        ('geral', 'Geral'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    referencia_id = models.CharField(max_length=100, verbose_name="ID de Referência")  # ID do curso, professor, etc.
    referencia_nome = models.CharField(max_length=500, verbose_name="Nome de Referência")
    
    # Estatísticas calculadas
    total_avaliacoes = models.IntegerField(default=0)
    media_professor = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    media_curso = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    media_administracao = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    media_geral = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    
    # Período das estatísticas
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    
    # Controle
    data_calculo = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Relatório de Estatísticas"
        verbose_name_plural = "Relatórios de Estatísticas"
        ordering = ['-data_calculo']
        unique_together = ['tipo', 'referencia_id', 'data_inicio', 'data_fim']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.referencia_nome} ({self.total_avaliacoes} avaliações)"