from django import forms
from django.contrib.auth.models import User
from .models import Curso, Coordenador, Professor, AvaliacaoConfig, AvaliacaoResposta


class CursoForm(forms.ModelForm):
    """Formulário para cadastro/edição de cursos"""
    
    class Meta:
        model = Curso
        fields = ['nome', 'codigo', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do curso'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único do curso'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CoordenadorForm(forms.ModelForm):
    """Formulário para cadastro/edição de coordenadores"""
    
    class Meta:
        model = Coordenador
        fields = ['nome', 'email', 'telefone', 'user', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do coordenador'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas usuários que não são coordenadores
        self.fields['user'].queryset = User.objects.filter(
            coordenador_fatesa__isnull=True
        )
        self.fields['user'].empty_label = "Selecione um usuário (opcional)"


class ProfessorForm(forms.ModelForm):
    """Formulário para cadastro/edição de professores"""
    
    class Meta:
        model = Professor
        fields = ['nome', 'email', 'telefone', 'especialidade', 'user', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do professor'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'especialidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Área de especialidade'
            }),
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas usuários que não são professores
        self.fields['user'].queryset = User.objects.filter(
            professor_fatesa__isnull=True
        )
        self.fields['user'].empty_label = "Selecione um usuário (opcional)"


class AvaliacaoConfigForm(forms.ModelForm):
    """Formulário para configuração de avaliação"""
    
    class Meta:
        model = AvaliacaoConfig
        fields = ['curso', 'coordenador', 'professores', 'turma']
        widgets = {
            'curso': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'coordenador': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'professores': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'multiple': True,
                'size': '8'
            }),
            'turma': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Turma A - Janeiro/2024',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas registros ativos
        self.fields['curso'].queryset = Curso.objects.filter(ativo=True).order_by('nome')
        self.fields['coordenador'].queryset = Coordenador.objects.filter(ativo=True).order_by('nome')
        self.fields['professores'].queryset = Professor.objects.filter(ativo=True).order_by('nome')
        
        # Labels personalizados
        self.fields['curso'].empty_label = "Selecione o curso"
        self.fields['coordenador'].empty_label = "Selecione o coordenador"


class AvaliacaoRespostaForm(forms.ModelForm):
    """Formulário para resposta do aluno"""
    
    class Meta:
        model = AvaliacaoResposta
        fields = [
            # Seção 1 - Professor
            'nota_relacionamento_professor',
            'nota_didatica_professor', 
            'nota_dominio_assunto',
            'professor_respeita_horarios',
            
            # Seção 2 - Origem
            'origem_conhecimento',
            
            # Seção 3 - Motivo
            'motivo_escolha',
            
            # Seção 4 - Curso
            'nota_conteudo_teorico',
            'nota_atividade_pratica',
            
            # Seção 5 - Administração
            'nota_portaria',
            'nota_atendimento_aluno',
            'nota_secretaria',
            'nota_recepcao_paciente',
            'nota_biblioteca',
            'nota_setor_comercial',
            'nota_limpeza',
            'nota_cantina',
            
            # Seção 6 - Comentários
            'comentarios_adicionais',
            'sugestoes_melhorias',
            'nome_aluno',
            'contato_aluno'
        ]
        
        widgets = {
            # Notas (0-10)
            'nota_relacionamento_professor': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_didatica_professor': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_dominio_assunto': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_conteudo_teorico': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_atividade_pratica': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_portaria': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_atendimento_aluno': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_secretaria': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_recepcao_paciente': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_biblioteca': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_setor_comercial': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_limpeza': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            'nota_cantina': forms.Select(attrs={
                'class': 'form-select nota-select',
                'required': True
            }),
            
            # Sim/Não
            'professor_respeita_horarios': forms.RadioSelect(
                choices=[(True, 'Sim'), (False, 'Não')],
                attrs={'class': 'form-check-input'}
            ),
            
            # Selects
            'origem_conhecimento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'motivo_escolha': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            
            # Textos
            'comentarios_adicionais': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Deixe seus comentários sobre o curso (opcional)'
            }),
            'sugestoes_melhorias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Sugestões para melhorar o curso (opcional)'
            }),
            'nome_aluno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome (opcional)'
            }),
            'contato_aluno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone ou email (opcional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar labels
        self.fields['nota_relacionamento_professor'].label = "Relacionamento professor-aluno"
        self.fields['nota_didatica_professor'].label = "Didática dos professores"
        self.fields['nota_dominio_assunto'].label = "Domínio do assunto pelos professores"
        self.fields['professor_respeita_horarios'].label = "O professor respeita os horários e fica disponível para dúvidas após as aulas?"
        
        self.fields['origem_conhecimento'].label = "Como você ficou sabendo da FATESA?"
        self.fields['motivo_escolha'].label = "O que motivou sua decisão de escolher a FATESA?"
        
        self.fields['nota_conteudo_teorico'].label = "Satisfação com o conteúdo teórico"
        self.fields['nota_atividade_pratica'].label = "Satisfação com a atividade prática"
        
        self.fields['nota_portaria'].label = "Portaria"
        self.fields['nota_atendimento_aluno'].label = "Atendimento ao aluno"
        self.fields['nota_secretaria'].label = "Secretaria"
        self.fields['nota_recepcao_paciente'].label = "Recepção Paciente"
        self.fields['nota_biblioteca'].label = "Biblioteca"
        self.fields['nota_setor_comercial'].label = "Setor Comercial"
        self.fields['nota_limpeza'].label = "Limpeza"
        self.fields['nota_cantina'].label = "Cantina"
        
        self.fields['comentarios_adicionais'].label = "Comentários adicionais"
        self.fields['sugestoes_melhorias'].label = "Sugestões de melhorias"
        self.fields['nome_aluno'].label = "Nome (opcional)"
        self.fields['contato_aluno'].label = "Contato (opcional)"


class FiltroRelatorioForm(forms.Form):
    """Formulário para filtros de relatórios"""
    
    PERIODO_CHOICES = [
        ('', 'Todos os períodos'),
        ('30', 'Últimos 30 dias'),
        ('90', 'Últimos 90 dias'),
        ('365', 'Último ano'),
    ]
    
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.filter(ativo=True).order_by('nome'),
        required=False,
        empty_label="Todos os cursos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    coordenador = forms.ModelChoiceField(
        queryset=Coordenador.objects.filter(ativo=True).order_by('nome'),
        required=False,
        empty_label="Todos os coordenadores",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    professor = forms.ModelChoiceField(
        queryset=Professor.objects.filter(ativo=True).order_by('nome'),
        required=False,
        empty_label="Todos os professores",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )