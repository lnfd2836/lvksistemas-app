from django import forms
from .models import TipoLoja


class TipoLojaForm(forms.ModelForm):
    """Formulário para criar e editar tipos de loja"""
    
    class Meta:
        model = TipoLoja
        fields = [
            'nome', 'descricao', 'icone', 'cor_primaria', 'cor_secundaria',
            'tem_categoria_produto', 'tem_marca_produto', 'tem_tamanho_produto',
            'tem_cor_produto', 'tem_peso_produto', 'tem_volume_produto',
            'tem_data_validade', 'tem_codigo_barras', 'tem_estoque_minimo',
            'tem_data_nascimento_cliente', 'tem_sexo_cliente', 'tem_cpf_cliente',
            'tem_rg_cliente', 'tem_cnpj_cliente', 'tem_crm_cliente',
            'tem_desconto_venda', 'tem_taxa_entrega', 'tem_mesa_venda', 'tem_garcom_venda',
            'ativo'
        ]
        widgets = {
            'nome': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icone': forms.TextInput(attrs={'class': 'form-control'}),
            'cor_primaria': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'cor_secundaria': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS aos campos booleanos
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['descricao']:
                field.widget.attrs.update({'class': 'form-control'})
            elif field_name in ['icone']:
                field.widget.attrs.update({'class': 'form-control'})