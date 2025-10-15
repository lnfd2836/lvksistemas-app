"""
Interface base para validadores de boleto
Define estruturas comuns e contratos para diferentes tipos de validação
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ValidationResult:
    """Resultado padronizado de validação de boleto"""
    
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    validation_type: str = "generic"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_error(self, error_message: str):
        """Adiciona um erro de validação"""
        self.is_valid = False
        self.errors.append(error_message)
    
    def add_warning(self, warning_message: str):
        """Adiciona um aviso de validação"""
        self.warnings.append(warning_message)
    
    def add_detail(self, key: str, value: Any):
        """Adiciona detalhes da validação"""
        self.details[key] = value
    
    def merge(self, other_result: 'ValidationResult'):
        """Combina este resultado com outro"""
        if not other_result.is_valid:
            self.is_valid = False
        
        self.errors.extend(other_result.errors)
        self.warnings.extend(other_result.warnings)
        self.details.update(other_result.details)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo do resultado"""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "validation_type": self.validation_type,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class BoletoComponents:
    """Componentes extraídos de um boleto"""
    
    # Componentes básicos (presentes em todos os layouts)
    banco: str = ""
    moeda: str = ""
    dv_geral: str = ""
    fator_vencimento: str = ""
    valor: str = ""
    campo_livre: str = ""
    
    # Componentes da linha digitável
    campo1: str = ""
    campo2: str = ""
    campo3: str = ""
    campo4: str = ""
    campo5: str = ""
    
    # Componentes específicos (variam por layout)
    codigo_cedente: str = ""
    nosso_numero: str = ""
    agencia: str = ""
    conta: str = ""
    carteira: str = ""
    
    # Metadados
    layout_type: str = ""
    input_format: str = ""  # "codigo_barras" ou "linha_digitavel"
    
    def to_dict(self) -> Dict[str, str]:
        """Converte para dicionário"""
        return {
            "banco": self.banco,
            "moeda": self.moeda,
            "dv_geral": self.dv_geral,
            "fator_vencimento": self.fator_vencimento,
            "valor": self.valor,
            "campo_livre": self.campo_livre,
            "campo1": self.campo1,
            "campo2": self.campo2,
            "campo3": self.campo3,
            "campo4": self.campo4,
            "campo5": self.campo5,
            "codigo_cedente": self.codigo_cedente,
            "nosso_numero": self.nosso_numero,
            "agencia": self.agencia,
            "conta": self.conta,
            "carteira": self.carteira,
            "layout_type": self.layout_type,
            "input_format": self.input_format
        }


class BoletoValidatorBase(ABC):
    """Classe base abstrata para validadores de boleto"""
    
    def __init__(self, validator_name: str):
        self.validator_name = validator_name
        self.supported_banks = []
        self.supported_layouts = []
    
    @abstractmethod
    def validate_format(self, codigo_input: str) -> ValidationResult:
        """
        Valida o formato básico do código
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            ValidationResult: Resultado da validação de formato
        """
        pass
    
    @abstractmethod
    def validate_dv(self, codigo_input: str) -> ValidationResult:
        """
        Valida dígitos verificadores
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            ValidationResult: Resultado da validação de DV
        """
        pass
    
    @abstractmethod
    def validate_business_rules(self, codigo_input: str) -> ValidationResult:
        """
        Valida regras de negócio específicas
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            ValidationResult: Resultado da validação de regras de negócio
        """
        pass
    
    @abstractmethod
    def extract_components(self, codigo_input: str) -> BoletoComponents:
        """
        Extrai componentes do código
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            BoletoComponents: Componentes extraídos
        """
        pass
    
    def validate_complete(self, codigo_input: str) -> ValidationResult:
        """
        Executa validação completa (template method)
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            ValidationResult: Resultado da validação completa
        """
        
        result = ValidationResult(validation_type=self.validator_name)
        
        try:
            # 1. Validação de formato
            format_result = self.validate_format(codigo_input)
            result.merge(format_result)
            
            if not format_result.is_valid:
                return result
            
            # 2. Validação de dígitos verificadores
            dv_result = self.validate_dv(codigo_input)
            result.merge(dv_result)
            
            # 3. Validação de regras de negócio
            business_result = self.validate_business_rules(codigo_input)
            result.merge(business_result)
            
            # 4. Extrair componentes para detalhes
            try:
                components = self.extract_components(codigo_input)
                result.add_detail("components", components.to_dict())
            except Exception as e:
                result.add_warning(f"Erro ao extrair componentes: {str(e)}")
            
        except Exception as e:
            result.add_error(f"Erro durante validação: {str(e)}")
        
        return result
    
    def supports_bank(self, bank_code: str) -> bool:
        """Verifica se suporta o banco"""
        return bank_code in self.supported_banks
    
    def supports_layout(self, layout_type: str) -> bool:
        """Verifica se suporta o layout"""
        return layout_type in self.supported_layouts
    
    def get_validator_info(self) -> Dict[str, Any]:
        """Retorna informações do validador"""
        return {
            "name": self.validator_name,
            "supported_banks": self.supported_banks,
            "supported_layouts": self.supported_layouts,
            "description": self.__doc__ or "Validador de boleto"
        }


