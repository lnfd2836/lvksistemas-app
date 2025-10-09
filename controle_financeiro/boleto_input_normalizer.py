"""
Normalizador de entrada para códigos de boleto
Processa diferentes formatos de entrada e normaliza para validação
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class NormalizedInput:
    """Resultado da normalização de entrada"""
    
    original_input: str
    normalized_code: str
    input_format: str  # "codigo_barras", "linha_digitavel", "unknown"
    is_valid_format: bool
    length: int
    errors: list
    warnings: list
    
    def __post_init__(self):
        if not hasattr(self, 'errors'):
            self.errors = []
        if not hasattr(self, 'warnings'):
            self.warnings = []


class BoletoInputNormalizer:
    """Normalizador de entrada para códigos de boleto"""
    
    def __init__(self):
        # Padrões de formatação comuns
        self.linha_digitavel_patterns = [
            # Formato padrão: AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D EEEEEEEEEEEEEE
            r'^\d{5}\.\d{5}\s+\d{5}\.\d{6}\s+\d{5}\.\d{6}\s+\d{1}\s+\d{14}$',
            # Formato sem pontos: AAAAA AAAAA BBBBB BBBBBB CCCCC CCCCCC D EEEEEEEEEEEEEE
            r'^\d{5}\s+\d{5}\s+\d{5}\s+\d{6}\s+\d{5}\s+\d{6}\s+\d{1}\s+\d{14}$',
            # Formato compacto: AAAAAAAAA BBBBBBBBBBB CCCCCCCCCCC D EEEEEEEEEEEEEE
            r'^\d{10}\s+\d{11}\s+\d{11}\s+\d{1}\s+\d{14}$'
        ]
        
        self.codigo_barras_patterns = [
            # Código de barras: 44 dígitos consecutivos
            r'^\d{44}$',
            # Código de barras com espaços: grupos de 4 dígitos
            r'^(\d{4}\s*){11}$'
        ]
    
    def normalize(self, codigo_input: str) -> NormalizedInput:
        """
        Normaliza entrada de código de boleto
        
        Args:
            codigo_input: Código de entrada em qualquer formato
            
        Returns:
            NormalizedInput: Resultado da normalização
        """
        
        result = NormalizedInput(
            original_input=codigo_input,
            normalized_code="",
            input_format="unknown",
            is_valid_format=False,
            length=0,
            errors=[],
            warnings=[]
        )
        
        # Validação inicial
        if not codigo_input:
            result.errors.append("Código não fornecido")
            return result
        
        if not isinstance(codigo_input, str):
            result.errors.append(f"Código deve ser string, recebido {type(codigo_input)}")
            return result
        
        # Limpeza básica
        cleaned_input = self._clean_input(codigo_input)
        result.normalized_code = self._extract_digits_only(cleaned_input)
        result.length = len(result.normalized_code)
        
        # Validar se contém apenas números após limpeza
        if not result.normalized_code.isdigit():
            result.errors.append("Código deve conter apenas números")
            return result
        
        # Detectar formato
        format_info = self._detect_format(result.normalized_code, cleaned_input)
        result.input_format = format_info["format"]
        result.is_valid_format = format_info["is_valid"]
        
        if format_info["errors"]:
            result.errors.extend(format_info["errors"])
        
        if format_info["warnings"]:
            result.warnings.extend(format_info["warnings"])
        
        return result
    
    def _clean_input(self, codigo_input: str) -> str:
        """
        Limpeza inicial da entrada
        
        Args:
            codigo_input: Código original
            
        Returns:
            str: Código com limpeza básica
        """
        
        # Remover quebras de linha e tabs
        cleaned = re.sub(r'[\r\n\t]', '', codigo_input)
        
        # Normalizar espaços múltiplos
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remover espaços no início e fim
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _extract_digits_only(self, codigo_input: str) -> str:
        """
        Extrai apenas dígitos do código
        
        Args:
            codigo_input: Código com formatação
            
        Returns:
            str: Apenas dígitos
        """
        
        return re.sub(r'[^0-9]', '', codigo_input)
    
    def _detect_format(self, codigo_limpo: str, codigo_formatado: str) -> Dict[str, Any]:
        """
        Detecta o formato do código
        
        Args:
            codigo_limpo: Código apenas com dígitos
            codigo_formatado: Código com formatação original
            
        Returns:
            Dict: Informações do formato detectado
        """
        
        result = {
            "format": "unknown",
            "is_valid": False,
            "errors": [],
            "warnings": []
        }
        
        length = len(codigo_limpo)
        
        # Código de barras (44 dígitos)
        if length == 44:
            result["format"] = "codigo_barras"
            result["is_valid"] = True
            
            # Verificar se estava formatado como código de barras
            if self._matches_codigo_barras_pattern(codigo_formatado):
                result["warnings"].append("Código de barras detectado com formatação")
        
        # Linha digitável (47 dígitos)
        elif length == 47:
            result["format"] = "linha_digitavel"
            result["is_valid"] = True
            
            # Verificar se estava formatado como linha digitável
            if self._matches_linha_digitavel_pattern(codigo_formatado):
                result["warnings"].append("Linha digitável detectada com formatação padrão")
            else:
                result["warnings"].append("Linha digitável detectada sem formatação padrão")
        
        # Linha digitável especial (48 dígitos - alguns casos raros)
        elif length == 48:
            result["format"] = "linha_digitavel_especial"
            result["is_valid"] = True
            result["warnings"].append("Linha digitável com 48 dígitos detectada (formato especial)")
        
        # Comprimentos inválidos
        else:
            result["errors"].append(
                f"Comprimento inválido: {length} dígitos. "
                f"Esperado: 44 (código de barras) ou 47-48 (linha digitável)"
            )
            
            # Tentar sugerir o que pode estar errado
            if length < 44:
                result["errors"].append("Código muito curto - verifique se não faltam dígitos")
            elif length > 48:
                result["errors"].append("Código muito longo - verifique se não há dígitos extras")
        
        return result
    
    def _matches_linha_digitavel_pattern(self, codigo_formatado: str) -> bool:
        """Verifica se corresponde a padrão de linha digitável"""
        
        for pattern in self.linha_digitavel_patterns:
            if re.match(pattern, codigo_formatado):
                return True
        return False
    
    def _matches_codigo_barras_pattern(self, codigo_formatado: str) -> bool:
        """Verifica se corresponde a padrão de código de barras"""
        
        for pattern in self.codigo_barras_patterns:
            if re.match(pattern, codigo_formatado):
                return True
        return False
    
    def validate_characters(self, codigo_input: str) -> Dict[str, Any]:
        """
        Valida caracteres permitidos na entrada
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            Dict: Resultado da validação de caracteres
        """
        
        result = {
            "is_valid": True,
            "invalid_chars": [],
            "suggestions": []
        }
        
        if not codigo_input:
            result["is_valid"] = False
            return result
        
        # Caracteres permitidos: dígitos, pontos, espaços, hífens
        allowed_pattern = r'^[0-9\.\s\-]+$'
        
        if not re.match(allowed_pattern, codigo_input):
            result["is_valid"] = False
            
            # Encontrar caracteres inválidos
            invalid_chars = set()
            for char in codigo_input:
                if not re.match(r'[0-9\.\s\-]', char):
                    invalid_chars.add(char)
            
            result["invalid_chars"] = list(invalid_chars)
            
            # Sugestões de correção
            if invalid_chars:
                result["suggestions"].append(
                    f"Remover caracteres inválidos: {', '.join(invalid_chars)}"
                )
                result["suggestions"].append(
                    "Usar apenas números, pontos, espaços e hífens"
                )
        
        return result
    
    def auto_detect_and_normalize(self, codigo_input: str) -> Dict[str, Any]:
        """
        Detecção automática e normalização completa
        
        Args:
            codigo_input: Código de entrada
            
        Returns:
            Dict: Resultado completo da normalização
        """
        
        # Normalização básica
        normalized = self.normalize(codigo_input)
        
        # Validação de caracteres
        char_validation = self.validate_characters(codigo_input)
        
        # Sugestões de formato
        format_suggestions = self._get_format_suggestions(normalized)
        
        return {
            "normalized": normalized,
            "character_validation": char_validation,
            "format_suggestions": format_suggestions,
            "is_processable": normalized.is_valid_format and char_validation["is_valid"]
        }
    
    def _get_format_suggestions(self, normalized: NormalizedInput) -> List[str]:
        """
        Gera sugestões de formato baseado na entrada
        
        Args:
            normalized: Resultado da normalização
            
        Returns:
            List[str]: Lista de sugestões
        """
        
        suggestions = []
        
        if not normalized.is_valid_format:
            if normalized.length < 44:
                suggestions.append("Verifique se o código está completo")
                suggestions.append("Código de barras deve ter 44 dígitos")
                suggestions.append("Linha digitável deve ter 47 dígitos")
            
            elif normalized.length > 48:
                suggestions.append("Código muito longo - remova dígitos extras")
                suggestions.append("Verifique se não há duplicação de dados")
            
            else:
                suggestions.append(f"Comprimento {normalized.length} não é padrão")
                suggestions.append("Verifique o formato do código")
        
        else:
            if normalized.input_format == "codigo_barras":
                suggestions.append("Código de barras detectado corretamente")
                suggestions.append("Formato: 44 dígitos consecutivos")
            
            elif normalized.input_format == "linha_digitavel":
                suggestions.append("Linha digitável detectada corretamente")
                suggestions.append("Formato padrão: AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D EEEEEEEEEEEEEE")
        
        return suggestions
    
    def format_for_display(self, codigo_limpo: str, format_type: str) -> str:
        """
        Formata código para exibição
        
        Args:
            codigo_limpo: Código apenas com dígitos
            format_type: Tipo de formato desejado
            
        Returns:
            str: Código formatado para exibição
        """
        
        if format_type == "linha_digitavel" and len(codigo_limpo) == 47:
            # Formato: AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D EEEEEEEEEEEEEE
            return (
                f"{codigo_limpo[0:5]}.{codigo_limpo[5:10]} "
                f"{codigo_limpo[10:15]}.{codigo_limpo[15:21]} "
                f"{codigo_limpo[21:26]}.{codigo_limpo[26:32]} "
                f"{codigo_limpo[32:33]} "
                f"{codigo_limpo[33:47]}"
            )
        
        elif format_type == "codigo_barras" and len(codigo_limpo) == 44:
            # Formato: grupos de 4 dígitos para legibilidade
            grupos = [codigo_limpo[i:i+4] for i in range(0, 44, 4)]
            return " ".join(grupos)
        
        else:
            # Retornar sem formatação se não for possível formatar
            return codigo_limpo