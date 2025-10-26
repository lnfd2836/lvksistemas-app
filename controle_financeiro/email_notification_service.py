"""
Serviço para envio de notificações por email com PDF de boletos
"""

import os
import logging
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import CobrancaAsaas
from .asaas_service import AsaasService
import requests

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Serviço para envio de notificações por email"""
    
    def __init__(self):
        self.asaas_service = AsaasService()
    
    def enviar_boleto_por_email(self, cobranca_asaas, dias_antecedencia=10):
        """
        Envia boleto por email para o admin da loja
        
        Args:
            cobranca_asaas: Instância da CobrancaAsaas
            dias_antecedencia: Dias de antecedência para envio
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            loja = cobranca_asaas.controle_financeiro.loja
            
            # Verificar se deve enviar (10 dias antes do vencimento)
            dias_para_vencimento = (cobranca_asaas.data_vencimento.date() - timezone.now().date()).days
            
            if dias_para_vencimento != dias_antecedencia:
                logger.info(f"Boleto {cobranca_asaas.asaas_id} não está no prazo para envio ({dias_para_vencimento} dias)")
                return False
            
            # Buscar email do admin da loja
            email_destino = None
            if loja.admin_user and loja.admin_user.email:
                email_destino = loja.admin_user.email
            elif loja.email:
                email_destino = loja.email
            else:
                logger.error(f"Loja {loja.nome} não possui email configurado")
                return False
            
            # Baixar PDF do boleto
            pdf_content = self._baixar_pdf_boleto(cobranca_asaas)
            if not pdf_content:
                logger.error(f"Não foi possível baixar PDF do boleto {cobranca_asaas.asaas_id}")
                return False
            
            # Preparar email
            assunto = f"Boleto - {loja.nome} - Vencimento em {dias_antecedencia} dias"
            
            contexto = {
                'loja': loja,
                'cobranca': cobranca_asaas,
                'dias_antecedencia': dias_antecedencia,
                'valor_formatado': f"R$ {cobranca_asaas.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'data_vencimento': cobranca_asaas.data_vencimento.strftime('%d/%m/%Y'),
                'codigo_banco': loja.db_name
            }
            
            # Renderizar template do email
            corpo_email = render_to_string('emails/boleto_notification.html', contexto)
            
            # Criar email
            email = EmailMessage(
                subject=assunto,
                body=corpo_email,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_destino],
            )
            email.content_subtype = 'html'
            
            # Anexar PDF
            nome_arquivo = f"boleto_{loja.db_name}_{cobranca_asaas.asaas_id}.pdf"
            email.attach(nome_arquivo, pdf_content, 'application/pdf')
            
            # Enviar email
            email.send()
            
            # Registrar envio
            cobranca_asaas.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: Email enviado para {email_destino}"
            cobranca_asaas.save()
            
            logger.info(f"Email enviado com sucesso para {email_destino} - Boleto {cobranca_asaas.asaas_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email do boleto {cobranca_asaas.asaas_id}: {str(e)}")
            return False
    
    def _baixar_pdf_boleto(self, cobranca_asaas):
        """Baixa o PDF do boleto do Asaas"""
        try:
            # Para teste: se não tem URL ou é uma cobrança de teste, usar PDF de teste
            if not cobranca_asaas.bank_slip_url or cobranca_asaas.asaas_id.startswith('test_'):
                logger.info(f"Usando PDF de teste para cobrança {cobranca_asaas.asaas_id}")
                try:
                    with open('test_boleto.pdf', 'rb') as f:
                        return f.read()
                except FileNotFoundError:
                    logger.error("Arquivo test_boleto.pdf não encontrado")
                    return None
            
            response = requests.get(
                cobranca_asaas.bank_slip_url,
                headers=self.asaas_service.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Erro ao baixar PDF: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao baixar PDF do boleto: {str(e)}")
            return None
    
    def processar_notificacoes_pendentes(self):
        """Processa todas as notificações pendentes"""
        try:
            # Buscar cobranças que vencem em 10 dias
            data_limite = timezone.now().date() + timedelta(days=10)
            
            cobrancas_para_notificar = CobrancaAsaas.objects.filter(
                data_vencimento__date=data_limite,
                status__in=['PENDING', 'OVERDUE']
            ).exclude(
                observacoes__icontains='Email enviado'
            )
            
            logger.info(f"Processando {len(cobrancas_para_notificar)} notificações de boleto")
            
            enviados = 0
            for cobranca in cobrancas_para_notificar:
                if self.enviar_boleto_por_email(cobranca):
                    enviados += 1
            
            logger.info(f"Processamento concluído: {enviados} emails enviados")
            return enviados
            
        except Exception as e:
            logger.error(f"Erro ao processar notificações: {str(e)}")
            return 0


# Instância global do serviço
email_service = EmailNotificationService()
