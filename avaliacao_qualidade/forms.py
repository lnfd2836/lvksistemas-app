from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import (
    PerfilUsuario, Curso, Coordenador, Professor, 
    AvaliacaoConfig, AvaliacaoResposta
)


class CadastroUsuarioForm(forms.ModelForm):
    """Formulário para cadastro de usuários do sistema FATESA"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o email'
        })
    )
    
    nome_completo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome completo'
        })
    )
    
    tipo_perfil = forms.ChoiceField(
        choices=PerfilUsuario.TIPO_PERFIL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    telefone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000'
        })
    )
    
    especialidade = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Especialidade (apenas para professores)'
        })
    )
    
    cursos_coordenados = forms.ModelMultipleChoiceField(
        queryset=None,  # Será definido no __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome de usuário'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir queryset para cursos coordenados
        try:
            self.fields['cursos_coordenados'].queryset = Curso.objects.filter(ativo=True)
        except Exception:
            # Se houver erro ao acessar o banco, usar queryset vazio
            self.fields['cursos_coordenados'].queryset = Curso.objects.none()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este email já está em uso.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_perfil = cleaned_data.get('tipo_perfil')
        especialidade = cleaned_data.get('especialidade')
        cursos_coordenados = cleaned_data.get('cursos_coordenados')
        
        # Validações específicas por tipo de perfil
        if tipo_perfil == 'professor' and not especialidade:
            self.add_error('especialidade', 'Especialidade é obrigatória para professores.')
        
        if tipo_perfil == 'coordenacao' and not cursos_coordenados:
            self.add_error('cursos_coordenados', 'Pelo menos um curso deve ser selecionado para coordenadores.')
        
        return cleaned_data
    
    def save(self, commit=True, loja_associada=None):
        import secrets
        import string
        from django.conf import settings
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome_completo'].split()[0]
        user.last_name = ' '.join(self.cleaned_data['nome_completo'].split()[1:])
        
        # Gerar senha provisória
        senha_provisoria = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        user.set_password(senha_provisoria)
        
        if commit:
            user.save()
            
            # Criar perfil
            perfil = PerfilUsuario.objects.create(
                user=user,
                tipo_perfil=self.cleaned_data['tipo_perfil'],
                nome_completo=self.cleaned_data['nome_completo'],
                telefone=self.cleaned_data.get('telefone', ''),
                especialidade=self.cleaned_data.get('especialidade', ''),
                loja_associada=loja_associada
            )
            
            # Adicionar cursos coordenados se for coordenador
            if self.cleaned_data.get('cursos_coordenados'):
                perfil.cursos_coordenados.set(self.cleaned_data['cursos_coordenados'])
            
            # Enviar email com credenciais
            self.enviar_email_credenciais(user, senha_provisoria, loja_associada)
        
        return user
    
    def enviar_email_credenciais(self, user, senha_provisoria, loja_associada):
        """Envia email com as credenciais de acesso"""
        
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            nome_loja = loja_associada.nome if loja_associada else "Sistema FATESA"
            
            assunto = f"Credenciais de Acesso - {nome_loja}"
            
            mensagem = f"""
Olá {user.first_name},

Suas credenciais de acesso ao Sistema FATESA foram criadas:

🏪 Loja: {nome_loja}
👤 Usuário: {user.username}
🔑 Senha: {senha_provisoria}
🌐 Acesso: http://localhost:8000/avaliacao-qualidade/

⚠️ IMPORTANTE:
- Esta é uma senha provisória
- Altere sua senha no primeiro acesso
- Mantenha suas credenciais em segurança

Para acessar o sistema:
1. Acesse o link acima
2. Faça login com suas credenciais
3. Altere sua senha no menu "Meu Perfil"

Em caso de dúvidas, entre em contato com o administrador.

