"""
Serviço para gerar boletos com PIX usando dados do Asaas localmente
Alternativa quando a API do Asaas não está funcionando
"""
import qrcode
from io import BytesIO
import base64
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class BoletoAsaasLocal:
    """Gera boletos com PIX usando dados do Asaas localmente"""
    
    def __init__(self):
        # Dados da conta Asaas (reais)
        self.conta_dados = {
            'banco': '461',  # Asaas I.P S.A
            'agencia': '0001',
            'conta': '194116-2',
            'nome_beneficiario': 'FELIX REPRESENTACOES E COMERCIO LTDA',
            'cnpj': '41.449.198/0001-72',
            'endereco': 'Rua das Empresas, 123 - Centro - São Paulo - SP',
            'chave_pix': '0be79c1f-73f8-41d9-a795-3401856ce31b'
        }
    
    def gerar_boleto_com_pix(self, controle_financeiro, dias_vencimento=30, descricao=None):
        """
        Gera um boleto com PIX usando dados locais
        
        Args:
            controle_financeiro: Instância do ControleFinanceiro
            dias_vencimento: Dias para vencimento
            descricao: Descrição da cobrança
            
        Returns:
            dict: Dados do boleto gerado
        """
        try:
            loja = controle_financeiro.loja
            valor = controle_financeiro.valor_mensal
            
            # Gerar ID único para o boleto
            boleto_id = f"ASAAS_{timezone.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:8]}"
            
            # Calcular data de vencimento
            data_vencimento = timezone.now().date() + timedelta(days=dias_vencimento)
            
            # Descrição padrão
            if not descricao:
                descricao = f"Mensalidade {controle_financeiro.plano.nome} - {loja.nome}"
            
            # Gerar código PIX
            pix_data = self._gerar_pix_copia_cola(
                valor=valor,
                beneficiario=self.conta_dados['nome_beneficiario'],
                cidade='SAO PAULO',
                identificador=boleto_id[-10:]  # Últimos 10 caracteres como identificador
            )
            
            # Gerar QR Code do PIX
            qr_code_base64 = self._gerar_qr_code(pix_data['pix_copia_cola'])
            
            # Gerar linha digitável (simulada para Asaas)
            linha_digitavel = self._gerar_linha_digitavel_asaas(
                valor=valor,
                vencimento=data_vencimento,
                identificador=boleto_id[-10:]
            )
            
            # Dados do boleto
            boleto_data = {
                'success': True,
                'boleto_id': boleto_id,
                'numero_boleto': boleto_id,
                'linha_digitavel': linha_digitavel,
                'codigo_barras': linha_digitavel.replace(' ', ''),
                'valor': float(valor),
                'data_vencimento': data_vencimento,
                'data_criacao': timezone.now().date(),
                'descricao': descricao,
                'status': 'PENDING',
                
                # Dados do PIX
                'pix': {
                    'qr_code_base64': qr_code_base64,
                    'copia_cola': pix_data['pix_copia_cola'],
                    'chave_pix': self.conta_dados['chave_pix'],
                    'expires_date': timezone.now() + timedelta(days=dias_vencimento)
                },
                
                # Dados do beneficiário
                'beneficiario': {
                    'nome': self.conta_dados['nome_beneficiario'],
                    'cnpj': self.conta_dados['cnpj'],
                    'banco': self.conta_dados['banco'],
                    'agencia': self.conta_dados['agencia'],
                    'conta': self.conta_dados['conta']
                },
                
                # Dados do pagador
                'pagador': {
                    'nome': loja.nome,
                    'cnpj': loja.cnpj,
                    'endereco': loja.endereco,
                    'cidade': loja.cidade,
                    'estado': loja.estado,
                    'cep': loja.cep
                },
                
                # URLs (simuladas)
                'invoice_url': f"https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/{boleto_id}/detalhes/",
                'bank_slip_url': f"https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/{boleto_id}/pdf/"
            }
            
            logger.info(f"Boleto local gerado com sucesso: {boleto_id}")
            return boleto_data
            
        except Exception as e:
            logger.error(f"Erro ao gerar boleto local: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _gerar_pix_copia_cola(self, valor, beneficiario, cidade, identificador):
        """
        Gera código PIX copia e cola
        Formato simplificado para teste
        """
        try:
            # Formato básico do PIX (EMV)
            # Este é um formato simplificado para demonstração
            pix_payload = (
                "00020126"  # Payload Format Indicator
                "580014BR.GOV.BCB.PIX"  # Merchant Account Information
                f"0136{self.conta_dados['chave_pix']}"  # PIX Key
                f"52040000"  # Merchant Category Code
                "5303986"  # Transaction Currency (BRL)
                f"54{len(str(valor)):02d}{valor:.2f}"  # Transaction Amount
                "5802BR"  # Country Code
                f"59{len(beneficiario):02d}{beneficiario}"  # Merchant Name
                f"60{len(cidade):02d}{cidade}"  # Merchant City
                f"62{len(identificador)+4:02d}05{len(identificador):02d}{identificador}"  # Additional Data
                "6304"  # CRC16 placeholder
            )
            
            # Calcular CRC16 (simplificado)
            crc = self._calcular_crc16(pix_payload)
            pix_payload += crc
            
            return {
                'pix_copia_cola': pix_payload,
                'chave_pix': self.conta_dados['chave_pix'],
                'valor': valor,
                'beneficiario': beneficiario
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar PIX: {str(e)}")
            # Fallback: PIX simplificado
            return {
                'pix_copia_cola': f"PIX_TESTE_{identificador}_{valor}",
                'chave_pix': self.conta_dados['chave_pix'],
                'valor': valor,
                'beneficiario': beneficiario
            }
    
    def _gerar_qr_code(self, pix_data):
        """Gera QR Code do PIX em base64"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(pix_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR Code: {str(e)}")
            return ""
    
    def _gerar_linha_digitavel_asaas(self, valor, vencimento, identificador):
        """
        Gera linha digitável para Asaas (formato simulado)
        """
        try:
            # Formato: 46191.23456 78901.234567 89012.345678 1 12345678901234
            banco = "461"  # Asaas
            moeda = "9"    # Real
            
            # Fator de vencimento (dias desde 07/10/1997)
            fator_vencimento = (vencimento - timezone.datetime(1997, 10, 7).date()).days
            
            # Valor em centavos (10 dígitos)
            valor_centavos = f"{int(valor * 100):010d}"
            
            # Nosso número (10 dígitos)
            nosso_numero = f"{identificador:0>10}"[:10]
            
            # Montar linha digitável
            campo1 = f"{banco}{moeda}{nosso_numero[:5]}"
            campo2 = f"{nosso_numero[5:]}{valor_centavos[:5]}"
            campo3 = f"{valor_centavos[5:]}"
            campo4 = "1"  # DV geral
            campo5 = f"{fator_vencimento:04d}{valor_centavos}"
            
            linha_digitavel = f"{campo1} {campo2} {campo3} {campo4} {campo5}"
            
            return linha_digitavel
            
        except Exception as e:
            logger.error(f"Erro ao gerar linha digitável: {str(e)}")
            return f"46191.00000 00000.000000 00000.000000 1 00000000000000"
    
    def _calcular_crc16(self, payload):
        """Calcula CRC16 para PIX (simplificado)"""
        try:
            # Implementação simplificada do CRC16
            # Para produção, usar biblioteca específica
            crc = 0xFFFF
            for byte in payload.encode():
                crc ^= byte << 8
                for _ in range(8):
                    if crc & 0x8000:
                        crc = (crc << 1) ^ 0x1021
                    else:
                        crc <<= 1
                    crc &= 0xFFFF
            
            return f"{crc:04X}"
            
        except:
            # Fallback: CRC fixo para teste
            return "1234"