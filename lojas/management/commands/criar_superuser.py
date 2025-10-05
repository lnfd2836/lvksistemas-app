"""
Comando para criar um super usuário
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario


class Command(BaseCommand):
    help = 'Cria um super usuário com perfil completo'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário')
        parser.add_argument('--email', type=str, help='Email do usuário')
        parser.add_argument('--password', type=str, help='Senha do usuário')
        parser.add_argument('--first-name', type=str, help='Primeiro nome')
        parser.add_argument('--last-name', type=str, help='Sobrenome')

    def handle(self, *args, **options):
        try:
            # Cria o usuário
            user = User.objects.create_user(
                username=options['username'],
                email=options['email'],
                password=options['password'],
                first_name=options['first_name'],
                last_name=options['last_name'],
                is_staff=True,
                is_superuser=True
            )

            # Cria o perfil
            PerfilUsuario.objects.create(
                user=user,
                is_super_admin=True,
                is_loja_admin=False
            )

            self.stdout.write(
                self.style.SUCCESS(f'Super usuário {user.username} criado com sucesso!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar super usuário: {e}')
            )



