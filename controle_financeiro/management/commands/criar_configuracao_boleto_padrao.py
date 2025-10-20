from django.core.management.base import BaseCommand
from controle_financeiro.models import ConfiguracaoBoleto


class Command(BaseCommand):
    help = 'Cria uma configuração de boleto padrão Asaas para o sistema'

    def handle(self, *args, **options):
        configuracao, created = ConfiguracaoBoleto.objects.get_or_create(
            nome_banco="Asaas I.P S.A",
            defaults={
                'codigo_banco': '461',
                'agencia': '0001',
                'conta': '194116-2',
                'carteira': '1',
                'codigo_cedente': 'ASAAS',
                'convenio': 'ASAAS',
                'nome_beneficiario': 'FELIX REPRESENTACOES E COMERCIO LTDA',
                'cnpj_beneficiario': '41.449.198/0001-72',
                'endereco_beneficiario': 'Endereço configurado no Asaas',
                'instrucoes': 'Pagamento processado automaticamente via Asaas. Após o vencimento, multa de 2% + juros de 1% ao mês.',
                'multa': 2.00,
                'juros': 1.00,
                'desconto': 0.00,
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Configuração Asaas "{configuracao.nome_banco}" criada com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Configuração Asaas "{configuracao.nome_banco}" já existe.')
            )

        self.stdout.write(
            self.style.SUCCESS('Configuração Asaas padrão configurada!')
        )
