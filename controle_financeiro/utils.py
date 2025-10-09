"""
Utilitários para o sistema de controle financeiro
"""

from django.contrib import messages
from django.utils import timezone
from .boleto_auto_validator import auto_validator
from .boleto_fix_especifico import (
    corrigir_boleto_especifico,
    processar_boleto_com_correcao_django,
    validar_e_corrigir_boleto_simples
)


def processar_boleto_com_correcao(request, codigo_input, context_name="boleto"):
    """
    Processa boleto com correção automática e adiciona mensagens apropriadas
    
    Args:
        request: Request do Django
        codigo_input: Código de barras ou linha digitável
        context_name: Nome para usar nas mensagens (ex: "boleto", "pagamento")
        
    Returns:
        Dict: Resultado do processamento
    """
    
    # Primeiro, tentar correção específica conhecida
    resultado_especifico = processar_boleto_com_correcao_django(request, codigo_input, context_name)
    
    if resultado_especifico['success']:
        return resultado_especifico
    
    # Se não há correção específica, usar validador automático
    result = auto_validator.validate_and_auto_correct(codigo_input)
    
    if result['success']:
        if result['corrected']:
            # Código foi corrigido automaticamente
            corrections_text = []
            for correction in result['corrections']:
                corrections_text.append(f"Campo {correction['campo']}")
            
            message = f"✅ {context_name.title()} processado com sucesso! "
            message += f"Foram corrigidos automaticamente erros nos dígitos verificadores dos campos: {', '.join(corrections_text)}."
            
            messages.success(request, message)
            
            # Adicionar mensagem informativa sobre a correção
            messages.info(request, 
                f"ℹ️ O código original tinha pequenos erros que foram corrigidos automaticamente. "
                f"Esta é uma funcionalidade de segurança para evitar rejeições por erros de digitação."
            )
        
        else:
            # Código já estava válido
            messages.success(request, f"✅ {context_name.title()} validado com sucesso!")
        
        return {
            'success': True,
            'codigo_final': result['final_code'],
            'foi_corrigido': result['corrected'],
            'message': result['message']
        }
    
    else:
        # Não foi possível processar
        error_message = f"❌ Erro no {context_name}: {result['message']}"
        
        if 'errors' in result:
            error_message += f" Detalhes: {', '.join(result['errors'])}"
        
        messages.error(request, error_message)
        
        # Sugerir ações
        messages.info(request, 
            f"💡 Sugestões: Verifique se o código foi digitado corretamente ou "
            f"solicite uma nova via do {context_name}."
        )
        
        return {
            'success': False,
            'codigo_final': codigo_input,
            'foi_corrigido': False,
            'message': result['message']
        }


def validar_codigo_boleto_simples(codigo_input):
    """
    Validação simples que retorna apenas True/False
    
    Args:
        codigo_input: Código de entrada
        
    Returns:
        bool: True se válido (com ou sem correção)
    """
    
    return auto_validator.is_valid_after_correction(codigo_input)


def obter_codigo_boleto_valido(codigo_input):
    """
    Obtém código válido (corrigido se necessário)
    
    Args:
        codigo_input: Código de entrada
        
    Returns:
        str: Código válido
    """
    
    valid_code, _ = auto_validator.get_valid_code(codigo_input)
    return valid_code


def log_correcao_boleto(boleto_obj, result):
    """
    Adiciona log de correção ao objeto boleto
    
    Args:
        boleto_obj: Instância do modelo BoletoGerado
        result: Resultado da validação/correção
    """
    
    if result.get('corrected'):
        corrections_info = []
        for correction in result['corrections']:
            corrections_info.append(f"Campo {correction['campo']}: DV {correction['dv_original']} → {correction['dv_correto']}")
        
        log_message = f"Correção automática: {', '.join(corrections_info)}"
        
        if boleto_obj.observacoes:
            boleto_obj.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: {log_message}"
        else:
            boleto_obj.observacoes = f"{timezone.now().strftime('%d/%m/%Y %H:%M')}: {log_message}"


class BoletoValidationMixin:
    """
    Mixin para views que precisam validar boletos
    """
    
    def validate_boleto_code(self, codigo_input, context_name="boleto"):
        """
        Valida código de boleto com correção automática
        
        Args:
            codigo_input: Código de entrada
            context_name: Nome para mensagens
            
        Returns:
            Dict: Resultado da validação
        """
        
        return processar_boleto_com_correcao(self.request, codigo_input, context_name)
    
    def get_valid_boleto_code(self, codigo_input):
        """
        Obtém código válido
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            str: Código válido
        """
        
        return obter_codigo_boleto_valido(codigo_input)