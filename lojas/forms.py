from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Loja, Cliente, Produto
from planos.models import PlanoComercial


class LojaForm(forms.ModelForm):
    """Formulário para criação e edição de lojas"""
    
    plano_comercial = forms.ModelChoiceField(
        queryset=PlanoComercial.objects.filter(status='ativo'),
        required=True,
        empty_label="Selecione um plano comercial",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'plano_comercial',
            'onchange': 'showPlanDetails(this.value)'
        }),
        help_text="Escolha o plano comercial que será associado à loja"
    )
    
    class Meta:
        model = Loja
        fields = [
            'nome', 'cnpj', 'email', 'telefone', 'endereco', 
            'cidade', 'estado', 'cep', 'status', 'tipo_loja', 'plano_comercial'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SP, RJ, MG...'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'tipo_loja': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campo estado agora é texto livre
        self.fields['estado'].required = False
        
        # Melhora o campo tipo_loja
        self.fields['tipo_loja'].required = False
        self.fields['tipo_loja'].empty_label = "Selecione o tipo de atividade da loja"
        
        # Filtra apenas tipos de loja ativos
        from modulos.models import TipoLoja
        self.fields['tipo_loja'].queryset = TipoLoja.objects.filter(ativo=True)
        
        # Configura o campo plano_comercial
        self.fields['plano_comercial'].queryset = PlanoComercial.objects.filter(
            status='ativo'
        ).order_by('ordem_exibicao', 'preco_mensal')
        
        # Se estamos editando uma loja existente, o plano não é obrigatório
        if self.instance and self.instance.pk:
            self.fields['plano_comercial'].required = False
            self.fields['plano_comercial'].help_text = "Deixe em branco para manter o plano atual"
    
    def clean_plano_comercial(self):
        """Valida a seleção do plano comercial"""
        plano = self.cleaned_data.get('plano_comercial')
        
        # Para novas lojas, o plano é obrigatório
        if not self.instance.pk and not plano:
            raise forms.ValidationError("É obrigatório selecionar um plano comercial para novas lojas.")
        
        # Verifica se o plano está ativo
        if plano and plano.status != 'ativo':
            raise forms.ValidationError("O plano selecionado não está ativo.")
        
        return plano
    
    def clean(self):
        """Validação geral do formulário"""
        cleaned_data = super().clean()
        
        # Validações adicionais podem ser adicionadas aqui
        return cleaned_data


class ClienteForm(forms.ModelForm):
    """Formulário para criação e edição de clientes"""
    
    class Meta:
        model = Cliente
        fields = [
            'nome', 'email', 'telefone', 'cpf', 'data_nascimento', 
            'sexo', 'endereco', 'cidade', 'estado', 'cep'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SP, RJ, MG...'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campo estado agora é texto livre
        self.fields['estado'].required = False


class ProdutoForm(forms.ModelForm):
    """Formulário para criação e edição de produtos"""
    
    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'categoria', 'preco', 'estoque', 
            'codigo_barras', 'imagem', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        loja_tipo = kwargs.pop('loja_tipo', None)
        super().__init__(*args, **kwargs)
        
        # Se for lanchonete, usar categorias específicas
        if loja_tipo == 'lanchonete':
            self.fields['categoria'].choices = [
                ('', 'Selecione uma categoria'),
                ('lanches', 'Lanches'),
                ('bebidas', 'Bebidas'),
                ('sobremesas', 'Sobremesas'),
                ('porcoes', 'Porções'),
                ('combos', 'Combos'),
                ('outros', 'Outros'),
            ]


class CustomUserCreationForm(UserCreationForm):
    """Formulário personalizado para criação de usuários"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona classes Bootstrap aos campos
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        
        return user
