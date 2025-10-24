from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avaliacao_qualidade.models import PerfilUsuario


class Command(BaseCommand):
    help = 'Verifica e lista os perfis dos usuários FATESA'

    def handle(self, *args, **options):
        self.stdout.write("=== VERIFICAÇÃO DE PERFIS FATESA ===\n")
        
        users = User.objects.all()
        self.stdout.write(f"Total de usuários no sistema: {users.count()}\n")
        
        for user in users:
            try:
                perfil = user.perfil_fatesa
                self.stdout.write(
                    f"✅ {user.username} - {perfil.get_tipo_perfil_display()} - {perfil.nome_completo}"
                )
            except PerfilUsuario.DoesNotExist:
                self.stdout.write(
                    f"❌ {user.username} - SEM PERFIL FATESA"
                )
        
        self.stdout.write(f"\n=== PERFIS FATESA EXISTENTES ===")
        perfis = PerfilUsuario.objects.all()
        self.stdout.write(f"Total de perfis: {perfis.count()}")
        
        for perfil in perfis:
            self.stdout.write(
                f"- {perfil.user.username}: {perfil.get_tipo_perfil_display()} - {perfil.nome_completo}"
            )