Atenciosamente,
Equipe FATESA
            """
            
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            print(f"✅ Email enviado para {user.email} com credenciais de acesso")
            
        except Exception as e:
            print(f"⚠️ Erro ao enviar email para {user.email}: {str(e)}")
            print(f"Credenciais: {user.username} / {senha_provisoria}")


class EditarUsuarioForm(forms.ModelForm):
    """Formulário para editar usuários existentes"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    
    nome_completo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    tipo_perfil = forms.ChoiceField(
        choices=PerfilUsuario.TIPO_PERFIL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    telefone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    especialidade = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    cursos_coordenados = forms.ModelMultipleChoiceField(
        queryset=None,  # Será definido no __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    ativo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.perfil = kwargs.pop('perfil', None)
        super().__init__(*args, **kwargs)
        
        # Definir queryset para cursos coordenados
        try:
            self.fields['cursos_coordenados'].queryset = Curso.objects.filter(ativo=True)
        except Exception:
            # Se houver erro ao acessar o banco, usar queryset vazio
            self.fields['cursos_coordenados'].queryset = Curso.objects.none()
        
        if self.perfil:
            self.fields['nome_completo'].initial = self.perfil.nome_completo
            self.fields['tipo_perfil'].initial = self.perfil.tipo_perfil
            self.fields['telefone'].initial = self.perfil.telefone
            self.fields['especialidade'].initial = self.perfil.especialidade
            self.fields['cursos_coordenados'].initial = self.perfil.cursos_coordenados.all()
            self.fields['ativo'].initial = self.perfil.ativo
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este email já está em uso.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Atualizar perfil
            if self.perfil:
                self.perfil.nome_completo = self.cleaned_data['nome_completo']
                self.perfil.tipo_perfil = self.cleaned_data['tipo_perfil']
                self.perfil.telefone = self.cleaned_data.get('telefone', '')
                self.perfil.especialidade = self.cleaned_data.get('especialidade', '')
                self.perfil.ativo = self.cleaned_data.get('ativo', True)
                self.perfil.save()
                
                # Atualizar cursos coordenados
                if self.cleaned_data.get('cursos_coordenados'):
                    self.perfil.cursos_coordenados.set(self.cleaned_data['cursos_coordenados'])
                else:
                    self.perfil.cursos_coordenados.clear()
        
        return user


class AlterarSenhaForm(forms.Form):
    """Formulário para alterar senha do usuário"""
    
    senha_atual = forms.CharField(
        required=False,  # Será obrigatório apenas se não for primeira alteração
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha atual'
        })
    )
    
    nova_senha = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha (mín. 8 caracteres)'
        })
    )
    
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
        # Verificar se é primeira alteração
        self.primeira_alteracao = False
        if hasattr(user, 'perfil_fatesa') and user.perfil_fatesa.deve_alterar_senha:
            self.primeira_alteracao = True
            # Na primeira alteração, não precisa da senha atual
            self.fields['senha_atual'].widget = forms.HiddenInput()
        else:
            self.fields['senha_atual'].required = True
    
    def clean_senha_atual(self):
        senha_atual = self.cleaned_data.get('senha_atual')
        
        # Se não é primeira alteração, validar senha atual
        if not self.primeira_alteracao and senha_atual:
            if not self.user.check_password(senha_atual):
                raise ValidationError('Senha atual incorreta.')
        
        return senha_atual
    
    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if nova_senha and confirmar_senha:
            if nova_senha != confirmar_senha:
                raise ValidationError('As senhas não coincidem.')
        
        # Validar força da senha
        if nova_senha:
            if len(nova_senha) < 8:
                raise ValidationError('A senha deve ter pelo menos 8 caracteres.')
        
        return cleaned_data
    
    def save(self):
        nova_senha = self.cleaned_data['nova_senha']
        self.user.set_password(nova_senha)
        self.user.save()
        return self.user

# === FORMS BÁSICOS DO SISTEMA ===

class CursoForm(forms.ModelForm):
    """Formulário para cursos"""
    
    class Meta:
        model = Curso
        fields = ['nome', 'codigo', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CoordenadorForm(forms.ModelForm):
    """Formulário para coordenadores"""
    
    class Meta:
        model = Coordenador
        fields = ['nome', 'email', 'telefone', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProfessorForm(forms.ModelForm):
    """Formulário para professores"""
    
    class Meta:
        model = Professor
        fields = ['nome', 'email', 'telefone', 'especialidade', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidade': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AvaliacaoConfigForm(forms.ModelForm):
    """Formulário para configuração de avaliações"""
    
    class Meta:
        model = AvaliacaoConfig
        fields = ['curso', 'coordenador', 'professores', 'turma']
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'coordenador': forms.Select(attrs={'class': 'form-select'}),
            'professores': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'turma': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AvaliacaoRespostaForm(forms.ModelForm):
    """Formulário para respostas de avaliação dos alunos"""
    
    class Meta:
        model = AvaliacaoResposta
        exclude = ['avaliacao_config', 'ip_address', 'user_agent', 'data_resposta']
        widgets = {
            # Notas (0-10)
            'nota_relacionamento_professor': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_didatica_professor': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_dominio_assunto': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_conteudo_teorico': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_atividade_pratica': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_portaria': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_atendimento_aluno': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_secretaria': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_recepcao_paciente': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_biblioteca': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_setor_comercial': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_limpeza': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            'nota_cantina': forms.Select(
                choices=[(i, str(i)) for i in range(11)],
                attrs={'class': 'form-select'}
            ),
            
            # Sim/Não
            'professor_respeita_horarios': forms.RadioSelect(
                choices=[(True, 'Sim'), (False, 'Não')],
                attrs={'class': 'form-check-input'}
            ),
            
            # Selects
            'origem_conhecimento': forms.Select(attrs={'class': 'form-select'}),
            'motivo_escolha': forms.Select(attrs={'class': 'form-select'}),
            
            # Textos
            'comentarios_adicionais': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Deixe seus comentários aqui...'
            }),
            'sugestoes_melhorias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Suas sugestões são importantes para nós...'
            }),
            
            # Dados opcionais
            'nome_aluno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome (opcional)'
            }),
            'contato_aluno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone ou email (opcional)'
            }),
        }