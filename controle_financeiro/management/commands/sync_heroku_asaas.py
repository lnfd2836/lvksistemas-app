"""
Comando para sincronizar cobranças do Asaas no Heroku
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.asaas_sync_service import get_sync_service
from lojas.models import Loja
from decimal import Decimal
from datetime import datetime, timedelta
import requests
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza cobranças do Asaas no ambiente Heroku'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força sincronização completa'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Dias para buscar cobranças (padrão: 30)'
        )
    
    def handle(self, *args, **options):
        force = options['force']
        days = options['days']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando sincronização Heroku-Asaas (últimos {days} dias)')
        )
        
        try:
            # 1. Verificar configuração
            if not self.check_configuration():
                return
            
            # 2. Buscar cobranças no Asaas
            asaas_payments = self.fetch_asaas_payments(days)
            
            if not asaas_payments:
                self.stdout.write(self.style.WARNING('❌ Nenhuma cobrança encontrada no Asaas'))
                return
            
            # 3. Sincronizar cobranças
            if force:
                synced = self.force_sync_all(asaas_payments)
            else:
                synced = self.sync_missing_only(asaas_payments)
            
            # 4. Executar sincronização do serviço
            self.run_sync_service()
            
            # 5. Mostrar resultado
            self.show_final_status(synced)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'💥 Erro durante sincronização: {str(e)}')
            )
    
    def check_configuration(self):
        """Verifica configuração do Asaas"""
        try:
            asaas_service = AsaasService()
            if asaas_service.validar_configuracao():
                self.stdout.write(self.style.SUCCESS('✅ Configuração do Asaas válida'))
                return True
            else:
                self.stdout.write(self.style.ERROR('❌ Configuração do Asaas inválida'))
                return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro na configuração: {str(e)}'))
            return False
    
    def fetch_asaas_payments(self, days):
        """Busca cobranças no Asaas"""
        try:
            asaas_service = AsaasService()
            data_inicio = (timezone.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            self.stdout.write(f'📡 Buscando cobranças desde {data_inicio}...')
            
            response = requests.get(
                f"{asaas_service.base_url}/payments",
                headers=asaas_service.headers,
                params={
                    'dateCreated[ge]': data_inicio,
                    'limit': 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('data', [])
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Encontradas {len(payments)} cobranças no Asaas')
                )
                
                return payments
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro na API: {response.status_code}')
                )
                return None
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao buscar cobranças: {str(e)}')
            )
            return None
    
    def sync_missing_only(self, asaas_payments):
        """Sincroniza apenas cobranças faltantes"""
        local_ids = set(CobrancaAsaas.objects.values_list('asaas_id', flat=True))
        asaas_ids = {p['id'] for p in asaas_payments}
        
        missing_ids = asaas_ids - local_ids
        
        if not missing_ids:
            self.stdout.write(self.style.SUCCESS('✅ Todas as cobranças já estão sincronizadas'))
            return 0
        
        self.stdout.write(f'🔄 Sincronizando {len(missing_ids)} cobranças faltantes...')
        
        synced_count = 0
        
        for payment in asaas_payments:
            if payment['id'] in missing_ids:
                if self.create_cobranca_from_payment(payment):
                    synced_count += 1
        
        return synced_count
    
    def force_sync_all(self, asaas_payments):
        """Força sincronização de todas as cobranças"""
        self.stdout.write('🔄 Forçando sincronização de todas as cobranças...')
        
        # Remover cobranças existentes (cuidado!)
        existing_count = CobrancaAsaas.objects.count()
        if existing_count > 0:
            self.stdout.write(f'⚠️ Removendo {existing_count} cobranças existentes...')
            CobrancaAsaas.objects.all().delete()
        
        synced_count = 0
        
        for payment in asaas_payments:
            if self.create_cobranca_from_payment(payment):
                synced_count += 1
        
        return synced_count
    
    def create_cobranca_from_payment(self, payment):
        """Cria cobrança a partir dos dados do Asaas"""
        try:
            # Identificar controle financeiro
            controle = self.identify_controle_financeiro(payment)
            
            if not controle:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Controle não identificado para {payment["id"]}')
                )
                return False
            
            # Criar cobrança
            cobranca = CobrancaAsaas.objects.create(
                asaas_id=payment['id'],
                controle_financeiro=controle,
                customer_id=payment.get('customer', ''),
                valor=Decimal(str(payment['value'])),
                data_vencimento=datetime.fromisoformat(payment['dueDate']).replace(tzinfo=timezone.get_current_timezone()),
                descricao=payment.get('description', ''),
                status=payment['status'],
                external_reference=payment.get('externalReference', ''),
                invoice_url=payment.get('invoiceUrl', ''),
                bank_slip_url=payment.get('bankSlipUrl', ''),
                invoice_number=payment.get('invoiceNumber', ''),
                api_response=payment,
                observacoes=f"Sincronizada via comando Heroku - {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            )
            
            # Se já foi paga, processar pagamento
            if payment['status'] in ['RECEIVED', 'CONFIRMED']:
                cobranca.marcar_como_paga()
            
            self.stdout.write(f'  ✅ {payment["id"]} → {controle.loja.nome}')
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Erro em {payment["id"]}: {str(e)}')
            )
            return False
    
    def identify_controle_financeiro(self, payment):
        """Identifica controle financeiro para uma cobrança"""
        
        # Método 1: Por referência externa
        external_ref = payment.get('externalReference', '')
        if external_ref and external_ref.startswith('CF_'):
            try:
                cf_id = external_ref.split('_')[1]
                return ControleFinanceiro.objects.get(id=cf_id)
            except (IndexError, ControleFinanceiro.DoesNotExist):
                pass
        
        # Método 2: Por dados do customer
        customer_id = payment.get('customer')
        if customer_id:
            try:
                asaas_service = AsaasService()
                
                customer_response = requests.get(
                    f"{asaas_service.base_url}/customers/{customer_id}",
                    headers=asaas_service.headers,
                    timeout=10
                )
                
                if customer_response.status_code == 200:
                    customer_data = customer_response.json()
                    customer_email = customer_data.get('email', '')
                    customer_cnpj = customer_data.get('cpfCnpj', '')
                    
                    # Buscar por email
                    if customer_email:
                        controle = ControleFinanceiro.objects.filter(
                            loja__email=customer_email
                        ).first()
                        if controle:
                            return controle
                    
                    # Buscar por CNPJ
                    if customer_cnpj:
                        cnpj_limpo = customer_cnpj.replace('.', '').replace('/', '').replace('-', '')
                        controle = ControleFinanceiro.objects.filter(
                            loja__cnpj__contains=cnpj_limpo[:8]
                        ).first()
                        if controle:
                            return controle
                            
            except Exception as e:
                logger.warning(f"Erro ao buscar customer {customer_id}: {str(e)}")
        
        # Método 3: Usar primeiro controle disponível (fallback)
        return ControleFinanceiro.objects.first()
    
    def run_sync_service(self):
        """Executa serviço de sincronização"""
        try:
            self.stdout.write('🔄 Executando serviço de sincronização...')
            
            sync_service = get_sync_service()
            result = sync_service.force_sync_now()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Sincronização: {result.get("updates_made", 0)} atualizações'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Erro no serviço de sincronização: {str(e)}')
            )
    
    def show_final_status(self, synced_count):
        """Mostra status final"""
        total_cobrancas = CobrancaAsaas.objects.count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 RESULTADO DA SINCRONIZAÇÃO'))
        self.stdout.write('='*50)
        
        self.stdout.write(f'✅ Cobranças sincronizadas: {synced_count}')
        self.stdout.write(f'📊 Total no sistema: {total_cobrancas}')
        
        # Mostrar por status
        if total_cobrancas > 0:
            status_count = {}
            for cobranca in CobrancaAsaas.objects.all():
                status = cobranca.status
                status_count[status] = status_count.get(status, 0) + 1
            
            self.stdout.write('\n📈 Por status:')
            for status, count in status_count.items():
                self.stdout.write(f'  • {status}: {count}')
        
        self.stdout.write('\n🎯 Sincronização concluída!')
        self.stdout.write('💡 Verifique a interface web para confirmar')