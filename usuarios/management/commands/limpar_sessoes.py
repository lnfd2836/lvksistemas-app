from django.core.management.base import BaseCommand
from usuarios.models import SessaoAtiva


class Command(BaseCommand):
    help = 'Limpa sessões expiradas e inválidas'

    def handle(self, *args, **options):
        """Executa a limpeza de sessões"""
        try:
            # Limpa sessões expiradas
            SessaoAtiva.limpar_sessoes_expiradas()
            
            # Conta quantas sessões foram limpas
            sessoes_limpas = SessaoAtiva.objects.filter(ativa=False).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Limpeza concluída! {sessoes_limpas} sessões foram marcadas como inativas.'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao limpar sessões: {str(e)}')
            )
