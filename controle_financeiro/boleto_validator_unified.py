"""
Validador Unificado de Boletos
Interface principal que integra todos os validadores e conversores
"""

import logging
from typing import Dict, Any, Optional, List

try:
    from .boleto_layout_detector import BoletoLayoutDetector, BoletoLayout
    from .boleto_input_normalizer import BoletoInputNormalizer
    from .boleto_format_converter import BoletoFormatConverter
    from .sigcb_validator import SIGCBValidator
    from .boleto_validator_base import ValidationResult, BoletoComponents
    from .boleto_error_messages import error_messages, ErrorCategory
    from .barcode_validator import BarcodeValidator  # Validador original
    from .boleto_dv_corrector import BoletoDVCorrector, DVCorrectionResult
    from .boleto_simple_corrector import BoletoSimpleCorrector
except ImportError:
    from boleto_layout_detector import BoletoLayoutDetector, BoletoLayout
    from boleto_input_normalizer import BoletoInputNormalizer
    from boleto_format_converter import BoletoFormatConverter
    from sigcb_validator import SIGCBValidator
    from boleto_validator_base import ValidationResult, BoletoComponents
    from boleto_error_messages import error_messages, ErrorCategory
    from barcode_validator import BarcodeValidator  # Validador original
    from boleto_dv_corrector import BoletoDVCorrector, DVCorrectionResult
    from boleto_simple_corrector import BoletoSimpleCorrector


# Configurar logging
logger = logging.getLogger('boleto_validation')


