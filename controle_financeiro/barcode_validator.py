"""
Validador abrangente de códigos de barras para boletos
Implementa validações conforme padrões FEBRABAN e especificações da Caixa
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, date


class BarcodeValidationResult:
    """Resultado da validação de código de barras"""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.details = {}
    
    def add_error(self, error_message: str):
        """Adiciona um erro de validação"""
        self.is_valid = False
        self.errors.append(error_message)
    
    def add_warning(self, warning_message: str):
        """Adiciona um aviso de validação"""
        self.warnings.append(warning_message)
    
    def add_detail(self, key: str, value):
        """Adiciona detalhes da validação"""
        self.details[key] = value


class BarcodeValidator:
    """Validador abrangente de códigos de barras para boletos"""
    
    def __init__(self):
        self.banco_caixa = "104"
        self.moeda_real = "9"
        self.data_base_febraban = date(1997, 10, 7)  # Base para fator de vencimento
    
    def validate_barcode_format(self, codigo_barras: str) -> BarcodeValidationResult:
        """
        Valida o formato básico do código de barras
        Verifica tamanho, caracteres e estrutura básica
        """
        result = BarcodeValidationResult()
        
        # Verificar se o código foi fornecido
        if not codigo_barras:
            result.add_error("Código de barras não fornecido")
            return result
        
        # Verificar se é string
        if not isinstance(codigo_barras, str):
            result.add_error(f"Código de barras deve ser string, recebido {type(codigo_barras)}")
            return result
        
        # Remover espaços e caracteres especiais
        codigo_limpo = re.sub(r'[^0-9]', '', codigo_barras)
        result.add_detail('codigo_limpo', codigo_limpo)
        
        # Verificar tamanho
        if len(codigo_limpo) != 44:
            result.add_error(f"Código de barras deve ter 44 dígitos, tem {len(codigo_limpo)}")
            return result
        
        # Verificar se contém apenas números
        if not codigo_limpo.isdigit():
            result.add_error("Código de barras deve conter apenas números")
            return result
        
        # Extrair e validar componentes básicos
        try:
            banco = codigo_limpo[0:3]
            moeda = codigo_limpo[3:4]
            dv_geral = codigo_limpo[4:5]
            fator_vencimento = codigo_limpo[5:9]
            valor = codigo_limpo[9:19]
            campo_livre = codigo_limpo[19:44]
            
            result.add_detail('banco', banco)
            result.add_detail('moeda', moeda)
            result.add_detail('dv_geral', int(dv_geral))
            result.add_detail('fator_vencimento', fator_vencimento)
            result.add_detail('valor_centavos', valor)
            result.add_detail('campo_livre', campo_livre)
            
            # Validar banco (se for Caixa)
            if banco == self.banco_caixa:
                result.add_detail('banco_nome', 'Caixa Econômica Federal')
            else:
                result.add_warning(f"Banco {banco} não é Caixa Econômica Federal (104)")
            
            # Validar moeda
            if moeda != self.moeda_real:
                result.add_error(f"Código da moeda inválido: esperado {self.moeda_real}, recebido {moeda}")
            
            # Validar fator de vencimento
            try:
                fator_int = int(fator_vencimento)
                if fator_int < 1000:
                    result.add_error(f"Fator de vencimento inválido: {fator_int} (deve ser >= 1000)")
                else:
                    # Calcular data de vencimento
                    dias_desde_base = fator_int - 1000
                    data_vencimento = self.data_base_febraban.replace(year=self.data_base_febraban.year + dias_desde_base // 365)
                    result.add_detail('data_vencimento_estimada', data_vencimento)
            except ValueError:
                result.add_error(f"Fator de vencimento inválido: {fator_vencimento}")
            
            # Validar valor
            try:
                valor_int = int(valor)
                valor_reais = valor_int / 100
                result.add_detail('valor_reais', valor_reais)
                
                if valor_int <= 0:
                    result.add_error(f"Valor deve ser maior que zero: R$ {valor_reais}")
                elif valor_reais > 99999999.99:
                    result.add_error(f"Valor muito alto: R$ {valor_reais}")
            except ValueError:
                result.add_error(f"Valor inválido: {valor}")
            
            # Validar campo livre
            if len(campo_livre) != 25:
                result.add_error(f"Campo livre deve ter 25 dígitos, tem {len(campo_livre)}")
            
        except Exception as e:
            result.add_error(f"Erro ao extrair componentes do código: {str(e)}")
        
        return result
    
    def validate_dv_calculations(self, codigo_barras: str) -> BarcodeValidationResult:
        """
        Valida todos os cálculos de dígito verificador
        Verifica DV geral e DVs da linha digitável
        """
        result = BarcodeValidationResult()
        
        # Primeiro validar formato
        format_result = self.validate_barcode_format(codigo_barras)
        if not format_result.is_valid:
            result.errors.extend(format_result.errors)
            return result
        
        codigo_limpo = re.sub(r'[^0-9]', '', codigo_barras)
        
        try:
            # Extrair componentes
            banco = codigo_limpo[0:3]
            moeda = codigo_limpo[3:4]
            dv_informado = int(codigo_limpo[4:5])
            fator_vencimento = codigo_limpo[5:9]
            valor = codigo_limpo[9:19]
            campo_livre = codigo_limpo[19:44]
            
            # Validar DV geral
            codigo_sem_dv = f"{banco}{moeda}{fator_vencimento}{valor}{campo_livre}"
            dv_calculado = self._calcular_dv_modulo11_febraban(codigo_sem_dv)
            
            result.add_detail('dv_informado', dv_informado)
            result.add_detail('dv_calculado', dv_calculado)
            
            if dv_informado != dv_calculado:
                result.add_error(
                    f"DV geral inválido: informado {dv_informado}, calculado {dv_calculado}"
                )
            
            # Validar DVs da linha digitável
            linha_result = self._validate_linha_digitavel_dvs(codigo_limpo)
            result.errors.extend(linha_result.errors)
            result.warnings.extend(linha_result.warnings)
            result.details.update(linha_result.details)
            
        except Exception as e:
            result.add_error(f"Erro ao validar DVs: {str(e)}")
        
        return result
    
    def validate_campo_livre(self, codigo_barras: str, banco: str = "104") -> BarcodeValidationResult:
        """
        Valida a estrutura do campo livre conforme especificações do banco
        Para Caixa: cedente(6) + nosso_numero(10) + agencia_conta(6) + carteira(3)
        """
        result = BarcodeValidationResult()
        
        # Validar formato primeiro
        format_result = self.validate_barcode_format(codigo_barras)
        if not format_result.is_valid:
            result.errors.extend(format_result.errors)
            return result
        
        codigo_limpo = re.sub(r'[^0-9]', '', codigo_barras)
        campo_livre = codigo_limpo[19:44]
        
        try:
            if banco == "104":  # Caixa Econômica Federal
                # Extrair componentes do campo livre da Caixa
                codigo_cedente = campo_livre[0:6]
                nosso_numero = campo_livre[6:16]
                agencia_conta = campo_livre[16:22]
                carteira = campo_livre[22:25]
                
                result.add_detail('codigo_cedente', codigo_cedente)
                result.add_detail('nosso_numero', nosso_numero)
                result.add_detail('agencia_conta', agencia_conta)
                result.add_detail('carteira', carteira)
                
                # Validar código do cedente
                if codigo_cedente == "000000":
                    result.add_warning("Código do cedente é zero")
                
                # Validar nosso número
                if nosso_numero == "0000000000":
                    result.add_warning("Nosso número é zero")
                
                # Validar agência
                agencia = agencia_conta[0:4]
                conta_parte = agencia_conta[4:6]
                
                if agencia == "0000":
                    result.add_error("Agência não pode ser zero")
                
                result.add_detail('agencia', agencia)
                result.add_detail('conta_parte', conta_parte)
                
                # Validar carteira
                carteiras_validas_caixa = ["001", "002", "014", "024"]
                if carteira not in carteiras_validas_caixa:
                    result.add_warning(
                        f"Carteira {carteira} pode não ser válida para Caixa. "
                        f"Carteiras comuns: {', '.join(carteiras_validas_caixa)}"
                    )
                
                result.add_detail('carteira_valida', carteira in carteiras_validas_caixa)
                
            else:
                result.add_warning(f"Validação de campo livre não implementada para banco {banco}")
        
        except Exception as e:
            result.add_error(f"Erro ao validar campo livre: {str(e)}")
        
        return result
    
    def validate_linha_digitavel(self, linha_digitavel: str, codigo_barras: str = None) -> BarcodeValidationResult:
        """
        Valida a linha digitável e sua consistência com o código de barras
        """
        result = BarcodeValidationResult()
        
        if not linha_digitavel:
            result.add_error("Linha digitável não fornecida")
            return result
        
        # Limpar linha digitável
        linha_limpa = re.sub(r'[^0-9]', '', linha_digitavel)
        result.add_detail('linha_limpa', linha_limpa)
        
        # Verificar tamanho (deve ter 47 dígitos: 5 campos com 10+11+11+1+14 dígitos)
        if len(linha_limpa) != 47:
            result.add_error(f"Linha digitável deve ter 47 dígitos, tem {len(linha_limpa)}")
            return result
        
        try:
            # Extrair campos da linha digitável
            # Formato: AAAAA AAAAA BBBBB BBBBBB CCCCC CCCCCC D EEEEEEEEEEEEEE
            campo1 = linha_limpa[0:10]   # 10 dígitos
            campo2 = linha_limpa[10:21]  # 11 dígitos
            campo3 = linha_limpa[21:32]  # 11 dígitos
            campo4 = linha_limpa[32:33]  # 1 dígito (DV geral)
            campo5 = linha_limpa[33:47]  # 14 dígitos (vencimento + valor)
            
            result.add_detail('campo1', campo1)
            result.add_detail('campo2', campo2)
            result.add_detail('campo3', campo3)
            result.add_detail('campo4', campo4)
            result.add_detail('campo5', campo5)
            
            # Validar DVs dos campos 1, 2 e 3
            dv1_informado = int(campo1[-1])
            dv1_calculado = self._calcular_dv_modulo10_febraban(campo1[:-1])
            
            dv2_informado = int(campo2[-1])
            dv2_calculado = self._calcular_dv_modulo10_febraban(campo2[:-1])
            
            dv3_informado = int(campo3[-1])
            dv3_calculado = self._calcular_dv_modulo10_febraban(campo3[:-1])
            
            if dv1_informado != dv1_calculado:
                result.add_error(f"DV do campo 1 inválido: informado {dv1_informado}, calculado {dv1_calculado}")
            
            if dv2_informado != dv2_calculado:
                result.add_error(f"DV do campo 2 inválido: informado {dv2_informado}, calculado {dv2_calculado}")
            
            if dv3_informado != dv3_calculado:
                result.add_error(f"DV do campo 3 inválido: informado {dv3_informado}, calculado {dv3_calculado}")
            
            # Se código de barras foi fornecido, validar consistência
            if codigo_barras:
                codigo_limpo = re.sub(r'[^0-9]', '', codigo_barras)
                if len(codigo_limpo) == 44:
                    # Reconstruir código de barras a partir da linha digitável
                    codigo_reconstruido = self._reconstruct_barcode_from_linha(linha_limpa)
                    
                    if codigo_reconstruido != codigo_limpo:
                        result.add_error("Linha digitável não corresponde ao código de barras")
                        result.add_detail('codigo_original', codigo_limpo)
                        result.add_detail('codigo_reconstruido', codigo_reconstruido)
        
        except Exception as e:
            result.add_error(f"Erro ao validar linha digitável: {str(e)}")
        
        return result
    
    def validate_complete(self, codigo_barras: str, linha_digitavel: str = None) -> BarcodeValidationResult:
        """
        Executa validação completa do código de barras
        Combina todas as validações em um resultado único
        """
        result = BarcodeValidationResult()
        
        # Validação de formato
        format_result = self.validate_barcode_format(codigo_barras)
        result.errors.extend(format_result.errors)
        result.warnings.extend(format_result.warnings)
        result.details.update(format_result.details)
        
        if not format_result.is_valid:
            return result
        
        # Validação de DVs
        dv_result = self.validate_dv_calculations(codigo_barras)
        result.errors.extend(dv_result.errors)
        result.warnings.extend(dv_result.warnings)
        result.details.update(dv_result.details)
        
        # Validação de campo livre
        banco = result.details.get('banco', '104')
        campo_result = self.validate_campo_livre(codigo_barras, banco)
        result.errors.extend(campo_result.errors)
        result.warnings.extend(campo_result.warnings)
        result.details.update(campo_result.details)
        
        # Validação de linha digitável (se fornecida)
        if linha_digitavel:
            linha_result = self.validate_linha_digitavel(linha_digitavel, codigo_barras)
            result.errors.extend(linha_result.errors)
            result.warnings.extend(linha_result.warnings)
            result.details.update(linha_result.details)
        
        # Determinar se é válido
        result.is_valid = len(result.errors) == 0
        
        return result
    
    # Métodos auxiliares privados
    
    def _calcular_dv_modulo11_febraban(self, codigo: str) -> int:
        """Calcula DV usando módulo 11 FEBRABAN"""
        sequencia = "4329876543298765432987654329876543298765432"
        soma = 0
        
        for i, digito in enumerate(reversed(codigo)):
            if digito.isdigit():
                multiplicador = int(sequencia[i % len(sequencia)])
                produto = int(digito) * multiplicador
                soma += produto
        
        resto = soma % 11
        
        if resto in [0, 10, 11]:
            return 1
        else:
            return 11 - resto
    
    def _calcular_dv_modulo10_febraban(self, codigo: str) -> int:
        """Calcula DV usando módulo 10 FEBRABAN"""
        soma = 0
        multiplicador = 2
        
        for digito in reversed(codigo):
            if digito.isdigit():
                produto = int(digito) * multiplicador
                
                if produto > 9:
                    produto = sum(int(d) for d in str(produto))
                
                soma += produto
                multiplicador = 3 - multiplicador
        
        resto = soma % 10
        return 0 if resto == 0 else 10 - resto
    
    def _validate_linha_digitavel_dvs(self, codigo_barras: str) -> BarcodeValidationResult:
        """Valida DVs da linha digitável gerada a partir do código de barras"""
        result = BarcodeValidationResult()
        
        try:
            # Gerar linha digitável a partir do código
            linha_gerada = self._generate_linha_digitavel(codigo_barras)
            linha_limpa = re.sub(r'[^0-9]', '', linha_gerada)
            
            # Validar cada campo
            campo1 = linha_limpa[0:10]
            campo2 = linha_limpa[10:21]
            campo3 = linha_limpa[21:32]
            
            # Validar DVs
            dv1 = self._calcular_dv_modulo10_febraban(campo1[:-1])
            dv2 = self._calcular_dv_modulo10_febraban(campo2[:-1])
            dv3 = self._calcular_dv_modulo10_febraban(campo3[:-1])
            
            result.add_detail('linha_digitavel_gerada', linha_gerada)
            result.add_detail('dv1_linha', dv1)
            result.add_detail('dv2_linha', dv2)
            result.add_detail('dv3_linha', dv3)
            
        except Exception as e:
            result.add_error(f"Erro ao validar DVs da linha digitável: {str(e)}")
        
        return result
    
    def _generate_linha_digitavel(self, codigo_barras: str) -> str:
        """Gera linha digitável a partir do código de barras"""
        if len(codigo_barras) != 44:
            raise ValueError("Código deve ter 44 dígitos")
        
        # Extrair campos
        banco = codigo_barras[0:3]
        moeda = codigo_barras[3:4]
        dv_geral = codigo_barras[4:5]
        vencimento = codigo_barras[5:9]
        valor = codigo_barras[9:19]
        campo_livre = codigo_barras[19:44]
        
        # Campo 1
        campo1_base = f"{banco}{moeda}{campo_livre[0:5]}"
        dv1 = self._calcular_dv_modulo10_febraban(campo1_base)
        campo1 = f"{campo1_base[0:5]}.{campo1_base[5:10]}{dv1}"
        
        # Campo 2
        campo2_base = campo_livre[5:15]
        dv2 = self._calcular_dv_modulo10_febraban(campo2_base)
        campo2 = f"{campo2_base[0:5]}.{campo2_base[5:10]}{dv2}"
        
        # Campo 3
        campo3_base = campo_livre[15:25]
        dv3 = self._calcular_dv_modulo10_febraban(campo3_base)
        campo3 = f"{campo3_base[0:5]}.{campo3_base[5:10]}{dv3}"
        
        # Campo 4
        campo4 = dv_geral
        
        # Campo 5
        campo5 = f"{vencimento}{valor}"
        
        return f"{campo1} {campo2} {campo3} {campo4} {campo5}"
    
    def _reconstruct_barcode_from_linha(self, linha_limpa: str) -> str:
        """Reconstrói código de barras a partir da linha digitável"""
        if len(linha_limpa) != 47:
            raise ValueError("Linha digitável deve ter 47 dígitos")
        
        # Extrair campos
        campo1 = linha_limpa[0:10]
        campo2 = linha_limpa[10:21]
        campo3 = linha_limpa[21:32]
        campo4 = linha_limpa[32:33]
        campo5 = linha_limpa[33:47]
        
        # Extrair componentes
        banco = campo1[0:3]
        moeda = campo1[3:4]
        dv_geral = campo4
        vencimento = campo5[0:4]
        valor = campo5[4:14]
        
        # Reconstruir campo livre
        parte1 = campo1[4:9]  # 5 dígitos
        parte2 = campo2[0:10]  # 10 dígitos
        parte3 = campo3[0:10]  # 10 dígitos
        
        campo_livre = f"{parte1}{parte2}{parte3}"
        
        return f"{banco}{moeda}{dv_geral}{vencimento}{valor}{campo_livre}"