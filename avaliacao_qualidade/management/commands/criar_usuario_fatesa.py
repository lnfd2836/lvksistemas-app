from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avaliacao_qualidade.models import PerfilUsuario


class Command(BaseCommand):
    help = 'Cria um usuário administrador para o sistema FATESA'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário')
        parser.add_argument('--email', type=str, help='Email do usuário')
        parser.add_argument('--password', type=str, help='Senha do usuário')
        parser.add_argument('--nome', type=str, help='Nome completo')
        parser.add_argument('--tipo', type=str, choices=['diretoria', 'coordenacao', 'professor', 'secretaria'], 
                          default='diretoria', help='Tipo de perfil')

    def handle(self, *args, **options):
        username = options.get('username') or input('Nome de usuário: ')
        email = options.get('email') or input('Email: ')
        password = options.get('password') or input('Senha: ')
        nome = options.get('nome') or input('Nome completo: ')
        tipo = options.get('tipo') or 'diretoria'

        # Verificar se usuário já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} já existe!')
            )
            return

        # Criar usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nome.split()[0],
            last_name=' '.join(nome.split()[1:]) if len(nome.split()) > 1 else ''
        )

        # Criar perfil
        perfil = PerfilUsuario.objects.create(
            user=user,
            tipo_perfil=tipo,
            nome_completo=nome
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Usuário {username} criado com sucesso!\n'
                f'Tipo: {perfil.get_tipo_perfil_display()}\n'
                f'Email: {email}'
            )
        )