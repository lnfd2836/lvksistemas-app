from django.core.management.base import BaseCommand
from planos.models import PlanoComercial
from decimal import Decimal


class Command(BaseCommand):
    help = 'Cria planos comerciais padrão no sistema'

    def handle(self, *args, **options):
        planos_padrao = [
            {
                'nome': 'Plano Básico',
                'tipo': 'basico',
                'descricao': 'Ideal para pequenas lojas que estão começando',
                'max_usuarios_simultaneos': 2,
                'max_pdvs': 1,
                'max_produtos': 100,
                'max_clientes': 200,
                'max_vendas_mes': 500,
                'backup_automatico': False,
                'relatorios_avancados': False,
                'integracao_api': False,
                'suporte_prioritario': False,
                'customizacao_avancada': False,
                'preco_mensal': Decimal('29.90'),
                'preco_anual': Decimal('299.00'),
                'status': 'ativo',
                'ordem_exibicao': 1,
                'destaque': False,
            },
            {
                'nome': 'Plano Intermediário',
                'tipo': 'intermediario',
                'descricao': 'Para lojas em crescimento com necessidades moderadas',
                'max_usuarios_simultaneos': 5,
                'max_pdvs': 3,
                'max_produtos': 500,
                'max_clientes': 1000,
                'max_vendas_mes': 2000,
                'backup_automatico': True,
                'relatorios_avancados': True,
                'integracao_api': False,
                'suporte_prioritario': False,
                'customizacao_avancada': False,
                'preco_mensal': Decimal('59.90'),
                'preco_anual': Decimal('599.00'),
                'status': 'ativo',
                'ordem_exibicao': 2,
                'destaque': True,
            },
            {
                'nome': 'Plano Avançado',
                'tipo': 'avancado',
                'descricao': 'Para lojas estabelecidas com alto volume de vendas',
                'max_usuarios_simultaneos': 10,
                'max_pdvs': 5,
                'max_produtos': 2000,
                'max_clientes': 5000,
                'max_vendas_mes': 10000,
                'backup_automatico': True,
                'relatorios_avancados': True,
                'integracao_api': True,
                'suporte_prioritario': True,
                'customizacao_avancada': False,
                'preco_mensal': Decimal('99.90'),
                'preco_anual': Decimal('999.00'),
                'status': 'ativo',
                'ordem_exibicao': 3,
                'destaque': False,
            },
            {
                'nome': 'Plano Premium',
                'tipo': 'premium',
                'descricao': 'Para lojas de grande porte com necessidades específicas',
                'max_usuarios_simultaneos': 20,
                'max_pdvs': 10,
                'max_produtos': 10000,
                'max_clientes': 20000,
                'max_vendas_mes': 50000,
                'backup_automatico': True,
                'relatorios_avancados': True,
                'integracao_api': True,
                'suporte_prioritario': True,
                'customizacao_avancada': True,
                'preco_mensal': Decimal('199.90'),
                'preco_anual': Decimal('1999.00'),
                'status': 'ativo',
                'ordem_exibicao': 4,
                'destaque': False,
            },
            {
                'nome': 'Plano Enterprise',
                'tipo': 'enterprise',
                'descricao': 'Solução completa para grandes empresas e redes de lojas',
                'max_usuarios_simultaneos': 50,
                'max_pdvs': 25,
                'max_produtos': 50000,
                'max_clientes': 100000,
                'max_vendas_mes': 200000,
                'backup_automatico': True,
                'relatorios_avancados': True,
                'integracao_api': True,
                'suporte_prioritario': True,
                'customizacao_avancada': True,
                'preco_mensal': Decimal('399.90'),
                'preco_anual': Decimal('3999.00'),
                'status': 'ativo',
                'ordem_exibicao': 5,
                'destaque': False,
            }
        ]

        # Verifica se já existem planos
        if PlanoComercial.objects.exists():
            self.stdout.write(
                self.style.WARNING('Planos já existem no sistema. Use --force para recriar.')
            )
            return

        # Cria os planos
        for plano_data in planos_padrao:
            plano = PlanoComercial.objects.create(**plano_data)
            self.stdout.write(
                self.style.SUCCESS(f'Plano "{plano.nome}" criado com sucesso!')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Total de {len(planos_padrao)} planos criados com sucesso!')
        )
