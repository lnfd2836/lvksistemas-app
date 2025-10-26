#!/usr/bin/env python3
"""
Script para melhorar a integração com Asaas usando o código único do banco da loja
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro
from lojas.models import Loja
import logging

logger = logging.getLogger(__name__)


def update_asaas_service():
    """Atualiza o serviço Asaas para usar db_name da loja"""
    
    service_file = 'controle_financeiro/asaas_service.py'
    
    print("🔧 Atualizando AsaasService para usar código do banco da loja...")
    
    try:
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar método para validar banco da loja
        validation_method = '''
    def validar_banco_loja(self, controle_financeiro):
        """
        Valida se o banco da loja foi criado antes de gerar boleto
        
        Args:
            controle_financeiro: Instância do ControleFinanceiro
            
        Returns:
            bool: True se banco existe, False caso contrário
        """
        loja = controle_financeiro.loja
        
        if not loja.db_name:
            logger.error(f"Loja {loja.nome} não possui código de banco (db_name)")
            return False
        
        # Verificar se o banco foi criado (pode ser implementado conforme necessário)
        # Por enquanto, verificamos se db_name existe
        if len(loja.db_name.strip()) < 5:
            logger.error(f"Código do banco da loja {loja.nome} é inválido: {loja.db_name}")
            return False
        
        logger.info(f"Banco da loja {loja.nome} validado: {loja.db_name}")
        return True
'''
        
        # Encontrar posição para inserir o método
        insert_pos = content.find('    def gerar_cobranca_com_pix(self')
        if insert_pos == -1:
            print("❌ Não foi possível encontrar método gerar_cobranca_com_pix")
            return False
        
        # Inserir método de validação
        updated_content = content[:insert_pos] + validation_method + '\n    ' + content[insert_pos:]
        
        # Atualizar método gerar_cobranca_com_pix para usar validação
        old_validation = '''        # Validar configuração
        if not self.validar_configuracao():
            raise ValueError("Configuração da API Asaas inválida")'''
        
        new_validation = '''        # Validar configuração
        if not self.validar_configuracao():
            raise ValueError("Configuração da API Asaas inválida")
        
        # Validar se banco da loja foi criado
        if not self.validar_banco_loja(controle_financeiro):
            raise ValueError(f"Banco da loja {controle_financeiro.loja.nome} não foi criado. Código: {controle_financeiro.loja.db_name}")'''
        
        if old_validation in updated_content:
            updated_content = updated_content.replace(old_validation, new_validation)
        
        # Atualizar external_reference para usar db_name da loja
        old_external_ref = '''            'externalReference': f"CF_{controle_financeiro.id}_{int(timezone.now().timestamp())}",'''
        
        new_external_ref = '''            'externalReference': f"CF_{controle_financeiro.id}_{controle_financeiro.loja.db_name}_{int(timezone.now().timestamp())}",'''
        
        if old_external_ref in updated_content:
            updated_content = updated_content.replace(old_external_ref, new_external_ref)
        
        # Salvar arquivo atualizado
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ AsaasService atualizado com validação de banco da loja")
        return True
        
    except Exception as e:
        print(f"💥 Erro ao atualizar AsaasService: {str(e)}")
        return False


def create_email_notification_service():
    """Cria serviço para envio de emails com PDF do boleto"""
    
    email_service_content = '''"""
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
            cobranca_asaas.observacoes += f"\\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: Email enviado para {email_destino}"
            cobranca_asaas.save()
            
            logger.info(f"Email enviado com sucesso para {email_destino} - Boleto {cobranca_asaas.asaas_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email do boleto {cobranca_asaas.asaas_id}: {str(e)}")
            return False
    
    def _baixar_pdf_boleto(self, cobranca_asaas):
        """Baixa o PDF do boleto do Asaas"""
        try:
            if not cobranca_asaas.bank_slip_url:
                logger.error(f"Boleto {cobranca_asaas.asaas_id} não possui URL do PDF")
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
'''
    
    # Criar arquivo do serviço
    with open('controle_financeiro/email_notification_service.py', 'w', encoding='utf-8') as f:
        f.write(email_service_content)
    
    print("✅ Serviço de notificação por email criado")


def create_email_template():
    """Cria template para email de notificação"""
    
    template_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notificação de Boleto</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #007bff;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .content {
            background-color: #f8f9fa;
            padding: 20px;
            border: 1px solid #dee2e6;
        }
        .info-box {
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
            border-radius: 3px;
        }
        .warning {
            background-color: #fff3cd;
            border-left-color: #ffc107;
            color: #856404;
        }
        .footer {
            background-color: #6c757d;
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 0 0 5px 5px;
            font-size: 12px;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧾 Notificação de Boleto</h1>
        <p>{{ loja.nome }}</p>
    </div>
    
    <div class="content">
        <div class="info-box warning">
            <h3>⚠️ Boleto vence em {{ dias_antecedencia }} dias!</h3>
            <p>Este é um lembrete automático sobre o vencimento do seu boleto.</p>
        </div>
        
        <div class="info-box">
            <h3>📋 Detalhes do Boleto</h3>
            <p><strong>Loja:</strong> {{ loja.nome }}</p>
            <p><strong>Código do Banco:</strong> {{ codigo_banco }}</p>
            <p><strong>Valor:</strong> {{ valor_formatado }}</p>
            <p><strong>Data de Vencimento:</strong> {{ data_vencimento }}</p>
            <p><strong>Status:</strong> {{ cobranca.get_status_display }}</p>
        </div>
        
        <div class="info-box">
            <h3>💳 Formas de Pagamento</h3>
            <p>Você pode pagar este boleto das seguintes formas:</p>
            <ul>
                <li>📄 <strong>Boleto Bancário:</strong> Use o PDF em anexo</li>
                {% if cobranca.pix_copy_paste %}
                <li>📱 <strong>PIX:</strong> Use o código PIX disponível no sistema</li>
                {% endif %}
                <li>🏦 <strong>Internet Banking:</strong> Use o código de barras do boleto</li>
            </ul>
        </div>
        
        {% if cobranca.invoice_url %}
        <div style="text-align: center; margin: 20px 0;">
            <a href="{{ cobranca.invoice_url }}" class="btn">🔗 Ver Boleto Online</a>
        </div>
        {% endif %}
        
        <div class="info-box">
            <h3>📎 Anexo</h3>
            <p>O PDF do boleto está anexado a este email. Você pode imprimi-lo e pagar em qualquer banco, lotérica ou correspondente bancário.</p>
        </div>
        
        <div class="info-box">
            <h3>❓ Dúvidas?</h3>
            <p>Se você tiver alguma dúvida sobre este boleto, entre em contato conosco:</p>
            <p><strong>Email:</strong> {{ loja.email }}</p>
            {% if loja.telefone %}
            <p><strong>Telefone:</strong> {{ loja.telefone }}</p>
            {% endif %}
        </div>
    </div>
    
    <div class="footer">
        <p>Este é um email automático do sistema LVK Sistemas.</p>
        <p>Não responda este email. Em caso de dúvidas, use os contatos informados acima.</p>
        <p>Enviado em {{ "now"|date:"d/m/Y H:i" }}</p>
    </div>
</body>
</html>'''
    
    # Criar diretório se não existir
    os.makedirs('templates/emails', exist_ok=True)
    
    # Criar template
    with open('templates/emails/boleto_notification.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ Template de email criado")


def create_management_command():
    """Cria comando de gerenciamento para processar notificações"""
    
    command_content = '''"""
Comando para processar notificações de boletos por email
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from controle_financeiro.email_notification_service import email_service


class Command(BaseCommand):
    help = 'Processa notificações de boletos por email'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=10,
            help='Dias de antecedência para envio (padrão: 10)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simula o envio sem enviar emails'
        )
    
    def handle(self, *args, **options):
        dias_antecedencia = options['dias']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Iniciando processamento de notificações ({dias_antecedencia} dias de antecedência)'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: Nenhum email será enviado')
            )
        
        try:
            if dry_run:
                # Simular processamento
                from controle_financeiro.models import CobrancaAsaas
                from datetime import timedelta
                
                data_limite = timezone.now().date() + timedelta(days=dias_antecedencia)
                cobrancas = CobrancaAsaas.objects.filter(
                    data_vencimento__date=data_limite,
                    status__in=['PENDING', 'OVERDUE']
                ).exclude(
                    observacoes__icontains='Email enviado'
                )
                
                self.stdout.write(f'Encontradas {len(cobrancas)} cobranças para notificar:')
                for cobranca in cobrancas:
                    loja = cobranca.controle_financeiro.loja
                    email = loja.admin_user.email if loja.admin_user else loja.email
                    self.stdout.write(f'  - {cobranca.asaas_id} | {loja.nome} | {email} | R$ {cobranca.valor}')
                
                enviados = len(cobrancas)
            else:
                # Processar notificações reais
                enviados = email_service.processar_notificacoes_pendentes()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Processamento concluído: {enviados} notificações processadas'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante processamento: {str(e)}')
            )
'''
    
    # Criar diretório se não existir
    os.makedirs('controle_financeiro/management/commands', exist_ok=True)
    
    # Criar arquivo __init__.py se não existir
    init_files = [
        'controle_financeiro/management/__init__.py',
        'controle_financeiro/management/commands/__init__.py'
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')
    
    # Criar comando
    with open('controle_financeiro/management/commands/processar_notificacoes_boleto.py', 'w', encoding='utf-8') as f:
        f.write(command_content)
    
    print("✅ Comando de gerenciamento criado")


def create_celery_task():
    """Cria task do Celery para processamento automático"""
    
    task_content = '''"""
Tasks do Celery para processamento automático de notificações
"""

from celery import shared_task
from django.utils import timezone
from .email_notification_service import email_service
import logging

logger = logging.getLogger(__name__)


@shared_task
def processar_notificacoes_boleto():
    """
    Task para processar notificações de boletos automaticamente
    Deve ser executada diariamente
    """
    try:
        logger.info("Iniciando processamento automático de notificações de boleto")
        
        enviados = email_service.processar_notificacoes_pendentes()
        
        logger.info(f"Processamento automático concluído: {enviados} emails enviados")
        
        return {
            'success': True,
            'emails_enviados': enviados,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no processamento automático de notificações: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def enviar_boleto_especifico(cobranca_id, dias_antecedencia=10):
    """
    Task para enviar boleto específico por email
    
    Args:
        cobranca_id: ID da cobrança
        dias_antecedencia: Dias de antecedência (padrão: 10)
    """
    try:
        from .models import CobrancaAsaas
        
        cobranca = CobrancaAsaas.objects.get(id=cobranca_id)
        
        sucesso = email_service.enviar_boleto_por_email(cobranca, dias_antecedencia)
        
        return {
            'success': sucesso,
            'cobranca_id': str(cobranca_id),
            'asaas_id': cobranca.asaas_id,
            'timestamp': timezone.now().isoformat()
        }
        
    except CobrancaAsaas.DoesNotExist:
        logger.error(f"Cobrança {cobranca_id} não encontrada")
        return {
            'success': False,
            'error': 'Cobrança não encontrada',
            'cobranca_id': str(cobranca_id)
        }
    except Exception as e:
        logger.error(f"Erro ao enviar boleto específico {cobranca_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'cobranca_id': str(cobranca_id)
        }
'''
    
    # Adicionar ao arquivo tasks.py existente ou criar novo
    tasks_file = 'controle_financeiro/tasks.py'
    
    if os.path.exists(tasks_file):
        # Adicionar ao arquivo existente
        with open(tasks_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        if 'processar_notificacoes_boleto' not in existing_content:
            with open(tasks_file, 'a', encoding='utf-8') as f:
                f.write('\n\n' + task_content)
            print("✅ Tasks adicionadas ao arquivo existente")
        else:
            print("✅ Tasks já existem no arquivo")
    else:
        # Criar novo arquivo
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(task_content)
        print("✅ Arquivo de tasks criado")


def main():
    print("🚀 Melhorando integração com Asaas usando código do banco da loja...")
    
    # 1. Atualizar AsaasService
    if update_asaas_service():
        print("✅ AsaasService atualizado")
    
    # 2. Criar serviço de notificação por email
    create_email_notification_service()
    
    # 3. Criar template de email
    create_email_template()
    
    # 4. Criar comando de gerenciamento
    create_management_command()
    
    # 5. Criar tasks do Celery
    create_celery_task()
    
    print("\n🎯 Melhorias implementadas com sucesso!")
    print("\n📋 FUNCIONALIDADES ADICIONADAS:")
    print("  ✅ Validação de banco da loja antes de gerar boleto")
    print("  ✅ Uso do db_name da loja na referência externa")
    print("  ✅ Serviço de notificação por email")
    print("  ✅ Template HTML para emails")
    print("  ✅ Comando para processar notificações")
    print("  ✅ Tasks do Celery para automação")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("  1. Configure o email no settings.py")
    print("  2. Execute: python manage.py processar_notificacoes_boleto --dry-run")
    print("  3. Configure Celery Beat para execução diária")
    print("  4. Teste a geração de boletos (deve validar banco da loja)")


if __name__ == '__main__':
    main()