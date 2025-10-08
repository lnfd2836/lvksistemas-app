"""
Comando para otimizar o sistema
"""
from django.core.management.base import BaseCommand
from django.db import connection
from lojas.models import Loja
from lojad.database_utils import otimizar_banco_loja


class Command(BaseCommand):
    help = 'Otimiza o sistema e todos os bancos de dados'

    def add_arguments(self, parser):
        parser.add_argument('--loja-id', type=str, help='ID da loja específica')
        parser.add_argument('--todas', action='store_true', help='Otimizar todas as lojas')

    def handle(self, *args, **options):
        if options['loja_id']:
            try:
                loja = Loja.objects.get(id=options['loja_id'])
                self.otimizar_loja(loja)
            except Loja.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Loja com ID {options["loja_id"]} não encontrada')
                )
        
        elif options['todas']:
            lojas = Loja.objects.all()
            for loja in lojas:
                self.otimizar_loja(loja)
        
        else:
            self.stdout.write(
                self.style.ERROR('Especifique --loja-id ou --todas')
            )

    def otimizar_loja(self, loja):
        try:
            if otimizar_banco_loja(loja):
                self.stdout.write(
                    self.style.SUCCESS(f'Loja {loja.nome} otimizada com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao otimizar loja {loja.nome}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao otimizar loja {loja.nome}: {e}')
            )






