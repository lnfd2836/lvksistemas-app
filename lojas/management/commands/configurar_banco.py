"""
Comando para configurar o banco de dados inicial
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Configura o banco de dados inicial do sistema'

    def handle(self, *args, **options):
        try:
            # Cria extensões necessárias
            with connection.cursor() as cursor:
                # Extensão para UUID
                cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
                
                # Extensão para criptografia
                cursor.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";")
                
                # Extensão para busca de texto
                cursor.execute("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";")
                
                # Extensão para estatísticas
                cursor.execute("CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\";")

            self.stdout.write(
                self.style.SUCCESS('Banco de dados configurado com sucesso!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao configurar banco de dados: {e}')
            )




