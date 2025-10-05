from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from usuarios.models import SessaoAtiva


class Command(BaseCommand):
    help = 'Limpa todas as sessões ativas e resolve problemas de redirect loop'

    def handle(self, *args, **options):
        # Remove todas as sessões ativas
        sessoes_removidas = SessaoAtiva.objects.all().delete()[0]
        
        # Remove todas as sessões do Django
        sessions_removidas = Session.objects.all().delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Limpeza concluída: {sessoes_removidas} sessões ativas e {sessions_removidas} sessões Django removidas'
            )
        )