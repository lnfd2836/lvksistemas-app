"""
Comando para gerar boletos automaticamente 10 dias antes do vencimento
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from controle_financeiro.models import ControleFinanceiro, BoletoGerado, ConfiguracaoBoleto
from controle_financeiro.services import BoletoService


class Command(BaseCommand):
    help = 'Gera boletos automaticamente para lojas que vencem em 10 dias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-antecedencia',
            type=int,
            default=10,
            help='Número de dias de antecedência para gerar o boleto (padrão: 10)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações, apenas mostra o que seria feito'
        )

    def handle(self, *args, **options):
        dias_antecedencia = options['dias_antecedencia']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Iniciando geração automática de boletos ({dias_antecedencia} dias de antecedência)'
            )
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita'))
        
        # Data limite para gerar boletos (10 dias antes do vencimento)
        data_limite = timezone.now() + timedelta(days=dias_antecedencia)
        
        # Busca controles financeiros que vencem em até X dias
        controles_vencendo = ControleFinanceiro.objects.filter(
            data_vencimento__lte=data_limite,
            data_vencimento__gt=timezone.now(),
            status='ativa'
        )
        
        self.stdout.write(f'Encontrados {controles_vencendo.count()} controles vencendo em até {dias_antecedencia} dias')
        
        # Verifica se há configuração de boleto ativa
        configuracao_ativa = ConfiguracaoBoleto.objects.filter(ativo=True).first()
        if not configuracao_ativa:
            self.stdout.write(
                self.style.ERROR('Nenhuma configuração de boleto ativa encontrada!')
            )
            return
        
        boletos_gerados = 0
        boletos_ja_existentes = 0
        
        for controle in controles_vencendo:
            # Verifica se já existe um boleto pendente para este controle
            boleto_existente = BoletoGerado.objects.filter(
                controle_financeiro=controle,
                status__in=['pendente', 'vencido'],
                data_vencimento__gte=timezone.now()
            ).exists()
            
            if boleto_existente:
                boletos_ja_existentes += 1
                self.stdout.write(
                    f'  - {controle.loja.nome}: Já possui boleto pendente'
                )
                continue
            
            if not dry_run:
                try:
                    # Gera o boleto usando o serviço
                    boleto_service = BoletoService()
                    boleto = boleto_service.gerar_boleto(controle, configuracao_ativa)
                    
                    boletos_gerados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ {controle.loja.nome}: Boleto {boleto.numero_boleto} gerado '
                            f'(Vence em: {boleto.data_vencimento.strftime("%d/%m/%Y")})'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ {controle.loja.nome}: Erro ao gerar boleto - {str(e)}'
                        )
                    )
            else:
                boletos_gerados += 1
                self.stdout.write(
                    f'  [DRY-RUN] {controle.loja.nome}: Boleto seria gerado '
                    f'(Vence em: {controle.data_vencimento.strftime("%d/%m/%Y")})'
                )
        
        # Resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Resumo da execução:')
        self.stdout.write(f'  - Boletos gerados: {boletos_gerados}')
        self.stdout.write(f'  - Boletos já existentes: {boletos_ja_existentes}')
        self.stdout.write(f'  - Total processado: {controles_vencendo.count()}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nNenhuma alteração foi feita (modo dry-run)'))
        else:
            self.stdout.write(self.style.SUCCESS('\nProcessamento concluído!'))