class DVCalculatorMixin:
    """Mixin com algoritmos de cálculo de dígito verificador"""
    
    def calculate_dv_modulo10_febraban(self, codigo: str) -> int:
        """
        Calcula DV usando módulo 10 FEBRABAN
        
        Args:
            codigo: Código para calcular DV
            
        Returns:
            int: Dígito verificador calculado
        """
        
        soma = 0
        multiplicador = 2
        
        for digito in reversed(codigo):
            if digito.isdigit():
                produto = int(digito) * multiplicador
                
                if produto > 9:
                    produto = sum(int(d) for d in str(produto))
                
                soma += produto
                multiplicador = 3 - multiplicador  # Alterna entre 2 e 1
        
        resto = soma % 10
        return 0 if resto == 0 else 10 - resto
    
    def calculate_dv_modulo11_febraban(self, codigo: str) -> int:
        """
        Calcula DV usando módulo 11 FEBRABAN
        
        Args:
            codigo: Código para calcular DV
            
        Returns:
            int: Dígito verificador calculado
        """
        
        soma = 0
        peso = 2
        
        # Multiplica cada dígito pela sequência de pesos (da direita para esquerda)
        for digito in reversed(codigo):
            if digito.isdigit():
                soma += int(digito) * peso
                peso += 1
                if peso > 9:
                    peso = 2
        
        resto = soma % 11
        
        if resto in [0, 10, 11]:
            return 1
        else:
            dv = 11 - resto
            if dv == 10:
                return 0
            return dv
    
    def calculate_dv_modulo11_caixa(self, codigo: str) -> int:
        """
        Calcula DV usando módulo 11 específico da Caixa
        
        Args:
            codigo: Código para calcular DV
            
        Returns:
            int: Dígito verificador calculado
        """
        
        sequencia = "4329876543298765432987654329876543298765"
        soma = 0
        
        for i, digito in enumerate(reversed(codigo)):
            if digito.isdigit():
                multiplicador = int(sequencia[i % len(sequencia)])
                produto = int(digito) * multiplicador
                soma += produto
        
        resto = soma % 11
        
        # Regras específicas da Caixa para alguns casos
        if resto in [0, 1, 10]:
            return 0
        else:
            return 11 - resto


class FormatNormalizerMixin:
    """Mixin com utilitários de normalização de formato"""
    
    def normalize_input(self, codigo_input: str) -> str:
        """
        Normaliza entrada removendo caracteres não numéricos
        
        Args:
            codigo_input: Código com ou sem formatação
            
        Returns:
            str: Código apenas com números
        """
        
        if not codigo_input or not isinstance(codigo_input, str):
            return ""
        
        import re
        return re.sub(r'[^0-9]', '', codigo_input)
    
    def detect_input_format(self, codigo_limpo: str) -> Optional[str]:
        """
        Detecta o formato da entrada
        
        Args:
            codigo_limpo: Código normalizado
            
        Returns:
            Optional[str]: Tipo de formato ou None
        """
        
        if not codigo_limpo or not codigo_limpo.isdigit():
            return None
        
        length = len(codigo_limpo)
        
        if length == 44:
            return "codigo_barras"
        elif length == 47:
            return "linha_digitavel"
        elif length == 48:
            return "linha_digitavel_especial"
        else:
            return None
    
    def format_linha_digitavel(self, linha_limpa: str) -> str:
        """
        Formata linha digitável com pontos e espaços
        
        Args:
            linha_limpa: Linha digitável sem formatação
            
        Returns:
            str: Linha digitável formatada
        """
        
        if len(linha_limpa) != 47:
            return linha_limpa
        
        # Formato: AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D EEEEEEEEEEEEEE
        campo1 = f"{linha_limpa[0:5]}.{linha_limpa[5:10]}"
        campo2 = f"{linha_limpa[10:15]}.{linha_limpa[15:21]}"
        campo3 = f"{linha_limpa[21:26]}.{linha_limpa[26:32]}"
        campo4 = linha_limpa[32:33]
        campo5 = linha_limpa[33:47]
        
        return f"{campo1} {campo2} {campo3} {campo4} {campo5}"