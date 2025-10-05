"""
Comando para criar uma nova loja via linha de comando
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from lojas.models import Loja


class Command(BaseCommand):
    help = 'Cria uma nova loja no sistema'

    def add_arguments(self, parser):
        parser.add_argument('--nome', type=str, help='Nome da loja')
        parser.add_argument('--cnpj', type=str, help='CNPJ da loja')
        parser.add_argument('--email', type=str, help='Email da loja')
        parser.add_argument('--telefone', type=str, help='Telefone da loja')
        parser.add_argument('--endereco', type=str, help='Endereço da loja')
        parser.add_argument('--cidade', type=str, help='Cidade da loja')
        parser.add_argument('--estado', type=str, help='Estado da loja')
        parser.add_argument('--cep', type=str, help='CEP da loja')

    def handle(self, *args, **options):
        try:
            # Cria o usuário administrador
            admin_user = User.objects.create_user(
                username=options['email'],
                email=options['email'],
                first_name=options['nome'].split()[0],
                last_name=' '.join(options['nome'].split()[1:]) if len(options['nome'].split()) > 1 else '',
                is_staff=True,
            )

            # Cria a loja
            loja = Loja.objects.create(
                nome=options['nome'],
                cnpj=options['cnpj'],
                email=options['email'],
                telefone=options['telefone'],
                endereco=options['endereco'],
                cidade=options['cidade'],
                estado=options['estado'],
                cep=options['cep'],
                admin_user=admin_user
            )
            
            # Define a senha do usuário administrador
            admin_user.set_password(loja.senha_provisoria)
            admin_user.save()

            # Loja criada com sucesso
            self.stdout.write(
                self.style.SUCCESS(f'Loja {loja.nome} criada com sucesso!')
            )
            self.stdout.write(f'Senha provisória: {loja.senha_provisoria}')

        except Exception as e:
            raise CommandError(f'Erro ao criar loja: {e}')
