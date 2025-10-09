"""
Manipulador de Erros de Boleto
Fornece soluções práticas para erros comuns de validação
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from .boleto_validator_unified import BoletoValidatorUnified
    from .boleto_simple_corrector import BoletoSimpleCorrector
except ImportError:
    from boleto_validator_unified import BoletoValidatorUnified
    from boleto_simple_corrector import BoletoSimpleCorrector


logger = logging.getLogger('boleto_error_handler')


@dataclass
class BoletoErrorSolution:
    """Solução para um erro de boleto"""
    error_type: str
    severity: str  # 'low', 'medium', 'high'
    title: str
    message: str
    action_options: List[Dict[str, Any]]
    can_proceed: bool
    corrected_code: Optional[str] = None


class BoletoErrorHandler:
    """
    Manipulador de erros que oferece soluções práticas
    """
    
    def __init__(self):
        self.validator = BoletoValidatorUnified()
        self.corrector = BoletoSimpleCorrector()
    
    def analyze_and_suggest_solution(self, codigo_input: str) -> BoletoErrorSolution:
        """
        Analisa erros e sugere soluções práticas
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            BoletoErrorSolution: Solução sugerida
        """
        
        # Primeiro, tentar validação normal
        validation_result = self.validator.validate(codigo_input)
        
        if validation_result.is_valid:
            return BoletoErrorSolution(
                error_type='none',
                severity='low',
                title='Boleto Válido',
                message='O código do boleto está correto e pode ser processado.',
                action_options=[
                    {
                        'action': 'proceed',
                        'label': 'Processar Boleto',
                        'description': 'Continuar com o processamento do boleto'
                    }
                ],
                can_proceed=True
            )
        
        # Analisar tipos de erro
        errors = validation_result.errors
        
        # Verificar se são apenas erros de DV
        dv_errors = [e for e in errors if 'DV' in e or 'dígito verificador' in e.lower()]
        
        if len(dv_errors) == len(errors) and len(dv_errors) <= 3:
            return self._handle_dv_errors(codigo_input, dv_errors)
        
        # Outros tipos de erro
        return self._handle_other_errors(codigo_input, errors)
    
    def _handle_dv_errors(self, codigo_input: str, dv_errors: List[str]) -> BoletoErrorSolution:
        """Manipula erros de dígito verificador"""
        
        # Tentar correção
        correction_result = self.corrector.correct_single_dv_error(codigo_input)
        
        if correction_result['success'] and correction_result.get('corrections'):
            corrections = correction_result['corrections']
            
            # Determinar severidade baseada no número de correções
            if len(corrections) == 1:
                severity = 'low'
                title = 'Erro Menor no Boleto'
                message = f'Foi detectado um erro no dígito verificador do campo {corrections[0]["campo"]}. Este tipo de erro é comum em boletos impressos.'
            else:
                severity = 'medium'
                title = 'Múltiplos Erros de Dígito'
                message = f'Foram detectados {len(corrections)} erros nos dígitos verificadores. Isso pode indicar problema na impressão do boleto.'
            
            # Formatar código corrigido
            corrected_formatted = self.corrector.format_for_display(correction_result['corrected_code'])
            
            return BoletoErrorSolution(
                error_type='dv_error',
                severity=severity,
                title=title,
                message=message,
                action_options=[
                    {
                        'action': 'use_corrected',
                        'label': 'Usar Código Corrigido',
                        'description': f'Processar com o código corrigido: {corrected_formatted}',
                        'corrected_code': correction_result['corrected_code']
                    },
                    {
                        'action': 'proceed_anyway',
                        'label': 'Processar Mesmo Assim',
                        'description': 'Processar o boleto original (não recomendado)',
                        'warning': True
                    },
                    {
                        'action': 'request_new',
                        'label': 'Solicitar Nova Via',
                        'description': 'Solicitar uma nova via do boleto ao emissor'
                    }
                ],
                can_proceed=True,
                corrected_code=correction_result['corrected_code']
            )
        
        else:
            return BoletoErrorSolution(
                error_type='dv_error_complex',
                severity='high',
                title='Erros Complexos no Boleto',
                message='Foram detectados múltiplos erros que não podem ser corrigidos automaticamente.',
                action_options=[
                    {
                        'action': 'request_new',
                        'label': 'Solicitar Nova Via',
                        'description': 'Recomendado: solicitar uma nova via do boleto'
                    },
                    {
                        'action': 'manual_check',
                        'label': 'Verificação Manual',
                        'description': 'Verificar manualmente os dados do boleto'
                    }
                ],
                can_proceed=False
            )
    
    def _handle_other_errors(self, codigo_input: str, errors: List[str]) -> BoletoErrorSolution:
        """Manipula outros tipos de erro"""
        
        # Verificar se é erro de formato
        format_errors = [e for e in errors if any(word in e.lower() for word in ['formato', 'comprimento', 'dígitos'])]
        
        if format_errors:
            return BoletoErrorSolution(
                error_type='format_error',
                severity='high',
                title='Formato Inválido',
                message='O código informado não está no formato correto de boleto.',
                action_options=[
                    {
                        'action': 'check_input',
                        'label': 'Verificar Digitação',
                        'description': 'Verificar se o código foi digitado corretamente'
                    },
                    {
                        'action': 'use_barcode',
                        'label': 'Usar Código de Barras',
                        'description': 'Tentar usar o código de barras em vez da linha digitável'
                    }
                ],
                can_proceed=False
            )
        
        # Erro genérico
        return BoletoErrorSolution(
            error_type='generic_error',
            severity='high',
            title='Erro na Validação',
            message='Foram detectados erros na validação do boleto.',
            action_options=[
                {
                    'action': 'check_boleto',
                    'label': 'Verificar Boleto',
                    'description': 'Verificar se o boleto está legível e correto'
                },
                {
                    'action': 'contact_support',
                    'label': 'Contatar Suporte',
                    'description': 'Entrar em contato com o suporte técnico'
                }
            ],
            can_proceed=False
        )
    
    def get_user_friendly_response(self, solution: BoletoErrorSolution) -> Dict[str, Any]:
        """
        Converte solução em resposta amigável para interface
        
        Args:
            solution: Solução do erro
            
        Returns:
            Dict: Resposta formatada para interface
        """
        
        return {
            'status': 'success' if solution.error_type == 'none' else 'error',
            'can_proceed': solution.can_proceed,
            'severity': solution.severity,
            'title': solution.title,
            'message': solution.message,
            'actions': solution.action_options,
            'corrected_code': solution.corrected_code,
            'error_type': solution.error_type
        }
    
    def process_user_choice(self, codigo_input: str, chosen_action: str) -> Dict[str, Any]:
        """
        Processa a escolha do usuário
        
        Args:
            codigo_input: Código original
            chosen_action: Ação escolhida pelo usuário
            
        Returns:
            Dict: Resultado do processamento
        """
        
        if chosen_action == 'use_corrected':
            # Usar código corrigido
            correction_result = self.corrector.correct_single_dv_error(codigo_input)
            
            if correction_result['success']:
                return {
                    'success': True,
                    'message': 'Código corrigido será usado para processamento',
                    'final_code': correction_result['corrected_code'],
                    'action_taken': 'correction_applied'
                }
        
        elif chosen_action == 'proceed_anyway':
            # Processar código original mesmo com erros
            return {
                'success': True,
                'message': 'Processando código original (com avisos)',
                'final_code': codigo_input,
                'action_taken': 'proceed_with_warnings',
                'warnings': ['Boleto processado com erros de validação']
            }
        
        elif chosen_action == 'proceed':
            # Processar código válido
            return {
                'success': True,
                'message': 'Boleto válido processado',
                'final_code': codigo_input,
                'action_taken': 'normal_processing'
            }
        
        else:
            # Outras ações (solicitar nova via, etc.)
            return {
                'success': False,
                'message': f'Ação {chosen_action} selecionada - processamento cancelado',
                'action_taken': chosen_action
            }


# Instância global
boleto_error_handler = BoletoErrorHandler()


def handle_boleto_error(codigo_input: str) -> Dict[str, Any]:
    """
    Função de conveniência para manipulação de erros
    
    Args:
        codigo_input: Código de entrada
        
    Returns:
        Dict: Solução sugerida
    """
    
    solution = boleto_error_handler.analyze_and_suggest_solution(codigo_input)
    return boleto_error_handler.get_user_friendly_response(solution)