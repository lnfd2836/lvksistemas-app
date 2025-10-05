from django import forms
from django.forms import inlineformset_factory
from .models import TipoLoja, CampoPersonalizado, ValorCampoPersonalizado
from lojas.models import Produto


class ProdutoFormDinamico(forms.ModelForm):
    """Formulário dinâmico para produtos baseado no tipo de loja"""
    
    def __init__(self, *args, **kwargs):
        tipo_loja = kwargs.pop('tipo_loja', None)
        super().__init__(*args, **kwargs)
        
        if tipo_loja:
            self.tipo_loja = tipo_loja
            self._adicionar_campos_personalizados()
    
    def _adicionar_campos_personalizados(self):
        """Adiciona campos personalizados baseados no tipo de loja"""
        if not hasattr(self, 'tipo_loja') or not self.tipo_loja:
            return
        
        # Campos personalizados do tipo de loja
        campos = CampoPersonalizado.objects.filter(
            tipo_loja=self.tipo_loja,
            ativo=True
        ).order_by('ordem')
        
        for campo in campos:
            field_name = f'campo_{campo.slug}'
            
            if campo.tipo_campo == 'texto':
                self.fields[field_name] = forms.CharField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            elif campo.tipo_campo == 'numero':
                self.fields[field_name] = forms.IntegerField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
            elif campo.tipo_campo == 'decimal':
                self.fields[field_name] = forms.DecimalField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
                )
            elif campo.tipo_campo == 'data':
                self.fields[field_name] = forms.DateField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                )
            elif campo.tipo_campo == 'hora':
                self.fields[field_name] = forms.TimeField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
                )
            elif campo.tipo_campo == 'boolean':
                self.fields[field_name] = forms.BooleanField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )
            elif campo.tipo_campo == 'escolha':
                opcoes = [(opcao, opcao) for opcao in campo.get_opcoes_list()]
                self.fields[field_name] = forms.ChoiceField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    choices=[('', 'Selecione...')] + opcoes,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            elif campo.tipo_campo == 'multipla_escolha':
                opcoes = [(opcao, opcao) for opcao in campo.get_opcoes_list()]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=campo.nome,
                    required=campo.obrigatorio,
                    choices=opcoes,
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                )
    
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'categoria', 'preco', 'estoque', 'codigo_barras', 'imagem', 'ativo']
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


class ClienteFormDinamico(forms.ModelForm):
    """Formulário dinâmico para clientes baseado no tipo de loja"""
    
    def __init__(self, *args, **kwargs):
        tipo_loja = kwargs.pop('tipo_loja', None)
        super().__init__(*args, **kwargs)
        
        if tipo_loja:
            self.tipo_loja = tipo_loja
            self._configurar_campos_cliente()
    
    def _configurar_campos_cliente(self):
        """Configura campos de cliente baseados no tipo de loja"""
        if not hasattr(self, 'tipo_loja') or not self.tipo_loja:
            return
        
        config = self.tipo_loja.get_configuracoes()
        
        # Configura campos baseado no tipo de loja
        if not config['data_nascimento_cliente']:
            self.fields.pop('data_nascimento', None)
        
        if not config['sexo_cliente']:
            self.fields.pop('sexo', None)
        
        if not config['cpf_cliente']:
            self.fields.pop('cpf', None)
    
    class Meta:
        from lojas.models import Cliente
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


class VendaFormDinamico(forms.ModelForm):
    """Formulário dinâmico para vendas baseado no tipo de loja"""
    
    def __init__(self, *args, **kwargs):
        tipo_loja = kwargs.pop('tipo_loja', None)
        super().__init__(*args, **kwargs)
        
        if tipo_loja:
            self.tipo_loja = tipo_loja
            self._configurar_campos_venda()
    
    def _configurar_campos_venda(self):
        """Configura campos de venda baseados no tipo de loja"""
        if not hasattr(self, 'tipo_loja') or not self.tipo_loja:
            return
        
        config = self.tipo_loja.get_configuracoes()
        
        # Adiciona campos específicos do tipo de loja
        if config['taxa_entrega']:
            self.fields['taxa_entrega'] = forms.DecimalField(
                label='Taxa de Entrega',
                required=False,
                initial=0,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
            )
        
        if config['mesa_venda']:
            self.fields['mesa'] = forms.CharField(
                label='Mesa',
                required=False,
                max_length=10,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
        
        if config['garcom_venda']:
            self.fields['garcom'] = forms.CharField(
                label='Garçom',
                required=False,
                max_length=100,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
    
    class Meta:
        from lojas.models import Venda
        model = Venda
        fields = ['cliente', 'valor_total', 'desconto', 'status']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
