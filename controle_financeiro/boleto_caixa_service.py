"""
Serviço específico para geração de boletos da Caixa Econômica Federal
Segue as especificações técnicas da CEF para boletos registrados
"""

from datetime import datetime, timedelta
from django.utils import timezone
import re


class BoletoCaixaService:
    """Serviço para geração de boletos válidos da Caixa Econômica Federal"""
    
    def __init__(self):
        self.codigo_banco = "104"  # Código da Caixa Econômica Federal
        self.moeda = "9"  # Real
        
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
        
        return {
            'numero_boleto': nosso_numero,
            'codigo_barras': codigo_barras,
            'linha_digitavel': linha_digitavel,
            'data_vencimento': data_vencimento,
            'valor': controle_financeiro.valor_mensal,
            'fator_vencimento': fator_vencimento
        }
    
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
        Formato: AAAANNNNNNNNNNN-D (Agência + Sequencial + DV)
        """
        
        # Para teste, usar timestamp como sequencial
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        sequencial = timestamp[-10:].zfill(10)  # Últimos 10 dígitos
        
        # Nosso número sem DV: Agência + Sequencial
        nosso_numero_base = f"{configuracao.agencia}{sequencial}"
        
        # Calcular dígito verificador
        dv = self._calcular_dv_nosso_numero_caixa(nosso_numero_base)
        
        # Nosso número completo
        nosso_numero = f"{nosso_numero_base}-{dv}"
        
        return nosso_numero
    
    def _calcular_dv_nosso_numero_caixa(self, nosso_numero):
        """Calcula dígito verificador do nosso número da Caixa (Módulo 11)"""
        
        sequencia = "4329876543298765432987654329876543298765"
        soma = 0
        
        for i, digito in enumerate(reversed(nosso_numero)):
            if digito.isdigit():
                produto = int(digito) * int(sequencia[i % len(sequencia)])
                soma += produto
        
        resto = soma % 11
        
        if resto == 0 or resto == 1:
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
        
        # Campo livre da Caixa (25 posições)
        # Formato: CCCCCC NNNNNNNNNN AAAAAA DDD
        # C = Código do cedente (6)
        # N = Nosso número sem DV (10) 
        # A = Agência (4) + zeros (2)
        # D = Carteira (3)
        
        codigo_cedente = configuracao.codigo_cedente.zfill(6)[:6]
        nosso_numero_limpo = re.sub(r'[^0-9]', '', nosso_numero)[-10:].zfill(10)
        agencia_campo = f"{configuracao.agencia}00"
        carteira_campo = configuracao.carteira.zfill(3)
        
        campo_livre = f"{codigo_cedente}{nosso_numero_limpo}{agencia_campo}{carteira_campo}"
        
        # Montar código sem DV
        codigo_sem_dv = f"{self.codigo_banco}{self.moeda}{fator_vencimento}{valor_centavos}{campo_livre}"
        
        # Calcular DV geral
        dv_geral = self._calcular_dv_codigo_barras(codigo_sem_dv)
        
        # Código de barras completo
        codigo_barras = f"{self.codigo_banco}{self.moeda}{dv_geral}{fator_vencimento}{valor_centavos}{campo_livre}"
        
        return codigo_barras
    
    def _calcular_dv_codigo_barras(self, codigo):
        """Calcula dígito verificador do código de barras (Módulo 11)"""
        
        sequencia = "432987654329876543298765432987654329876543298765432"
        soma = 0
        
        for i, digito in enumerate(reversed(codigo)):
            if digito.isdigit():
                produto = int(digito) * int(sequencia[i % len(sequencia)])
                soma += produto
        
        resto = soma % 11
        
        if resto == 0 or resto == 1 or resto == 10:
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
        """Calcula dígito verificador módulo 10"""
        
        sequencia = "2121212121212121212121212121212121212121"
        soma = 0
        
        for i, digito in enumerate(reversed(codigo)):
            if digito.isdigit():
                produto = int(digito) * int(sequencia[i % len(sequencia)])
                if produto > 9:
                    produto = sum(int(d) for d in str(produto))
                soma += produto
        
        resto = soma % 10
        return 0 if resto == 0 else 10 - resto