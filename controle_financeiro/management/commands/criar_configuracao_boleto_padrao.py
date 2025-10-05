from django.core.management.base import BaseCommand
from controle_financeiro.models import ConfiguracaoBoleto


class Command(BaseCommand):
    help = 'Cria uma configuração de boleto padrão para o sistema'

    def handle(self, *args, **options):
        configuracao, created = ConfiguracaoBoleto.objects.get_or_create(
            nome_banco="Banco do Brasil",
            defaults={
                'codigo_banco': '001',
                'agencia': '1234',
                'conta': '12345678',
                'carteira': '17',
                'nome_beneficiario': 'Sistema de Lojas - Empresa Exemplo',
                'cnpj_beneficiario': '12.345.678/0001-90',
                'endereco_beneficiario': 'Rua Exemplo, 123 - Centro - São Paulo/SP - CEP: 01234-567',
                'instrucoes': 'Não receber após o vencimento. Em caso de dúvidas, entre em contato conosco.',
                'multa': 2.00,
                'juros': 1.00,
                'desconto': 0.00,
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Configuração de boleto "{configuracao.nome_banco}" criada com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Configuração de boleto "{configuracao.nome_banco}" já existe.')
            )

        self.stdout.write(
            self.style.SUCCESS('Configuração de boleto padrão configurada!')
        )