class BoletoValidatorUnified:
    """
    Validador unificado que integra todos os validadores específicos
    Interface principal para validação de boletos no sistema
    """
    
    def __init__(self):
        # Componentes principais
        self.layout_detector = BoletoLayoutDetector()
        self.input_normalizer = BoletoInputNormalizer()
        self.format_converter = BoletoFormatConverter()
        self.dv_corrector = BoletoDVCorrector()
        self.simple_corrector = BoletoSimpleCorrector()
        
        # Validadores específicos
        self.sigcb_validator = SIGCBValidator()
        self.legacy_validator = BarcodeValidator()  # Validador original para compatibilidade
        
        # Cache de validações
        self._validation_cache = {}
        self._cache_enabled = True
        
        # Configurações de correção de DV
        self.dv_correction_mode = 'warning'  # 'strict', 'warning', 'auto'
    
    def validate(self, codigo_input: str, enable_cache: bool = True) -> ValidationResult:
        """
        Método principal de validação - detecta layout automaticamente
        
        Args:
            codigo_input: Código de barras ou linha digitável
            enable_cache: Se deve usar cache de validações
            
        Returns:
            ValidationResult: Resultado completo da validação
        """
        
        # Verificar cache
        if enable_cache and self._cache_enabled:
            cache_key = self._generate_cache_key(codigo_input)
            if cache_key in self._validation_cache:
                logger.debug(f"Validation cache hit for {codigo_input[:10]}...")
                return self._validation_cache[cache_key]
        
        result = ValidationResult(validation_type="Unified_Validation")
        
        try:
            # Log da tentativa de validação
            logger.info(f"Starting validation for input: {codigo_input[:10]}...")
            
            # 1. Normalizar entrada
            normalized = self.input_normalizer.normalize(codigo_input)
            
            if not normalized.is_valid_format:
                for error in normalized.errors:
                    result.add_error(error)
                logger.warning(f"Input format validation failed: {normalized.errors}")
                return self._cache_result(codigo_input, result, enable_cache)
            
            result.add_detail("normalized_input", normalized.normalized_code)
            result.add_detail("input_format", normalized.input_format)
            result.add_detail("original_length", len(codigo_input))
            result.add_detail("normalized_length", len(normalized.normalized_code))
            
            # 2. Detectar layout
            layout = self.layout_detector.detect_layout(normalized.normalized_code)
            bank_info = self.layout_detector.get_bank_info(normalized.normalized_code)
            
            result.add_detail("detected_layout", layout.value if isinstance(layout, BoletoLayout) else str(layout))
            result.add_detail("bank_info", bank_info)
            
            logger.info(f"Detected layout: {layout}, Bank: {bank_info['nome']}")
            
            # 3. Validar com validador específico
            specific_result = self._validate_with_specific_validator(normalized.normalized_code, layout)
            result.merge(specific_result)
            
            # 4. Validações adicionais
            self._perform_additional_validations(normalized.normalized_code, layout, result)
            
            # 5. Log do resultado
            if result.is_valid:
                logger.info(f"Validation successful for {bank_info['nome']} {layout}")
            else:
                logger.warning(f"Validation failed: {result.errors}")
            
        except Exception as e:
            error_msg = f"Unexpected error during validation: {str(e)}"
            result.add_error(error_msg)
            logger.error(error_msg, exc_info=True)
        
        return self._cache_result(codigo_input, result, enable_cache)
    
    def validate_and_convert(self, codigo_input: str, target_format: str = "auto") -> Dict[str, Any]:
        """
        Valida e converte código para formato desejado
        
        Args:
            codigo_input: Código de entrada
            target_format: Formato desejado ("codigo_barras", "linha_digitavel", "auto")
            
        Returns:
            Dict: Resultado completo com validação e conversão
        """
        
        # Validar primeiro
        validation_result = self.validate(codigo_input)
        
        result = {
            "validation": validation_result,
            "conversion": None,
            "formatted_code": codigo_input
        }
        
        if not validation_result.is_valid:
            return result
        
        # Determinar formato de destino
        if target_format == "auto":
            input_format = validation_result.details.get("input_format", "")
            target_format = "linha_digitavel" if input_format == "codigo_barras" else "codigo_barras"
        
        # Converter se necessário
        try:
            conversion_result = self.format_converter.auto_convert(codigo_input, target_format)
            result["conversion"] = conversion_result
            
            if conversion_result.success:
                result["formatted_code"] = self.format_converter.format_for_display(
                    conversion_result.converted_code, target_format
                )
            
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}")
            validation_result.add_warning(f"Conversão falhou: {str(e)}")
        
        return result
    
    def validate_with_legacy_compatibility(self, codigo_input: str) -> Dict[str, Any]:
        """
        Validação com compatibilidade ao validador legado
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            Dict: Resultado no formato compatível com sistema legado
        """
        
        # Validação nova
        new_result = self.validate(codigo_input)
        
        # Validação legada para comparação
        legacy_result = None
        try:
            legacy_result = self.legacy_validator.validate_complete(codigo_input)
        except Exception as e:
            logger.warning(f"Legacy validation failed: {str(e)}")
        
        return {
            "new_validation": new_result,
            "legacy_validation": legacy_result,
            "is_valid": new_result.is_valid,
            "errors": new_result.errors,
            "warnings": new_result.warnings,
            "details": new_result.details,
            "compatibility_check": self._check_compatibility(new_result, legacy_result)
        }
    
    def get_validation_info(self, codigo_input: str) -> Dict[str, Any]:
        """
        Retorna informações detalhadas sobre o código sem validar completamente
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            Dict: Informações do código
        """
        
        try:
            # Normalizar
            normalized = self.input_normalizer.normalize(codigo_input)
            
            if not normalized.is_valid_format:
                return {
                    "valid_format": False,
                    "errors": normalized.errors,
                    "suggestions": []
                }
            
            # Detectar layout e banco
            layout = self.layout_detector.detect_layout(normalized.normalized_code)
            bank_info = self.layout_detector.get_bank_info(normalized.normalized_code)
            
            # Extrair componentes básicos
            components = None
            try:
                if layout == BoletoLayout.SIGCB:
                    components = self.sigcb_validator.extract_components(normalized.normalized_code)
                
            except Exception as e:
                logger.debug(f"Component extraction failed: {str(e)}")
            
            return {
                "valid_format": True,
                "input_format": normalized.input_format,
                "detected_layout": layout.value if isinstance(layout, BoletoLayout) else str(layout),
                "bank_info": bank_info,
                "components": components.to_dict() if components else None,
                "length": len(normalized.normalized_code),
                "errors": [],
                "suggestions": self._get_improvement_suggestions(layout, bank_info)
            }
            
        except Exception as e:
            return {
                "valid_format": False,
                "errors": [f"Erro ao analisar código: {str(e)}"],
                "suggestions": ["Verifique se o código está correto"]
            }
    
    def _validate_with_specific_validator(self, codigo_normalizado: str, layout: BoletoLayout) -> ValidationResult:
        """Valida com validador específico do layout"""
        
        try:
            if layout == BoletoLayout.SIGCB:
                return self.sigcb_validator.validate_complete(codigo_normalizado)
            else:
                # Para outros layouts, usar validador legado
                return self.legacy_validator.validate_complete(codigo_normalizado)
                
        except Exception as e:
            result = ValidationResult(validation_type=f"{layout}_Validation")
            result.add_error(f"Erro no validador específico: {str(e)}")
            return result
    
    def _perform_additional_validations(self, codigo_normalizado: str, layout: BoletoLayout, result: ValidationResult):
        """Executa validações adicionais"""
        
        try:
            # Validação de formato de entrada
            format_validation = self.layout_detector.validate_format(codigo_normalizado)
            
            if not format_validation["is_valid"]:
                for error in format_validation["errors"]:
                    result.add_warning(f"Formato: {error}")
            
            # Validação específica por layout
            if layout == BoletoLayout.SIGCB:
                self._validate_sigcb_specific_rules(codigo_normalizado, result)
            
        except Exception as e:
            result.add_warning(f"Validação adicional falhou: {str(e)}")
    
    def _validate_sigcb_specific_rules(self, codigo_normalizado: str, result: ValidationResult):
        """Validações específicas para SIGCB"""
        
        try:
            # Verificar se realmente é da Caixa
            if codigo_normalizado[0:3] != "104":
                result.add_error("Código não é da Caixa Econômica Federal")
                return
            
            # Validações específicas do SIGCB
            components = self.sigcb_validator.extract_components(codigo_normalizado)
            
            # Verificar carteira
            if hasattr(components, 'carteira') and components.carteira:
                if components.carteira not in ["001", "002", "014", "024"]:
                    result.add_warning(f"Carteira {components.carteira} pode não ser padrão da Caixa")
            
            # Verificar nosso número
            if hasattr(components, 'nosso_numero') and components.nosso_numero == "0000000000":
                result.add_error("Nosso número não pode ser zero")
            
        except Exception as e:
            result.add_warning(f"Validação SIGCB específica falhou: {str(e)}")
    
    def _check_compatibility(self, new_result: ValidationResult, legacy_result) -> Dict[str, Any]:
        """Verifica compatibilidade entre validadores"""
        
        if not legacy_result:
            return {"compatible": None, "reason": "Legacy validator failed"}
        
        # Comparar resultados básicos
        new_valid = new_result.is_valid
        legacy_valid = legacy_result.is_valid
        
        compatible = new_valid == legacy_valid
        
        return {
            "compatible": compatible,
            "new_valid": new_valid,
            "legacy_valid": legacy_valid,
            "reason": "Results match" if compatible else "Validation results differ"
        }
    
    def _get_improvement_suggestions(self, layout: BoletoLayout, bank_info: Dict[str, Any]) -> List[str]:
        """Gera sugestões de melhoria"""
        
        suggestions = []
        
        if layout == BoletoLayout.SIGCB:
            suggestions.append("Código da Caixa detectado - usando validação SIGCB")
            suggestions.append("Certifique-se de que o convênio está ativo na Caixa")
        
        elif layout == BoletoLayout.FEBRABAN_PADRAO:
            suggestions.append(f"Código do {bank_info['nome']} - usando validação FEBRABAN padrão")
        
        else:
            suggestions.append("Layout não reconhecido - usando validação genérica")
            suggestions.append("Verifique se o código está correto")
        
        return suggestions
    
    def _generate_cache_key(self, codigo_input: str) -> str:
        """Gera chave para cache"""
        import hashlib
        return hashlib.md5(codigo_input.encode()).hexdigest()
    
    def _cache_result(self, codigo_input: str, result: ValidationResult, enable_cache: bool) -> ValidationResult:
        """Armazena resultado no cache"""
        
        if enable_cache and self._cache_enabled:
            cache_key = self._generate_cache_key(codigo_input)
            self._validation_cache[cache_key] = result
            
            # Limitar tamanho do cache
            if len(self._validation_cache) > 1000:
                # Remove 20% dos itens mais antigos
                items_to_remove = list(self._validation_cache.keys())[:200]
                for key in items_to_remove:
                    del self._validation_cache[key]
        
        return result
    
    def clear_cache(self):
        """Limpa cache de validações"""
        self._validation_cache.clear()
        logger.info("Validation cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "cache_enabled": self._cache_enabled,
            "cache_size": len(self._validation_cache),
            "cache_keys": list(self._validation_cache.keys())[:10]  # Primeiras 10 chaves
        }
    
    def get_user_friendly_errors(self, validation_result: ValidationResult) -> List[Dict[str, Any]]:
        """
        Converte erros técnicos em mensagens amigáveis para o usuário
        
        Args:
            validation_result: Resultado da validação
            
        Returns:
            List[Dict]: Lista de erros formatados para usuário
        """
        
        friendly_errors = []
        
        for error in validation_result.errors:
            formatted_error = error_messages.format_error_for_user(error)
            friendly_errors.append(formatted_error)
        
        # Adicionar dicas baseadas no layout detectado
        detected_layout = validation_result.details.get("detected_layout")
        if detected_layout and not validation_result.errors:
            tips = error_messages.get_validation_tips(detected_layout)
            friendly_errors.append({
                "title": "Dicas de Validação",
                "message": "Boleto validado com sucesso",
                "tips": tips,
                "severity": "info"
            })
        
        return friendly_errors
    
    def validate_with_friendly_errors(self, codigo_input: str) -> Dict[str, Any]:
        """
        Validação com mensagens de erro amigáveis
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            Dict: Resultado com mensagens amigáveis
        """
        
        validation_result = self.validate(codigo_input)
        
        return {
            "is_valid": validation_result.is_valid,
            "technical_result": validation_result,
            "user_errors": self.get_user_friendly_errors(validation_result),
            "help_info": error_messages.get_format_help(),
            "suggestions": error_messages.get_validation_tips(
                validation_result.details.get("detected_layout")
            )
        }
    
    def validate_with_dv_correction(self, codigo_input: str, correction_mode: str = None) -> Dict[str, Any]:
        """
        Validação com correção automática de DV
        
        Args:
            codigo_input: Código de entrada
            correction_mode: Modo de correção ('strict', 'warning', 'auto')
            
        Returns:
            Dict: Resultado com validação e correção
        """
        
        if correction_mode is None:
            correction_mode = self.dv_correction_mode
        
        # Primeiro, tentar correção de DV
        correction_result = self.dv_corrector.correct_dv_errors(codigo_input, correction_mode)
        
        # Validar o código (original ou corrigido)
        codigo_para_validar = correction_result.corrected_code if correction_result.is_corrected else codigo_input
        validation_result = self.validate(codigo_para_validar)
        
        # Preparar resultado combinado
        result = {
            "is_valid": validation_result.is_valid,
            "original_code": codigo_input,
            "final_code": codigo_para_validar,
            "dv_correction": correction_result,
            "validation": validation_result,
            "user_message": self.dv_corrector.get_user_friendly_message(correction_result)
        }
        
        # Se ainda há erros após correção, incluir informações de debug
        if not validation_result.is_valid:
            result["remaining_errors"] = validation_result.errors
            result["debug_info"] = {
                "corrections_attempted": len(correction_result.corrections_made),
                "confidence_level": correction_result.confidence_level,
                "warnings": correction_result.warnings
            }
        
        return result
    
    def set_dv_correction_mode(self, mode: str):
        """
        Define o modo de correção de DV
        
        Args:
            mode: 'strict' (não corrige), 'warning' (corrige e avisa), 'auto' (corrige silenciosamente)
        """
        
        valid_modes = ['strict', 'warning', 'auto']
        if mode not in valid_modes:
            raise ValueError(f"Modo inválido: {mode}. Válidos: {valid_modes}")
        
        self.dv_correction_mode = mode
        logger.info(f"DV correction mode set to: {mode}")
    
    def validate_with_simple_correction(self, codigo_input: str) -> Dict[str, Any]:
        """
        Validação com correção simples de DV
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            Dict: Resultado com validação e correção simples
        """
        
        # Tentar correção simples primeiro
        correction_result = self.simple_corrector.correct_single_dv_error(codigo_input)
        
        # Usar código corrigido se a correção foi bem-sucedida
        codigo_para_validar = (
            correction_result['corrected_code'] 
            if correction_result['success'] and correction_result.get('corrections')
            else codigo_input
        )
        
        # Validar o código (original ou corrigido)
        validation_result = self.validate(codigo_para_validar)
        
        # Preparar resultado combinado
        result = {
            "is_valid": validation_result.is_valid,
            "original_code": codigo_input,
            "final_code": codigo_para_validar,
            "correction_applied": correction_result['success'] and bool(correction_result.get('corrections')),
            "correction_result": correction_result,
            "validation_result": validation_result
        }
        
        # Adicionar mensagem amigável
        if correction_result['success']:
            result["user_message"] = self.simple_corrector.get_user_friendly_message(correction_result)
        else:
            result["user_message"] = {
                'type': 'error',
                'title': 'Erro no Boleto',
                'message': correction_result.get('error', 'Erro na validação'),
                'action_required': True
            }
        
        # Se ainda há erros após correção, incluir informações
        if not validation_result.is_valid:
            result["remaining_errors"] = validation_result.errors
            result["debug_info"] = {
                "correction_attempted": correction_result['success'],
                "corrections_made": len(correction_result.get('corrections', [])),
                "validation_errors": len(validation_result.errors)
            }
        
        return result
    
    def enable_cache(self, enabled: bool = True):
        """Habilita/desabilita cache"""
        self._cache_enabled = enabled
        if not enabled:
            self.clear_cache()
        logger.info(f"Validation cache {'enabled' if enabled else 'disabled'}")


# Instância global para uso no sistema
boleto_validator = BoletoValidatorUnified()


def validate_boleto_code(codigo_input: str) -> Dict[str, Any]:
    """
    Função de conveniência para validação de boleto
    Interface compatível com o sistema existente
    
    Args:
        codigo_input: Código de barras ou linha digitável
        
    Returns:
        Dict: Resultado da validação
    """
    
    return boleto_validator.validate_with_legacy_compatibility(codigo_input)


def validate_boleto_simple(codigo_input: str) -> bool:
    """
    Validação simples que retorna apenas True/False
    
    Args:
        codigo_input: Código de barras ou linha digitável
        
    Returns:
        bool: True se válido, False caso contrário
    """
    
    try:
        result = boleto_validator.validate(codigo_input)
        return result.is_valid
    except Exception:
        return False