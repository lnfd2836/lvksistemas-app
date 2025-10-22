"""
Comando para gerar uma cobrança de teste no Asaas
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from controle_financeiro.models import ControleFinanceiro, CobrancaAsaas
from controle_financeiro.asaas_service import AsaasService
from lojas.models import Loja
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Gera uma cobrança de teste no Asaas com PIX'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loja-id',
            type=int,
            help='ID da loja para gerar cobrança (opcional)'
        )
        parser.add_argument(
            '--valor',
            type=float,
            default=50.00,
            help='Valor da cobrança de teste (padrão: R$ 50,00)'
        )
        parser.add_argument(
            '--dias-vencimento',
            type=int,
            default=7,
            help='Dias para vencimento (padrão: 7 dias)'
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write("🚀 Iniciando geração de cobrança de teste...")
            
            # Buscar loja
            loja_id = options.get('loja_id')
            if loja_id:
                try:
                    loja = Loja.objects.get(id=loja_id)
                    self.stdout.write(f"✅ Loja encontrada: {loja.nome}")
                except Loja.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"❌ Loja com ID {loja_id} não encontrada"))
                    return
            else:
                # Buscar primeira loja disponível
                loja = Loja.objects.first()
                if not loja:
                    self.stdout.write(self.style.ERROR("❌ Nenhuma loja encontrada no sistema"))
                    return
                self.stdout.write(f"✅ Usando primeira loja disponível: {loja.nome}")
            
            # Buscar ou criar controle financeiro
            try:
                controle = ControleFinanceiro.objects.get(loja=loja)
                self.stdout.write(f"✅ Controle financeiro encontrado")
            except ControleFinanceiro.DoesNotExist:
                self.stdout.write(self.style.WARNING("⚠️ Controle financeiro não encontrado, criando..."))
                # Aqui você pode criar um controle básico se necessário
                self.stdout.write(self.style.ERROR("❌ Implemente criação de controle financeiro"))
                return
            
            # Configurar parâmetros
            valor = Decimal(str(options['valor']))
            dias_vencimento = options['dias_vencimento']
            
            self.stdout.write(f"💰 Valor: R$ {valor}")
            self.stdout.write(f"📅 Vencimento: {dias_vencimento} dias")
            
            # Inicializar serviço Asaas
            self.stdout.write("🔧 Inicializando serviço Asaas...")
            asaas_service = AsaasService()
            
            # Validar configuração
            if not asaas_service.validar_configuracao():
                self.stdout.write(self.style.ERROR("❌ Configuração do Asaas inválida"))
                return
            
            self.stdout.write("✅ Configuração Asaas válida")
            
            # Gerar cobrança
            self.stdout.write("📄 Gerando cobrança com PIX...")
            
            resultado = asaas_service.gerar_cobranca_com_pix(
                controle,
                dias_vencimento=dias_vencimento,
                descricao=f"Cobrança de teste - {loja.nome} - {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            )
            
            if resultado.get('success'):
                cobranca_data = resultado['cobranca']
                pix_data = resultado.get('pix', {})
                
                # Salvar no banco
                cobranca = CobrancaAsaas.objects.create(
                    asaas_id=cobranca_data['id'],
                    controle_financeiro=controle,
                    customer_id=cobranca_data['customer'],
                    valor=cobranca_data['value'],
                    data_vencimento=timezone.datetime.fromisoformat(cobranca_data['dueDate']).replace(tzinfo=timezone.utc),
                    descricao=cobranca_data['description'],
                    status=cobranca_data['status'],
                    invoice_url=cobranca_data.get('invoiceUrl', ''),
                    bank_slip_url=cobranca_data.get('bankSlipUrl', ''),
                    invoice_number=cobranca_data.get('invoiceNumber', ''),
                    external_reference=cobranca_data.get('externalReference', ''),
                    api_response=cobranca_data
                )
                
                # Atualizar dados do PIX
                if pix_data:
                    cobranca.pix_qr_code = pix_data.get('qrCode', '')
                    cobranca.pix_copy_paste = pix_data.get('payload', '')
                    if pix_data.get('expirationDate'):
                        cobranca.pix_expires_date = timezone.datetime.fromisoformat(
                            pix_data['expirationDate'].replace('Z', '+00:00')
                        )
                    cobranca.save()
                
                # Exibir resultados
                self.stdout.write(self.style.SUCCESS("🎉 Cobrança gerada com sucesso!"))
                self.stdout.write(f"🆔 ID Asaas: {cobranca.asaas_id}")
                self.stdout.write(f"💰 Valor: R$ {cobranca.valor}")
                self.stdout.write(f"📅 Vencimento: {cobranca.data_vencimento.strftime('%d/%m/%Y')}")
                self.stdout.write(f"🏪 Loja: {loja.nome}")
                
                if cobranca.invoice_url:
                    self.stdout.write(f"🔗 URL do Boleto: {cobranca.invoice_url}")
                
                if cobranca.pix_copy_paste:
                    self.stdout.write("📱 PIX Copia e Cola:")
                    self.stdout.write(f"   {cobranca.pix_copy_paste[:50]}...")
                
                self.stdout.write("\n✅ Cobrança salva no banco de dados local")
                self.stdout.write(f"🔍 ID local: {cobranca.id}")
                
            else:
                error_msg = resultado.get('error', 'Erro desconhecido')
                self.stdout.write(self.style.ERROR(f"❌ Erro ao gerar cobrança: {error_msg}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro geral: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())