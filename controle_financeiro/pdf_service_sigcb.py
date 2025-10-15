"""
Serviço para geração de PDFs de boletos - Layout CAIXA SIGCB
Implementa o novo padrão SIGCB (Sistema de Gestão de Cobrança Bancária) da Caixa
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing, Rect
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
import tempfile
import os


class BoletoPDFServiceSIGCB:
    """Serviço para geração de PDFs de boletos - Layout CAIXA SIGCB"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 1.5 * cm  # Margem menor para aproveitar melhor o espaço
        
        # Cores padrão SIGCB Caixa
        self.cor_caixa_azul = colors.Color(0, 0.4, 0.8)  # Azul Caixa
        self.cor_caixa_laranja = colors.Color(1, 0.6, 0)  # Laranja Caixa
        self.cor_fundo_cabecalho = colors.Color(0.95, 0.95, 0.95)  # Cinza claro
        
    def gerar_pdf_boleto_sigcb(self, boleto):
        """
        Gera PDF do boleto seguindo layout SIGCB da Caixa
        
        Args:
            boleto: Instância do BoletoGerado
            
        Returns:
            HttpResponse: PDF do boleto no formato SIGCB
        """
        
        # Criar buffer para o PDF
        buffer = BytesIO()
        
        # Criar documento PDF com configurações SIGCB
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=f"Boleto SIGCB {boleto.numero_boleto}",
            author="Sistema LVK - Caixa SIGCB"
        )
        
        # Criar conteúdo do boleto SIGCB
        story = []
        
        # Cabeçalho SIGCB
        story.extend(self._criar_cabecalho_sigcb(boleto))
        
        # Ficha de Compensação (parte principal do boleto)
        story.extend(self._criar_ficha_compensacao_sigcb(boleto))
        
        # Código de barras SIGCB
        story.extend(self._criar_codigo_barras_sigcb(boleto))
        
        # Recibo do Sacado (canhoto) - formato SIGCB
        story.extend(self._criar_recibo_sacado_sigcb(boleto))
        
        # Gerar PDF
        doc.build(story)
        
        # Preparar resposta HTTP
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="boleto_sigcb_{boleto.numero_boleto}.pdf"'
        
        return response
    
    def _criar_cabecalho_sigcb(self, boleto):
        """Cria cabeçalho no padrão SIGCB da Caixa"""
        
        # Logo e identificação da Caixa - Layout SIGCB
        cabecalho_data = [
            [
                "CAIXA ECONÔMICA FEDERAL",
                "104-0",
                "FICHA DE COMPENSAÇÃO"
            ]
        ]
        
        cabecalho_table = Table(cabecalho_data, colWidths=[10*cm, 3*cm, 5*cm])
        cabecalho_table.setStyle(TableStyle([
            # Fundo azul Caixa
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_caixa_azul),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 14),  # Nome da Caixa maior
            ('FONTSIZE', (1, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 2, colors.white),
        ]))
        
        return [cabecalho_table, Spacer(1, 5)]
    
    def _criar_ficha_compensacao_sigcb(self, boleto):
        """Cria a ficha de compensação no padrão SIGCB"""
        
        # Linha 1: Local de Pagamento e Vencimento
        linha1_data = [
            ["Local de Pagamento", "Vencimento"],
            ["PREFERENCIALMENTE NAS CASAS LOTÉRICAS ATÉ O VALOR LIMITE", boleto.data_vencimento.strftime("%d/%m/%Y")]
        ]
        
        linha1_table = Table(linha1_data, colWidths=[13*cm, 5*cm])
        linha1_table.setStyle(self._get_table_style_sigcb())
        
        # Linha 2: Beneficiário e Agência/Código do Beneficiário
        linha2_data = [
            ["Beneficiário", "Agência/Código Beneficiário"],
            [boleto.configuracao.nome_beneficiario.upper(), f"{boleto.configuracao.agencia}/{boleto.configuracao.codigo_cedente}"]
        ]
        
        linha2_table = Table(linha2_data, colWidths=[13*cm, 5*cm])
        linha2_table.setStyle(self._get_table_style_sigcb())
        
        # Linha 3: Data do Documento, Número do Documento, Espécie Doc, Aceite, Data Processamento
        linha3_data = [
            ["Data do Documento", "Nº do Documento", "Espécie Doc.", "Aceite", "Data de Processamento"],
            [
                boleto.data_criacao.strftime("%d/%m/%Y"),
                boleto.numero_boleto,
                "DM",
                "N",
                boleto.data_criacao.strftime("%d/%m/%Y")
            ]
        ]
        
        linha3_table = Table(linha3_data, colWidths=[3*cm, 4*cm, 2.5*cm, 2*cm, 6.5*cm])
        linha3_table.setStyle(self._get_table_style_sigcb())
        
        # Linha 4: Uso do Banco, Carteira, Espécie, Quantidade, Valor
        linha4_data = [
            ["Uso do Banco", "Carteira", "Espécie", "Quantidade", "Valor"],
            ["", boleto.configuracao.carteira, "R$", "", f"{boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")]
        ]
        
        linha4_table = Table(linha4_data, colWidths=[3*cm, 2.5*cm, 2*cm, 3*cm, 7.5*cm])
        linha4_table.setStyle(self._get_table_style_sigcb())
        
        # Linha 5: Instruções e Valor do Documento
        instrucoes_texto = self._get_instrucoes_sigcb(boleto)
        
        linha5_data = [
            ["Instruções (Texto de responsabilidade do beneficiário)", "(-) Desconto / Abatimentos"],
            [instrucoes_texto, ""]
        ]
        
        linha5_table = Table(linha5_data, colWidths=[13*cm, 5*cm], rowHeights=[2*cm, None])
        linha5_table.setStyle(self._get_table_style_sigcb_instrucoes())
        
        # Linha 6: Mais campos de valores
        linha6_data = [
            ["", "(-) Outras deduções"],
            ["", "(+) Mora / Multa"],
            ["", "(+) Outros acréscimos"],
            ["", "(=) Valor cobrado"]
        ]
        
        linha6_table = Table(linha6_data, colWidths=[13*cm, 5*cm])
        linha6_table.setStyle(self._get_table_style_sigcb())
        
        # Sacado (Pagador)
        sacado_data = [
            ["Sacado"],
            [self._get_dados_sacado_sigcb(boleto)]
        ]
        
        sacado_table = Table(sacado_data, colWidths=[18*cm])
        sacado_table.setStyle(self._get_table_style_sigcb())
        
        return [
            linha1_table,
            linha2_table, 
            linha3_table,
            linha4_table,
            linha5_table,
            linha6_table,
            sacado_table,
            Spacer(1, 10)
        ]
    
    def _criar_codigo_barras_sigcb(self, boleto):
        """Cria código de barras no padrão SIGCB com múltiplas tentativas"""
        
        # Linha digitável em destaque
        linha_style = ParagraphStyle(
            'LinhaDigitavelSIGCB',
            fontSize=11,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Courier-Bold',
            spaceAfter=5
        )
        
        linha_digitavel = Paragraph(f"<b>{boleto.linha_digitavel}</b>", linha_style)
        
        # Preparar código de barras - garantir que seja válido
        codigo_limpo = ''.join(filter(str.isdigit, boleto.codigo_barras))
        if len(codigo_limpo) != 44:
            codigo_limpo = codigo_limpo.ljust(44, '0')[:44]
        
        # Método 1: Tentar Interleaved 2 of 5 (conforme manual da Caixa)
        try:
            from reportlab.graphics.barcode import createBarcodeDrawing
            from reportlab.graphics.shapes import Drawing, Rect
            
            # Criar código de barras Interleaved 2 of 5 conforme especificação da Caixa
            # Usar createBarcodeDrawing que é mais confiável
            drawing = createBarcodeDrawing(
                'I2of5',
                value=codigo_limpo,
                barHeight=13*mm,   # Altura conforme manual (13mm)
                barWidth=0.4*mm,   # Largura das barras otimizada
                humanReadable=0,   # Sem texto abaixo
                checksum=0,
                bearers=0,
                quiet=1,           # Zona silenciosa
                lquiet=5*mm,       # Margem esquerda conforme manual (5mm)
                rquiet=5*mm        # Margem direita
            )
            
            # O drawing já está posicionado corretamente pelo createBarcodeDrawing
            
            # Título explicativo
            titulo_style = ParagraphStyle(
                'TituloBarcodeSIGCB',
                fontSize=9,
                textColor=colors.black,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            titulo = Paragraph("📱 <b>Código de Barras - Escaneie com leitor ou câmera do celular</b>", titulo_style)
            
            return [linha_digitavel, Spacer(1, 5), titulo, drawing, Spacer(1, 10)]
            
        except Exception as e1:
            print(f"Método 1 falhou: {e1}")
            
            # Método 2: Tentar python-barcode com imagem
            try:
                from barcode import Code128 as BarcodeCode128
                from barcode.writer import ImageWriter
                from reportlab.platypus import Image as ReportLabImage
                import io
                
                # Gerar código de barras como imagem
                barcode_generator = BarcodeCode128(codigo_limpo, writer=ImageWriter())
                
                # Configurações para melhor qualidade
                options = {
                    'module_width': 0.4,      # Largura das barras
                    'module_height': 15.0,    # Altura das barras
                    'quiet_zone': 3.0,        # Zona silenciosa
                    'font_size': 0,           # Sem texto
                    'text_distance': 0.0,
                    'background': 'white',
                    'foreground': 'black',
                    'write_text': False,
                    'dpi': 300                # Alta resolução
                }
                
                # Gerar imagem em memória
                buffer = io.BytesIO()
                barcode_generator.write(buffer, options=options)
                buffer.seek(0)
                
                # Criar imagem para o PDF
                barcode_image = ReportLabImage(buffer, width=16*cm, height=2*cm)
                
                # Título explicativo
                titulo_style = ParagraphStyle(
                    'TituloBarcodeSIGCB2',
                    fontSize=9,
                    textColor=colors.black,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                )
                
                titulo = Paragraph("📱 <b>Código de Barras - Escaneie com leitor ou câmera do celular</b>", titulo_style)
                
                return [linha_digitavel, Spacer(1, 5), titulo, barcode_image, Spacer(1, 10)]
                
            except Exception as e2:
                print(f"Método 2 falhou: {e2}")
                
                # Método 3: Fallback com código numérico formatado
                try:
                    codigo_formatado_style = ParagraphStyle(
                        'CodigoFormatadoSIGCB',
                        fontSize=8,
                        textColor=colors.black,
                        alignment=TA_CENTER,
                        fontName='Courier-Bold',
                        spaceAfter=5
                    )
                    
                    # Formatar código em grupos de 4 dígitos
                    codigo_formatado = ' '.join([codigo_limpo[i:i+4] for i in range(0, len(codigo_limpo), 4)])
                    codigo_texto = Paragraph(f"<b>Código de Barras (44 dígitos):</b><br/>{codigo_formatado}", codigo_formatado_style)
                    
                    # Aviso sobre código visual
                    aviso_style = ParagraphStyle(
                        'AvisoSIGCB',
                        fontSize=9,
                        textColor=colors.red,
                        alignment=TA_CENTER,
                        fontName='Helvetica'
                    )
                    
                    aviso = Paragraph("⚠️ <b>Use a linha digitável acima para pagamento</b><br/>Código de barras visual não disponível", aviso_style)
                    
                    return [linha_digitavel, Spacer(1, 10), codigo_texto, Spacer(1, 5), aviso, Spacer(1, 10)]
                    
                except Exception as e3:
                    print(f"Método 3 falhou: {e3}")
                    
                    # Último fallback - apenas linha digitável
                    return [linha_digitavel, Spacer(1, 15)]
    
    def _criar_recibo_sacado_sigcb(self, boleto):
        """Cria recibo do sacado no padrão SIGCB"""
        
        # Linha de corte SIGCB
        corte_style = ParagraphStyle(
            'CorteSIGCB',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        linha_corte = Paragraph("✂ " + "- " * 40 + " Recibo do Sacado " + "- " * 40 + " ✂", corte_style)
        
        # Cabeçalho do recibo
        recibo_cabecalho = [
            ["CAIXA ECONÔMICA FEDERAL", "104-0", boleto.data_vencimento.strftime("%d/%m/%Y")]
        ]
        
        recibo_cabecalho_table = Table(recibo_cabecalho, colWidths=[10*cm, 3*cm, 5*cm])
        recibo_cabecalho_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_fundo_cabecalho),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        # Dados do recibo
        recibo_dados = [
            ["Nosso Número", "Vencimento", "Valor do Documento"],
            [boleto.numero_boleto, boleto.data_vencimento.strftime("%d/%m/%Y"), f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")]
        ]
        
        recibo_dados_table = Table(recibo_dados, colWidths=[6*cm, 6*cm, 6*cm])
        recibo_dados_table.setStyle(self._get_table_style_sigcb())
        
        # Beneficiário e Sacado no recibo
        recibo_partes = [
            ["Beneficiário", "Sacado"],
            [boleto.configuracao.nome_beneficiario, boleto.controle_financeiro.loja.nome]
        ]
        
        recibo_partes_table = Table(recibo_partes, colWidths=[9*cm, 9*cm])
        recibo_partes_table.setStyle(self._get_table_style_sigcb())
        
        # Autenticação mecânica
        auth_style = ParagraphStyle(
            'AuthSIGCB',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_RIGHT
        )
        
        autenticacao = Paragraph("Autenticação Mecânica - FICHA DE COMPENSAÇÃO", auth_style)
        
        return [
            Spacer(1, 20),
            linha_corte,
            Spacer(1, 10),
            recibo_cabecalho_table,
            recibo_dados_table,
            recibo_partes_table,
            Spacer(1, 10),
            autenticacao
        ]
    
    def _get_table_style_sigcb(self):
        """Retorna estilo padrão para tabelas SIGCB"""
        return TableStyle([
            # Cabeçalhos
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_fundo_cabecalho),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            
            # Alinhamento
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Espaçamento
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
    
    def _get_table_style_sigcb_instrucoes(self):
        """Retorna estilo para tabela de instruções SIGCB"""
        style = self._get_table_style_sigcb()
        style.add('VALIGN', (0, 1), (0, 1), 'TOP')  # Instruções alinhadas ao topo
        return style
    
    def _get_instrucoes_sigcb(self, boleto):
        """Retorna instruções formatadas para SIGCB"""
        instrucoes = []
        
        # Instrução personalizada se existir
        if boleto.configuracao.instrucoes:
            instrucoes.append(boleto.configuracao.instrucoes)
        
        # Instruções padrão SIGCB
        instrucoes.extend([
            "NÃO RECEBER APÓS O VENCIMENTO",
            f"MULTA DE {boleto.configuracao.multa}% APÓS O VENCIMENTO" if boleto.configuracao.multa > 0 else "",
            f"JUROS DE {boleto.configuracao.juros}% AO MÊS" if boleto.configuracao.juros > 0 else "",
            "PAGÁVEL EM QUALQUER BANCO ATÉ O VENCIMENTO"
        ])
        
        # Filtrar instruções vazias e juntar
        instrucoes_filtradas = [i for i in instrucoes if i.strip()]
        return "\n".join(instrucoes_filtradas)
    
    def _get_dados_sacado_sigcb(self, boleto):
        """Retorna dados do sacado formatados para SIGCB"""
        loja = boleto.controle_financeiro.loja
        
        dados = [
            f"Nome: {loja.nome.upper()}",
            f"CNPJ: {self._formatar_cnpj(loja.cnpj)}",
        ]
        
        if loja.endereco:
            dados.append(f"Endereço: {loja.endereco}")
        
        if loja.cidade and loja.estado:
            dados.append(f"Cidade: {loja.cidade}/{loja.estado}")
        
        if loja.cep:
            dados.append(f"CEP: {loja.cep}")
        
        return " - ".join(dados)
    
    def _formatar_cnpj(self, cnpj):
        """Formata CNPJ para exibição"""
        if not cnpj:
            return "Não informado"
        
        # Remove caracteres não numéricos
        cnpj_numeros = ''.join(filter(str.isdigit, cnpj))
        
        # Formata se tiver 14 dígitos
        if len(cnpj_numeros) == 14:
            return f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:14]}"
        
        return cnpj  # Retorna original se não conseguir formatar