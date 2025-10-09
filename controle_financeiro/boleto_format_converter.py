"""
Conversor universal de formatos de boleto
Converte entre linha digitável e código de barras para diferentes layouts
"""

from typing import Dict, Any, Optional
from enum import Enum

try:
    from .boleto_layout_detector import BoletoLayoutDetector, BoletoLayout
    from .boleto_input_normalizer import BoletoInputNormalizer
    from .sigcb_validator import SIGCBValidator
    from .boleto_validator_base import ValidationResult, DVCalculatorMixin, FormatNormalizerMixin
except ImportError:
    from boleto_layout_detector import BoletoLayoutDetector, BoletoLayout
    from boleto_input_normalizer import BoletoInputNormalizer
    from sigcb_validator import SIGCBValidator
    from boleto_validator_base import ValidationResult, DVCalculatorMixin, FormatNormalizerMixin


class ConversionResult:
    """Resultado da conversão de formato"""
    
    def __init__(self):
        self.success = False
        self.converted_code = ""
        self.original_format = ""
        self.target_format = ""
        self.layout_type = ""
        self.errors = []
        self.warnings = []
        self.details = {}
    
    def add_error(self, error: str):
        """Adiciona erro"""
        self.success = False
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Adiciona aviso"""
        self.warnings.append(warning)
    
    def add_detail(self, key: str, value: Any):
        """Adiciona detalhe"""
        self.details[key] = value


class BoletoFormatConverter(DVCalculatorMixin, FormatNormalizerMixin):
    """Conversor universal de formatos de boleto"""
    
    def __init__(self):
        self.layout_detector = BoletoLayoutDetector()
        self.input_normalizer = BoletoInputNormalizer()
        self.sigcb_validator = SIGCBValidator()
    
    def linha_to_codigo_barras(self, linha_digitavel: str, layout: Optional[str] = None) -> ConversionResult:
        """
        Converte linha digitável para código de barras
        
        Args:
            linha_digitavel: Linha digitável de entrada
            layout: Layout específico (opcional, será detectado automaticamente)
            
        Returns:
            ConversionResult: Resultado da conversão
        """
        
        result = ConversionResult()
        result.original_format = "linha_digitavel"
        result.target_format = "codigo_barras"
        
        try:
            # Normalizar entrada
            normalized = self.input_normalizer.normalize(linha_digitavel)
            
            if not normalized.is_valid_format:
                for error in normalized.errors:
                    result.add_error(error)
                return result
            
            if normalized.input_format != "linha_digitavel":
                result.add_error(f"Entrada não é linha digitável: {normalized.input_format}")
                return result
            
            # Detectar layout
            detected_layout = layout or self.layout_detector.detect_layout(normalized.normalized_code)
            result.layout_type = detected_layout.value if isinstance(detected_layout, BoletoLayout) else str(detected_layout)
            
            # Converter baseado no layout
            if detected_layout == BoletoLayout.SIGCB:
                codigo_barras = self.sigcb_validator.convert_linha_to_codigo(normalized.normalized_code)
            else:
                codigo_barras = self._convert_linha_febraban_padrao(normalized.normalized_code)
            
            result.converted_code = codigo_barras
            result.success = True
            result.add_detail("original_length", len(normalized.normalized_code))
            result.add_detail("converted_length", len(codigo_barras))
            
        except Exception as e:
            result.add_error(f"Erro na conversão: {str(e)}")
        
        return result
    
    def codigo_barras_to_linha(self, codigo_barras: str, layout: Optional[str] = None) -> ConversionResult:
        """
        Converte código de barras para linha digitável
        
        Args:
            codigo_barras: Código de barras de entrada
            layout: Layout específico (opcional, será detectado automaticamente)
            
        Returns:
            ConversionResult: Resultado da conversão
        """
        
        result = ConversionResult()
        result.original_format = "codigo_barras"
        result.target_format = "linha_digitavel"
        
        try:
            # Normalizar entrada
            normalized = self.input_normalizer.normalize(codigo_barras)
            
            if not normalized.is_valid_format:
                for error in normalized.errors:
                    result.add_error(error)
                return result
            
            if normalized.input_format != "codigo_barras":
                result.add_error(f"Entrada não é código de barras: {normalized.input_format}")
                return result
            
            # Detectar layout
            detected_layout = layout or self.layout_detector.detect_layout(normalized.normalized_code)
            result.layout_type = detected_layout.value if isinstance(detected_layout, BoletoLayout) else str(detected_layout)
            
            # Converter baseado no layout
            if detected_layout == BoletoLayout.SIGCB:
                linha_digitavel = self.sigcb_validator.convert_codigo_to_linha(normalized.normalized_code)
            else:
                linha_digitavel = self._convert_codigo_febraban_padrao(normalized.normalized_code)
            
            result.converted_code = linha_digitavel
            result.success = True
            result.add_detail("original_length", len(normalized.normalized_code))
            result.add_detail("converted_length", len(linha_digitavel))
            
        except Exception as e:
            result.add_error(f"Erro na conversão: {str(e)}")
        
        return result
    
    def auto_convert(self, codigo_input: str, target_format: str) -> ConversionResult:
        """
        Conversão automática detectando formato de entrada
        
        Args:
            codigo_input: Código de entrada (qualquer formato)
            target_format: Formato desejado ("codigo_barras" ou "linha_digitavel")
            
        Returns:
            ConversionResult: Resultado da conversão
        """
        
        # Normalizar entrada
        normalized = self.input_normalizer.normalize(codigo_input)
        
        if not normalized.is_valid_format:
            result = ConversionResult()
            for error in normalized.errors:
                result.add_error(error)
            return result
        
        # Determinar conversão necessária
        if normalized.input_format == target_format:
            # Já está no formato desejado
            result = ConversionResult()
            result.success = True
            result.converted_code = normalized.normalized_code
            result.original_format = normalized.input_format
            result.target_format = target_format
            result.add_warning("Código já estava no formato desejado")
            return result
        
        # Executar conversão
        if target_format == "codigo_barras":
            return self.linha_to_codigo_barras(codigo_input)
        elif target_format == "linha_digitavel":
            return self.codigo_barras_to_linha(codigo_input)
        else:
            result = ConversionResult()
            result.add_error(f"Formato de destino inválido: {target_format}")
            return result
    
    def validate_conversion(self, original: str, converted: str) -> ValidationResult:
        """
        Valida se a conversão foi feita corretamente
        
        Args:
            original: Código original
            converted: Código convertido
            
        Returns:
            ValidationResult: Resultado da validação
        """
        
        result = ValidationResult(validation_type="Conversion_Validation")
        
        try:
            # Normalizar ambos
            original_norm = self.input_normalizer.normalize(original)
            converted_norm = self.input_normalizer.normalize(converted)
            
            if not original_norm.is_valid_format or not converted_norm.is_valid_format:
                result.add_error("Formato inválido em um dos códigos")
                return result
            
            # Detectar layouts
            original_layout = self.layout_detector.detect_layout(original_norm.normalized_code)
            converted_layout = self.layout_detector.detect_layout(converted_norm.normalized_code)
            
            # Layouts devem ser do mesmo banco
            original_bank = self.layout_detector.get_bank_info(original_norm.normalized_code)
            converted_bank = self.layout_detector.get_bank_info(converted_norm.normalized_code)
            
            if original_bank["codigo"] != converted_bank["codigo"]:
                result.add_error(
                    f"Bancos diferentes: original {original_bank['codigo']}, "
                    f"convertido {converted_bank['codigo']}"
                )
            
            # Validar conversão bidirecional
            if original_layout == BoletoLayout.SIGCB:
                self._validate_sigcb_conversion(original_norm.normalized_code, converted_norm.normalized_code, result)
            else:
                self._validate_febraban_conversion(original_norm.normalized_code, converted_norm.normalized_code, result)
            
        except Exception as e:
            result.add_error(f"Erro na validação de conversão: {str(e)}")
        
        return result
    
    def _convert_linha_febraban_padrao(self, linha_digitavel: str) -> str:
        """Converte linha digitável FEBRABAN padrão para código de barras"""
        
        if len(linha_digitavel) != 47:
            raise ValueError(f"Linha digitável deve ter 47 dígitos, tem {len(linha_digitavel)}")
        
        # Extrair campos
        campo1 = linha_digitavel[0:10]
        campo2 = linha_digitavel[10:21]
        campo3 = linha_digitavel[21:32]
        campo4 = linha_digitavel[32:33]
        campo5 = linha_digitavel[33:47]
        
        # Extrair componentes
        banco = campo1[0:3]
        moeda = campo1[3:4]
        dv_geral = campo4
        vencimento = campo5[0:4]
        valor = campo5[4:14]
        
        # Reconstruir campo livre
        parte1 = campo1[4:9]  # 5 dígitos (sem DV)
        parte2 = campo2[0:10]  # 10 dígitos (sem DV)
        parte3 = campo3[0:10]  # 10 dígitos (sem DV)
        
        campo_livre = f"{parte1}{parte2}{parte3}"
        
        return f"{banco}{moeda}{dv_geral}{vencimento}{valor}{campo_livre}"
    
    def _convert_codigo_febraban_padrao(self, codigo_barras: str) -> str:
        """Converte código de barras FEBRABAN padrão para linha digitável"""
        
        if len(codigo_barras) != 44:
            raise ValueError(f"Código de barras deve ter 44 dígitos, tem {len(codigo_barras)}")
        
        # Extrair componentes
        banco = codigo_barras[0:3]
        moeda = codigo_barras[3:4]
        dv_geral = codigo_barras[4:5]
        vencimento = codigo_barras[5:9]
        valor = codigo_barras[9:19]
        campo_livre = codigo_barras[19:44]
        
        # Campo 1: Banco + Moeda + primeiros 5 do campo livre + DV
        campo1_base = f"{banco}{moeda}{campo_livre[0:5]}"
        dv1 = self.calculate_dv_modulo10_febraban(campo1_base)
        campo1 = f"{campo1_base}{dv1}"
        
        # Campo 2: Próximos 10 dígitos do campo livre + DV
        campo2_base = campo_livre[5:15]
        dv2 = self.calculate_dv_modulo10_febraban(campo2_base)
        campo2 = f"{campo2_base}{dv2}"
        
        # Campo 3: Últimos 10 dígitos do campo livre + DV
        campo3_base = campo_livre[15:25]
        dv3 = self.calculate_dv_modulo10_febraban(campo3_base)
        campo3 = f"{campo3_base}{dv3}"
        
        # Campo 4: DV geral
        campo4 = dv_geral
        
        # Campo 5: Fator vencimento + valor
        campo5 = f"{vencimento}{valor}"
        
        return f"{campo1}{campo2}{campo3}{campo4}{campo5}"
    
    def _validate_sigcb_conversion(self, original: str, converted: str, result: ValidationResult):
        """Valida conversão SIGCB"""
        
        try:
            # Usar validador SIGCB para validar ambos
            original_validation = self.sigcb_validator.validate_complete(original)
            converted_validation = self.sigcb_validator.validate_complete(converted)
            
            if not original_validation.is_valid:
                result.add_error("Código original SIGCB inválido")
            
            if not converted_validation.is_valid:
                result.add_error("Código convertido SIGCB inválido")
            
            # Comparar componentes essenciais
            if original_validation.is_valid and converted_validation.is_valid:
                original_components = original_validation.details.get("components", {})
                converted_components = converted_validation.details.get("components", {})
                
                essential_fields = ["banco", "valor", "fator_vencimento", "campo_livre"]
                
                for field in essential_fields:
                    if original_components.get(field) != converted_components.get(field):
                        result.add_error(f"Campo {field} diferente após conversão")
            
        except Exception as e:
            result.add_error(f"Erro na validação SIGCB: {str(e)}")
    
    def _validate_febraban_conversion(self, original: str, converted: str, result: ValidationResult):
        """Valida conversão FEBRABAN padrão"""
        
        try:
            # Validação básica de formato
            original_format = self.detect_input_format(original)
            converted_format = self.detect_input_format(converted)
            
            if not original_format or not converted_format:
                result.add_error("Formato inválido detectado")
                return
            
            # Extrair componentes básicos para comparação
            if original_format == "codigo_barras" and converted_format == "linha_digitavel":
                # Reconverter linha para código e comparar
                reconverted = self._convert_linha_febraban_padrao(converted)
                if reconverted != original:
                    result.add_error("Conversão bidirecional falhou")
            
            elif original_format == "linha_digitavel" and converted_format == "codigo_barras":
                # Reconverter código para linha e comparar
                reconverted = self._convert_codigo_febraban_padrao(converted)
                if reconverted != original:
                    result.add_error("Conversão bidirecional falhou")
            
        except Exception as e:
            result.add_error(f"Erro na validação FEBRABAN: {str(e)}")
    
    def get_supported_layouts(self) -> Dict[str, Any]:
        """Retorna layouts suportados"""
        
        return {
            "SIGCB": {
                "name": "CAIXA SIGCB",
                "bank": "104",
                "description": "Layout específico da Caixa Econômica Federal",
                "supported_conversions": ["linha_digitavel", "codigo_barras"]
            },
            "FEBRABAN_PADRAO": {
                "name": "FEBRABAN Padrão",
                "bank": "varies",
                "description": "Layout padrão FEBRABAN para diversos bancos",
                "supported_conversions": ["linha_digitavel", "codigo_barras"]
            }
        }
    
    def format_for_display(self, codigo: str, format_type: str = "auto") -> str:
        """
        Formata código para exibição
        
        Args:
            codigo: Código a ser formatado
            format_type: Tipo de formatação ("auto", "linha_digitavel", "codigo_barras")
            
        Returns:
            str: Código formatado
        """
        
        normalized = self.input_normalizer.normalize(codigo)
        
        if not normalized.is_valid_format:
            return codigo  # Retorna original se não conseguir normalizar
        
        # Determinar formato de exibição
        if format_type == "auto":
            format_type = normalized.input_format
        
        return self.input_normalizer.format_for_display(normalized.normalized_code, format_type)