"""
EXEMPLO DE USO DA CORREÇÃO AUTOMÁTICA DE BOLETOS

Este arquivo mostra como integrar a correção automática no sistema existente.
"""

# ============================================================================
# 1. EXEMPLO EM VIEW DE PROCESSAMENTO DE BOLETO
# ============================================================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from controle_financeiro.utils import processar_boleto_com_correcao, BoletoValidationMixin
from controle_financeiro.models import BoletoGerado


@login_required
def processar_pagamento_boleto(request):
    """Exemplo de view que processa pagamento via boleto"""
    
    if request.method == 'POST':
        linha_digitavel = request.POST.get('linha_digitavel', '').strip()
        
        if not linha_digitavel:
            messages.error(request, "Por favor, informe a linha digitável do boleto.")
            return render(request, 'boleto_form.html')
        
        # CORREÇÃO AUTOMÁTICA APLICADA AQUI
        resultado = processar_boleto_com_correcao(request, linha_digitavel, "boleto")
        
        if resultado['success']:
            # Usar o código corrigido (se foi corrigido) ou original (se já estava válido)
            codigo_final = resultado['codigo_final']
            
            # Processar o boleto normalmente
            try:
                # Buscar boleto no banco ou criar novo
                boleto = BoletoGerado.objects.filter(linha_digitavel=codigo_final).first()
                
                if boleto:
                    boleto.marcar_como_pago()
                    messages.success(request, f"Pagamento do boleto {boleto.numero_boleto} confirmado!")
                else:
                    messages.warning(request, "Boleto não encontrado no sistema.")
                
                return redirect('dashboard_financeiro')
                
            except Exception as e:
                messages.error(request, f"Erro ao processar boleto: {str(e)}")
        
        # Se chegou aqui, houve erro (mensagens já foram adicionadas pela função)
        return render(request, 'boleto_form.html', {'linha_digitavel': linha_digitavel})
    
    return render(request, 'boleto_form.html')


# ============================================================================
# 2. EXEMPLO USANDO MIXIN EM CLASS-BASED VIEW
# ============================================================================

from django.views.generic import FormView
from django import forms


class BoletoForm(forms.Form):
    linha_digitavel = forms.CharField(
        max_length=54,
        label="Linha Digitável",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a linha digitável do boleto'
        })
    )


class ProcessarBoletoView(BoletoValidationMixin, FormView):
    """Exemplo usando class-based view com mixin"""
    
    template_name = 'boleto_form.html'
    form_class = BoletoForm
    success_url = '/dashboard/'
    
    def form_valid(self, form):
        linha_digitavel = form.cleaned_data['linha_digitavel']
        
        # Usar o mixin para validar
        resultado = self.validate_boleto_code(linha_digitavel, "boleto")
        
        if resultado['success']:
            codigo_final = resultado['codigo_final']
            
            # Processar boleto...
            # (mesmo código do exemplo anterior)
            
            return super().form_valid(form)
        
        else:
            # Erro já foi adicionado às mensagens pelo mixin
            return self.form_invalid(form)


# ============================================================================
# 3. EXEMPLO DE VALIDAÇÃO EM FORMULÁRIO DJANGO
# ============================================================================

from controle_financeiro.boleto_auto_validator import validate_boleto_auto


class BoletoFormComValidacao(forms.Form):
    linha_digitavel = forms.CharField(max_length=54, label="Linha Digitável")
    
    def clean_linha_digitavel(self):
        linha_digitavel = self.cleaned_data['linha_digitavel']
        
        # Validar com correção automática
        resultado = validate_boleto_auto(linha_digitavel)
        
        if not resultado['success']:
            raise forms.ValidationError(f"Código inválido: {resultado['message']}")
        
        # Retornar código corrigido (se foi corrigido) ou original
        codigo_final = resultado['final_code']
        
        # Adicionar informação sobre correção ao formulário
        if resultado['corrected']:
            self.add_error(None, forms.ValidationError(
                f"Código corrigido automaticamente: {resultado['message']}",
                code='info'
            ))
        
        return codigo_final


# ============================================================================
# 4. EXEMPLO DE USO DIRETO NAS FUNÇÕES
# ============================================================================

from controle_financeiro.boleto_auto_validator import (
    get_valid_boleto_code, 
    is_boleto_valid,
    validate_boleto_auto
)


def exemplo_uso_direto():
    """Exemplos de uso direto das funções"""
    
    # Código com erro (exemplo do usuário)
    codigo_com_erro = "10492.67014 51854.100826 72946.570149 8 22600000002990"
    
    # 1. Verificar se é válido (com correção automática)
    if is_boleto_valid(codigo_com_erro):
        print("✅ Código é válido (pode ter sido corrigido automaticamente)")
    else:
        print("❌ Código inválido e não pode ser corrigido")
    
    # 2. Obter código válido
    codigo_valido = get_valid_boleto_code(codigo_com_erro)
    print(f"Código final: {codigo_valido}")
    
    # 3. Validação completa com detalhes
    resultado = validate_boleto_auto(codigo_com_erro)
    
    if resultado['success']:
        print(f"✅ Sucesso: {resultado['message']}")
        print(f"Código original: {resultado['original_code']}")
        print(f"Código final: {resultado['final_code']}")
        print(f"Foi corrigido: {resultado['corrected']}")
        
        if resultado['corrected']:
            print("Correções aplicadas:")
            for correction in resultado['corrections']:
                print(f"  - Campo {correction['campo']}: {correction['dv_original']} → {correction['dv_correto']}")
    
    else:
        print(f"❌ Erro: {resultado['message']}")


# ============================================================================
# 5. EXEMPLO DE INTEGRAÇÃO COM MODELO EXISTENTE
# ============================================================================

# No seu modelo BoletoGerado (já implementado acima), você pode usar:

def exemplo_modelo():
    """Exemplo de como o modelo usa correção automática"""
    
    # Criar boleto com código que tem erro
    boleto = BoletoGerado(
        linha_digitavel="10492.67014 51854.100826 72946.570149 8 22600000002990",
        # ... outros campos
    )
    
    # Ao salvar, a correção é aplicada automaticamente
    boleto.save()
    
    # O código foi corrigido automaticamente e salvo
    print(f"Código salvo: {boleto.linha_digitavel}")
    print(f"Observações: {boleto.observacoes}")  # Contém log da correção


# ============================================================================
# 6. TEMPLATE EXEMPLO
# ============================================================================

TEMPLATE_EXEMPLO = """
<!-- boleto_form.html -->
<form method="post">
    {% csrf_token %}
    
    <div class="form-group">
        <label for="linha_digitavel">Linha Digitável do Boleto:</label>
        <input type="text" 
               name="linha_digitavel" 
               class="form-control" 
               placeholder="Digite ou cole a linha digitável"
               value="{{ linha_digitavel|default:'' }}">
        <small class="form-text text-muted">
            💡 O sistema corrige automaticamente pequenos erros de digitação
        </small>
    </div>
    
    <button type="submit" class="btn btn-primary">
        <i class="fas fa-check"></i> Processar Boleto
    </button>
</form>

<!-- Mensagens automáticas aparecerão aqui -->
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    {% endfor %}
{% endif %}
"""


if __name__ == "__main__":
    # Executar exemplo
    exemplo_uso_direto()