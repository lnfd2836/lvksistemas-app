from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lojas.models import Loja


class Command(BaseCommand):
    help = 'Associa usuários à loja FATESA'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário específico')
        parser.add_argument('--todos', action='store_true', help='Associar todos os usuários com perfil FATESA')

    def handle(self, *args, **options):
        try:
            loja_fatesa = Loja.objects.get(nome="Controle de qualidade")
        except Loja.DoesNotExist:
            self.stdout.write(self.style.ERROR("Loja FATESA não encontrada!"))
            return
        
        username = options.get('username')
        todos = options.get('todos')
        
        if username:
            # Associar usuário específico
            try:
                user = User.objects.get(username=username)
                user.loja_admin = loja_fatesa
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Usuário {username} associado à loja FATESA!')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuário {username} não encontrado!')
                )
        
        elif todos:
            # Associar todos os usuários com perfil FATESA
            from avaliacao_qualidade.models import PerfilUsuario
            
            perfis = PerfilUsuario.objects.all()
            count = 0
            
            for perfil in perfis:
                user = perfil.user
                user.loja_admin = loja_fatesa
                user.save()
                count += 1
                self.stdout.write(f"✅ {user.username} associado à loja FATESA")
            
            self.stdout.write(
                self.style.SUCCESS(f'\n{count} usuários associados à loja FATESA!')
            )
        
        else:
            # Listar usuários sem loja
            users_sem_loja = User.objects.filter(loja_admin__isnull=True)
            if users_sem_loja.exists():
                self.stdout.write("Usuários sem loja associada:")
                for user in users_sem_loja:
                    self.stdout.write(f"- {user.username}")
                
                self.stdout.write("\nUse --todos para associar todos os usuários com perfil FATESA")
                self.stdout.write("Ou --username=NOME para associar um usuário específico")
            else:
                self.stdout.write("Todos os usuários já possuem loja associada.")