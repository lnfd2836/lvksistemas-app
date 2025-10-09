"""
Corretor de Dígitos Verificadores para Boletos
Permite corrigir automaticamente DVs inválidos em boletos com erros de impressão
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

try:
    from .boleto_validator_base import DVCalculatorMixin, FormatNormalizerMixin
    from .boleto_input_normalizer import BoletoInputNormalizer
except ImportError:
    from boleto_validator_base import DVCalculatorMixin, FormatNormalizerMixin
    from boleto_input_normalizer import BoletoInputNormalizer


logger = logging.getLogger('boleto_dv_corrector')


@dataclass
class DVCorrectionResult:
    """Resultado de uma correção de DV"""
    original_code: str
    corrected_code: str
    corrections_made: List[Dict[str, Any]]
    is_corrected: bool
    confidence_level: str  # 'high', 'medium', 'low'
    warnings: List[str]


class BoletoDVCorrector(DVCalculatorMixin, FormatNormalizerMixin):
    """
    Corretor de dígitos verificadores para boletos
    Permite corrigir automaticamente DVs inválidos
    """
    
    def __init__(self):
        self.normalizer = BoletoInputNormalizer()
        
        # Configurações de correção
        self.correction_modes = {
            'strict': False,      # Não corrige, apenas valida
            'warning': True,      # Corrige mas avisa
            'auto': True,         # Corrige automaticamente
            'interactive': True   # Pergunta ao usuário
        }
        
        self.default_mode = 'warning'
    
    def correct_dv_errors(self, codigo_input: str, mode: str = None) -> DVCorrectionResult:
        """
        Corrige erros de DV em boleto
        
        Args:
            codigo_input: Código de barras ou linha digitável
            mode: Modo de correção ('strict', 'warning', 'auto', 'interactive')
            
        Returns:
            DVCorrectionResult: Resultado da correção
        """
        
        if mode is None:
            mode = self.default_mode
        
        # Normalizar entrada
        normalized = self.normalizer.normalize(codigo_input)
        
        if not normalized.is_valid_format:
            return DVCorrectionResult(
                original_code=codigo_input,
                corrected_code=codigo_input,
                corrections_made=[],
                is_corrected=False,
                confidence_level='low',
                warnings=[f"Formato inválido: {normalized.errors}"]
            )
        
        # Detectar formato
        input_format = normalized.input_format
        codigo_limpo = normalized.normalized_code
        
        if input_format == "linha_digitavel":
            return self._correct_linha_digitavel_dv(codigo_limpo, mode)
        elif input_format == "codigo_barras":
            return self._correct_codigo_barras_dv(codigo_limpo, mode)
        else:
            return DVCorrectionResult(
                original_code=codigo_input,
                corrected_code=codigo_input,
                corrections_made=[],
                is_corrected=False,
                confidence_level='low',
                warnings=[f"Formato não suportado: {input_format}"]
            )
    
    def _correct_linha_digitavel_dv(self, linha_digitavel: str, mode: str) -> DVCorrectionResult:
        """Corrige DVs da linha digitável"""
        
        if len(linha_digitavel) != 47:
            return DVCorrectionResult(
                original_code=linha_digitavel,
                corrected_code=linha_digitavel,
                corrections_made=[],
                is_corrected=False,
                confidence_level='low',
                warnings=[f"Comprimento inválido: {len(linha_digitavel)} (esperado 47)"]
            )
        
        corrections = []
        warnings = []
        corrected_code = linha_digitavel
        
        # Extrair campos
        campo1 = linha_digitavel[0:11]   # 10 dígitos + DV
        campo2 = linha_digitavel[11:22]  # 10 dígitos + DV
        campo3 = linha_digitavel[22:33]  # 10 dígitos + DV
        campo4 = linha_digitavel[33:34]  # DV geral
        campo5 = linha_digitavel[34:47]  # Vencimento + valor
        
        # Verificar e corrigir campo 1
        dv1_result = self._check_and_correct_campo_dv(campo1, 1, mode)
        if dv1_result['corrected']:
            corrections.append(dv1_result)
            corrected_code = corrected_code[:0] + dv1_result['corrected_campo'] + corrected_code[11:]
        
        # Verificar e corrigir campo 2
        dv2_result = self._check_and_correct_campo_dv(campo2, 2, mode)
        if dv2_result['corrected']:
            corrections.append(dv2_result)
            start_pos = 11
            corrected_code = corrected_code[:start_pos] + dv2_result['corrected_campo'] + corrected_code[start_pos+11:]
        
        # Verificar e corrigir campo 3
        dv3_result = self._check_and_correct_campo_dv(campo3, 3, mode)
        if dv3_result['corrected']:
            corrections.append(dv3_result)
            start_pos = 22
            corrected_code = corrected_code[:start_pos] + dv3_result['corrected_campo'] + corrected_code[start_pos+11:]
        
        # Verificar DV geral (campo 4)
        # Para isso, precisamos reconstruir o código de barras
        try:
            codigo_barras_reconstruido = self._reconstruct_codigo_from_linha(corrected_code)
            dv_geral_result = self._check_and_correct_dv_geral(codigo_barras_reconstruido, campo4, mode)
            
            if dv_geral_result['corrected']:
                corrections.append(dv_geral_result)
                corrected_code = corrected_code[:33] + dv_geral_result['dv_correto'] + corrected_code[34:]
        
        except Exception as e:
            warnings.append(f"Não foi possível verificar DV geral: {str(e)}")
        
        # Determinar nível de confiança
        confidence_level = self._calculate_confidence_level(corrections, warnings)
        
        # Adicionar avisos baseados no modo
        if corrections and mode == 'warning':
            warnings.append(f"Foram corrigidos {len(corrections)} dígitos verificadores")
        
        return DVCorrectionResult(
            original_code=linha_digitavel,
            corrected_code=corrected_code,
            corrections_made=corrections,
            is_corrected=len(corrections) > 0,
            confidence_level=confidence_level,
            warnings=warnings
        )
    
    def _correct_codigo_barras_dv(self, codigo_barras: str, mode: str) -> DVCorrectionResult:
        """Corrige DV do código de barras"""
        
        if len(codigo_barras) != 44:
            return DVCorrectionResult(
                original_code=codigo_barras,
                corrected_code=codigo_barras,
                corrections_made=[],
                is_corrected=False,
                confidence_level='low',
                warnings=[f"Comprimento inválido: {len(codigo_barras)} (esperado 44)"]
            )
        
        corrections = []
        warnings = []
        
        # Verificar DV geral (posição 4)
        dv_informado = codigo_barras[4]
        dv_geral_result = self._check_and_correct_dv_geral(codigo_barras, dv_informado, mode)
        
        corrected_code = codigo_barras
        
        if dv_geral_result['corrected']:
            corrections.append(dv_geral_result)
            corrected_code = codigo_barras[:4] + dv_geral_result['dv_correto'] + codigo_barras[5:]
        
        # Determinar nível de confiança
        confidence_level = self._calculate_confidence_level(corrections, warnings)
        
        if corrections and mode == 'warning':
            warnings.append("Foi corrigido o dígito verificador geral")
        
        return DVCorrectionResult(
            original_code=codigo_barras,
            corrected_code=corrected_code,
            corrections_made=corrections,
            is_corrected=len(corrections) > 0,
            confidence_level=confidence_level,
            warnings=warnings
        )
    
    def _check_and_correct_campo_dv(self, campo: str, campo_num: int, mode: str) -> Dict[str, Any]:
        """Verifica e corrige DV de um campo específico"""
        
        if len(campo) != 11:
            return {'corrected': False, 'error': f'Campo {campo_num} tem comprimento inválido'}
        
        campo_sem_dv = campo[:-1]
        dv_informado = int(campo[-1])
        dv_calculado = self.calculate_dv_modulo10_febraban(campo_sem_dv)
        
        if dv_informado == dv_calculado:
            return {'corrected': False, 'valid': True}
        
        # DV está incorreto
        if mode == 'strict':
            return {
                'corrected': False,
                'error': f'DV do campo {campo_num} inválido: informado {dv_informado}, calculado {dv_calculado}'
            }
        
        # Corrigir DV
        campo_corrigido = campo_sem_dv + str(dv_calculado)
        
        return {
            'corrected': True,
            'campo_num': campo_num,
            'campo_original': campo,
            'corrected_campo': campo_corrigido,
            'dv_original': dv_informado,
            'dv_correto': dv_calculado,
            'tipo': 'campo_dv',
            'descricao': f'Campo {campo_num}: DV corrigido de {dv_informado} para {dv_calculado}'
        }
    
    def _check_and_correct_dv_geral(self, codigo_barras: str, dv_informado: str, mode: str) -> Dict[str, Any]:
        """Verifica e corrige DV geral"""
        
        # Extrair código sem DV para cálculo
        codigo_sem_dv = codigo_barras[:4] + codigo_barras[5:]
        dv_informado_int = int(dv_informado)
        dv_calculado = self.calculate_dv_modulo11_febraban(codigo_sem_dv)
        
        if dv_informado_int == dv_calculado:
            return {'corrected': False, 'valid': True}
        
        # DV está incorreto
        if mode == 'strict':
            return {
                'corrected': False,
                'error': f'DV geral inválido: informado {dv_informado_int}, calculado {dv_calculado}'
            }
        
        return {
            'corrected': True,
            'tipo': 'dv_geral',
            'dv_original': dv_informado_int,
            'dv_correto': str(dv_calculado),
            'descricao': f'DV geral corrigido de {dv_informado_int} para {dv_calculado}'
        }
    
    def _reconstruct_codigo_from_linha(self, linha_digitavel: str) -> str:
        """Reconstrói código de barras a partir da linha digitável"""
        
        if len(linha_digitavel) != 47:
            raise ValueError(f"Linha digitável deve ter 47 dígitos, tem {len(linha_digitavel)}")
        
        # Extrair campos (sem os DVs)
        campo1 = linha_digitavel[0:10]    # 10 dígitos sem DV
        campo2 = linha_digitavel[11:21]   # 10 dígitos sem DV  
        campo3 = linha_digitavel[22:32]   # 10 dígitos sem DV
        campo4 = linha_digitavel[33:34]   # DV geral
        campo5 = linha_digitavel[34:47]   # Vencimento + valor (13 dígitos)
        
        # Montar código de barras conforme padrão FEBRABAN
        banco = campo1[0:3]               # 104
        moeda = campo1[3:4]               # 9
        campo_livre_p1 = campo1[4:10]     # 267014 (6 dígitos)
        campo_livre_p2 = campo2           # 5182301939 (10 dígitos)
        campo_livre_p3 = campo3[1:10]     # 294657014 (9 dígitos, remove primeiro)
        
        vencimento = campo5[0:4]          # 2600 (4 dígitos)
        valor = campo5[4:14]              # 0000002990 (10 dígitos)
        
        # Código de barras: banco(3) + moeda(1) + DV(1) + vencimento(4) + valor(10) + campo_livre(25)
        campo_livre = campo_livre_p1 + campo_livre_p2 + campo_livre_p3
        codigo_barras = banco + moeda + campo4 + vencimento + valor + campo_livre
        
        return codigo_barras
    
    def _calculate_confidence_level(self, corrections: List[Dict], warnings: List[str]) -> str:
        """Calcula nível de confiança da correção"""
        
        if not corrections:
            return 'high'  # Nenhuma correção necessária
        
        num_corrections = len(corrections)
        
        if num_corrections == 1:
            # Uma correção apenas - confiança média a alta
            correction_type = corrections[0].get('tipo', '')
            if correction_type == 'campo_dv':
                return 'high'  # Correção de DV de campo é confiável
            else:
                return 'medium'
        
        elif num_corrections <= 2:
            return 'medium'  # Poucas correções
        
        else:
            return 'low'  # Muitas correções - pode haver problema maior
    
    def format_correction_summary(self, result: DVCorrectionResult) -> str:
        """Formata resumo das correções para exibição"""
        
        if not result.is_corrected:
            return "Nenhuma correção necessária - boleto válido"
        
        summary = f"Correções realizadas ({result.confidence_level} confiança):\n"
        
        for correction in result.corrections_made:
            summary += f"  • {correction['descricao']}\n"
        
        if result.warnings:
            summary += "\nAvisos:\n"
            for warning in result.warnings:
                summary += f"  ⚠ {warning}\n"
        
        summary += f"\nCódigo original:  {result.original_code}\n"
        summary += f"Código corrigido: {result.corrected_code}"
        
        return summary
    
    def get_user_friendly_message(self, result: DVCorrectionResult) -> Dict[str, Any]:
        """Retorna mensagem amigável para o usuário"""
        
        if not result.is_corrected:
            return {
                'type': 'success',
                'title': 'Boleto Válido',
                'message': 'O código do boleto está correto e foi validado com sucesso.',
                'action_required': False
            }
        
        if result.confidence_level == 'high':
            return {
                'type': 'warning',
                'title': 'Boleto Corrigido Automaticamente',
                'message': f'Foram corrigidos {len(result.corrections_made)} dígitos verificadores. O boleto pode ser processado normalmente.',
                'details': [c['descricao'] for c in result.corrections_made],
                'action_required': False,
                'corrected_code': result.corrected_code
            }
        
        elif result.confidence_level == 'medium':
            return {
                'type': 'warning',
                'title': 'Boleto Corrigido com Ressalvas',
                'message': 'Foram encontrados alguns erros que foram corrigidos automaticamente. Recomenda-se verificar o boleto original.',
                'details': [c['descricao'] for c in result.corrections_made],
                'action_required': True,
                'corrected_code': result.corrected_code
            }
        
        else:  # low confidence
            return {
                'type': 'error',
                'title': 'Boleto com Muitos Erros',
                'message': 'Foram encontrados muitos erros no boleto. Recomenda-se verificar o boleto original ou solicitar uma segunda via.',
                'details': [c['descricao'] for c in result.corrections_made],
                'action_required': True,
                'corrected_code': result.corrected_code
            }


# Instância global
boleto_dv_corrector = BoletoDVCorrector()


def correct_boleto_dv(codigo_input: str, mode: str = 'warning') -> DVCorrectionResult:
    """
    Função de conveniência para correção de DV
    
    Args:
        codigo_input: Código de barras ou linha digitável
        mode: Modo de correção ('strict', 'warning', 'auto')
        
    Returns:
        DVCorrectionResult: Resultado da correção
    """
    
    return boleto_dv_corrector.correct_dv_errors(codigo_input, mode)