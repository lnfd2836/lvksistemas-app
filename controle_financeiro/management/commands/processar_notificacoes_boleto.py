"""
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
