"""
Formulários para o CRM de Vendas
"""
from django import forms
from django.core.validators import validate_email
from .models import Lead, Orcamento, ItemOrcamento, Proposta, Contrato, ProdutoServico, AssinaturaDigital, HistoricoContato
import re


class LeadForm(forms.ModelForm):
    """Formulário para criação e edição de leads"""
    
    class Meta:
        model = Lead
        fields = [
            'tipo_pessoa', 'nome', 'cpf', 'rg', 'cnpj', 'inscricao_estadual', 
            'inscricao_municipal', 'nome_fantasia', 'email', 'telefone', 'celular', 
            'whatsapp', 'empresa', 'cargo', 'ramo_atividade', 'endereco', 'cidade', 
            'estado', 'cep', 'origem', 'interesse_principal', 'observacoes', 
            'observacoes_interesse', 'valor_estimado', 'orcamento_disponivel', 
            'probabilidade', 'prazo_decisao', 'decisor', 'responsavel'
        ]
        widgets = {
            'tipo_pessoa': forms.Select(attrs={'class': 'form-select', 'onchange': 'togglePessoaFields()'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo ou Razão Social'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RG'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-control'}),
            'inscricao_municipal': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 3000-0000'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 90000-0000'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 90000-0000'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Empresa onde trabalha'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo na empresa'}),
            'ramo_atividade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ramo de atividade'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Endereço completo'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF', 'maxlength': 2}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'origem': forms.Select(attrs={'class': 'form-select'}),
            'interesse_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva o principal interesse do cliente'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações gerais'}),
            'observacoes_interesse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalhes específicos do interesse'}),
            'valor_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'orcamento_disponivel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'probabilidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'prazo_decisao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 30 dias, 2 meses'}),
            'decisor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf and self.cleaned_data.get('tipo_pessoa') == 'fisica':
            # Remove caracteres não numéricos
            cpf = re.sub(r'\D', '', cpf)
            if len(cpf) != 11:
                raise forms.ValidationError('CPF deve ter 11 dígitos')
        return cpf
    
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj and self.cleaned_data.get('tipo_pessoa') == 'juridica':
            # Remove caracteres não numéricos
            cnpj = re.sub(r'\D', '', cnpj)
            if len(cnpj) != 14:
                raise forms.ValidationError('CNPJ deve ter 14 dígitos')
        return cnpj
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_pessoa = cleaned_data.get('tipo_pessoa')
        
        if tipo_pessoa == 'fisica':
            if not cleaned_data.get('cpf'):
                self.add_error('cpf', 'CPF é obrigatório para Pessoa Física')
        elif tipo_pessoa == 'juridica':
            if not cleaned_data.get('cnpj'):
                self.add_error('cnpj', 'CNPJ é obrigatório para Pessoa Jurídica')
        
        return cleaned_data


class ProdutoServicoForm(forms.ModelForm):
    """Formulário para produtos e serviços"""
    
    class Meta:
        model = ProdutoServico
        fields = ['tipo', 'codigo', 'nome', 'descricao', 'categoria', 'preco_base', 'unidade', 'ativo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código interno'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto/serviço'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoria'}),
            'preco_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'un, h, kg, m²'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OrcamentoForm(forms.ModelForm):
    """Formulário para orçamentos"""
    
    class Meta:
        model = Orcamento
        fields = [
            'lead', 'titulo', 'descricao', 'condicoes_pagamento', 
            'prazo_entrega', 'validade_dias', 'desconto', 'impostos'
        ]
        widgets = {
            'lead': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do orçamento'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'condicoes_pagamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'prazo_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'validade_dias': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'impostos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class ItemOrcamentoForm(forms.ModelForm):
    """Formulário para itens do orçamento"""
    
    class Meta:
        model = ItemOrcamento
        fields = [
            'produto_servico', 'descricao', 'detalhes', 'quantidade', 
            'unidade', 'valor_unitario', 'desconto_percentual', 'desconto_valor'
        ]
        widgets = {
            'produto_servico': forms.Select(attrs={'class': 'form-select', 'onchange': 'preencherDadosProduto()'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'detalhes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'desconto_percentual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'desconto_valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class PropostaForm(forms.ModelForm):
    """Formulário para propostas"""
    
    class Meta:
        model = Proposta
        fields = [
            'lead', 'orcamento', 'titulo', 'resumo_executivo', 'objetivos', 
            'metodologia', 'cronograma', 'investimento', 'valor_total', 
            'condicoes_comerciais', 'prazo_validade'
        ]
        widgets = {
            'lead': forms.Select(attrs={'class': 'form-select'}),
            'orcamento': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'resumo_executivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'metodologia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cronograma': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'investimento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'condicoes_comerciais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prazo_validade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class ContratoForm(forms.ModelForm):
    """Formulário para contratos"""
    
    class Meta:
        model = Contrato
        fields = [
            'lead', 'proposta', 'titulo', 'objeto', 'clausulas', 'valor_total',
            'data_inicio', 'data_fim', 'prazo_meses', 'forma_pagamento', 'condicoes_especiais'
        ]
        widgets = {
            'lead': forms.Select(attrs={'class': 'form-select'}),
            'proposta': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'clausulas': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prazo_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'forma_pagamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'condicoes_especiais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class HistoricoContatoForm(forms.ModelForm):
    """Formulário para registro de contatos"""
    
    class Meta:
        model = HistoricoContato
        fields = [
            'tipo', 'assunto', 'descricao', 'resultado', 'proximo_passo', 'data_proximo_contato'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assunto do contato'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o contato realizado'}),
            'resultado': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Resultado obtido'}),
            'proximo_passo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Próximos passos'}),
            'data_proximo_contato': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class AssinaturaDigitalForm(forms.ModelForm):
    """Formulário para solicitação de assinatura digital"""
    
    class Meta:
        model = AssinaturaDigital
        fields = [
            'nome_signatario', 'email_signatario', 'cpf_signatario', 'observacoes'
        ]
        widgets = {
            'nome_signatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do signatário'}),
            'email_signatario': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'cpf_signatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações sobre a assinatura'}),
        }