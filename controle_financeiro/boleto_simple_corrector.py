"""
Corretor Simples de DV para Boletos
Foca apenas na correção do erro específico encontrado
"""

import logging
from typing import Dict, Any, Optional

try:
    from .boleto_validator_base import DVCalculatorMixin, FormatNormalizerMixin
    from .boleto_input_normalizer import BoletoInputNormalizer
except ImportError:
    from boleto_validator_base import DVCalculatorMixin, FormatNormalizerMixin
    from boleto_input_normalizer import BoletoInputNormalizer


logger = logging.getLogger('boleto_simple_corrector')


class BoletoSimpleCorrector(DVCalculatorMixin, FormatNormalizerMixin):
    """
    Corretor simples que foca apenas no erro específico
    Corrige apenas DVs inválidos sem alterar a estrutura geral
    """
    
    def __init__(self):
        self.normalizer = BoletoInputNormalizer()
    
    def correct_single_dv_error(self, codigo_input: str) -> Dict[str, Any]:
        """
        Corrige um único erro de DV na linha digitável
        
        Args:
            codigo_input: Linha digitável com erro
            
        Returns:
            Dict: Resultado da correção
        """
        
        # Normalizar entrada
        normalized = self.normalizer.normalize(codigo_input)
        
        if not normalized.is_valid_format or normalized.input_format != "linha_digitavel":
            return {
                'success': False,
                'error': 'Formato inválido ou não é linha digitável',
                'original_code': codigo_input,
                'corrected_code': codigo_input
            }
        
        linha_limpa = normalized.normalized_code
        
        if len(linha_limpa) != 47:
            return {
                'success': False,
                'error': f'Comprimento inválido: {len(linha_limpa)} (esperado 47)',
                'original_code': codigo_input,
                'corrected_code': codigo_input
            }
        
        # Verificar cada campo individualmente
        errors_found = []
        corrections = []
        
        # Campo 1: posições 0-10 (10 dígitos + DV)
        campo1 = linha_limpa[0:11]
        dv1_error = self._check_campo_dv(campo1, 1)
        if dv1_error:
            errors_found.append(dv1_error)
        
        # Campo 2: posições 11-21 (10 dígitos + DV)
        campo2 = linha_limpa[11:22]
        dv2_error = self._check_campo_dv(campo2, 2)
        if dv2_error:
            errors_found.append(dv2_error)
        
        # Campo 3: posições 22-32 (10 dígitos + DV)
        campo3 = linha_limpa[22:33]
        dv3_error = self._check_campo_dv(campo3, 3)
        if dv3_error:
            errors_found.append(dv3_error)
        
        # Se não há erros, retornar sucesso
        if not errors_found:
            return {
                'success': True,
                'message': 'Nenhuma correção necessária - boleto válido',
                'original_code': codigo_input,
                'corrected_code': codigo_input,
                'corrections': []
            }
        
        # Se há apenas um erro, corrigir
        if len(errors_found) == 1:
            error = errors_found[0]
            corrected_code = self._apply_single_correction(linha_limpa, error)
            
            return {
                'success': True,
                'message': f'Corrigido DV do campo {error["campo"]}: {error["dv_original"]} → {error["dv_correto"]}',
                'original_code': codigo_input,
                'corrected_code': corrected_code,
                'corrections': [error],
                'confidence': 'high'
            }
        
        # Se há múltiplos erros, avaliar se pode corrigir
        else:
            # Se são apenas erros de DV (não estruturais), pode tentar corrigir
            if len(errors_found) <= 3 and all('dv_correto' in error for error in errors_found):
                corrected_code = self._apply_multiple_corrections(linha_limpa, errors_found)
                
                return {
                    'success': True,
                    'message': f'Corrigidos {len(errors_found)} dígitos verificadores',
                    'original_code': codigo_input,
                    'corrected_code': corrected_code,
                    'corrections': errors_found,
                    'confidence': 'medium' if len(errors_found) == 2 else 'low'
                }
            else:
                return {
                    'success': False,
                    'error': f'Múltiplos erros encontrados ({len(errors_found)}). Correção automática não recomendada.',
                    'original_code': codigo_input,
                    'corrected_code': codigo_input,
                    'errors_found': errors_found,
                    'confidence': 'low'
                }
    
    def _check_campo_dv(self, campo: str, campo_num: int) -> Optional[Dict[str, Any]]:
        """Verifica DV de um campo específico"""
        
        if len(campo) != 11:
            return {
                'campo': campo_num,
                'error': f'Campo {campo_num} tem comprimento inválido: {len(campo)}'
            }
        
        campo_sem_dv = campo[:-1]
        dv_informado = int(campo[-1])
        dv_calculado = self.calculate_dv_modulo10_febraban(campo_sem_dv)
        
        if dv_informado != dv_calculado:
            return {
                'campo': campo_num,
                'campo_completo': campo,
                'campo_sem_dv': campo_sem_dv,
                'dv_original': dv_informado,
                'dv_correto': dv_calculado,
                'error_message': f'DV do campo {campo_num} inválido: informado {dv_informado}, calculado {dv_calculado}'
            }
        
        return None
    
    def _apply_single_correction(self, linha_limpa: str, error: Dict[str, Any]) -> str:
        """Aplica uma única correção na linha digitável"""
        
        campo_num = error['campo']
        dv_correto = error['dv_correto']
        
        # Determinar posições do campo
        if campo_num == 1:
            start_pos = 0
            end_pos = 11
        elif campo_num == 2:
            start_pos = 11
            end_pos = 22
        elif campo_num == 3:
            start_pos = 22
            end_pos = 33
        else:
            raise ValueError(f"Campo inválido: {campo_num}")
        
        # Substituir apenas o último dígito (DV) do campo
        campo_corrigido = linha_limpa[start_pos:end_pos-1] + str(dv_correto)
        
        # Montar linha corrigida
        corrected_line = (
            linha_limpa[:start_pos] + 
            campo_corrigido + 
            linha_limpa[end_pos:]
        )
        
        return corrected_line
    
    def _apply_multiple_corrections(self, linha_limpa: str, errors: list) -> str:
        """Aplica múltiplas correções na linha digitável"""
        
        corrected_line = linha_limpa
        
        # Aplicar correções em ordem reversa para não afetar posições
        for error in sorted(errors, key=lambda x: x['campo'], reverse=True):
            campo_num = error['campo']
            dv_correto = error['dv_correto']
            
            # Determinar posições do campo
            if campo_num == 1:
                start_pos = 0
                end_pos = 11
            elif campo_num == 2:
                start_pos = 11
                end_pos = 22
            elif campo_num == 3:
                start_pos = 22
                end_pos = 33
            else:
                continue  # Pular campos inválidos
            
            # Substituir apenas o último dígito (DV) do campo
            campo_corrigido = corrected_line[start_pos:end_pos-1] + str(dv_correto)
            
            # Montar linha corrigida
            corrected_line = (
                corrected_line[:start_pos] + 
                campo_corrigido + 
                corrected_line[end_pos:]
            )
        
        return corrected_line
    
    def format_for_display(self, linha_digitavel: str) -> str:
        """Formata linha digitável para exibição"""
        
        if len(linha_digitavel) != 47:
            return linha_digitavel
        
        # Formato: XXXXX.XXXXX XXXXX.XXXXXX XXXXX.XXXXXX X XXXXXXXXXXXXXX
        return (
            f"{linha_digitavel[0:5]}.{linha_digitavel[5:10]} "
            f"{linha_digitavel[10:15]}.{linha_digitavel[15:21]} "
            f"{linha_digitavel[21:26]}.{linha_digitavel[26:32]} "
            f"{linha_digitavel[32:33]} "
            f"{linha_digitavel[33:47]}"
        )
    
    def get_user_friendly_message(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna mensagem amigável para o usuário"""
        
        if not result['success']:
            return {
                'type': 'error',
                'title': 'Erro no Boleto',
                'message': result.get('error', 'Erro desconhecido'),
                'action_required': True
            }
        
        if not result.get('corrections'):
            return {
                'type': 'success',
                'title': 'Boleto Válido',
                'message': 'O código do boleto está correto.',
                'action_required': False
            }
        
        corrections = result['corrections']
        formatted_original = self.format_for_display(result['original_code'])
        formatted_corrected = self.format_for_display(result['corrected_code'])
        
        if len(corrections) == 1:
            correction = corrections[0]
            return {
                'type': 'warning',
                'title': 'Boleto Corrigido',
                'message': f'Foi corrigido um erro no dígito verificador do campo {correction["campo"]}.',
                'details': {
                    'campo': correction['campo'],
                    'dv_original': correction['dv_original'],
                    'dv_correto': correction['dv_correto'],
                    'linha_original': formatted_original,
                    'linha_corrigida': formatted_corrected
                },
                'action_required': False,
                'confidence': result.get('confidence', 'medium')
            }
        else:
            # Múltiplas correções
            campos_corrigidos = [str(c['campo']) for c in corrections]
            return {
                'type': 'warning',
                'title': 'Boleto Corrigido',
                'message': f'Foram corrigidos erros nos dígitos verificadores dos campos {", ".join(campos_corrigidos)}.',
                'details': {
                    'corrections': corrections,
                    'linha_original': formatted_original,
                    'linha_corrigida': formatted_corrected,
                    'total_corrections': len(corrections)
                },
                'action_required': result.get('confidence') == 'low',
                'confidence': result.get('confidence', 'medium')
            }


# Instância global
boleto_simple_corrector = BoletoSimpleCorrector()


def correct_boleto_simple(codigo_input: str) -> Dict[str, Any]:
    """
    Função de conveniência para correção simples
    
    Args:
        codigo_input: Linha digitável
        
    Returns:
        Dict: Resultado da correção
    """
    
    return boleto_simple_corrector.correct_single_dv_error(codigo_input)