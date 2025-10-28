from django import forms
from .models import TipoLoja


class TipoLojaForm(forms.ModelForm):
    """Formulário simplificado para criar e editar tipos de loja"""
    
    class Meta:
        model = TipoLoja
        fields = [
            'nome', 'descricao', 'icone', 'cor_primaria', 'cor_secundaria', 'ativo'
        ]
        widgets = {
            'nome': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: fas fa-store'}),
            'cor_primaria': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'cor_secundaria': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'nome': 'Selecione o tipo de loja que melhor descreve o negócio',
            'descricao': 'Descrição detalhada do tipo de loja',
            'icone': 'Classe CSS do ícone (Font Awesome)',
            'cor_primaria': 'Cor principal para temas e interface',
            'cor_secundaria': 'Cor secundária para detalhes',
        }