"""
Serviço para geração de PDFs do CRM
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
from django.utils import timezone
from io import BytesIO
import os
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """
    Serviço para geração de PDFs personalizados
    """
    
    @classmethod
    def gerar_orcamento_pdf(cls, orcamento):
        """
        Gera PDF do orçamento
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )
            
            # Cabeçalho
            story.append(Paragraph(f"ORÇAMENTO Nº {orcamento.numero}", title_style))
            story.append(Spacer(1, 20))
            
            # Dados da empresa
            empresa_data = [
                ['DADOS DA EMPRESA', ''],
                ['Nome:', orcamento.loja.nome],
                ['Email:', orcamento.loja.email or ''],
                ['Telefone:', orcamento.loja.telefone or ''],
                ['Endereço:', f"{orcamento.loja.endereco}, {orcamento.loja.cidade}/{orcamento.loja.estado}"],
            ]
            
            empresa_table = Table(empresa_data, colWidths=[2*inch, 4*inch])
            empresa_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(empresa_table)
            story.append(Spacer(1, 20))
            
            # Dados do cliente
            cliente_data = [
                ['DADOS DO CLIENTE', ''],
                ['Nome:', orcamento.lead.nome],
                ['Email:', orcamento.lead.email],
                ['Telefone:', orcamento.lead.telefone or ''],
                ['Empresa:', orcamento.lead.empresa or ''],
            ]
            
            cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
            cliente_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(cliente_table)
            story.append(Spacer(1, 30))
            
            # Itens do orçamento
            story.append(Paragraph("ITENS DO ORÇAMENTO", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Cabeçalho da tabela de itens
            itens_data = [['Item', 'Descrição', 'Qtd', 'Valor Unit.', 'Total']]
            
            # Adicionar itens
            for i, item in enumerate(orcamento.itens.all(), 1):
                itens_data.append([
                    str(i),
                    item.descricao,
                    f"{item.quantidade} {item.unidade}",
                    f"R$ {item.valor_unitario:,.2f}",
                    f"R$ {item.valor_total:,.2f}"
                ])
            
            # Totais
            itens_data.extend([
                ['', '', '', 'Subtotal:', f"R$ {orcamento.subtotal:,.2f}"],
                ['', '', '', 'Desconto:', f"R$ {orcamento.desconto:,.2f}"],
                ['', '', '', 'Impostos:', f"R$ {orcamento.impostos:,.2f}"],
                ['', '', '', 'TOTAL:', f"R$ {orcamento.total:,.2f}"],
            ])
            
            itens_table = Table(itens_data, colWidths=[0.5*inch, 3*inch, 1*inch, 1.5*inch, 1.5*inch])
            itens_table.setStyle(TableStyle([
                # Cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Itens
                ('ALIGN', (0, 1), (0, -5), 'CENTER'),  # Número do item
                ('ALIGN', (2, 1), (2, -5), 'CENTER'),  # Quantidade
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Valores
                ('FONTNAME', (0, 1), (-1, -5), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -5), 9),
                
                # Totais
                ('FONTNAME', (3, -4), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (3, -1), (-1, -1), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (3, -1), (-1, -1), colors.whitesmoke),
                
                # Bordas
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(itens_table)
            story.append(Spacer(1, 30))
            
            # Condições
            story.append(Paragraph("CONDIÇÕES COMERCIAIS", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            condicoes_text = f"""
            <b>Condições de Pagamento:</b> {orcamento.condicoes_pagamento}<br/>
            <b>Prazo de Entrega:</b> {orcamento.prazo_entrega}<br/>
            <b>Validade da Proposta:</b> {orcamento.validade_dias} dias<br/>
            <b>Data de Expiração:</b> {orcamento.data_expiracao.strftime('%d/%m/%Y') if orcamento.data_expiracao else 'N/A'}
            """
            
            story.append(Paragraph(condicoes_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Observações
            if orcamento.descricao:
                story.append(Paragraph("OBSERVAÇÕES", styles['Heading2']))
                story.append(Paragraph(orcamento.descricao, styles['Normal']))
            
            # Rodapé
            story.append(Spacer(1, 30))
            rodape = f"Orçamento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}"
            story.append(Paragraph(rodape, styles['Normal']))
            
            # Gerar PDF
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF do orçamento {orcamento.numero} gerado com sucesso")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF do orçamento {orcamento.numero}: {e}")
            return None
    
    @classmethod
    def gerar_proposta_pdf(cls, proposta):
        """
        Gera PDF da proposta comercial
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )
            
            # Título
            story.append(Paragraph(f"PROPOSTA COMERCIAL", title_style))
            story.append(Paragraph(f"{proposta.titulo}", styles['Heading2']))
            story.append(Spacer(1, 30))
            
            # Resumo Executivo
            story.append(Paragraph("RESUMO EXECUTIVO", styles['Heading2']))
            story.append(Paragraph(proposta.resumo_executivo, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Objetivos
            story.append(Paragraph("OBJETIVOS", styles['Heading2']))
            story.append(Paragraph(proposta.objetivos, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Metodologia
            if proposta.metodologia:
                story.append(Paragraph("METODOLOGIA", styles['Heading2']))
                story.append(Paragraph(proposta.metodologia, styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Cronograma
            if proposta.cronograma:
                story.append(Paragraph("CRONOGRAMA", styles['Heading2']))
                story.append(Paragraph(proposta.cronograma, styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Investimento
            story.append(Paragraph("INVESTIMENTO", styles['Heading2']))
            story.append(Paragraph(proposta.investimento, styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Valor total destacado
            valor_style = ParagraphStyle(
                'ValorTotal',
                parent=styles['Normal'],
                fontSize=18,
                textColor=colors.HexColor('#e74c3c'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            story.append(Paragraph(f"<b>VALOR TOTAL: R$ {proposta.valor_total:,.2f}</b>", valor_style))
            
            # Condições Comerciais
            story.append(Paragraph("CONDIÇÕES COMERCIAIS", styles['Heading2']))
            story.append(Paragraph(proposta.condicoes_comerciais, styles['Normal']))
            
            # Gerar PDF
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF da proposta {proposta.numero} gerado com sucesso")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF da proposta {proposta.numero}: {e}")
            return None
    
    @classmethod
    def gerar_contrato_pdf(cls, contrato):
        """
        Gera PDF do contrato
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )
            
            # Título
            story.append(Paragraph(f"CONTRATO DE PRESTAÇÃO DE SERVIÇOS", title_style))
            story.append(Paragraph(f"Nº {contrato.numero}", styles['Heading2']))
            story.append(Spacer(1, 30))
            
            # Partes
            story.append(Paragraph("DAS PARTES", styles['Heading2']))
            
            contratante_text = f"""
            <b>CONTRATANTE:</b> {contrato.lead.nome}<br/>
            <b>Email:</b> {contrato.lead.email}<br/>
            <b>Empresa:</b> {contrato.lead.empresa or 'N/A'}<br/>
            """
            
            contratada_text = f"""
            <b>CONTRATADA:</b> {contrato.loja.nome}<br/>
            <b>CNPJ:</b> {contrato.loja.cnpj or 'N/A'}<br/>
            <b>Email:</b> {contrato.loja.email or 'N/A'}<br/>
            """
            
            story.append(Paragraph(contratante_text, styles['Normal']))
            story.append(Spacer(1, 10))
            story.append(Paragraph(contratada_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Objeto
            story.append(Paragraph("DO OBJETO", styles['Heading2']))
            story.append(Paragraph(contrato.objeto, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Valor
            story.append(Paragraph("DO VALOR", styles['Heading2']))
            valor_text = f"O valor total do contrato é de <b>R$ {contrato.valor_total:,.2f}</b>."
            story.append(Paragraph(valor_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Forma de Pagamento
            story.append(Paragraph("DA FORMA DE PAGAMENTO", styles['Heading2']))
            story.append(Paragraph(contrato.forma_pagamento, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Prazo
            story.append(Paragraph("DO PRAZO", styles['Heading2']))
            prazo_text = f"""
            O presente contrato terá vigência de {contrato.data_inicio.strftime('%d/%m/%Y')} 
            até {contrato.data_fim.strftime('%d/%m/%Y')}, totalizando {contrato.prazo_meses} meses.
            """
            story.append(Paragraph(prazo_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Cláusulas
            story.append(Paragraph("DAS CLÁUSULAS GERAIS", styles['Heading2']))
            story.append(Paragraph(contrato.clausulas, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Condições Especiais
            if contrato.condicoes_especiais:
                story.append(Paragraph("DAS CONDIÇÕES ESPECIAIS", styles['Heading2']))
                story.append(Paragraph(contrato.condicoes_especiais, styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Assinaturas
            story.append(Spacer(1, 50))
            story.append(Paragraph("_" * 50, styles['Normal']))
            story.append(Paragraph("CONTRATANTE", styles['Normal']))
            story.append(Spacer(1, 30))
            story.append(Paragraph("_" * 50, styles['Normal']))
            story.append(Paragraph("CONTRATADA", styles['Normal']))
            
            # Data
            story.append(Spacer(1, 30))
            data_text = f"Data: {timezone.now().strftime('%d/%m/%Y')}"
            story.append(Paragraph(data_text, styles['Normal']))
            
            # Gerar PDF
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF do contrato {contrato.numero} gerado com sucesso")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF do contrato {contrato.numero}: {e}")
            return None
