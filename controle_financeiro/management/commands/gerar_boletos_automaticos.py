"""
Comando para gerar boletos automaticamente 10 dias antes do vencimento
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from controle_financeiro.models import ControleFinanceiro, CobrancaAsaas
from controle_financeiro.asaas_central_service import AsaasCentralService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Gera boletos automaticamente 10 dias antes do vencimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-antecedencia',
            type=int,
            default=10,
            help='Dias de antecedência para gerar o boleto (padrão: 10)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações (apenas mostra o que seria feito)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a geração mesmo se já existir cobrança'
        )

    def handle(self, *args, **options):
        dias_antecedencia = options['dias_antecedencia']
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🚀 Iniciando geração automática de boletos ({dias_antecedencia} dias de antecedência)'
            )
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  Modo DRY RUN - Nenhuma alteração será feita'))
        
        # Data limite para gerar boletos
        data_limite = timezone.now().date() + timedelta(days=dias_antecedencia)
        
        # Buscar controles financeiros que precisam de boleto
        controles = ControleFinanceiro.objects.filter(
            status='ativo',
            data_vencimento__date__lte=data_limite,
            loja__status='ativa'
        ).select_related('loja', 'plano')
        
        self.stdout.write(f'📋 Encontrados {controles.count()} controles para verificar')
        
        gerados = 0
        erros = 0
        ja_existem = 0
        
        for controle in controles:
            try:
                # Verificar se já existe cobrança ativa para este controle
                cobranca_existente = CobrancaAsaas.objects.filter(
                    controle_financeiro=controle,
                    status__in=['PENDING', 'CONFIRMED', 'RECEIVED']
                ).first()
                
                if cobranca_existente and not force:
                    ja_existem += 1
                    self.stdout.write(
                        f'   ℹ️  {controle.loja.nome}: Já possui cobrança ativa ({cobranca_existente.asaas_id})'
                    )
                    continue
                
                dias_para_vencimento = (controle.data_vencimento.date() - timezone.now().date()).days
                
                self.stdout.write(
                    f'   🏪 {controle.loja.nome}: Vence em {dias_para_vencimento} dias'
                )
                
                if not dry_run:
                    # Gerar cobrança via Asaas
                    asaas_service = AsaasCentralService()
                    
                    # Calcular dias de vencimento (mínimo 1 dia)
                    dias_vencimento = max(1, dias_para_vencimento)
                    
                    cobranca = asaas_service.gerar_cobranca_loja(controle, dias_vencimento)
                    
                    if cobranca:
                        gerados += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'   ✅ Boleto gerado: {cobranca["id"]} - R$ {cobranca["value"]}'
                            )
                        )
                    else:
                        erros += 1
                        self.stdout.write(
                            self.style.ERROR(f'   ❌ Erro ao gerar boleto para {controle.loja.nome}')
                        )
                else:
                    self.stdout.write(f'   🔄 Seria gerado boleto para {controle.loja.nome}')
                    gerados += 1
                    
            except Exception as e:
                erros += 1
                logger.error(f'Erro ao processar controle {controle.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erro: {controle.loja.nome} - {str(e)}')
                )
        
        # Resumo final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RESUMO DA EXECUÇÃO'))
        self.stdout.write('='*60)
        self.stdout.write(f'   📋 Controles verificados: {controles.count()}')
        self.stdout.write(f'   ✅ Boletos gerados: {gerados}')
        self.stdout.write(f'   ℹ️  Já existiam: {ja_existem}')
        self.stdout.write(f'   ❌ Erros: {erros}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  Modo DRY RUN - Execute sem --dry-run para aplicar'))
        else:
            self.stdout.write(self.style.SUCCESS('\n🎉 Execução concluída!'))
        
        return f'Gerados: {gerados}, Erros: {erros}'