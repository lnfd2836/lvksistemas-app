from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lojas.models import Loja


class Command(BaseCommand):
    help = 'Verifica o acesso dos usuários à loja FATESA'

    def handle(self, *args, **options):
        self.stdout.write("=== VERIFICAÇÃO DE ACESSO À LOJA FATESA ===\n")
        
        try:
            loja_fatesa = Loja.objects.get(nome="Controle de qualidade")
            self.stdout.write(f"✅ Loja FATESA encontrada: {loja_fatesa.nome} (ID: {loja_fatesa.id})\n")
        except Loja.DoesNotExist:
            self.stdout.write("❌ Loja FATESA não encontrada!\n")
            return
        
        users = User.objects.all()
        self.stdout.write(f"Total de usuários: {users.count()}\n")
        
        for user in users:
            try:
                loja_admin = user.loja_admin
                if loja_admin == loja_fatesa:
                    self.stdout.write(f"✅ {user.username} - TEM ACESSO à loja FATESA")
                else:
                    self.stdout.write(f"❌ {user.username} - Acesso à loja: {loja_admin.nome}")
            except:
                self.stdout.write(f"❌ {user.username} - SEM LOJA ASSOCIADA")
        
        self.stdout.write(f"\n=== USUÁRIOS DA LOJA FATESA ===")
        usuarios_fatesa = User.objects.filter(loja_admin=loja_fatesa)
        self.stdout.write(f"Total: {usuarios_fatesa.count()}")
        
        for user in usuarios_fatesa:
            perfil = "SEM PERFIL FATESA"
            try:
                perfil = user.perfil_fatesa.get_tipo_perfil_display()
            except:
                pass
            self.stdout.write(f"- {user.username}: {perfil}")