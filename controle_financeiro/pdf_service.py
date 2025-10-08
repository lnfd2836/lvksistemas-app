"""
Serviço para geração de PDFs de boletos
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
import tempfile
import os


class BoletoPDFService:
    """Serviço para geração de PDFs de boletos"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2 * cm
        
    def gerar_pdf_boleto(self, boleto):
        """
        Gera PDF do boleto
        
        Args:
            boleto: Instância do BoletoGerado
            
        Returns:
            HttpResponse: PDF do boleto
        """
        
        # Criar buffer para o PDF
        buffer = BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Criar conteúdo do boleto
        story = []
        
        # Adicionar cabeçalho
        story.extend(self._criar_cabecalho(boleto))
        
        # Adicionar dados do beneficiário
        story.extend(self._criar_dados_beneficiario(boleto))
        
        # Adicionar dados do pagador
        story.extend(self._criar_dados_pagador(boleto))
        
        # Adicionar informações do boleto
        story.extend(self._criar_informacoes_boleto(boleto))
        
        # Adicionar código de barras
        story.extend(self._criar_codigo_barras(boleto))
        
        # Adicionar instruções
        story.extend(self._criar_instrucoes(boleto))
        
        # Adicionar recibo do sacado (canhoto)
        story.extend(self._criar_recibo_sacado(boleto))
        
        # Gerar PDF
        doc.build(story)
        
        # Preparar resposta HTTP
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="boleto_{boleto.numero_boleto}.pdf"'
        
        return response
    
    def _criar_cabecalho(self, boleto):
        """Cria o cabeçalho do boleto"""
        styles = getSampleStyleSheet()
        
        # Título
        titulo_style = ParagraphStyle(
            'TituloBoleto',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        titulo = Paragraph("BOLETO DE COBRANÇA", titulo_style)
        
        # Informações do banco
        banco_data = [
            [f"{boleto.configuracao.codigo_banco}-X", boleto.configuracao.nome_banco, "Vencimento", boleto.data_vencimento.strftime("%d/%m/%Y")],
            ["", "", "Valor do Documento", f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")]
        ]
        
        banco_table = Table(banco_data, colWidths=[3*cm, 8*cm, 3*cm, 4*cm])
        banco_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return [titulo, Spacer(1, 10), banco_table, Spacer(1, 20)]
    
    def _criar_dados_beneficiario(self, boleto):
        """Cria seção com dados do beneficiário"""
        styles = getSampleStyleSheet()
        
        beneficiario_style = ParagraphStyle(
            'Beneficiario',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        
        beneficiario_data = [
            ["Beneficiário:", boleto.configuracao.nome_beneficiario],
            ["CNPJ:", boleto.configuracao.cnpj_beneficiario],
            ["Endereço:", boleto.configuracao.endereco_beneficiario],
            ["Agência/Conta:", f"{boleto.configuracao.agencia} / {boleto.configuracao.conta}"],
        ]
        
        beneficiario_table = Table(beneficiario_data, colWidths=[3*cm, 15*cm])
        beneficiario_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        return [beneficiario_table, Spacer(1, 15)]
    
    def _criar_dados_pagador(self, boleto):
        """Cria seção com dados do pagador (loja)"""
        styles = getSampleStyleSheet()
        
        loja = boleto.controle_financeiro.loja
        
        pagador_data = [
            ["Pagador:", loja.nome],
            ["CNPJ:", loja.cnpj],
            ["Endereço:", loja.endereco],
            ["Email:", loja.email],
            ["Telefone:", loja.telefone],
        ]
        
        pagador_table = Table(pagador_data, colWidths=[3*cm, 15*cm])
        pagador_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        return [pagador_table, Spacer(1, 15)]
    
    def _criar_informacoes_boleto(self, boleto):
        """Cria seção com informações do boleto"""
        
        info_data = [
            ["Número do Boleto:", boleto.numero_boleto, "Data de Emissão:", boleto.data_criacao.strftime("%d/%m/%Y")],
            ["Nosso Número:", boleto.numero_boleto[-10:], "Data de Vencimento:", boleto.data_vencimento.strftime("%d/%m/%Y")],
            ["Carteira:", boleto.configuracao.carteira, "Valor do Documento:", f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ]
        
        # Adicionar informações de multa e juros se configuradas
        if boleto.configuracao.multa > 0:
            info_data.append(["Multa após vencimento:", f"{boleto.configuracao.multa}%", "Juros ao mês:", f"{boleto.configuracao.juros}%"])
        
        if boleto.configuracao.desconto > 0:
            info_data.append(["Desconto até vencimento:", f"{boleto.configuracao.desconto}%", "", ""])
        
        info_table = Table(info_data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        return [info_table, Spacer(1, 20)]
    
    def _criar_codigo_barras(self, boleto):
        """Cria código de barras do boleto"""
        
        # Linha digitável
        linha_style = ParagraphStyle(
            'LinhaDigitavel',
            fontSize=12,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Courier-Bold',
            spaceAfter=10
        )
        
        linha_digitavel = Paragraph(f"<b>{boleto.linha_digitavel}</b>", linha_style)
        
        # Código de barras visual (barrinhas) para leitura com câmera
        try:
            # Preparar código de barras - usar apenas números
            barcode_value = ''.join(filter(str.isdigit, boleto.codigo_barras))
            
            # Garantir que tenha pelo menos 20 dígitos e no máximo 44
            if len(barcode_value) < 20:
                barcode_value = barcode_value.ljust(44, '0')
            elif len(barcode_value) > 44:
                barcode_value = barcode_value[:44]
            
            # Método 1: Tentar usar python-barcode para gerar imagem
            try:
                from barcode import Code128 as BarcodeCode128
                from barcode.writer import ImageWriter
                from PIL import Image
                import io
                
                # Gerar código de barras como imagem
                barcode_generator = BarcodeCode128(barcode_value, writer=ImageWriter())
                
                # Configurar opções da imagem - SEM texto duplicado
                options = {
                    'module_width': 0.3,
                    'module_height': 12.0,
                    'quiet_zone': 2.0,
                    'font_size': 0,  # Remove texto abaixo do código de barras
                    'text_distance': 0.0,
                    'background': 'white',
                    'foreground': 'black',
                    'write_text': False,  # Não escrever texto
                }
                
                # Gerar imagem em memória
                buffer = io.BytesIO()
                barcode_generator.write(buffer, options=options)
                buffer.seek(0)
                
                # Criar imagem para o PDF
                from reportlab.platypus import Image as ReportLabImage
                
                barcode_image = ReportLabImage(buffer, width=15*cm, height=2*cm)
                
                return [
                    linha_digitavel,
                    Spacer(1, 10),
                    barcode_image,
                    Spacer(1, 20)
                ]
                
            except Exception as e1:
                print(f"Método 1 falhou: {e1}")
                
                # Método 2: Usar reportlab Code128 com configurações otimizadas
                try:
                    from reportlab.graphics.barcode.code128 import Code128
                    from reportlab.graphics.shapes import Drawing
                    
                    # Criar código de barras com configurações para leitura por câmera
                    barcode = Code128(
                        barcode_value,
                        barHeight=15*mm,  # Altura maior para melhor leitura
                        barWidth=0.4*mm,  # Largura das barras otimizada
                        humanReadable=0,  # NÃO mostrar números abaixo (evita duplicação)
                        checksum=0,
                        bearers=0
                    )
                    
                    # Criar drawing com fundo branco
                    drawing = Drawing(18*cm, 3*cm)
                    
                    # Adicionar fundo branco
                    from reportlab.graphics.shapes import Rect
                    fundo = Rect(0, 0, 18*cm, 3*cm, fillColor=colors.white, strokeColor=colors.white)
                    drawing.add(fundo)
                    
                    # Centralizar o código de barras
                    barcode.x = 1*cm
                    barcode.y = 0.5*cm
                    
                    # Adicionar código de barras
                    drawing.add(barcode)
                    
                    # Adicionar título
                    titulo_style = ParagraphStyle(
                        'TituloBarcode',
                        fontSize=10,
                        textColor=colors.black,
                        alignment=TA_CENTER,
                        fontName='Helvetica-Bold'
                    )
                    
                    titulo = Paragraph("📱 <b>Escaneie com a câmera do seu celular ou app bancário</b>", titulo_style)
                    
                    return [
                        linha_digitavel,
                        Spacer(1, 10),
                        titulo,
                        Spacer(1, 5),
                        drawing,
                        Spacer(1, 20)
                    ]
                    
                except Exception as e2:
                    print(f"Método 2 falhou: {e2}")
                    raise e2
            
        except Exception as e:
            # Fallback final - QR Code como alternativa
            try:
                import qrcode
                from reportlab.platypus import Image as ReportLabImage
                import io
                
                # Criar QR Code com a linha digitável
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=4,
                    border=2,
                )
                
                # Adicionar dados do boleto ao QR Code
                qr_data = f"Boleto: {boleto.linha_digitavel}\nValor: R$ {boleto.valor}\nVencimento: {boleto.data_vencimento.strftime('%d/%m/%Y')}"
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                # Gerar imagem do QR Code
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                # Salvar em buffer
                buffer = io.BytesIO()
                qr_img.save(buffer, format='PNG')
                buffer.seek(0)
                
                # Criar imagem para o PDF
                qr_image = ReportLabImage(buffer, width=4*cm, height=4*cm)
                
                # Estilo para explicação
                qr_style = ParagraphStyle(
                    'QRExplicacao',
                    fontSize=10,
                    textColor=colors.blue,
                    alignment=TA_CENTER
                )
                
                qr_explicacao = Paragraph(
                    "📱 <b>QR Code alternativo</b><br/>Escaneie com a câmera para ver dados do boleto", 
                    qr_style
                )
                
                # Código como texto para backup
                codigo_style = ParagraphStyle(
                    'CodigoTexto',
                    fontSize=8,
                    textColor=colors.black,
                    alignment=TA_CENTER,
                    fontName='Courier'
                )
                
                codigo_limpo = ''.join(filter(str.isdigit, boleto.codigo_barras))[:44]
                codigo_formatado = ' '.join([codigo_limpo[i:i+4] for i in range(0, len(codigo_limpo), 4)])
                codigo_texto = Paragraph(f"Código de Barras: {codigo_formatado}", codigo_style)
                
                return [
                    linha_digitavel,
                    Spacer(1, 10),
                    qr_explicacao,
                    Spacer(1, 5),
                    qr_image,
                    Spacer(1, 10),
                    codigo_texto,
                    Spacer(1, 20)
                ]
                
            except Exception as e3:
                # Último fallback - apenas texto
                fallback_style = ParagraphStyle(
                    'Fallback',
                    fontSize=10,
                    textColor=colors.blue,
                    alignment=TA_CENTER
                )
                
                fallback_msg = Paragraph(
                    "Use a linha digitável acima para pagamento em qualquer banco ou app bancário", 
                    fallback_style
                )
                
                return [
                    linha_digitavel,
                    Spacer(1, 10),
                    fallback_msg,
                    Spacer(1, 20)
                ]
    
    def _criar_instrucoes(self, boleto):
        """Cria seção de instruções"""
        styles = getSampleStyleSheet()
        
        instrucoes_style = ParagraphStyle(
            'Instrucoes',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            leftIndent=10,
            rightIndent=10
        )
        
        titulo_instrucoes = Paragraph("<b>INSTRUÇÕES:</b>", instrucoes_style)
        
        instrucoes_texto = boleto.configuracao.instrucoes or "Não receber após o vencimento."
        
        instrucoes_lista = [
            "• " + instrucoes_texto,
            "• Em caso de dúvidas, entre em contato conosco.",
            "• Pagamento pode ser feito em qualquer banco, casa lotérica ou internet banking.",
            "• Após o vencimento, cobrar multa e juros conforme configurado.",
        ]
        
        instrucoes_paragrafos = [titulo_instrucoes, Spacer(1, 5)]
        
        for instrucao in instrucoes_lista:
            instrucoes_paragrafos.append(Paragraph(instrucao, instrucoes_style))
            instrucoes_paragrafos.append(Spacer(1, 3))
        
        return instrucoes_paragrafos + [Spacer(1, 20)]
    
    def _criar_recibo_sacado(self, boleto):
        """Cria recibo do sacado (canhoto)"""
        styles = getSampleStyleSheet()
        
        # Linha pontilhada de corte
        corte_style = ParagraphStyle(
            'Corte',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        linha_corte = Paragraph("✂ " + "- " * 50 + " RECIBO DO PAGADOR " + "- " * 50 + " ✂", corte_style)
        
        # Dados resumidos do recibo
        recibo_data = [
            ["Beneficiário:", boleto.configuracao.nome_beneficiario, "Vencimento:", boleto.data_vencimento.strftime("%d/%m/%Y")],
            ["Pagador:", boleto.controle_financeiro.loja.nome, "Valor:", f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Número do Boleto:", boleto.numero_boleto, "Data de Pagamento:", "_____/_____/_____"],
        ]
        
        recibo_table = Table(recibo_data, colWidths=[3*cm, 6*cm, 3*cm, 6*cm])
        recibo_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        # Assinatura
        assinatura_style = ParagraphStyle(
            'Assinatura',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_RIGHT
        )
        
        assinatura = Paragraph("Autenticação Mecânica: ________________________", assinatura_style)
        
        return [
            Spacer(1, 30),
            linha_corte,
            Spacer(1, 10),
            recibo_table,
            Spacer(1, 15),
            assinatura
        ]