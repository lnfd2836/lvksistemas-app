"""
Serviço específico para geração de boletos da Caixa Econômica Federal
Segue as especificações técnicas da CEF para boletos registrados
"""

from datetime import datetime, timedelta
from django.utils import timezone
import re
from .barcode_validator import BarcodeValidator, BarcodeValidationResult


class BoletoCaixaService:
    """Serviço para geração de boletos válidos da Caixa Econômica Federal"""
    
    def __init__(self):
        self.codigo_banco = "104"  # Código da Caixa Econômica Federal
        self.moeda = "9"  # Real
        self.validator = BarcodeValidator()  # Validador de códigos de barras
        
    def gerar_boleto_caixa(self, controle_financeiro, configuracao, dias_vencimento=30):
        """
        Gera boleto válido da Caixa Econômica Federal
        
        Args:
            controle_financeiro: Instância do ControleFinanceiro
            configuracao: Instância do ConfiguracaoBoleto
            dias_vencimento: Dias para vencimento (padrão 30)
            
        Returns:
            dict: Dados do boleto gerado
        """
        
        # Validar configuração da Caixa
        self._validar_configuracao_caixa(configuracao)
        
        # Gerar nosso número (sequencial da Caixa)
        nosso_numero = self._gerar_nosso_numero_caixa(configuracao)
        
        # Calcular data de vencimento
        data_vencimento = timezone.now() + timedelta(days=dias_vencimento)
        
        # Calcular fator de vencimento
        fator_vencimento = self._calcular_fator_vencimento(data_vencimento)
        
        # Gerar código de barras
        codigo_barras = self._gerar_codigo_barras_caixa(
            configuracao, 
            nosso_numero, 
            controle_financeiro.valor_mensal,
            fator_vencimento
        )
        
        # Gerar linha digitável
        linha_digitavel = self._gerar_linha_digitavel_caixa(codigo_barras)
        
        # Validação completa do boleto gerado
        validation_result = self._validar_boleto_completo(codigo_barras, linha_digitavel)
        
        # Se a validação falhou, lançar erro com detalhes
        if not validation_result.is_valid:
            error_details = "; ".join(validation_result.errors)
            raise ValueError(f"Boleto gerado é inválido: {error_details}")
        
        # Preparar resultado com informações de validação
        resultado = {
            'numero_boleto': nosso_numero,
            'codigo_barras': codigo_barras,
            'linha_digitavel': linha_digitavel,
            'data_vencimento': data_vencimento,
            'valor': controle_financeiro.valor_mensal,
            'fator_vencimento': fator_vencimento,
            'validation_result': validation_result,
            'is_valid': validation_result.is_valid,
            'validation_warnings': validation_result.warnings
        }
        
        return resultado
    
    def _validar_configuracao_caixa(self, configuracao):
        """Valida se a configuração está adequada para a Caixa"""
        
        if configuracao.codigo_banco != "104":
            raise ValueError("Código do banco deve ser 104 para Caixa Econômica Federal")
        
        if not configuracao.agencia or len(configuracao.agencia) != 4:
            raise ValueError("Agência deve ter exatamente 4 dígitos")
        
        if not configuracao.conta:
            raise ValueError("Número da conta é obrigatório")
        
        if not configuracao.codigo_cedente:
            raise ValueError("Código do cedente é obrigatório para boletos da Caixa")
        
        # Validar carteira (Caixa usa carteiras específicas)
        carteiras_validas = ['1', '2', '14', '24']
        if configuracao.carteira not in carteiras_validas:
            raise ValueError(f"Carteira deve ser uma das seguintes: {', '.join(carteiras_validas)}")
    
    def _gerar_nosso_numero_caixa(self, configuracao):
        """
        Gera nosso número para a Caixa
        Formato: NNNNNNNNNN (10 dígitos) - APENAS NÚMEROS
        Para a Caixa, o nosso número é sequencial sem DV no campo livre
        """
        
        # Gerar sequencial baseado em timestamp para garantir unicidade
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        microseconds = str(timezone.now().microsecond).zfill(6)[:4]  # 4 dígitos dos microsegundos
        
        # Combinar timestamp + microsegundos para criar sequencial único
        sequencial_completo = f"{timestamp}{microseconds}"
        
        # Pegar os últimos 10 dígitos para formar o nosso número
        nosso_numero = sequencial_completo[-10:].zfill(10)
        
        # Garantir que seja apenas números
        nosso_numero = re.sub(r'[^0-9]', '0', nosso_numero)
        
        return nosso_numero
    
    def _calcular_dv_nosso_numero_caixa(self, nosso_numero):
        """
        Calcula dígito verificador do nosso número da Caixa (Módulo 11)
        Para a Caixa, o DV do nosso número segue regras específicas
        """
        
        # Sequência de multiplicação para módulo 11
        sequencia = "4329876543298765432987654329876543298765"
        soma = 0
        
        for i, digito in enumerate(reversed(nosso_numero)):
            if digito.isdigit():
                multiplicador = int(sequencia[i % len(sequencia)])
                produto = int(digito) * multiplicador
                soma += produto
        
        resto = soma % 11
        
        # Regras específicas da Caixa para DV do nosso número:
        # Se resto = 0 ou 1, DV = 0
        # Se resto = 10, DV = 0 (diferente do DV geral)
        # Caso contrário, DV = 11 - resto
        if resto in [0, 1, 10]:
            return 0
        else:
            return 11 - resto
    
    def _calcular_fator_vencimento(self, data_vencimento):
        """
        Calcula fator de vencimento conforme padrão FEBRABAN
        Base: 07/10/1997 = fator 1000
        """
        
        data_base = datetime(1997, 10, 7).date()
        data_venc = data_vencimento.date() if hasattr(data_vencimento, 'date') else data_vencimento
        
        diferenca = (data_venc - data_base).days
        fator = 1000 + diferenca
        
        # Fator deve ter 4 dígitos
        return str(fator).zfill(4)
    
    def _gerar_codigo_barras_caixa(self, configuracao, nosso_numero, valor, fator_vencimento):
        """
        Gera código de barras da Caixa Econômica Federal
        Posições: AAABCCCCCDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
        A = Código do banco (104)
        B = Código da moeda (9)
        C = DV geral
        D = Fator de vencimento (4) + Valor (10) + Campo livre (25)
        """
        
        # Valor em centavos (10 dígitos)
        valor_centavos = f"{int(valor * 100):010d}"
        
        # Campo livre da Caixa (25 posições) - Formato específico da CEF
        # Posições 20-44 do código de barras (25 dígitos)
        # Formato: CCCCCC NNNNNNNNNN DDDDDD CCC
        # C (1-6):   Código do cedente/beneficiário (6 dígitos)
        # N (7-16):  Nosso número sem DV (10 dígitos)
        # D (17-22): Agência (4 dígitos) + Conta (2 primeiros dígitos)
        # C (23-25): Carteira (3 dígitos)
        
        # Código do cedente (6 dígitos) - Primeiro truncar, depois preencher
        cedente_limpo = re.sub(r'[^0-9]', '', str(configuracao.codigo_cedente or ''))[:6]
        codigo_cedente = cedente_limpo.zfill(6)
        
        # Nosso número sem DV (10 dígitos) - Pegar os últimos 10 dígitos
        nosso_numero_completo = re.sub(r'[^0-9]', '', str(nosso_numero))
        nosso_numero_limpo = nosso_numero_completo[-10:].zfill(10)
        
        # Agência (4 dígitos) + primeiros 2 dígitos da conta
        agencia_completa = re.sub(r'[^0-9]', '', str(configuracao.agencia))[:4]
        agencia_limpa = agencia_completa.zfill(4)
        
        conta_completa = re.sub(r'[^0-9]', '', str(configuracao.conta))[:2]  # Primeiros 2 dígitos
        conta_limpa = conta_completa.zfill(2)
        
        agencia_conta_campo = f"{agencia_limpa}{conta_limpa}"
        
        # Carteira (3 dígitos) - Primeiro limpar, depois truncar, depois preencher
        carteira_original = str(configuracao.carteira)
        carteira_sem_letras = re.sub(r'[^0-9]', '', carteira_original)
        carteira_limpa = carteira_sem_letras[:3]  # Máximo 3 dígitos
        carteira_campo = carteira_limpa.zfill(3)  # Preencher com zeros à esquerda
        
        # Debug temporário - remover após correção
        if len(carteira_campo) != 3:
            raise ValueError(
                f"ERRO CARTEIRA DEBUG: original='{carteira_original}', "
                f"sem_letras='{carteira_sem_letras}', limpa='{carteira_limpa}', "
                f"final='{carteira_campo}' ({len(carteira_campo)} dígitos)"
            )
        
        # Validar tamanhos dos componentes antes de montar
        if len(codigo_cedente) != 6:
            raise ValueError(f"Código do cedente deve ter 6 dígitos: {codigo_cedente} ({len(codigo_cedente)})")
        if len(nosso_numero_limpo) != 10:
            raise ValueError(f"Nosso número deve ter 10 dígitos: {nosso_numero_limpo} ({len(nosso_numero_limpo)})")
        if len(agencia_conta_campo) != 6:
            raise ValueError(f"Agência+conta deve ter 6 dígitos: {agencia_conta_campo} ({len(agencia_conta_campo)})")
        if len(carteira_campo) != 3:
            raise ValueError(f"Carteira deve ter 3 dígitos: {carteira_campo} ({len(carteira_campo)})")
        
        # Montar campo livre: cedente(6) + nosso_numero(10) + agencia_conta(6) + carteira(3) = 25 dígitos
        campo_livre = f"{codigo_cedente}{nosso_numero_limpo}{agencia_conta_campo}{carteira_campo}"
        
        # Validar campo livre antes de continuar
        if len(campo_livre) != 25:
            raise ValueError(f"Campo livre deve ter exatamente 25 dígitos, mas tem {len(campo_livre)}: {campo_livre}")
        
        # Montar código sem DV para cálculo do DV geral
        # Formato: banco(3) + moeda(1) + vencimento(4) + valor(10) + campo_livre(25) = 43 dígitos
        codigo_sem_dv = f"{self.codigo_banco}{self.moeda}{fator_vencimento}{valor_centavos}{campo_livre}"
        
        # Validar código sem DV
        if len(codigo_sem_dv) != 43:
            raise ValueError(f"Código sem DV deve ter 43 dígitos, mas tem {len(codigo_sem_dv)}: {codigo_sem_dv}")
        
        # Calcular DV geral usando módulo 11 FEBRABAN
        dv_geral = self._calcular_dv_codigo_barras(codigo_sem_dv)
        
        # Montar código de barras completo
        # Formato: banco(3) + moeda(1) + dv(1) + vencimento(4) + valor(10) + campo_livre(25) = 44 dígitos
        codigo_barras = f"{self.codigo_banco}{self.moeda}{dv_geral}{fator_vencimento}{valor_centavos}{campo_livre}"
        
        # Validação final rigorosa
        if len(codigo_barras) != 44:
            raise ValueError(f"Código de barras deve ter exatamente 44 dígitos, mas tem {len(codigo_barras)}: {codigo_barras}")
        
        if not codigo_barras.isdigit():
            raise ValueError(f"Código de barras deve conter apenas dígitos: {codigo_barras}")
        
        # Validar o código de barras gerado
        self._validar_codigo_barras_gerado(codigo_barras)
        
        return codigo_barras
    
    def _validar_codigo_barras_gerado(self, codigo_barras):
        """
        Valida se o código de barras gerado está correto
        Verifica formato, DV e estrutura
        """
        
        if len(codigo_barras) != 44:
            raise ValueError(f"Código de barras inválido: deve ter 44 dígitos, tem {len(codigo_barras)}")
        
        if not codigo_barras.isdigit():
            raise ValueError(f"Código de barras inválido: deve conter apenas números")
        
        # Extrair componentes para validação
        banco = codigo_barras[0:3]
        moeda = codigo_barras[3:4]
        dv_informado = int(codigo_barras[4:5])
        vencimento = codigo_barras[5:9]
        valor = codigo_barras[9:19]
        campo_livre = codigo_barras[19:44]
        
        # Validar banco
        if banco != "104":
            raise ValueError(f"Código do banco inválido: esperado 104, recebido {banco}")
        
        # Validar moeda
        if moeda != "9":
            raise ValueError(f"Código da moeda inválido: esperado 9, recebido {moeda}")
        
        # Validar campo livre
        if len(campo_livre) != 25:
            raise ValueError(f"Campo livre inválido: deve ter 25 dígitos, tem {len(campo_livre)}")
        
        # Recalcular DV para validação
        codigo_sem_dv = f"{banco}{moeda}{vencimento}{valor}{campo_livre}"
        dv_calculado = self._calcular_dv_codigo_barras(codigo_sem_dv)
        
        if dv_informado != dv_calculado:
            raise ValueError(
                f"DV inválido: calculado {dv_calculado}, informado {dv_informado}. "
                f"Código sem DV: {codigo_sem_dv}"
            )
    
    def _calcular_dv_codigo_barras(self, codigo):
        """
        Calcula dígito verificador do código de barras (Módulo 11 FEBRABAN)
        Sequência de multiplicação: 4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2
        """
        
        # Sequência de multiplicação padrão FEBRABAN para módulo 11
        sequencia = "4329876543298765432987654329876543298765432"
        soma = 0
        
        # Multiplica cada dígito pela sequência correspondente (da direita para esquerda)
        for i, digito in enumerate(reversed(codigo)):
            if digito.isdigit():
                multiplicador = int(sequencia[i % len(sequencia)])
                produto = int(digito) * multiplicador
                soma += produto
        
        resto = soma % 11
        
        # Regras FEBRABAN para módulo 11:
        # Se resto = 0, 10 ou 11, DV = 1
        # Caso contrário, DV = 11 - resto
        if resto in [0, 10, 11]:
            return 1
        else:
            return 11 - resto
    
    def _gerar_linha_digitavel_caixa(self, codigo_barras):
        """
        Gera linha digitável a partir do código de barras
        Formato: AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D EEEEEEEEEEEEEE
        """
        
        if len(codigo_barras) != 44:
            raise ValueError("Código de barras deve ter 44 dígitos")
        
        # Extrair campos do código de barras
        banco = codigo_barras[0:3]      # 104
        moeda = codigo_barras[3:4]      # 9
        dv_geral = codigo_barras[4:5]   # DV
        vencimento = codigo_barras[5:9] # Fator vencimento
        valor = codigo_barras[9:19]     # Valor
        campo_livre = codigo_barras[19:44]  # Campo livre (25)
        
        # Campo 1: Banco + Moeda + primeiros 5 do campo livre + DV
        campo1_base = f"{banco}{moeda}{campo_livre[0:5]}"
        dv1 = self._calcular_dv_modulo10(campo1_base)
        campo1 = f"{campo1_base[0:5]}.{campo1_base[5:10]}{dv1}"
        
        # Campo 2: Próximos 10 dígitos do campo livre + DV
        campo2_base = campo_livre[5:15]
        dv2 = self._calcular_dv_modulo10(campo2_base)
        campo2 = f"{campo2_base[0:5]}.{campo2_base[5:10]}{dv2}"
        
        # Campo 3: Últimos 10 dígitos do campo livre + DV
        campo3_base = campo_livre[15:25]
        dv3 = self._calcular_dv_modulo10(campo3_base)
        campo3 = f"{campo3_base[0:5]}.{campo3_base[5:10]}{dv3}"
        
        # Campo 4: DV geral
        campo4 = dv_geral
        
        # Campo 5: Fator vencimento + valor
        campo5 = f"{vencimento}{valor}"
        
        return f"{campo1} {campo2} {campo3} {campo4} {campo5}"
    
    def _calcular_dv_modulo10(self, codigo):
        """
        Calcula dígito verificador módulo 10 (FEBRABAN)
        Multiplica alternadamente por 2 e 1, da direita para esquerda
        Se o produto for maior que 9, soma os dígitos
        """
        
        soma = 0
        multiplicador = 2  # Começa com 2
        
        # Processa da direita para esquerda
        for digito in reversed(codigo):
            if digito.isdigit():
                produto = int(digito) * multiplicador
                
                # Se produto > 9, soma os dígitos (ex: 18 = 1+8 = 9)
                if produto > 9:
                    produto = sum(int(d) for d in str(produto))
                
                soma += produto
                
                # Alterna multiplicador entre 2 e 1
                multiplicador = 3 - multiplicador  # 2->1, 1->2
        
        resto = soma % 10
        return 0 if resto == 0 else 10 - resto
    
    def _validar_boleto_completo(self, codigo_barras: str, linha_digitavel: str) -> BarcodeValidationResult:
        """
        Executa validação completa do boleto gerado
        Utiliza o BarcodeValidator para verificar todos os aspectos do boleto
        """
        try:
            # Executar validação completa
            validation_result = self.validator.validate_complete(codigo_barras, linha_digitavel)
            
            # Adicionar validações específicas da Caixa
            self._validar_especificacoes_caixa(codigo_barras, validation_result)
            
            return validation_result
            
        except Exception as e:
            # Se houver erro na validação, criar resultado com erro
            result = BarcodeValidationResult()
            result.add_error(f"Erro durante validação: {str(e)}")
            return result
    
    def _validar_especificacoes_caixa(self, codigo_barras: str, result: BarcodeValidationResult):
        """
        Adiciona validações específicas da Caixa Econômica Federal
        """
        try:
            # Extrair campo livre para validações específicas
            campo_livre = codigo_barras[19:44]
            
            # Validar estrutura específica da Caixa
            codigo_cedente = campo_livre[0:6]
            nosso_numero = campo_livre[6:16]
            agencia_conta = campo_livre[16:22]
            carteira = campo_livre[22:25]
            
            # Validações específicas da Caixa
            if codigo_cedente == "000000":
                result.add_warning("Código do cedente é zero - verificar configuração")
            
            if nosso_numero == "0000000000":
                result.add_error("Nosso número não pode ser zero")
            
            agencia = agencia_conta[0:4]
            if agencia == "0000":
                result.add_error("Agência não pode ser zero")
            
            # Validar carteira específica da Caixa
            carteiras_caixa = ["001", "002", "014", "024"]
            if carteira not in carteiras_caixa:
                result.add_warning(f"Carteira {carteira} pode não ser padrão da Caixa")
            
            # Adicionar detalhes específicos da Caixa
            result.add_detail('caixa_codigo_cedente', codigo_cedente)
            result.add_detail('caixa_nosso_numero', nosso_numero)
            result.add_detail('caixa_agencia', agencia)
            result.add_detail('caixa_carteira', carteira)
            result.add_detail('caixa_carteira_valida', carteira in carteiras_caixa)
            
        except Exception as e:
            result.add_error(f"Erro na validação específica da Caixa: {str(e)}")
    
    def validar_boleto_existente(self, codigo_barras: str, linha_digitavel: str = None) -> BarcodeValidationResult:
        """
        Método público para validar boletos existentes
        Pode ser usado para verificar boletos já salvos no banco de dados
        """
        return self._validar_boleto_completo(codigo_barras, linha_digitavel)