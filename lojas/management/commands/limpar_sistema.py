"""
Comando para limpar dados antigos do sistema
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from usuarios.models import LogAcesso
from dashboard.models import Notificacao
from lojas.models import BackupLoja


class Command(BaseCommand):
    help = 'Limpa dados antigos do sistema'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=90, help='Dias para manter os dados')
        parser.add_argument('--confirmar', action='store_true', help='Confirma a limpeza')

    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(
                self.style.WARNING('Use --confirmar para executar a limpeza')
            )
            return

        try:
            dias = options['dias']
            data_limite = timezone.now() - timedelta(days=dias)
            
            # Limpa logs antigos
            logs_removidos = LogAcesso.objects.filter(
                data_acesso__lt=data_limite
            ).delete()
            
            # Limpa notificações antigas
            notificacoes_removidas = Notificacao.objects.filter(
                data_criacao__lt=data_limite,
                lida=True
            ).delete()
            
            # Limpa backups antigos (mantém apenas os últimos 30 dias)
            data_limite_backup = timezone.now() - timedelta(days=30)
            backups_removidos = BackupLoja.objects.filter(
                data_backup__lt=data_limite_backup
            ).delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'Limpeza concluída:')
            )
            self.stdout.write(f'  Logs removidos: {logs_removidos[0]}')
            self.stdout.write(f'  Notificações removidas: {notificacoes_removidas[0]}')
            self.stdout.write(f'  Backups removidos: {backups_removidos[0]}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao limpar sistema: {e}')
            )




