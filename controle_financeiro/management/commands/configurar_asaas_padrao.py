"""
Comando para configurar uma conta padrão do Asaas
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from controle_financeiro.models import ConfiguracaoBoleto


class Command(BaseCommand):
    help = 'Configura uma conta padrão do Asaas para geração de boletos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nome-beneficiario',
            type=str,
            help='Nome do beneficiário (empresa)'
        )
        parser.add_argument(
            '--cnpj-beneficiario',
            type=str,
            help='CNPJ do beneficiário'
        )
        parser.add_argument(
            '--endereco-beneficiario',
            type=str,
            help='Endereço do beneficiário'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Configuração Padrão Asaas ===\n')
        )

        # Verificar se já existe uma configuração Asaas
        config_existente = ConfiguracaoBoleto.objects.filter(
            nome_banco__icontains='Asaas'
        ).first()

        if config_existente:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Já existe uma configuração Asaas: {config_existente.nome_beneficiario}')
            )
            
            resposta = input('Deseja atualizar? (s/N): ')
            if resposta.lower() != 's':
                self.stdout.write('Operação cancelada.')
                return
            
            config = config_existente
        else:
            config = ConfiguracaoBoleto()

        # Dados padrão do Asaas
        config.nome_banco = 'Asaas I.P S.A'
        config.codigo_banco = '461'
        config.agencia = '0001'
        config.conta = '194116-2'
        config.carteira = '1'  # Carteira padrão Asaas
        config.codigo_cedente = 'ASAAS'  # Reduzido para caber no campo
        config.convenio = 'ASAAS'  # Reduzido para caber no campo

        # Dados do beneficiário (opcionais via parâmetros)
        if options.get('nome_beneficiario'):
            config.nome_beneficiario = options['nome_beneficiario']
        elif not config.nome_beneficiario:
            config.nome_beneficiario = 'FELIX REPRESENTACOES E COMERCIO LTDA'

        if options.get('cnpj_beneficiario'):
            config.cnpj_beneficiario = options['cnpj_beneficiario']
        elif not config.cnpj_beneficiario:
            config.cnpj_beneficiario = '41.449.198/0001-72'

        if options.get('endereco_beneficiario'):
            config.endereco_beneficiario = options['endereco_beneficiario']
        elif not config.endereco_beneficiario:
            config.endereco_beneficiario = 'Endereço configurado no Asaas'

        # Configurações padrão
        config.instrucoes = (
            'Pagamento processado automaticamente via Asaas. '
            'Após o vencimento, multa de 2% + juros de 1% ao mês. '
            'Dúvidas: entre em contato conosco.'
        )
        config.multa = 2.00
        config.juros = 1.00
        config.desconto = 0.00
        config.ativo = True

        # Salvar configuração
        config.save()

        self.stdout.write(
            self.style.SUCCESS('✅ Configuração Asaas criada/atualizada com sucesso!')
        )

        # Mostrar resumo
        self.stdout.write('\n📋 Resumo da configuração:')
        self.stdout.write(f'   ID: {config.id}')
        self.stdout.write(f'   Banco: {config.nome_banco} ({config.codigo_banco})')
        self.stdout.write(f'   Beneficiário: {config.nome_beneficiario}')
        self.stdout.write(f'   CNPJ: {config.cnpj_beneficiario}')
        self.stdout.write(f'   Multa: {config.multa}%')
        self.stdout.write(f'   Juros: {config.juros}% ao mês')

        # Verificar API Key
        api_key = getattr(settings, 'ASAAS_API_KEY', None)
        if api_key:
            self.stdout.write(f'\n✅ API Key configurada: {api_key[:8]}...')
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  API Key não configurada. Adicione ASAAS_API_KEY no .env')
            )

        self.stdout.write(
            self.style.SUCCESS('\n🚀 Sistema pronto para gerar cobranças via Asaas!')
        )

        # Próximos passos
        self.stdout.write('\n📋 Próximos passos:')
        self.stdout.write('   1. Configure sua conta no painel do Asaas')
        self.stdout.write('   2. Obtenha sua API Key')
        self.stdout.write('   3. Configure o webhook para receber notificações')
        self.stdout.write('   4. Teste a integração com: python manage.py testar_asaas')