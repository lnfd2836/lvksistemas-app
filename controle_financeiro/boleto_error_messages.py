"""
Mensagens de erro específicas e amigáveis para validação de boletos
Centraliza todas as mensagens de erro e sugestões de correção
"""

from typing import Dict, List, Any
from enum import Enum


class ErrorCategory(Enum):
    """Categorias de erro para classificação"""
    FORMAT = "format"
    DV = "dv"
    BUSINESS = "business"
    SIGCB = "sigcb"
    CONVERSION = "conversion"
    SYSTEM = "system"


class BoletoErrorMessages:
    """Centralizador de mensagens de erro para boletos"""
    
    def __init__(self):
        # Mensagens de erro por categoria
        self.error_messages = {
            # Erros de formato
            ErrorCategory.FORMAT: {
                "empty_code": {
                    "message": "Código de barras não foi fornecido",
                    "suggestion": "Digite ou cole o código de barras do boleto",
                    "example": "Exemplo: 10492.67014 51500.171429 22946.570144 7 22600000002990"
                },
                "invalid_length": {
                    "message": "Comprimento do código inválido: {length} dígitos",
                    "suggestion": "Código de barras deve ter 44 dígitos ou linha digitável 47 dígitos",
                    "example": "Verifique se o código está completo"
                },
                "invalid_characters": {
                    "message": "Código contém caracteres inválidos: {chars}",
                    "suggestion": "Use apenas números, pontos, espaços e hífens",
                    "example": "Remova letras, símbolos especiais ou caracteres estranhos"
                },
                "not_numeric": {
                    "message": "Código deve conter apenas números após formatação",
                    "suggestion": "Verifique se não há letras misturadas com os números",
                    "example": "Correto: 1049267014... | Incorreto: 104O267014..."
                }
            },
            
            # Erros de dígito verificador
            ErrorCategory.DV: {
                "dv_geral_invalid": {
                    "message": "Dígito verificador geral inválido: informado {informed}, calculado {calculated}",
                    "suggestion": "Verifique se o código foi digitado corretamente",
                    "example": "Confira cada dígito do código de barras"
                },
                "dv_campo1_invalid": {
                    "message": "Dígito verificador do campo 1 inválido",
                    "suggestion": "Erro nos primeiros dígitos da linha digitável",
                    "example": "Verifique os primeiros 10 dígitos: AAAAA.AAAAA"
                },
                "dv_campo2_invalid": {
                    "message": "Dígito verificador do campo 2 inválido",
                    "suggestion": "Erro no segundo grupo da linha digitável",
                    "example": "Verifique os dígitos: BBBBB.BBBBBB"
                },
                "dv_campo3_invalid": {
                    "message": "Dígito verificador do campo 3 inválido",
                    "suggestion": "Erro no terceiro grupo da linha digitável",
                    "example": "Verifique os dígitos: CCCCC.CCCCCC"
                }
            },
            
            # Erros de regras de negócio
            ErrorCategory.BUSINESS: {
                "invalid_bank": {
                    "message": "Banco não reconhecido: {bank_code}",
                    "suggestion": "Verifique se o código é de um banco válido",
                    "example": "Códigos comuns: 104 (Caixa), 001 (BB), 341 (Itaú)"
                },
                "invalid_currency": {
                    "message": "Código da moeda inválido: {currency}",
                    "suggestion": "Moeda deve ser 9 (Real brasileiro)",
                    "example": "O 4º dígito do código deve ser 9"
                },
                "invalid_due_date": {
                    "message": "Fator de vencimento inválido: {factor}",
                    "suggestion": "Data de vencimento pode estar incorreta",
                    "example": "Verifique se o boleto não está muito antigo"
                },
                "invalid_amount": {
                    "message": "Valor inválido: R$ {amount}",
                    "suggestion": "Valor deve ser maior que zero",
                    "example": "Verifique se o valor do boleto está correto"
                },
                "zero_agency": {
                    "message": "Agência não pode ser zero",
                    "suggestion": "Código da agência deve ser válido",
                    "example": "Agência deve ter 4 dígitos não-zero"
                }
            },
            
            # Erros específicos do SIGCB (Caixa)
            ErrorCategory.SIGCB: {
                "not_caixa": {
                    "message": "Código não é da Caixa Econômica Federal",
                    "suggestion": "Este validador é específico para boletos da Caixa (código 104)",
                    "example": "Para outros bancos, use validação FEBRABAN padrão"
                },
                "invalid_carteira": {
                    "message": "Carteira {carteira} pode não ser válida para a Caixa",
                    "suggestion": "Carteiras comuns da Caixa: 001, 002, 014, 024",
                    "example": "Verifique com seu gerente se a carteira está correta"
                },
                "zero_cedente": {
                    "message": "Código do cedente é zero",
                    "suggestion": "Verifique a configuração do convênio com a Caixa",
                    "example": "Entre em contato com seu gerente para ativar o convênio"
                },
                "zero_nosso_numero": {
                    "message": "Nosso número não pode ser zero",
                    "suggestion": "Nosso número deve ser gerado automaticamente",
                    "example": "Verifique a configuração de geração de boletos"
                },
                "convenio_inactive": {
                    "message": "Convênio pode não estar ativo",
                    "suggestion": "Convênio deve ser ativado pela Caixa para funcionar",
                    "example": "Entre em contato com seu gerente da Caixa"
                }
            },
            
            # Erros de conversão
            ErrorCategory.CONVERSION: {
                "conversion_failed": {
                    "message": "Falha na conversão entre formatos",
                    "suggestion": "Código pode estar corrompido ou incompleto",
                    "example": "Verifique se todos os dígitos estão presentes"
                },
                "bidirectional_failed": {
                    "message": "Conversão bidirecional falhou",
                    "suggestion": "Inconsistência entre linha digitável e código de barras",
                    "example": "Verifique se o código não foi alterado manualmente"
                },
                "format_mismatch": {
                    "message": "Formato de entrada não corresponde ao esperado",
                    "suggestion": "Verifique se está usando o formato correto",
                    "example": "Linha digitável: 47 dígitos | Código de barras: 44 dígitos"
                }
            },
            
            # Erros de sistema
            ErrorCategory.SYSTEM: {
                "validation_error": {
                    "message": "Erro interno durante validação: {error}",
                    "suggestion": "Tente novamente ou entre em contato com o suporte",
                    "example": "Se o problema persistir, reporte o erro"
                },
                "layout_detection_failed": {
                    "message": "Não foi possível detectar o layout do boleto",
                    "suggestion": "Código pode estar em formato não reconhecido",
                    "example": "Verifique se é um boleto bancário válido"
                }
            }
        }
        
        # Exemplos de códigos válidos
        self.valid_examples = {
            "caixa_linha": "10492.67014 51500.171429 22946.570144 7 22600000002990",
            "caixa_codigo": "10497226000000029902670151500171422294657014",
            "bb_linha": "00190.00009 79001.00000.000007 84600000001000",
            "itau_linha": "34191.79001 01043.520150 00081.846000 1 84600000001000"
        }
    
    def get_error_message(self, category: ErrorCategory, error_type: str, **kwargs) -> Dict[str, str]:
        """
        Retorna mensagem de erro formatada
        
        Args:
            category: Categoria do erro
            error_type: Tipo específico do erro
            **kwargs: Parâmetros para formatação da mensagem
            
        Returns:
            Dict: Mensagem formatada com sugestões
        """
        
        if category not in self.error_messages:
            return self._get_generic_error(error_type, **kwargs)
        
        if error_type not in self.error_messages[category]:
            return self._get_generic_error(error_type, **kwargs)
        
        error_info = self.error_messages[category][error_type]
        
        try:
            formatted_message = error_info["message"].format(**kwargs)
        except (KeyError, ValueError):
            formatted_message = error_info["message"]
        
        return {
            "message": formatted_message,
            "suggestion": error_info["suggestion"],
            "example": error_info["example"],
            "category": category.value,
            "severity": self._get_error_severity(category)
        }
    
    def get_format_help(self, input_format: str = None) -> Dict[str, Any]:
        """
        Retorna ajuda sobre formatos de boleto
        
        Args:
            input_format: Formato específico para ajuda
            
        Returns:
            Dict: Informações de ajuda
        """
        
        help_info = {
            "formats": {
                "linha_digitavel": {
                    "description": "Linha digitável com 47 dígitos",
                    "format": "AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D EEEEEEEEEEEEEE",
                    "example": self.valid_examples["caixa_linha"],
                    "tips": [
                        "Pode ser digitada com ou sem pontos e espaços",
                        "Deve ter exatamente 47 dígitos numéricos",
                        "É o formato mais comum em boletos impressos"
                    ]
                },
                "codigo_barras": {
                    "description": "Código de barras com 44 dígitos",
                    "format": "44 dígitos consecutivos",
                    "example": self.valid_examples["caixa_codigo"],
                    "tips": [
                        "Formato interno usado pelos bancos",
                        "Deve ter exatamente 44 dígitos numéricos",
                        "Pode ser lido por câmeras e scanners"
                    ]
                }
            },
            "banks": {
                "104": {"name": "Caixa Econômica Federal", "layout": "SIGCB"},
                "001": {"name": "Banco do Brasil", "layout": "FEBRABAN"},
                "341": {"name": "Itaú Unibanco", "layout": "FEBRABAN"},
                "237": {"name": "Bradesco", "layout": "FEBRABAN"},
                "033": {"name": "Santander", "layout": "FEBRABAN"}
            }
        }
        
        if input_format and input_format in help_info["formats"]:
            return help_info["formats"][input_format]
        
        return help_info
    
    def get_validation_tips(self, detected_layout: str = None) -> List[str]:
        """
        Retorna dicas de validação baseadas no layout
        
        Args:
            detected_layout: Layout detectado do boleto
            
        Returns:
            List[str]: Lista de dicas
        """
        
        general_tips = [
            "Verifique se todos os dígitos estão corretos",
            "Certifique-se de que não há espaços extras no início ou fim",
            "Confirme se o código não foi alterado manualmente",
            "Use sempre o código original do boleto"
        ]
        
        if detected_layout == "SIGCB":
            sigcb_tips = [
                "Boleto da Caixa detectado - usando validação SIGCB",
                "Certifique-se de que o convênio está ativo na Caixa",
                "Verifique se a carteira está configurada corretamente",
                "Entre em contato com seu gerente se houver problemas"
            ]
            return sigcb_tips + general_tips
        
        elif detected_layout == "FEBRABAN_PADRAO":
            febraban_tips = [
                "Usando validação FEBRABAN padrão",
                "Verifique se o banco está correto",
                "Confirme se o boleto não está vencido há muito tempo"
            ]
            return febraban_tips + general_tips
        
        return general_tips
    
    def _get_generic_error(self, error_type: str, **kwargs) -> Dict[str, str]:
        """Retorna erro genérico quando tipo específico não é encontrado"""
        
        return {
            "message": f"Erro de validação: {error_type}",
            "suggestion": "Verifique se o código de barras está correto",
            "example": "Digite novamente o código do boleto",
            "category": "generic",
            "severity": "error"
        }
    
    def _get_error_severity(self, category: ErrorCategory) -> str:
        """Determina severidade do erro baseada na categoria"""
        
        severity_map = {
            ErrorCategory.FORMAT: "error",
            ErrorCategory.DV: "error",
            ErrorCategory.BUSINESS: "warning",
            ErrorCategory.SIGCB: "warning",
            ErrorCategory.CONVERSION: "error",
            ErrorCategory.SYSTEM: "error"
        }
        
        return severity_map.get(category, "error")
    
    def format_error_for_user(self, error_message: str, category: ErrorCategory = None) -> Dict[str, Any]:
        """
        Formata erro para exibição amigável ao usuário
        
        Args:
            error_message: Mensagem de erro original
            category: Categoria do erro (opcional)
            
        Returns:
            Dict: Erro formatado para usuário
        """
        
        # Tentar detectar tipo de erro pela mensagem
        detected_info = self._detect_error_type(error_message)
        
        if detected_info:
            return detected_info
        
        # Fallback para erro genérico
        return {
            "title": "Erro de Validação",
            "message": error_message,
            "suggestion": "Verifique se o código de barras está correto e tente novamente",
            "action": "Digite o código novamente",
            "severity": "error",
            "show_examples": True
        }
    
    def _detect_error_type(self, error_message: str) -> Dict[str, Any]:
        """Detecta tipo de erro pela mensagem"""
        
        error_lower = error_message.lower()
        
        # Detectar erros comuns
        if "dígito verificador" in error_lower or "dv" in error_lower:
            return {
                "title": "Dígito Verificador Inválido",
                "message": "Um ou mais dígitos verificadores estão incorretos",
                "suggestion": "Verifique se o código foi digitado corretamente",
                "action": "Confira cada dígito do código",
                "severity": "error",
                "show_examples": False
            }
        
        elif "comprimento" in error_lower or "dígitos" in error_lower:
            return {
                "title": "Tamanho Incorreto",
                "message": "O código não tem o tamanho correto",
                "suggestion": "Código de barras: 44 dígitos | Linha digitável: 47 dígitos",
                "action": "Verifique se o código está completo",
                "severity": "error",
                "show_examples": True
            }
        
        elif "caixa" in error_lower or "104" in error_lower:
            return {
                "title": "Erro Específico da Caixa",
                "message": error_message,
                "suggestion": "Verifique configurações específicas da Caixa Econômica Federal",
                "action": "Entre em contato com seu gerente se necessário",
                "severity": "warning",
                "show_examples": False
            }
        
        return None


# Instância global para uso no sistema
error_messages = BoletoErrorMessages()


def format_validation_error(error: str, category: str = None) -> Dict[str, Any]:
    """
    Função de conveniência para formatar erros de validação
    
    Args:
        error: Mensagem de erro
        category: Categoria do erro (opcional)
        
    Returns:
        Dict: Erro formatado
    """
    
    cat = None
    if category:
        try:
            cat = ErrorCategory(category)
        except ValueError:
            pass
    
    return error_messages.format_error_for_user(error, cat)


def get_boleto_help(format_type: str = None) -> Dict[str, Any]:
    """
    Função de conveniência para obter ajuda sobre boletos
    
    Args:
        format_type: Tipo de formato para ajuda específica
        
    Returns:
        Dict: Informações de ajuda
    """
    
    return error_messages.get_format_help(format_type)