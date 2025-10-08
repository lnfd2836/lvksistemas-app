"""
Comando para criar backup de uma loja
"""
from django.core.management.base import BaseCommand, CommandError
from lojas.models import Loja, BackupLoja
from lojad.database_utils import criar_backup_loja
from django.utils import timezone
import os


class Command(BaseCommand):
    help = 'Cria backup de uma loja específica'

    def add_arguments(self, parser):
        parser.add_argument('--loja-id', type=str, help='ID da loja')
        parser.add_argument('--todas', action='store_true', help='Backup de todas as lojas')

    def handle(self, *args, **options):
        if options['loja_id']:
            try:
                loja = Loja.objects.get(id=options['loja_id'])
                self.criar_backup_loja(loja)
            except Loja.DoesNotExist:
                raise CommandError(f'Loja com ID {options["loja_id"]} não encontrada')
        
        elif options['todas']:
            lojas = Loja.objects.all()
            for loja in lojas:
                self.criar_backup_loja(loja)
        
        else:
            raise CommandError('Especifique --loja-id ou --todas')

    def criar_backup_loja(self, loja):
        try:
            sucesso, resultado = criar_backup_loja(loja)
            
            if sucesso:
                # Registra o backup
                BackupLoja.objects.create(
                    loja=loja,
                    nome_arquivo=f"backup_{loja.db_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
                    tamanho_arquivo=os.path.getsize(resultado) if os.path.exists(resultado) else 0,
                    caminho_arquivo=resultado,
                    sucesso=True,
                    observacoes="Backup criado com sucesso"
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Backup da loja {loja.nome} criado com sucesso!')
                )
            else:
                # Registra o erro
                BackupLoja.objects.create(
                    loja=loja,
                    nome_arquivo=f"backup_{loja.db_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
                    tamanho_arquivo=0,
                    caminho_arquivo="",
                    sucesso=False,
                    observacoes=f"Erro: {resultado}"
                )
                
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar backup da loja {loja.nome}: {resultado}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar backup da loja {loja.nome}: {e}')
            )






