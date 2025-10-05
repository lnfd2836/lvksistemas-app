from django.core.management.base import BaseCommand
from controle_financeiro.models import PlanoFinanceiro


class Command(BaseCommand):
    help = 'Cria planos financeiros iniciais para o sistema'

    def handle(self, *args, **options):
        planos = [
            {
                'nome': 'Básico',
                'descricao': 'Plano básico para pequenas lojas',
                'valor_mensal': 29.90,
                'dias_trial': 30,
            },
            {
                'nome': 'Profissional',
                'descricao': 'Plano profissional para lojas médias',
                'valor_mensal': 59.90,
                'dias_trial': 30,
            },
            {
                'nome': 'Empresarial',
                'descricao': 'Plano empresarial para grandes lojas',
                'valor_mensal': 99.90,
                'dias_trial': 30,
            },
            {
                'nome': 'Premium',
                'descricao': 'Plano premium com recursos avançados',
                'valor_mensal': 149.90,
                'dias_trial': 30,
            },
        ]

        for plano_data in planos:
            plano, created = PlanoFinanceiro.objects.get_or_create(
                nome=plano_data['nome'],
                defaults=plano_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Plano "{plano.nome}" criado com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plano "{plano.nome}" já existe.')
                )

        self.stdout.write(
            self.style.SUCCESS('Planos financeiros configurados com sucesso!')
        )
