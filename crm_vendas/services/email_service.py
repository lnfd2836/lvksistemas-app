"""
Serviço para envio de emails do CRM
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import logging
import uuid
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Serviço para envio de emails com templates personalizados
    """
    
    @classmethod
    def enviar_orcamento(cls, orcamento, template_personalizado=None):
        """
        Envia orçamento por email
        """
        try:
            # Preparar contexto
            context = {
                'orcamento': orcamento,
                'lead': orcamento.lead,
                'loja': orcamento.loja,
                'itens': orcamento.itens.all(),
                'data_envio': timezone.now(),
                'link_visualizacao': cls._gerar_link_visualizacao(orcamento),
                'link_aprovacao': cls._gerar_link_aprovacao(orcamento),
            }
            
            # Template do email
            template = template_personalizado or 'crm_vendas/emails/orcamento.html'
            
            # Renderizar email
            html_content = render_to_string(template, context)
            text_content = render_to_string('crm_vendas/emails/orcamento.txt', context)
            
            # Assunto personalizado
            assunto = orcamento.email_assunto or f"Orçamento {orcamento.numero} - {orcamento.loja.nome}"
            
            # Criar email
            email = EmailMultiAlternatives(
                subject=assunto,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[orcamento.lead.email],
                reply_to=[orcamento.loja.email] if orcamento.loja.email else None
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Anexar PDF do orçamento
            pdf_content = cls._gerar_pdf_orcamento(orcamento)
            if pdf_content:
                email.attach(f"Orcamento_{orcamento.numero}.pdf", pdf_content, "application/pdf")
            
            # Enviar
            email.send()
            
            # Registrar envio
            cls._registrar_envio_email(orcamento, assunto, html_content)
            
            # Atualizar status
            orcamento.status = 'enviado'
            orcamento.data_envio = timezone.now()
            orcamento.email_enviado = True
            orcamento.save()
            
            logger.info(f"Orçamento {orcamento.numero} enviado para {orcamento.lead.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar orçamento {orcamento.numero}: {e}")
            return False
    
    @classmethod
    def enviar_proposta(cls, proposta, template_personalizado=None):
        """
        Envia proposta comercial por email
        """
        try:
            context = {
                'proposta': proposta,
                'lead': proposta.lead,
                'loja': proposta.loja,
                'data_envio': timezone.now(),
                'link_visualizacao': cls._gerar_link_visualizacao_proposta(proposta),
            }
            
            template = template_personalizado or 'crm_vendas/emails/proposta.html'
            html_content = render_to_string(template, context)
            text_content = render_to_string('crm_vendas/emails/proposta.txt', context)
            
            assunto = f"Proposta Comercial - {proposta.titulo}"
            
            email = EmailMultiAlternatives(
                subject=assunto,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[proposta.lead.email],
                reply_to=[proposta.loja.email] if proposta.loja.email else None
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Anexar PDF da proposta
            pdf_content = cls._gerar_pdf_proposta(proposta)
            if pdf_content:
                email.attach(f"Proposta_{proposta.numero}.pdf", pdf_content, "application/pdf")
            
            email.send()
            
            # Atualizar status
            proposta.status = 'enviada'
            proposta.data_envio = timezone.now()
            proposta.save()
            
            logger.info(f"Proposta {proposta.numero} enviada para {proposta.lead.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar proposta {proposta.numero}: {e}")
            return False
    
    @classmethod
    def enviar_contrato(cls, contrato, template_personalizado=None):
        """
        Envia contrato por email
        """
        try:
            context = {
                'contrato': contrato,
                'lead': contrato.lead,
                'loja': contrato.loja,
                'data_envio': timezone.now(),
                'link_assinatura': cls._gerar_link_assinatura(contrato),
            }
            
            template = template_personalizado or 'crm_vendas/emails/contrato.html'
            html_content = render_to_string(template, context)
            text_content = render_to_string('crm_vendas/emails/contrato.txt', context)
            
            assunto = f"Contrato para Assinatura - {contrato.titulo}"
            
            email = EmailMultiAlternatives(
                subject=assunto,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contrato.lead.email],
                reply_to=[contrato.loja.email] if contrato.loja.email else None
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Anexar PDF do contrato
            pdf_content = cls._gerar_pdf_contrato(contrato)
            if pdf_content:
                email.attach(f"Contrato_{contrato.numero}.pdf", pdf_content, "application/pdf")
            
            email.send()
            
            # Atualizar status
            contrato.status = 'enviado'
            contrato.save()
            
            logger.info(f"Contrato {contrato.numero} enviado para {contrato.lead.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar contrato {contrato.numero}: {e}")
            return False
    
    @classmethod
    def _gerar_link_visualizacao(cls, orcamento):
        """Gera link para visualização do orçamento"""
        site_url = getattr(settings, 'SITE_URL', 'https://lvksistemas-app-4f6fa281e217.herokuapp.com')
        return f"{site_url}/crm/orcamento/{orcamento.id}/visualizar/"
    
    @classmethod
    def _gerar_link_aprovacao(cls, orcamento):
        """Gera link para aprovação do orçamento"""
        site_url = getattr(settings, 'SITE_URL', 'https://lvksistemas-app-4f6fa281e217.herokuapp.com')
        return f"{site_url}/crm/orcamento/{orcamento.id}/aprovar/"
    
    @classmethod
    def _gerar_link_visualizacao_proposta(cls, proposta):
        """Gera link para visualização da proposta"""
        site_url = getattr(settings, 'SITE_URL', 'https://lvksistemas-app-4f6fa281e217.herokuapp.com')
        return f"{site_url}/crm/proposta/{proposta.id}/visualizar/"
    
    @classmethod
    def _gerar_link_assinatura(cls, contrato):
        """Gera link para assinatura do contrato"""
        site_url = getattr(settings, 'SITE_URL', 'https://lvksistemas-app-4f6fa281e217.herokuapp.com')
        return f"{site_url}/crm/contrato/{contrato.id}/assinar/"
    
    @classmethod
    def enviar_solicitacao_assinatura(cls, assinatura_digital):
        """
        Envia email com solicitação de assinatura digital
        """
        try:
            # Verificar configurações de email
            if not settings.DEFAULT_FROM_EMAIL:
                logger.error("DEFAULT_FROM_EMAIL não configurado")
                return False
            
            # Determinar documento e tipo
            documento = None
            tipo_doc = assinatura_digital.tipo_documento
            
            if tipo_doc == 'orcamento':
                documento = assinatura_digital.orcamento
                titulo_doc = f"Orçamento {documento.numero}"
            elif tipo_doc == 'proposta':
                documento = assinatura_digital.proposta
                titulo_doc = f"Proposta {documento.numero}"
            elif tipo_doc == 'contrato':
                documento = assinatura_digital.contrato
                titulo_doc = f"Contrato {documento.numero}"
            else:
                logger.error(f"Tipo de documento inválido: {tipo_doc}")
                return False
            
            # Gerar link de assinatura
            site_url = getattr(settings, 'SITE_URL', 'https://lvksistemas-app-4f6fa281e217.herokuapp.com')
            link_assinatura = f"{site_url}/crm/assinar/{assinatura_digital.token_acesso}/"
            
            # Preparar contexto
            context = {
                'assinatura': assinatura_digital,
                'documento': documento,
                'lead': assinatura_digital.lead,
                'loja': documento.loja,
                'titulo_documento': titulo_doc,
                'tipo_documento': tipo_doc,
                'tipo_signatario': assinatura_digital.tipo_signatario,
                'link_assinatura': link_assinatura,
                'data_expiracao': assinatura_digital.data_expiracao,
                'data_envio': timezone.now(),
            }
            
            # Renderizar email
            html_content = render_to_string('crm_vendas/emails/assinatura_digital.html', context)
            text_content = render_to_string('crm_vendas/emails/assinatura_digital.txt', context)
            
            # Assunto
            if assinatura_digital.tipo_signatario == 'empresa':
                assunto = f"Assinatura da Empresa Solicitada - {titulo_doc}"
            else:
                assunto = f"Assinatura Digital Solicitada - {titulo_doc}"
            
            # Criar email
            email = EmailMultiAlternatives(
                subject=assunto,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[assinatura_digital.email_signatario],
                reply_to=[documento.loja.email] if documento.loja.email else None
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Anexar PDF do documento
            pdf_content = None
            if tipo_doc == 'orcamento':
                pdf_content = cls._gerar_pdf_orcamento(documento)
                filename = f"Orcamento_{documento.numero}.pdf"
            elif tipo_doc == 'proposta':
                pdf_content = cls._gerar_pdf_proposta(documento)
                filename = f"Proposta_{documento.numero}.pdf"
            elif tipo_doc == 'contrato':
                pdf_content = cls._gerar_pdf_contrato(documento)
                filename = f"Contrato_{documento.numero}.pdf"
            
            if pdf_content:
                email.attach(filename, pdf_content, "application/pdf")
            
            # Enviar
            email.send()
            
            # Atualizar status da assinatura
            assinatura_digital.status = 'enviado'
            assinatura_digital.data_envio = timezone.now()
            assinatura_digital.save()
            
            # Registrar no histórico do lead
            from ..models import HistoricoContato
            HistoricoContato.objects.create(
                lead=assinatura_digital.lead,
                tipo='email',
                assunto=f'Solicitação de Assinatura Digital - {titulo_doc}',
                descricao=f'Email enviado para {assinatura_digital.email_signatario} solicitando assinatura digital do {titulo_doc}',
                resultado='Email de assinatura enviado com sucesso',
                data_contato=timezone.now()
            )
            
            logger.info(f"Email de assinatura enviado para {assinatura_digital.email_signatario} - {titulo_doc}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de assinatura: {e}")
            return False
    
    @classmethod
    def _registrar_envio_email(cls, documento, assunto, conteudo):
        """Registra o envio do email no log"""
        from ..models import EmailLog
        
        # Determinar tipo de documento
        if hasattr(documento, 'itens'):  # Orçamento
            EmailLog.objects.create(
                lead=documento.lead,
                orcamento=documento,
                destinatario=documento.lead.email,
                assunto=assunto,
                corpo=conteudo,
                status='enviado'
            )
        elif hasattr(documento, 'resumo_executivo'):  # Proposta
            EmailLog.objects.create(
                lead=documento.lead,
                proposta=documento,
                destinatario=documento.lead.email,
                assunto=assunto,
                corpo=conteudo,
                status='enviado'
            )
        elif hasattr(documento, 'clausulas'):  # Contrato
            EmailLog.objects.create(
                lead=documento.lead,
                contrato=documento,
                destinatario=documento.lead.email,
                assunto=assunto,
                corpo=conteudo,
                status='enviado'
            )
    
    @classmethod
    def _gerar_pdf_orcamento(cls, orcamento):
        """Gera PDF do orçamento"""
        from .pdf_service import PDFService
        return PDFService.gerar_orcamento_pdf(orcamento)
    
    @classmethod
    def _gerar_pdf_proposta(cls, proposta):
        """Gera PDF da proposta"""
        from .pdf_service import PDFService
        return PDFService.gerar_proposta_pdf(proposta)
    
    @classmethod
    def _gerar_pdf_contrato(cls, contrato):
        """Gera PDF do contrato"""
        from .pdf_service import PDFService
        return PDFService.gerar_contrato_pdf(contrato)


class EmailTrackingService:
    """
    Serviço para rastreamento de emails
    """
    
    @classmethod
    def registrar_abertura(cls, token_rastreamento, ip_address=None):
        """Registra abertura do email"""
        from ..models import EmailLog
        
        try:
            email_log = EmailLog.objects.get(token_rastreamento=token_rastreamento)
            if not email_log.data_abertura:  # Primeira abertura
                email_log.data_abertura = timezone.now()
                email_log.ip_abertura = ip_address
                email_log.status = 'aberto'
                email_log.save()
                
                # Atualizar status do documento relacionado
                if email_log.orcamento:
                    email_log.orcamento.status = 'visualizado'
                    email_log.orcamento.data_visualizacao = timezone.now()
                    email_log.orcamento.save()
                
                logger.info(f"Email {email_log.id} aberto por {email_log.destinatario}")
            
            return True
            
        except EmailLog.DoesNotExist:
            logger.warning(f"Token de rastreamento não encontrado: {token_rastreamento}")
            return False
    
    @classmethod
    def registrar_clique(cls, token_rastreamento, ip_address=None):
        """Registra clique no email"""
        from ..models import EmailLog
        
        try:
            email_log = EmailLog.objects.get(token_rastreamento=token_rastreamento)
            email_log.data_clique = timezone.now()
            email_log.status = 'clicado'
            email_log.save()
            
            logger.info(f"Link clicado no email {email_log.id}")
            return True
            
        except EmailLog.DoesNotExist:
            return False
