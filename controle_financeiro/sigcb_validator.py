"""
Validador específico para layout CAIXA SIGCB
Implementa validação conforme especificações da Caixa Econômica Federal
"""

import re
from datetime import datetime, date
from typing import Dict, Any, Optional
try:
    from .boleto_validator_base import (
        BoletoValidatorBase, 
        ValidationResult, 
        BoletoComponents,
        DVCalculatorMixin,
        FormatNormalizerMixin
    )
except ImportError:
    from boleto_validator_base import (
        BoletoValidatorBase, 
        ValidationResult, 
        BoletoComponents,
        DVCalculatorMixin,
        FormatNormalizerMixin
    )


class SIGCBValidator(BoletoValidatorBase, DVCalculatorMixin, FormatNormalizerMixin):
    """Validador específico para layout CAIXA SIGCB"""
    
    def __init__(self):
        super().__init__("SIGCB_Validator")
        self.supported_banks = ["104"]  # Caixa Econômica Federal
        self.supported_layouts = ["SIGCB"]
        
        # Configurações específicas da Caixa
        self.banco_caixa = "104"
        self.moeda_real = "9"
        self.carteiras_validas = ["001", "002", "014", "024"]
        self.data_base_febraban = date(1997, 10, 7)
    
    def validate_format(self, codigo_input: str) -> ValidationResult:
        """
        Valida formato específico do SIGCB
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            ValidationResult: Resultado da validação de formato
        """
        
        result = ValidationResult(validation_type="SIGCB_Format")
        
        # Normalizar entrada
        codigo_limpo = self.normalize_input(codigo_input)
        
        if not codigo_limpo:
            result.add_error("Código não fornecido")
            return result
        
        # Detectar formato
        input_format = self.detect_input_format(codigo_limpo)
        
        if not input_format:
            result.add_error(
                f"Formato não reconhecido: {len(codigo_limpo)} dígitos. "
                f"SIGCB aceita: 44 (código de barras) ou 47 (linha digitável)"
            )
            return result
        
        result.add_detail("input_format", input_format)
        result.add_detail("codigo_limpo", codigo_limpo)
        result.add_detail("length", len(codigo_limpo))
        
        # Validar se é da Caixa
        banco = self._extract_bank_code(codigo_limpo, input_format)
        
        if banco != self.banco_caixa:
            result.add_error(
                f"Código não é da Caixa Econômica Federal. "
                f"Banco detectado: {banco}, esperado: {self.banco_caixa}"
            )
            return result
        
        result.add_detail("banco", banco)
        result.add_detail("banco_nome", "Caixa Econômica Federal")
        
        return result
    
    def validate_dv(self, codigo_input: str) -> ValidationResult:
        """
        Valida dígitos verificadores específicos do SIGCB
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            ValidationResult: Resultado da validação de DV
        """
        
        result = ValidationResult(validation_type="SIGCB_DV")
        
        # Validar formato primeiro
        format_result = self.validate_format(codigo_input)
        if not format_result.is_valid:
            result.merge(format_result)
            return result
        
        codigo_limpo = format_result.details["codigo_limpo"]
        input_format = format_result.details["input_format"]
        
        try:
            if input_format == "codigo_barras":
                self._validate_codigo_barras_dv(codigo_limpo, result)
            elif input_format == "linha_digitavel":
                self._validate_linha_digitavel_dv(codigo_limpo, result)
                
        except Exception as e:
            result.add_error(f"Erro na validação de DV: {str(e)}")
        
        return result
    
    def validate_business_rules(self, codigo_input: str) -> ValidationResult:
        """
        Valida regras de negócio específicas do SIGCB
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            ValidationResult: Resultado da validação de regras de negócio
        """
        
        result = ValidationResult(validation_type="SIGCB_Business")
        
        try:
            # Extrair componentes
            components = self.extract_components(codigo_input)
            
            # Validar moeda
            if components.moeda != self.moeda_real:
                result.add_error(
                    f"Código da moeda inválido: {components.moeda}, esperado: {self.moeda_real}"
                )
            
            # Validar fator de vencimento
            self._validate_fator_vencimento(components.fator_vencimento, result)
            
            # Validar valor
            self._validate_valor(components.valor, result)
            
            # Validar campo livre específico da Caixa
            self._validate_campo_livre_sigcb(components, result)
            
        except Exception as e:
            result.add_error(f"Erro na validação de regras de negócio: {str(e)}")
        
        return result
    
    def extract_components(self, codigo_input: str) -> BoletoComponents:
        """
        Extrai componentes específicos do SIGCB
        
        Args:
            codigo_input: Código de barras ou linha digitável
            
        Returns:
            BoletoComponents: Componentes extraídos
        """
        
        codigo_limpo = self.normalize_input(codigo_input)
        input_format = self.detect_input_format(codigo_limpo)
        
        components = BoletoComponents()
        components.layout_type = "SIGCB"
        components.input_format = input_format
        
        if input_format == "codigo_barras":
            self._extract_from_codigo_barras(codigo_limpo, components)
        elif input_format == "linha_digitavel":
            self._extract_from_linha_digitavel(codigo_limpo, components)
        
        return components
    
    def _extract_bank_code(self, codigo_limpo: str, input_format: str) -> str:
        """Extrai código do banco"""
        
        if input_format in ["codigo_barras", "linha_digitavel"]:
            return codigo_limpo[0:3]
        return ""
    
    def _validate_codigo_barras_dv(self, codigo_barras: str, result: ValidationResult):
        """Valida DV do código de barras"""
        
        if len(codigo_barras) != 44:
            result.add_error(f"Código de barras deve ter 44 dígitos, tem {len(codigo_barras)}")
            return
        
        # Extrair componentes
        banco = codigo_barras[0:3]
        moeda = codigo_barras[3:4]
        dv_informado = int(codigo_barras[4:5])
        fator_vencimento = codigo_barras[5:9]
        valor = codigo_barras[9:19]
        campo_livre = codigo_barras[19:44]
        
        # Calcular DV geral
        codigo_sem_dv = f"{banco}{moeda}{fator_vencimento}{valor}{campo_livre}"
        dv_calculado = self.calculate_dv_modulo11_febraban(codigo_sem_dv)
        
        result.add_detail("dv_informado", dv_informado)
        result.add_detail("dv_calculado", dv_calculado)
        
        if dv_informado != dv_calculado:
            result.add_error(
                f"DV geral inválido: informado {dv_informado}, calculado {dv_calculado}"
            )
    
    def _validate_linha_digitavel_dv(self, linha_digitavel: str, result: ValidationResult):
        """Valida DVs da linha digitável"""
        
        if len(linha_digitavel) != 47:
            result.add_error(f"Linha digitável deve ter 47 dígitos, tem {len(linha_digitavel)}")
            return
        
        # Extrair campos
        campo1 = linha_digitavel[0:10]
        campo2 = linha_digitavel[10:21]
        campo3 = linha_digitavel[21:32]
        campo4 = linha_digitavel[32:33]
        campo5 = linha_digitavel[33:47]
        
        # Validar DV do campo 1
        dv1_informado = int(campo1[-1])
        dv1_calculado = self.calculate_dv_modulo10_febraban(campo1[:-1])
        
        if dv1_informado != dv1_calculado:
            result.add_error(
                f"DV do campo 1 inválido: informado {dv1_informado}, calculado {dv1_calculado}"
            )
        
        # Validar DV do campo 2
        dv2_informado = int(campo2[-1])
        dv2_calculado = self.calculate_dv_modulo10_febraban(campo2[:-1])
        
        if dv2_informado != dv2_calculado:
            result.add_error(
                f"DV do campo 2 inválido: informado {dv2_informado}, calculado {dv2_calculado}"
            )
        
        # Validar DV do campo 3
        dv3_informado = int(campo3[-1])
        dv3_calculado = self.calculate_dv_modulo10_febraban(campo3[:-1])
        
        if dv3_informado != dv3_calculado:
            result.add_error(
                f"DV do campo 3 inválido: informado {dv3_informado}, calculado {dv3_calculado}"
            )
        
        # Adicionar detalhes dos DVs
        result.add_detail("dv_campo1", {"informado": dv1_informado, "calculado": dv1_calculado})
        result.add_detail("dv_campo2", {"informado": dv2_informado, "calculado": dv2_calculado})
        result.add_detail("dv_campo3", {"informado": dv3_informado, "calculado": dv3_calculado})
        
        # Validar consistência com código de barras
        try:
            codigo_reconstruido = self._reconstruct_codigo_from_linha(linha_digitavel)
            self._validate_codigo_barras_dv(codigo_reconstruido, result)
        except Exception as e:
            result.add_warning(f"Não foi possível validar consistência: {str(e)}")
    
    def _validate_fator_vencimento(self, fator_vencimento: str, result: ValidationResult):
        """Valida fator de vencimento"""
        
        try:
            fator_int = int(fator_vencimento)
            
            if fator_int < 1000:
                result.add_error(f"Fator de vencimento inválido: {fator_int} (deve ser >= 1000)")
                return
            
            # Calcular data de vencimento estimada
            dias_desde_base = fator_int - 1000
            
            # Tratamento do ciclo FEBRABAN (reinicia a cada ~24 anos)
            if fator_int > 9999:
                result.add_warning("Fator de vencimento no segundo ciclo FEBRABAN")
            
            # Estimar data (aproximada)
            anos_aproximados = dias_desde_base // 365
            data_estimada = self.data_base_febraban.replace(
                year=self.data_base_febraban.year + anos_aproximados
            )
            
            result.add_detail("fator_vencimento", fator_int)
            result.add_detail("data_vencimento_estimada", data_estimada.isoformat())
            
        except ValueError:
            result.add_error(f"Fator de vencimento inválido: {fator_vencimento}")
    
    def _validate_valor(self, valor: str, result: ValidationResult):
        """Valida valor do boleto"""
        
        try:
            valor_int = int(valor)
            valor_reais = valor_int / 100
            
            result.add_detail("valor_centavos", valor_int)
            result.add_detail("valor_reais", valor_reais)
            
            if valor_int <= 0:
                result.add_error(f"Valor deve ser maior que zero: R$ {valor_reais:.2f}")
            elif valor_reais > 99999999.99:
                result.add_error(f"Valor muito alto: R$ {valor_reais:.2f}")
            
        except ValueError:
            result.add_error(f"Valor inválido: {valor}")
    
    def _validate_campo_livre_sigcb(self, components: BoletoComponents, result: ValidationResult):
        """Valida campo livre específico do SIGCB"""
        
        if len(components.campo_livre) != 25:
            result.add_error(f"Campo livre deve ter 25 dígitos, tem {len(components.campo_livre)}")
            return
        
        # Extrair componentes do campo livre SIGCB
        # Formato: CCCCCC NNNNNNNNNN DDDDDD CCC
        # C (1-6):   Código do cedente (6 dígitos)
        # N (7-16):  Nosso número (10 dígitos)
        # D (17-22): Agência (4) + Conta (2 primeiros dígitos)
        # C (23-25): Carteira (3 dígitos)
        
        codigo_cedente = components.campo_livre[0:6]
        nosso_numero = components.campo_livre[6:16]
        agencia_conta = components.campo_livre[16:22]
        carteira = components.campo_livre[22:25]
        
        # Atualizar componentes
        components.codigo_cedente = codigo_cedente
        components.nosso_numero = nosso_numero
        components.agencia = agencia_conta[0:4]
        components.conta = agencia_conta[4:6]
        components.carteira = carteira
        
        # Validações específicas
        if codigo_cedente == "000000":
            result.add_warning("Código do cedente é zero - verificar configuração")
        
        if nosso_numero == "0000000000":
            result.add_error("Nosso número não pode ser zero")
        
        if components.agencia == "0000":
            result.add_error("Agência não pode ser zero")
        
        # Validar carteira
        if carteira not in self.carteiras_validas:
            result.add_warning(
                f"Carteira {carteira} pode não ser padrão da Caixa. "
                f"Carteiras válidas: {', '.join(self.carteiras_validas)}"
            )
        
        # Adicionar detalhes
        result.add_detail("sigcb_codigo_cedente", codigo_cedente)
        result.add_detail("sigcb_nosso_numero", nosso_numero)
        result.add_detail("sigcb_agencia", components.agencia)
        result.add_detail("sigcb_conta_parte", components.conta)
        result.add_detail("sigcb_carteira", carteira)
        result.add_detail("sigcb_carteira_valida", carteira in self.carteiras_validas)
    
    def _extract_from_codigo_barras(self, codigo_barras: str, components: BoletoComponents):
        """Extrai componentes do código de barras"""
        
        components.banco = codigo_barras[0:3]
        components.moeda = codigo_barras[3:4]
        components.dv_geral = codigo_barras[4:5]
        components.fator_vencimento = codigo_barras[5:9]
        components.valor = codigo_barras[9:19]
        components.campo_livre = codigo_barras[19:44]
    
    def _extract_from_linha_digitavel(self, linha_digitavel: str, components: BoletoComponents):
        """Extrai componentes da linha digitável"""
        
        # Extrair campos
        components.campo1 = linha_digitavel[0:10]
        components.campo2 = linha_digitavel[10:21]
        components.campo3 = linha_digitavel[21:32]
        components.campo4 = linha_digitavel[32:33]
        components.campo5 = linha_digitavel[33:47]
        
        # Reconstruir código de barras para extrair outros componentes
        codigo_barras = self._reconstruct_codigo_from_linha(linha_digitavel)
        self._extract_from_codigo_barras(codigo_barras, components)
    
    def _reconstruct_codigo_from_linha(self, linha_digitavel: str) -> str:
        """Reconstrói código de barras a partir da linha digitável"""
        
        if len(linha_digitavel) != 47:
            raise ValueError("Linha digitável deve ter 47 dígitos")
        
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
    
    def convert_linha_to_codigo(self, linha_digitavel: str) -> str:
        """
        Converte linha digitável para código de barras
        
        Args:
            linha_digitavel: Linha digitável SIGCB
            
        Returns:
            str: Código de barras correspondente
        """
        
        # Validar entrada
        codigo_limpo = self.normalize_input(linha_digitavel)
        
        if len(codigo_limpo) != 47:
            raise ValueError(f"Linha digitável deve ter 47 dígitos, tem {len(codigo_limpo)}")
        
        # Validar se é SIGCB
        if codigo_limpo[0:3] != self.banco_caixa:
            raise ValueError(f"Linha digitável não é da Caixa (banco {codigo_limpo[0:3]})")
        
        return self._reconstruct_codigo_from_linha(codigo_limpo)
    
    def convert_codigo_to_linha(self, codigo_barras: str) -> str:
        """
        Converte código de barras para linha digitável
        
        Args:
            codigo_barras: Código de barras SIGCB
            
        Returns:
            str: Linha digitável correspondente
        """
        
        # Validar entrada
        codigo_limpo = self.normalize_input(codigo_barras)
        
        if len(codigo_limpo) != 44:
            raise ValueError(f"Código de barras deve ter 44 dígitos, tem {len(codigo_limpo)}")
        
        # Validar se é SIGCB
        if codigo_limpo[0:3] != self.banco_caixa:
            raise ValueError(f"Código de barras não é da Caixa (banco {codigo_limpo[0:3]})")
        
        # Extrair componentes
        banco = codigo_limpo[0:3]
        moeda = codigo_limpo[3:4]
        dv_geral = codigo_limpo[4:5]
        vencimento = codigo_limpo[5:9]
        valor = codigo_limpo[9:19]
        campo_livre = codigo_limpo[19:44]
        
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
        
        return f"{campo1} {campo2} {campo3} {campo4} {campo5}"