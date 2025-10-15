from django import forms
from django.contrib.auth.models import User
from .models import (
    ServicoEstetica, ProtocoloEmagrecimento, Agendamento, 
    Retorno, FichaAnamnese, EvolucaoTratamento, PacoteTratamento
)
from lojas.models import Cliente


class AgendamentoForm(forms.ModelForm):
    """Formulário para criação de agendamentos"""
    
    class Meta:
        model = Agendamento
        fields = [
            'cliente', 'servico', 'protocolo', 'data_agendamento', 
            'hora_inicio', 'profissional', 'observacoes'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'servico': forms.Select(attrs={'class': 'form-control'}),
            'protocolo': forms.Select(attrs={'class': 'form-control'}),
            'data_agendamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'profissional': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nome')
        self.fields['servico'].queryset = ServicoEstetica.objects.filter(ativo=True).order_by('categoria', 'nome')
        self.fields['protocolo'].queryset = ProtocoloEmagrecimento.objects.filter(ativo=True).order_by('nome')
        self.fields['profissional'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['protocolo'].required = False


class ServicoEsteticaForm(forms.ModelForm):
    """Formulário para criação/edição de serviços de estética"""
    
    class Meta:
        model = ServicoEstetica
        fields = [
            'nome', 'descricao', 'categoria', 'duracao_minutos', 
            'preco', 'preco_promocional', 'requer_consulta_medica', 
            'idade_minima', 'contraindicacoes', 'cuidados_pos_procedimento'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'duracao_minutos': forms.Select(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_promocional': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'requer_consulta_medica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'idade_minima': forms.NumberInput(attrs={'class': 'form-control'}),
            'contraindicacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cuidados_pos_procedimento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProtocoloEmagrecimentoForm(forms.ModelForm):
    """Formulário para criação/edição de protocolos de emagrecimento"""
    
    class Meta:
        model = ProtocoloEmagrecimento
        fields = [
            'nome', 'descricao', 'tipo_protocolo', 'numero_sessoes', 
            'intervalo_dias', 'duracao_sessao_minutos', 'preco_total', 
            'preco_sessao', 'indicacoes', 'contraindicacoes', 'resultados_esperados'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo_protocolo': forms.Select(attrs={'class': 'form-control'}),
            'numero_sessoes': forms.NumberInput(attrs={'class': 'form-control'}),
            'intervalo_dias': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracao_sessao_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
            'preco_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_sessao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'indicacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contraindicacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resultados_esperados': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FichaAnamneseForm(forms.ModelForm):
    """Formulário para ficha de anamnese do cliente"""
    
    class Meta:
        model = FichaAnamnese
        fields = [
            'tipo_pele', 'alergias', 'medicamentos_uso', 'tratamentos_anteriores',
            'problemas_circulatorios', 'diabetes', 'hipertensao', 'gravidez', 
            'amamentacao', 'objetivos_tratamento', 'expectativas'
        ]
        widgets = {
            'tipo_pele': forms.Select(attrs={'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medicamentos_uso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamentos_anteriores': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'problemas_circulatorios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'diabetes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hipertensao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gravidez': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'amamentacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'objetivos_tratamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'expectativas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EvolucaoTratamentoForm(forms.ModelForm):
    """Formulário para evolução do tratamento"""
    
    class Meta:
        model = EvolucaoTratamento
        fields = [
            'agendamento', 'peso_inicial', 'peso_atual', 'medidas_corporais',
            'fotos_antes', 'fotos_depois', 'observacoes_profissional', 
            'observacoes_cliente', 'proximos_passos'
        ]
        widgets = {
            'agendamento': forms.Select(attrs={'class': 'form-control'}),
            'peso_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'peso_atual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'medidas_corporais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fotos_antes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fotos_depois': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observacoes_profissional': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'observacoes_cliente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proximos_passos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, cliente=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente:
            self.fields['agendamento'].queryset = Agendamento.objects.filter(
                cliente=cliente
            ).order_by('-data_agendamento')


class RetornoForm(forms.ModelForm):
    """Formulário para agendamento de retornos"""
    
    class Meta:
        model = Retorno
        fields = [
            'agendamento_original', 'tipo_retorno', 'data_retorno', 
            'hora_retorno', 'motivo_retorno', 'observacoes'
        ]
        widgets = {
            'agendamento_original': forms.Select(attrs={'class': 'form-control'}),
            'tipo_retorno': forms.Select(attrs={'class': 'form-control'}),
            'data_retorno': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_retorno': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo_retorno': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PacoteTratamentoForm(forms.ModelForm):
    """Formulário para criação/edição de pacotes de tratamento"""
    
    class Meta:
        model = PacoteTratamento
        fields = [
            'nome', 'descricao', 'servicos', 'protocolo', 'numero_sessoes',
            'validade_dias', 'preco_total', 'desconto_percentual'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'servicos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'protocolo': forms.Select(attrs={'class': 'form-control'}),
            'numero_sessoes': forms.NumberInput(attrs={'class': 'form-control'}),
            'validade_dias': forms.NumberInput(attrs={'class': 'form-control'}),
            'preco_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desconto_percentual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servicos'].queryset = ServicoEstetica.objects.filter(ativo=True).order_by('categoria', 'nome')
        self.fields['protocolo'].queryset = ProtocoloEmagrecimento.objects.filter(ativo=True).order_by('nome')
        self.fields['protocolo'].required = False


class FiltroAgendamentosForm(forms.Form):
    """Formulário de filtros para agendamentos"""
    
    STATUS_CHOICES = [('', 'Todos os Status')] + list(Agendamento.STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    profissional = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="Todos os Profissionais",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FiltroServicosForm(forms.Form):
    """Formulário de filtros para serviços"""
    
    CATEGORIA_CHOICES = [('', 'Todas as Categorias')] + list(ServicoEstetica.CATEGORIA_CHOICES)
    
    categoria = forms.ChoiceField(
        choices=CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    ativo = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Ativos'), ('false', 'Inativos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FiltroProtocolosForm(forms.Form):
    """Formulário de filtros para protocolos"""
    
    TIPO_PROTOCOLO_CHOICES = [('', 'Todos os Tipos')] + list(ProtocoloEmagrecimento.TIPO_PROTOCOLO_CHOICES)
    
    tipo_protocolo = forms.ChoiceField(
        choices=TIPO_PROTOCOLO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    ativo = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Ativos'), ('false', 'Inativos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class RelatoriosForm(forms.Form):
    """Formulário de filtros para relatórios"""
    
    data_inicio = forms.DateField(
        label="Data Início",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    data_fim = forms.DateField(
        label="Data Fim",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
