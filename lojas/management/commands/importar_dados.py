"""
Comando para importar dados de um arquivo CSV
"""
import csv
from django.core.management.base import BaseCommand
from lojas.models import Loja, Cliente, Produto
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Importa dados de um arquivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('--arquivo', type=str, help='Caminho do arquivo CSV')
        parser.add_argument('--tipo', type=str, choices=['lojas', 'clientes', 'produtos'], help='Tipo de dados')

    def handle(self, *args, **options):
        if not options['arquivo'] or not options['tipo']:
            self.stdout.write(
                self.style.ERROR('Especifique --arquivo e --tipo')
            )
            return

        try:
            with open(options['arquivo'], 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                if options['tipo'] == 'lojas':
                    self.importar_lojas(reader)
                elif options['tipo'] == 'clientes':
                    self.importar_clientes(reader)
                elif options['tipo'] == 'produtos':
                    self.importar_produtos(reader)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao importar dados: {e}')
            )

    def importar_lojas(self, reader):
        for row in reader:
            try:
                # Cria usuário administrador
                admin_user = User.objects.create_user(
                    username=row['email'],
                    email=row['email'],
                    first_name=row['nome'].split()[0],
                    last_name=' '.join(row['nome'].split()[1:]) if len(row['nome'].split()) > 1 else '',
                    is_staff=True,
                )
                
                # Cria loja
                Loja.objects.create(
                    nome=row['nome'],
                    cnpj=row['cnpj'],
                    email=row['email'],
                    telefone=row['telefone'],
                    endereco=row['endereco'],
                    cidade=row['cidade'],
                    estado=row['estado'],
                    cep=row['cep'],
                    admin_user=admin_user
                )
                
                self.stdout.write(f'Loja {row["nome"]} importada com sucesso!')
                
            except Exception as e:
                self.stdout.write(f'Erro ao importar loja {row["nome"]}: {e}')

    def importar_clientes(self, reader):
        for row in reader:
            try:
                # Busca a loja
                loja = Loja.objects.get(id=row['loja_id'])
                
                # Cria cliente
                Cliente.objects.create(
                    loja=loja,
                    nome=row['nome'],
                    email=row['email'],
                    telefone=row['telefone'],
                    cpf=row['cpf'],
                    data_nascimento=row['data_nascimento'],
                    sexo=row['sexo'],
                    endereco=row['endereco'],
                    cidade=row['cidade'],
                    estado=row['estado'],
                    cep=row['cep']
                )
                
                self.stdout.write(f'Cliente {row["nome"]} importado com sucesso!')
                
            except Exception as e:
                self.stdout.write(f'Erro ao importar cliente {row["nome"]}: {e}')

    def importar_produtos(self, reader):
        for row in reader:
            try:
                # Busca a loja
                loja = Loja.objects.get(id=row['loja_id'])
                
                # Cria produto
                Produto.objects.create(
                    loja=loja,
                    nome=row['nome'],
                    descricao=row['descricao'],
                    categoria=row['categoria'],
                    preco=row['preco'],
                    estoque=row['estoque'],
                    codigo_barras=row.get('codigo_barras', ''),
                    ativo=row.get('ativo', 'true').lower() == 'true'
                )
                
                self.stdout.write(f'Produto {row["nome"]} importado com sucesso!')
                
            except Exception as e:
                self.stdout.write(f'Erro ao importar produto {row["nome"]}: {e}')


