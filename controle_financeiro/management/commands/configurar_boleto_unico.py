from django.core.management.base import BaseCommand
from controle_financeiro.models import ConfiguracaoBoleto


class Command(BaseCommand):
    help = 'Configura apenas uma configuração de boleto ativa (configuração única)'

    def handle(self, *args, **options):
        # Desativa todas as configurações existentes
        ConfiguracaoBoleto.objects.update(ativo=False)
        
        # Cria ou ativa uma configuração única
        configuracao, created = ConfiguracaoBoleto.objects.get_or_create(
            nome_banco="Banco Principal",
            defaults={
                'codigo_banco': '001',
                'agencia': '1234',
                'conta': '12345678',
                'carteira': '17',
                'codigo_cedente': '1234567890',
                'nome_beneficiario': 'Sistema de Lojas - Empresa Principal',
                'cnpj_beneficiario': '12.345.678/0001-90',
                'endereco_beneficiario': 'Rua Principal, 123 - Centro - São Paulo/SP - CEP: 01234-567',
                'instrucoes': 'Não receber após o vencimento. Em caso de dúvidas, entre em contato conosco.',
                'multa': 2.00,
                'juros': 1.00,
                'desconto': 0.00,
                'ativo': True
            }
        )
        
        if not created:
            # Se já existe, apenas ativa
            configuracao.ativo = True
            configuracao.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Configuração única "{configuracao.nome_banco}" configurada!')
        )
        self.stdout.write(
            self.style.SUCCESS('Todas as outras configurações foram desativadas.')
        )
        self.stdout.write(
            self.style.SUCCESS('Todos os boletos usarão esta configuração bancária.')
        )
