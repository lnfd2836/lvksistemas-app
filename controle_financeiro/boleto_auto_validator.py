"""
Validador Automático de Boletos
Aplica correção automática transparente ao usuário
"""

import logging
from typing import Dict, Any, Optional, Tuple

try:
    from .boleto_simple_corrector import BoletoSimpleCorrector
    from .boleto_validator_unified import BoletoValidatorUnified
except ImportError:
    from boleto_simple_corrector import BoletoSimpleCorrector
    from boleto_validator_unified import BoletoValidatorUnified


logger = logging.getLogger('boleto_auto_validator')


class BoletoAutoValidator:
    """
    Validador que aplica correção automática de forma transparente
    """
    
    def __init__(self, auto_correct: bool = True, log_corrections: bool = True):
        self.corrector = BoletoSimpleCorrector()
        self.validator = BoletoValidatorUnified()
        self.auto_correct = auto_correct
        self.log_corrections = log_corrections
    
    def validate_and_auto_correct(self, codigo_input: str) -> Dict[str, Any]:
        """
        Valida e corrige automaticamente o código
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            Dict: Resultado com código final e informações de correção
        """
        
        # Primeiro, tentar validação normal
        validation_result = self.validator.validate(codigo_input)
        
        if validation_result.is_valid:
            # Código já é válido
            return {
                'success': True,
                'is_valid': True,
                'original_code': codigo_input,
                'final_code': codigo_input,
                'corrected': False,
                'message': 'Código válido - nenhuma correção necessária',
                'corrections': []
            }
        
        # Se não é válido e correção automática está habilitada
        if self.auto_correct:
            correction_result = self.corrector.correct_single_dv_error(codigo_input)
            
            if correction_result['success'] and correction_result.get('corrections'):
                # Código foi corrigido - validar novamente
                corrected_code = correction_result['corrected_code']
                final_validation = self.validator.validate(corrected_code)
                
                if final_validation.is_valid:
                    # Correção bem-sucedida
                    corrections_info = []
                    for correction in correction_result['corrections']:
                        corrections_info.append(f"Campo {correction['campo']}: DV {correction['dv_original']} → {correction['dv_correto']}")
                    
                    message = f"Código corrigido automaticamente: {', '.join(corrections_info)}"
                    
                    if self.log_corrections:
                        logger.info(f"Auto-correction applied: {message}")
                    
                    return {
                        'success': True,
                        'is_valid': True,
                        'original_code': codigo_input,
                        'final_code': corrected_code,
                        'corrected': True,
                        'message': message,
                        'corrections': correction_result['corrections'],
                        'correction_confidence': correction_result.get('confidence', 'medium')
                    }
                
                else:
                    # Correção não resolveu o problema
                    return {
                        'success': False,
                        'is_valid': False,
                        'original_code': codigo_input,
                        'final_code': codigo_input,
                        'corrected': False,
                        'message': 'Código tem erros que não podem ser corrigidos automaticamente',
                        'errors': final_validation.errors
                    }
            
            else:
                # Não foi possível corrigir
                return {
                    'success': False,
                    'is_valid': False,
                    'original_code': codigo_input,
                    'final_code': codigo_input,
                    'corrected': False,
                    'message': correction_result.get('error', 'Código inválido e não pode ser corrigido'),
                    'errors': validation_result.errors
                }
        
        else:
            # Correção automática desabilitada
            return {
                'success': False,
                'is_valid': False,
                'original_code': codigo_input,
                'final_code': codigo_input,
                'corrected': False,
                'message': 'Código inválido (correção automática desabilitada)',
                'errors': validation_result.errors
            }
    
    def get_valid_code(self, codigo_input: str) -> Tuple[str, bool]:
        """
        Retorna código válido e se foi corrigido
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            Tuple[str, bool]: (código_final, foi_corrigido)
        """
        
        result = self.validate_and_auto_correct(codigo_input)
        
        if result['success']:
            return result['final_code'], result['corrected']
        else:
            # Se não conseguiu corrigir, retorna o original
            return codigo_input, False
    
    def is_valid_after_correction(self, codigo_input: str) -> bool:
        """
        Verifica se o código é válido (após correção se necessário)
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            bool: True se válido (original ou corrigido)
        """
        
        result = self.validate_and_auto_correct(codigo_input)
        return result['success'] and result['is_valid']


# Instância global para uso no sistema
auto_validator = BoletoAutoValidator(auto_correct=True, log_corrections=True)


def validate_boleto_auto(codigo_input: str) -> Dict[str, Any]:
    """
    Função de conveniência para validação automática
    
    Args:
        codigo_input: Código de barras ou linha digitável
        
    Returns:
        Dict: Resultado da validação com correção automática
    """
    
    return auto_validator.validate_and_auto_correct(codigo_input)


def get_valid_boleto_code(codigo_input: str) -> str:
    """
    Função de conveniência que retorna código válido
    
    Args:
        codigo_input: Código de entrada
        
    Returns:
        str: Código válido (original ou corrigido)
    """
    
    valid_code, _ = auto_validator.get_valid_code(codigo_input)
    return valid_code


def is_boleto_valid(codigo_input: str) -> bool:
    """
    Função de conveniência para verificar se boleto é válido
    
    Args:
        codigo_input: Código de entrada
        
    Returns:
        bool: True se válido (com ou sem correção)
    """
    
    return auto_validator.is_valid_after_correction(codigo_input)