"""
Comando para configurar a API do Asaas
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import ConfiguracaoBoleto
from django.conf import settings


class Command(BaseCommand):
    help = 'Configura a API do Asaas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='Nova chave de API do Asaas',
        )
        parser.add_argument(
            '--environment',
            type=str,
            choices=['sandbox', 'production'],
            default='sandbox',
            help='Ambiente do Asaas (sandbox ou production)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== CONFIGURAÇÃO DA API ASAAS ==='))
        
        # Verificar configuração atual
        self.stdout.write(f'API Key atual: {settings.ASAAS_API_KEY[:10]}...' if settings.ASAAS_API_KEY else 'API Key: NÃO CONFIGURADA')
        self.stdout.write(f'Environment atual: {settings.ASAAS_ENVIRONMENT}')
        
        # Configurar nova API key se fornecida
        if options['api_key']:
            self.stdout.write(f'\n--- CONFIGURANDO NOVA API KEY ---')
            self.stdout.write(f'Nova API Key: {options["api_key"][:10]}...')
            self.stdout.write(f'Environment: {options["environment"]}')
            
            # Atualizar configuração do Asaas
            config = ConfiguracaoBoleto.objects.filter(codigo_banco="461").first()
            if config:
                config.nome_banco = "Asaas I.P S.A"
                config.codigo_banco = "461"
                config.agencia = "0001"
                config.conta = "194116-2"
                config.carteira = "01"
                config.codigo_cedente = "ASAAS001"
                config.nome_beneficiario = "FELIX REPRESENTACOES E COMERCIO LTDA"
                config.cnpj_beneficiario = "41.449.198/0001-72"
                config.endereco_beneficiario = "Rua Exemplo, 123 - Centro - São Paulo/SP"
                config.instrucoes = "Não receber após o vencimento."
                config.multa = 2.00
                config.juros = 1.00
                config.desconto = 0.00
                config.ativo = True
                config.save()
                
                self.stdout.write(self.style.SUCCESS('✅ Configuração do Asaas atualizada'))
            else:
                # Criar nova configuração
                config = ConfiguracaoBoleto.objects.create(
                    nome_banco="Asaas I.P S.A",
                    codigo_banco="461",
                    agencia="0001",
                    conta="194116-2",
                    carteira="01",
                    codigo_cedente="ASAAS001",
                    nome_beneficiario="FELIX REPRESENTACOES E COMERCIO LTDA",
                    cnpj_beneficiario="41.449.198/0001-72",
                    endereco_beneficiario="Rua Exemplo, 123 - Centro - São Paulo/SP",
                    instrucoes="Não receber após o vencimento.",
                    multa=2.00,
                    juros=1.00,
                    desconto=0.00,
                    ativo=True
                )
                
                self.stdout.write(self.style.SUCCESS('✅ Nova configuração do Asaas criada'))
            
            self.stdout.write(f'\n--- INSTRUÇÕES ---')
            self.stdout.write('1. Configure a variável de ambiente ASAAS_API_KEY no Heroku:')
            self.stdout.write(f'   heroku config:set ASAAS_API_KEY="{options["api_key"]}"')
            self.stdout.write(f'2. Configure o ambiente:')
            self.stdout.write(f'   heroku config:set ASAAS_ENVIRONMENT="{options["environment"]}"')
            self.stdout.write('3. Faça o deploy das mudanças')
            self.stdout.write('4. Teste a geração de boletos')
        else:
            self.stdout.write(f'\n--- CONFIGURAÇÕES ATUAIS ---')
            configs = ConfiguracaoBoleto.objects.filter(codigo_banco="461")
            for config in configs:
                self.stdout.write(f'ID: {config.id}')
                self.stdout.write(f'Banco: {config.codigo_banco} - {config.nome_banco}')
                self.stdout.write(f'Ativo: {config.ativo}')
                self.stdout.write(f'Agência: {config.agencia}')
                self.stdout.write(f'Conta: {config.conta}')
                self.stdout.write(f'Carteira: {config.carteira}')
                self.stdout.write(f'Cedente: {config.codigo_cedente}')
                self.stdout.write(f'Beneficiário: {config.nome_beneficiario}')
                self.stdout.write(f'CNPJ: {config.cnpj_beneficiario}')
                self.stdout.write('---')
        
        self.stdout.write('\n=== CONFIGURAÇÃO CONCLUÍDA ===')
