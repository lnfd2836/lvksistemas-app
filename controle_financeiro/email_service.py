"""
Serviço para envio de emails de boletos
"""

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class BoletoEmailService:
    """Serviço para envio de boletos por email"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@sistema.com')
    
    def enviar_boleto_por_email(self, boleto, incluir_pdf=True):
        """
        Envia boleto por email para o administrador da loja
        
        Args:
            boleto: Instância do BoletoGerado
            incluir_pdf: Se deve anexar o PDF do boleto
            
        Returns:
            bool: True se enviado com sucesso
        """
        
        try:
            loja = boleto.controle_financeiro.loja
            admin_email = loja.admin_user.email
            
            if not admin_email:
                logger.warning(f'Loja {loja.nome} não possui email do administrador configurado')
                return False
            
            # Preparar contexto para o template
            context = {
                'boleto': boleto,
                'loja': loja,
                'beneficiario': boleto.configuracao.nome_beneficiario,
                'valor_formatado': f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'vencimento_formatado': boleto.data_vencimento.strftime("%d/%m/%Y"),
                'dias_para_vencimento': boleto.dias_para_vencimento,
            }
            
            # Renderizar template do email
            subject = f'Boleto de Cobrança - {loja.nome} - Vencimento {context["vencimento_formatado"]}'
            
            html_content = render_to_string('controle_financeiro/emails/boleto_email.html', context)
            text_content = render_to_string('controle_financeiro/emails/boleto_email.txt', context)
            
            # Criar email
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[admin_email],
                reply_to=[self.from_email]
            )
            
            # Adicionar versão HTML
            email.attach_alternative(html_content, "text/html")
            
            # Anexar PDF se solicitado
            if incluir_pdf:
                try:
                    # Usar layout específico para boletos do Asaas
                    if boleto.configuracao.codigo_banco == "461":
                        from .pdf_service import BoletoPDFService
                        
                        pdf_service = BoletoPDFService()
                        pdf_response = pdf_service.gerar_pdf_boleto_asaas(boleto)
                    else:
                        from .pdf_service import BoletoPDFService
                        
                        pdf_service = BoletoPDFService()
                        pdf_response = pdf_service.gerar_pdf_boleto(boleto)
                    
                    # Gerar PDF em memória
                    buffer = BytesIO()
                    
                    # Extrair conteúdo do PDF da resposta HTTP
                    if hasattr(pdf_response, 'content'):
                        pdf_content = pdf_response.content
                    else:
                        # Se for um HttpResponse, precisamos ler o conteúdo
                        pdf_content = b''.join(pdf_response.streaming_content) if hasattr(pdf_response, 'streaming_content') else pdf_response.getvalue()
                    
                    # Anexar PDF
                    email.attach(
                        f'boleto_{boleto.numero_boleto}.pdf',
                        pdf_content,
                        'application/pdf'
                    )
                    
                    logger.info(f'PDF anexado ao email do boleto {boleto.numero_boleto}')
                    
                except Exception as e:
                    logger.error(f'Erro ao anexar PDF do boleto {boleto.numero_boleto}: {str(e)}')
                    # Continua enviando o email mesmo sem o PDF
            
            # Enviar email
            email.send()
            
            logger.info(f'Email do boleto {boleto.numero_boleto} enviado para {admin_email}')
            
            # Registrar envio no boleto
            if not boleto.observacoes:
                boleto.observacoes = ""
            
            boleto.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: Email enviado para {admin_email}"
            boleto.save()
            
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar email do boleto {boleto.numero_boleto}: {str(e)}')
            return False
    
    def enviar_lembrete_vencimento(self, boleto, dias_restantes):
        """
        Envia lembrete de vencimento próximo
        
        Args:
            boleto: Instância do BoletoGerado
            dias_restantes: Quantos dias restam para o vencimento
            
        Returns:
            bool: True se enviado com sucesso
        """
        
        try:
            loja = boleto.controle_financeiro.loja
            admin_email = loja.admin_user.email
            
            if not admin_email:
                return False
            
            # Preparar contexto
            context = {
                'boleto': boleto,
                'loja': loja,
                'dias_restantes': dias_restantes,
                'valor_formatado': f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'vencimento_formatado': boleto.data_vencimento.strftime("%d/%m/%Y"),
                'urgente': dias_restantes <= 3,
            }
            
            # Definir assunto baseado na urgência
            if dias_restantes <= 1:
                subject = f'🚨 URGENTE - Boleto vence hoje - {loja.nome}'
            elif dias_restantes <= 3:
                subject = f'⚠️ Boleto vence em {dias_restantes} dias - {loja.nome}'
            else:
                subject = f'📅 Lembrete: Boleto vence em {dias_restantes} dias - {loja.nome}'
            
            # Renderizar templates
            html_content = render_to_string('controle_financeiro/emails/lembrete_vencimento.html', context)
            text_content = render_to_string('controle_financeiro/emails/lembrete_vencimento.txt', context)
            
            # Criar e enviar email
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[admin_email],
                reply_to=[self.from_email]
            )
            
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f'Lembrete de vencimento enviado para {admin_email} - Boleto {boleto.numero_boleto}')
            
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar lembrete de vencimento: {str(e)}')
            return False
    
    def enviar_confirmacao_pagamento(self, boleto):
        """
        Envia confirmação de pagamento recebido
        
        Args:
            boleto: Instância do BoletoGerado (já pago)
            
        Returns:
            bool: True se enviado com sucesso
        """
        
        try:
            loja = boleto.controle_financeiro.loja
            admin_email = loja.admin_user.email
            
            if not admin_email:
                return False
            
            context = {
                'boleto': boleto,
                'loja': loja,
                'valor_formatado': f"R$ {boleto.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'data_pagamento': boleto.data_pagamento.strftime("%d/%m/%Y %H:%M") if boleto.data_pagamento else "N/A",
            }
            
            subject = f'✅ Pagamento Confirmado - {loja.nome} - {context["valor_formatado"]}'
            
            html_content = render_to_string('controle_financeiro/emails/confirmacao_pagamento.html', context)
            text_content = render_to_string('controle_financeiro/emails/confirmacao_pagamento.txt', context)
            
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[admin_email],
                reply_to=[self.from_email]
            )
            
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f'Confirmação de pagamento enviada para {admin_email} - Boleto {boleto.numero_boleto}')
            
            return True
            
        except Exception as e:
            logger.error(f'Erro ao enviar confirmação de pagamento: {str(e)}')
            return False