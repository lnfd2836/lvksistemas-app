"""
Comando para exportar dados do sistema
"""
import csv
from django.core.management.base import BaseCommand
from lojas.models import Loja, Cliente, Produto, Venda
from django.utils import timezone


class Command(BaseCommand):
    help = 'Exporta dados do sistema para arquivos CSV'

    def add_arguments(self, parser):
        parser.add_argument('--tipo', type=str, choices=['lojas', 'clientes', 'produtos', 'vendas'], help='Tipo de dados')
        parser.add_argument('--loja-id', type=str, help='ID da loja específica')
        parser.add_argument('--arquivo', type=str, help='Nome do arquivo de saída')

    def handle(self, *args, **options):
        if not options['tipo']:
            self.stdout.write(
                self.style.ERROR('Especifique --tipo')
            )
            return

        try:
            if options['tipo'] == 'lojas':
                self.exportar_lojas(options)
            elif options['tipo'] == 'clientes':
                self.exportar_clientes(options)
            elif options['tipo'] == 'produtos':
                self.exportar_produtos(options)
            elif options['tipo'] == 'vendas':
                self.exportar_vendas(options)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao exportar dados: {e}')
            )

    def exportar_lojas(self, options):
        arquivo = options.get('arquivo', f'lojas_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        with open(arquivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Nome', 'CNPJ', 'Email', 'Telefone', 'Cidade', 'Estado', 'Status', 'Data Criação'])
            
            for loja in Loja.objects.all():
                writer.writerow([
                    loja.id,
                    loja.nome,
                    loja.cnpj,
                    loja.email,
                    loja.telefone,
                    loja.cidade,
                    loja.estado,
                    loja.status,
                    loja.data_criacao.strftime('%d/%m/%Y %H:%M')
                ])
        
        self.stdout.write(f'Lojas exportadas para {arquivo}')

    def exportar_clientes(self, options):
        arquivo = options.get('arquivo', f'clientes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        with open(arquivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Loja', 'Nome', 'Email', 'Telefone', 'CPF', 'Cidade', 'Estado', 'Ativo', 'Data Cadastro'])
            
            clientes = Cliente.objects.all()
            if options.get('loja_id'):
                clientes = clientes.filter(loja_id=options['loja_id'])
            
            for cliente in clientes:
                writer.writerow([
                    cliente.id,
                    cliente.loja.nome,
                    cliente.nome,
                    cliente.email,
                    cliente.telefone,
                    cliente.cpf,
                    cliente.cidade,
                    cliente.estado,
                    'Sim' if cliente.ativo else 'Não',
                    cliente.data_cadastro.strftime('%d/%m/%Y %H:%M')
                ])
        
        self.stdout.write(f'Clientes exportados para {arquivo}')

    def exportar_produtos(self, options):
        arquivo = options.get('arquivo', f'produtos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        with open(arquivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Loja', 'Nome', 'Categoria', 'Preço', 'Estoque', 'Código Barras', 'Ativo', 'Data Cadastro'])
            
            produtos = Produto.objects.all()
            if options.get('loja_id'):
                produtos = produtos.filter(loja_id=options['loja_id'])
            
            for produto in produtos:
                writer.writerow([
                    produto.id,
                    produto.loja.nome,
                    produto.nome,
                    produto.categoria,
                    produto.preco,
                    produto.estoque,
                    produto.codigo_barras,
                    'Sim' if produto.ativo else 'Não',
                    produto.data_cadastro.strftime('%d/%m/%Y %H:%M')
                ])
        
        self.stdout.write(f'Produtos exportados para {arquivo}')

    def exportar_vendas(self, options):
        arquivo = options.get('arquivo', f'vendas_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        with open(arquivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Loja', 'Número Venda', 'Cliente', 'Valor Total', 'Desconto', 'Valor Final', 'Status', 'Data Venda'])
            
            vendas = Venda.objects.all()
            if options.get('loja_id'):
                vendas = vendas.filter(loja_id=options['loja_id'])
            
            for venda in vendas:
                writer.writerow([
                    venda.id,
                    venda.loja.nome,
                    venda.numero_venda,
                    venda.cliente.nome,
                    venda.valor_total,
                    venda.desconto,
                    venda.valor_final,
                    venda.status,
                    venda.data_venda.strftime('%d/%m/%Y %H:%M')
                ])
        
        self.stdout.write(f'Vendas exportadas para {arquivo}')



