"""
Serviço específico para geração de PDFs de boletos do Asaas
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


class BoletoPDFServiceAsaas:
    """Serviço específico para geração de PDFs de boletos do Asaas"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2 * cm
    
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
        
    def gerar_pdf_boleto_asaas(self, boleto):
        """
        Gera PDF do boleto do Asaas
        
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
        
        # Adicionar cabeçalho específico do Asaas
        story.extend(self._criar_cabecalho_asaas(boleto))
        
        # Adicionar dados do beneficiário
        story.extend(self._criar_dados_beneficiario(boleto))
        
        # Adicionar dados do pagador
        story.extend(self._criar_dados_pagador(boleto))
        
        # Adicionar informações do boleto
        story.extend(self._criar_informacoes_boleto(boleto))
        
        # Adicionar PIX QR Code (específico do Asaas)
        story.extend(self._criar_pix_qrcode(boleto))
        
        # Adicionar código de barras específico do Asaas
        story.extend(self._criar_codigo_barras_asaas(boleto))
        
        # Adicionar instruções específicas do Asaas
        story.extend(self._criar_instrucoes_asaas(boleto))
        
        # Adicionar recibo do sacado (canhoto)
        story.extend(self._criar_recibo_sacado(boleto))
        
        # Gerar PDF
        doc.build(story)
        
        # Preparar resposta HTTP
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="boleto_asaas_{boleto.numero_boleto}.pdf"'
        
        return response
    
    def _criar_cabecalho_asaas(self, boleto):
        """Cria o cabeçalho específico do boleto do Asaas"""
        styles = getSampleStyleSheet()
        
        # Título específico do Asaas
        titulo_style = ParagraphStyle(
            'TituloBoletoAsaas',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        titulo = Paragraph("<b>BOLETO DE COBRANÇA - ASAAS</b>", titulo_style)
        
        # Linha separadora
        linha_style = ParagraphStyle(
            'Linha',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        linha = Paragraph("─" * 100, linha_style)
        
        # Informações principais do Asaas
        banco_data = [
            # Primeira linha - Banco e código
            [
                f"{boleto.configuracao.codigo_banco}-X", 
                "ASAAS I.P S.A", 
                "VENCIMENTO", 
                boleto.data_vencimento.strftime("%d/%m/%Y")
            ],
            # Segunda linha - Espaço e valor
            [
                "", 
                "", 
                "VALOR DO DOCUMENTO", 
                f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ]
        ]
        
        banco_table = Table(banco_data, colWidths=[2.5*cm, 9*cm, 3.5*cm, 3*cm])
        banco_table.setStyle(TableStyle([
            # Estilo da primeira linha (cabeçalho)
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Estilo da segunda linha (valores)
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            
            # Alinhamento
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
        ]))
        
        return [titulo, Spacer(1, 5), linha, Spacer(1, 10), banco_table, Spacer(1, 20)]
    
    def _criar_dados_beneficiario(self, boleto):
        """Cria seção com dados do beneficiário"""
        styles = getSampleStyleSheet()
        
        # Título da seção
        titulo_style = ParagraphStyle(
            'TituloBeneficiario',
            fontSize=12,
            textColor=colors.darkblue,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        
        titulo = Paragraph("📋 DADOS DO BENEFICIÁRIO (ASAAS)", titulo_style)
        
        # Dados do beneficiário
        beneficiario_data = [
            ["Beneficiário:", boleto.configuracao.nome_beneficiario.upper()],
            ["CNPJ:", self._formatar_cnpj(boleto.configuracao.cnpj_beneficiario)],
            ["Endereço:", boleto.configuracao.endereco_beneficiario],
            ["Banco:", f"{boleto.configuracao.codigo_banco} - {boleto.configuracao.nome_banco}"],
            ["Agência:", boleto.configuracao.agencia],
            ["Conta:", boleto.configuracao.conta],
            ["Carteira:", boleto.configuracao.carteira],
        ]
        
        beneficiario_table = Table(beneficiario_data, colWidths=[4*cm, 14*cm])
        beneficiario_table.setStyle(TableStyle([
            # Labels (coluna 0)
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            
            # Valores (coluna 1)
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            
            # Espaçamento e bordas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return [titulo, beneficiario_table, Spacer(1, 20)]
    
    def _criar_dados_pagador(self, boleto):
        """Cria seção com dados do pagador"""
        styles = getSampleStyleSheet()
        
        # Título da seção
        titulo_style = ParagraphStyle(
            'TituloPagador',
            fontSize=12,
            textColor=colors.darkgreen,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        
        titulo = Paragraph("👤 DADOS DO PAGADOR", titulo_style)
        
        # Dados do pagador
        pagador_data = [
            ["Nome:", boleto.controle_financeiro.loja.nome.upper()],
            ["CNPJ:", self._formatar_cnpj(boleto.controle_financeiro.loja.cnpj)],
            ["Endereço:", boleto.controle_financeiro.loja.endereco],
            ["Cidade:", f"{boleto.controle_financeiro.loja.cidade} - {boleto.controle_financeiro.loja.estado}"],
            ["CEP:", boleto.controle_financeiro.loja.cep],
        ]
        
        pagador_table = Table(pagador_data, colWidths=[4*cm, 14*cm])
        pagador_table.setStyle(TableStyle([
            # Labels (coluna 0)
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkgreen),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            
            # Valores (coluna 1)
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            
            # Espaçamento e bordas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return [titulo, pagador_table, Spacer(1, 20)]
    
    def _criar_informacoes_boleto(self, boleto):
        """Cria seção com informações do boleto"""
        
        # Título da seção
        titulo_style = ParagraphStyle(
            'TituloInfo',
            fontSize=12,
            textColor=colors.darkorange,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        
        titulo = Paragraph("📄 INFORMAÇÕES DO BOLETO", titulo_style)
        
        # Calcular dias para vencimento
        dias_vencimento = (boleto.data_vencimento.date() - timezone.now().date()).days
        status_vencimento = "No prazo"
        if dias_vencimento < 0:
            status_vencimento = f"Vencido há {abs(dias_vencimento)} dias"
        elif dias_vencimento == 0:
            status_vencimento = "Vence hoje"
        elif dias_vencimento <= 3:
            status_vencimento = f"Vence em {dias_vencimento} dias"
        
        # Informações principais do boleto
        info_data = [
            ["Número do Boleto:", boleto.numero_boleto, "Data de Emissão:", boleto.data_criacao.strftime("%d/%m/%Y")],
            ["Nosso Número:", boleto.numero_boleto[-10:], "Data de Vencimento:", boleto.data_vencimento.strftime("%d/%m/%Y")],
            ["Status do Boleto:", boleto.get_status_display().upper(), "Situação:", status_vencimento],
            ["Valor do Documento:", f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "Carteira:", boleto.configuracao.carteira],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
        info_table.setStyle(TableStyle([
            # Labels (colunas 0 e 2)
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 9),
            ('FONTSIZE', (2, 0), (2, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkorange),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.darkorange),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            
            # Valores (colunas 1 e 3)
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('FONTSIZE', (3, 0), (3, -1), 9),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('TEXTCOLOR', (3, 0), (3, -1), colors.black),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            
            # Espaçamento e bordas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            
            # Destacar linha do valor
            ('BACKGROUND', (0, 3), (-1, 3), colors.lightyellow),
            ('FONTSIZE', (0, 3), (-1, 3), 10),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ]))
        
        return [titulo, info_table, Spacer(1, 20)]
    
    def _criar_codigo_barras_asaas(self, boleto):
        """Cria código de barras específico do Asaas"""
        
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
        
        # Código de barras visual para leitura com câmera
        try:
            # Preparar código de barras - usar apenas números
            barcode_value = ''.join(filter(str.isdigit, boleto.codigo_barras))
            
            # Garantir que tenha pelo menos 20 dígitos e no máximo 44
            if len(barcode_value) < 20:
                barcode_value = barcode_value.ljust(44, '0')
            elif len(barcode_value) > 44:
                barcode_value = barcode_value[:44]
            
            # Usar reportlab Code128
            from reportlab.graphics.barcode.code128 import Code128
            from reportlab.graphics.shapes import Drawing
            
            # Criar código de barras
            barcode = Code128(
                barcode_value,
                barHeight=15*mm,
                barWidth=0.4*mm,
                humanReadable=0,
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
                'TituloCodigoBarras',
                fontSize=10,
                textColor=colors.black,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=5
            )
            
            titulo = Paragraph("<b>CÓDIGO DE BARRAS PARA PAGAMENTO</b>", titulo_style)
            
            return [
                titulo,
                linha_digitavel,
                Spacer(1, 10),
                drawing,
                Spacer(1, 20)
            ]
            
        except Exception as e:
            print(f"Erro ao gerar código de barras: {e}")
            # Fallback: apenas linha digitável
            return [
                linha_digitavel,
                Spacer(1, 20)
            ]
    
    def _criar_instrucoes_asaas(self, boleto):
        """Cria instruções específicas do Asaas"""
        styles = getSampleStyleSheet()
        
        # Título da seção
        titulo_style = ParagraphStyle(
            'TituloInstrucoes',
            fontSize=12,
            textColor=colors.darkred,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        
        titulo = Paragraph("📋 INSTRUÇÕES DE PAGAMENTO - ASAAS", titulo_style)
        
        # Instruções específicas do Asaas
        instrucoes_texto = f"""
        <b>INSTRUÇÕES PARA PAGAMENTO:</b><br/><br/>
        
        1. <b>PIX:</b> Escaneie o código QR ou use a linha digitável para pagamento via PIX<br/>
        2. <b>Boleto Bancário:</b> Pague em qualquer banco, casa lotérica ou internet banking<br/>
        3. <b>Vencimento:</b> {boleto.data_vencimento.strftime("%d/%m/%Y")}<br/>
        4. <b>Valor:</b> R$ {boleto.valor:,.2f}<br/><br/>
        
        <b>IMPORTANTE:</b><br/>
        • Este boleto é válido apenas para pagamento via Asaas<br/>
        • Após o vencimento, serão cobrados juros e multa conforme legislação<br/>
        • Em caso de dúvidas, entre em contato com o suporte<br/><br/>
        
        <b>DADOS PARA PIX:</b><br/>
        • Chave PIX: {boleto.linha_digitavel}<br/>
        • Valor: R$ {boleto.valor:,.2f}<br/>
        • Vencimento: {boleto.data_vencimento.strftime("%d/%m/%Y")}
        """
        
        instrucoes_style = ParagraphStyle(
            'InstrucoesTexto',
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica',
            spaceAfter=10,
            leftIndent=20
        )
        
        instrucoes = Paragraph(instrucoes_texto, instrucoes_style)
        
        return [titulo, instrucoes, Spacer(1, 20)]
    
    def _criar_recibo_sacado(self, boleto):
        """Cria recibo do sacado (canhoto)"""
        styles = getSampleStyleSheet()
        
        # Título da seção
        titulo_style = ParagraphStyle(
            'TituloRecibo',
            fontSize=12,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        
        titulo = Paragraph("📄 RECIBO DO SACADO", titulo_style)
        
        # Linha separadora
        linha_style = ParagraphStyle(
            'LinhaRecibo',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        linha = Paragraph("─" * 100, linha_style)
        
        # Dados do recibo
        recibo_data = [
            ["Beneficiário:", boleto.configuracao.nome_beneficiario.upper()],
            ["Pagador:", boleto.controle_financeiro.loja.nome.upper()],
            ["Valor:", f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Vencimento:", boleto.data_vencimento.strftime("%d/%m/%Y")],
            ["Nosso Número:", boleto.numero_boleto],
        ]
        
        recibo_table = Table(recibo_data, colWidths=[4*cm, 14*cm])
        recibo_table.setStyle(TableStyle([
            # Labels (coluna 0)
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            
            # Valores (coluna 1)
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            
            # Espaçamento e bordas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return [titulo, linha, Spacer(1, 10), recibo_table, Spacer(1, 20)]
    
    def _criar_pix_qrcode(self, boleto):
        """Cria a seção do PIX QR Code para boletos Asaas"""
        styles = getSampleStyleSheet()
        
        titulo_style = ParagraphStyle(
            'TituloPix',
            fontSize=12,
            textColor=colors.blue,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        
        titulo = Paragraph("✨ PAGAMENTO VIA PIX", titulo_style)
        
        # Buscar dados de PIX do Asaas
        from .models import CobrancaAsaas
        cobranca_asaas = CobrancaAsaas.objects.filter(controle_financeiro=boleto.controle_financeiro).first()
        
        if not cobranca_asaas:
            return [
                titulo,
                Paragraph("<i>Informações PIX não disponíveis para este boleto.</i>", styles['Normal']),
                Spacer(1, 20)
            ]

        try:
            # Verificar se há QR Code base64
            if not cobranca_asaas.pix_qr_code:
                return [
                    titulo,
                    Paragraph("<i>QR Code PIX não disponível para este boleto.</i>", styles['Normal']),
                    Spacer(1, 20)
                ]
            
            # Decodificar a imagem base64 do QR Code
            import base64
            qr_code_data = base64.b64decode(cobranca_asaas.pix_qr_code)
            
            # Criar imagem para o PDF
            from reportlab.platypus import Image as ReportLabImage
            qr_image = ReportLabImage(BytesIO(qr_code_data), width=4*cm, height=4*cm)
            
            # Tabela para organizar QR Code e linha copiável
            pix_data = [
                [qr_image, Paragraph(f"<b>Chave PIX (Copia e Cola):</b><br/><font size=9>{cobranca_asaas.pix_copy_paste}</font>", styles['Normal'])]
            ]
            
            pix_table = Table(pix_data, colWidths=[5*cm, 12*cm])
            pix_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            return [
                titulo,
                Paragraph("Escaneie o QR Code ou use a chave Copia e Cola para pagar via PIX.", styles['Normal']),
                Spacer(1, 5),
                pix_table,
                Spacer(1, 20)
            ]
        except Exception as e:
            return [
                titulo,
                Paragraph(f"<i>Erro ao gerar QR Code PIX: {str(e)}</i>", styles['Normal']),
                Spacer(1, 20)
            ]
