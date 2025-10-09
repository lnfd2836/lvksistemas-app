"""
Detector de Layout de Boletos
Identifica o tipo de layout baseado no banco e características específicas
"""

import re
from typing import Optional, Dict, Any
from enum import Enum


class BoletoLayout(Enum):
    """Tipos de layout de boleto suportados"""
    SIGCB = "SIGCB"  # Layout específico da Caixa Econômica Federal
    FEBRABAN_PADRAO = "FEBRABAN_PADRAO"  # Layout padrão FEBRABAN
    OUTROS = "OUTROS"  # Outros layouts específicos


class BoletoLayoutDetector:
    """Detecta o layout específico do boleto baseado no banco e características"""
    
    def __init__(self):
        # Mapeamento de bancos para layouts específicos
        self.banco_layouts = {
            "104": BoletoLayout.SIGCB,  # Caixa Econômica Federal
            "001": BoletoLayout.FEBRABAN_PADRAO,  # Banco do Brasil
            "341": BoletoLayout.FEBRABAN_PADRAO,  # Itaú
            "237": BoletoLayout.FEBRABAN_PADRAO,  # Bradesco
            "033": BoletoLayout.FEBRABAN_PADRAO,  # Santander
        }
    
    def detect_layout(self, codigo_input: str) -> BoletoLayout:
        """
        Detecta o layout do boleto baseado no código de entrada
        
        Args:
            codigo_input: Código de barras (44 dígitos) ou linha digitável (47-48 dígitos)
            
        Returns:
            BoletoLayout: Tipo de layout detectado
        """
        
        # Normalizar entrada
        codigo_limpo = self._normalize_input(codigo_input)
        
        if not codigo_limpo:
            return BoletoLayout.OUTROS
        
        # Detectar banco
        banco = self._extract_bank_code(codigo_limpo)
        
        if not banco:
            return BoletoLayout.OUTROS
        
        # Retornar layout específico do banco
        return self.banco_layouts.get(banco, BoletoLayout.FEBRABAN_PADRAO)
    
    def is_caixa_sigcb(self, codigo_input: str) -> bool:
        """
        Verifica se é boleto Caixa com layout SIGCB
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            bool: True se for Caixa SIGCB
        """
        
        layout = self.detect_layout(codigo_input)
        return layout == BoletoLayout.SIGCB
    
    def get_bank_info(self, codigo_input: str) -> Dict[str, Any]:
        """
        Extrai informações do banco do código
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            Dict: Informações do banco
        """
        
        codigo_limpo = self._normalize_input(codigo_input)
        banco = self._extract_bank_code(codigo_limpo)
        layout = self.detect_layout(codigo_input)
        
        # Mapeamento de nomes dos bancos
        banco_nomes = {
            "104": "Caixa Econômica Federal",
            "001": "Banco do Brasil",
            "341": "Itaú Unibanco",
            "237": "Bradesco",
            "033": "Santander",
        }
        
        return {
            "codigo": banco,
            "nome": banco_nomes.get(banco, f"Banco {banco}"),
            "layout": layout.value,
            "is_sigcb": layout == BoletoLayout.SIGCB,
            "is_febraban_padrao": layout == BoletoLayout.FEBRABAN_PADRAO
        }
    
    def _normalize_input(self, codigo_input: str) -> str:
        """
        Normaliza a entrada removendo caracteres não numéricos
        
        Args:
            codigo_input: Código com ou sem formatação
            
        Returns:
            str: Código apenas com números
        """
        
        if not codigo_input or not isinstance(codigo_input, str):
            return ""
        
        # Remove tudo que não é número
        codigo_limpo = re.sub(r'[^0-9]', '', codigo_input)
        
        return codigo_limpo
    
    def _extract_bank_code(self, codigo_limpo: str) -> Optional[str]:
        """
        Extrai o código do banco do código normalizado
        
        Args:
            codigo_limpo: Código apenas com números
            
        Returns:
            Optional[str]: Código do banco (3 dígitos) ou None
        """
        
        if not codigo_limpo:
            return None
        
        # Verificar se é código de barras (44 dígitos)
        if len(codigo_limpo) == 44:
            return codigo_limpo[0:3]
        
        # Verificar se é linha digitável (47 dígitos)
        elif len(codigo_limpo) == 47:
            return codigo_limpo[0:3]
        
        # Verificar se é linha digitável com 48 dígitos (alguns casos especiais)
        elif len(codigo_limpo) == 48:
            return codigo_limpo[0:3]
        
        # Se não é um formato reconhecido, tentar extrair os primeiros 3 dígitos
        elif len(codigo_limpo) >= 3:
            return codigo_limpo[0:3]
        
        return None
    
    def validate_format(self, codigo_input: str) -> Dict[str, Any]:
        """
        Valida o formato básico do código de entrada
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            Dict: Resultado da validação de formato
        """
        
        result = {
            "is_valid": False,
            "format_type": None,
            "length": 0,
            "expected_length": None,
            "errors": []
        }
        
        if not codigo_input:
            result["errors"].append("Código não fornecido")
            return result
        
        if not isinstance(codigo_input, str):
            result["errors"].append(f"Código deve ser string, recebido {type(codigo_input)}")
            return result
        
        codigo_limpo = self._normalize_input(codigo_input)
        result["length"] = len(codigo_limpo)
        
        # Verificar se contém apenas números após normalização
        if not codigo_limpo.isdigit():
            result["errors"].append("Código deve conter apenas números")
            return result
        
        # Identificar tipo de formato
        if len(codigo_limpo) == 44:
            result["format_type"] = "codigo_barras"
            result["expected_length"] = 44
            result["is_valid"] = True
        elif len(codigo_limpo) == 47:
            result["format_type"] = "linha_digitavel"
            result["expected_length"] = 47
            result["is_valid"] = True
        elif len(codigo_limpo) == 48:
            result["format_type"] = "linha_digitavel_especial"
            result["expected_length"] = 48
            result["is_valid"] = True
        else:
            result["errors"].append(
                f"Comprimento inválido: {len(codigo_limpo)} dígitos. "
                f"Esperado: 44 (código de barras) ou 47-48 (linha digitável)"
            )
        
        return result
    
    def get_layout_specifications(self, layout: BoletoLayout) -> Dict[str, Any]:
        """
        Retorna especificações do layout
        
        Args:
            layout: Tipo de layout
            
        Returns:
            Dict: Especificações do layout
        """
        
        specifications = {
            BoletoLayout.SIGCB: {
                "name": "CAIXA SIGCB",
                "description": "Layout específico da Caixa Econômica Federal",
                "bank_code": "104",
                "field_structure": {
                    "codigo_cedente": {"start": 19, "end": 25, "length": 6},
                    "nosso_numero": {"start": 25, "end": 35, "length": 10},
                    "agencia_conta": {"start": 35, "end": 41, "length": 6},
                    "carteira": {"start": 41, "end": 44, "length": 3}
                },
                "valid_carteiras": ["001", "002", "014", "024"],
                "dv_algorithm": "modulo_11_febraban"
            },
            BoletoLayout.FEBRABAN_PADRAO: {
                "name": "FEBRABAN Padrão",
                "description": "Layout padrão FEBRABAN para bancos diversos",
                "bank_code": "varies",
                "field_structure": {
                    "campo_livre": {"start": 19, "end": 44, "length": 25}
                },
                "dv_algorithm": "modulo_11_febraban"
            },
            BoletoLayout.OUTROS: {
                "name": "Outros",
                "description": "Layouts específicos não mapeados",
                "bank_code": "varies",
                "field_structure": {},
                "dv_algorithm": "varies"
            }
        }
        
        return specifications.get(layout, specifications[BoletoLayout.OUTROS])