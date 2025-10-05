from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from modulos.management.commands.criar_tipos_loja import Command as CriarTiposCommand
from controle_financeiro.management.commands.criar_planos_financeiros import Command as CriarPlanosCommand
from controle_financeiro.management.commands.criar_configuracao_boleto_padrao import Command as CriarBoletoCommand


class Command(BaseCommand):
    help = 'Configura o sistema no Heroku'

    def handle(self, *args, **options):
        self.stdout.write('Configurando sistema no Heroku...')
        
        # Cria superusuário
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='pjluiz25@hotmail.com',
                password='admin123',
                first_name='Admin',
                last_name='Sistema'
            )
            self.stdout.write(self.style.SUCCESS('Superusuário criado com sucesso!'))
        else:
            self.stdout.write('Superusuário já existe!')
        
        # Cria tipos de loja
        try:
            criar_tipos = CriarTiposCommand()
            criar_tipos.handle()
            self.stdout.write(self.style.SUCCESS('Tipos de loja criados!'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar tipos de loja: {e}'))
        
        # Cria planos financeiros
        try:
            criar_planos = CriarPlanosCommand()
            criar_planos.handle()
            self.stdout.write(self.style.SUCCESS('Planos financeiros criados!'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar planos: {e}'))
        
        # Cria configuração de boleto
        try:
            criar_boleto = CriarBoletoCommand()
            criar_boleto.handle()
            self.stdout.write(self.style.SUCCESS('Configuração de boleto criada!'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar configuração de boleto: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Sistema configurado com sucesso!'))
