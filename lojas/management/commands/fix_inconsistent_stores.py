"""
Management command to fix stores with inconsistent financial data.
This command identifies stores that have ControleFinanceiro but no AssinaturaLoja
and creates the missing records to ensure data consistency.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from lojas.models import Loja
from controle_financeiro.models import ControleFinanceiro
from planos.models import AssinaturaLoja, PlanoComercial
from lojas.utils.plan_mapping import fix_inconsistent_store_data
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix stores with inconsistent financial data (ControleFinanceiro without AssinaturaLoja)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )
        parser.add_argument(
            '--store-id',
            type=str,
            help='Fix only a specific store by ID',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        store_id = options['store_id']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Scanning for stores with inconsistent financial data...')
        )
        
        # Find stores with ControleFinanceiro but no AssinaturaLoja
        inconsistent_stores = self.find_inconsistent_stores(store_id)
        
        if not inconsistent_stores:
            self.stdout.write(
                self.style.SUCCESS('✅ No inconsistent stores found. All stores have proper financial records.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  Found {len(inconsistent_stores)} stores with inconsistent data:')
        )
        
        # Display inconsistent stores
        for loja in inconsistent_stores:
            controle = ControleFinanceiro.objects.filter(loja=loja).first()
            self.stdout.write(f'  - {loja.nome} (ID: {loja.id})')
            if verbose and controle:
                self.stdout.write(f'    ControleFinanceiro: {controle.plano.nome} - R$ {controle.valor_mensal}')
                self.stdout.write(f'    Status: {controle.status}')
                self.stdout.write(f'    Vencimento: {controle.data_vencimento}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN: No changes were made. Use without --dry-run to apply fixes.')
            )
            return
        
        # Confirm before making changes
        if not store_id:  # Only ask for confirmation when fixing multiple stores
            confirm = input('\nDo you want to fix these inconsistent stores? (yes/no): ')
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.ERROR('❌ Operation cancelled.'))
                return
        
        # Fix inconsistent stores
        fixed_count = 0
        error_count = 0
        
        for loja in inconsistent_stores:
            try:
                with transaction.atomic():
                    assinatura = fix_inconsistent_store_data(loja)
                    if assinatura:
                        fixed_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Fixed: {loja.nome} - Created AssinaturaLoja with plan {assinatura.plano.nome}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Skipped: {loja.nome} - Already has AssinaturaLoja')
                        )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error fixing {loja.nome}: {str(e)}')
                )
                logger.error(f'Error fixing store {loja.nome} (ID: {loja.id}): {str(e)}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'📊 SUMMARY:'))
        self.stdout.write(f'  - Stores scanned: {Loja.objects.count()}')
        self.stdout.write(f'  - Inconsistent stores found: {len(inconsistent_stores)}')
        self.stdout.write(f'  - Successfully fixed: {fixed_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  - Errors: {error_count}'))
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully fixed {fixed_count} stores!')
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'\n⚠️  {error_count} stores had errors. Check logs for details.')
            )

    def find_inconsistent_stores(self, store_id=None):
        """Find stores with ControleFinanceiro but no AssinaturaLoja"""
        
        # Base query for stores with ControleFinanceiro
        stores_with_controle = Loja.objects.filter(
            controlefinanceiro__isnull=False
        )
        
        # Filter by specific store if provided
        if store_id:
            try:
                stores_with_controle = stores_with_controle.filter(id=store_id)
            except Exception:
                raise CommandError(f'Invalid store ID: {store_id}')
        
        # Find stores without AssinaturaLoja
        inconsistent_stores = []
        for loja in stores_with_controle:
            if not AssinaturaLoja.objects.filter(loja=loja).exists():
                inconsistent_stores.append(loja)
        
        return inconsistent_stores

    def create_missing_plano_comercial(self, controle_financeiro):
        """Create a PlanoComercial based on existing ControleFinanceiro"""
        
        # Try to find existing PlanoComercial with same name and price
        plano_comercial = PlanoComercial.objects.filter(
            nome=controle_financeiro.plano.nome,
            preco_mensal=controle_financeiro.valor_mensal
        ).first()
        
        if plano_comercial:
            return plano_comercial
        
        # Create new PlanoComercial
        plano_comercial = PlanoComercial.objects.create(
            nome=controle_financeiro.plano.nome,
            tipo='basico',  # Default type
            descricao=controle_financeiro.plano.descricao or f'Plano migrado automaticamente - {controle_financeiro.plano.nome}',
            preco_mensal=controle_financeiro.valor_mensal,
            status='ativo',
            # Set reasonable defaults for limits
            max_usuarios_simultaneos=5,
            max_pdvs=2,
            max_produtos=500,
            max_clientes=1000,
            max_vendas_mes=1000,
        )
        
        return plano_comercial