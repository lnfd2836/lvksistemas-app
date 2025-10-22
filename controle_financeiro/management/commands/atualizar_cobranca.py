from django.core.management.base import BaseCommand
from controle_financeiro.models import CobrancaAsaas
from controle_financeiro.asaas_service import AsaasService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Atualiza uma cobrança específica do Asaas'

    def add_arguments(self, parser):
        parser.add_argument('cobranca_id', type=str, help='ID da cobrança (UUID)')

    def handle(self, *args, **options):
        cobranca_id = options['cobranca_id']
        
        try:
            cobranca = CobrancaAsaas.objects.get(id=cobranca_id)
            self.stdout.write(f"Encontrada cobrança: {cobranca.asaas_id}")
            
            # Inicializar serviço Asaas
            asaas_service = AsaasService()
            
            # Consultar cobrança no Asaas
            self.stdout.write("Consultando cobrança no Asaas...")
            dados_atualizados = asaas_service.consultar_cobranca(cobranca.asaas_id)
            
            if dados_atualizados:
                self.stdout.write("Dados recebidos do Asaas:")
                self.stdout.write(f"Status: {dados_atualizados.get('status')}")
                self.stdout.write(f"Bank Slip URL: {dados_atualizados.get('bankSlipUrl')}")
                self.stdout.write(f"Invoice URL: {dados_atualizados.get('invoiceUrl')}")
                
                # Atualizar dados da cobrança
                cobranca.atualizar_dados_asaas(dados_atualizados)
                self.stdout.write("Cobrança atualizada no banco de dados")
                
                # Tentar gerar PIX se não existir
                if not cobranca.pix_qr_code:
                    self.stdout.write("Tentando gerar PIX...")
                    pix_data = asaas_service._gerar_pix_cobranca(cobranca.asaas_id)
                    
                    if pix_data:
                        self.stdout.write("PIX gerado com sucesso!")
                        cobranca.pix_qr_code = pix_data.get('qrCode', '')
                        cobranca.pix_copy_paste = pix_data.get('payload', '')
                        if pix_data.get('expirationDate'):
                            from django.utils import timezone
                            cobranca.pix_expires_date = timezone.datetime.fromisoformat(
                                pix_data['expirationDate'].replace('Z', '+00:00')
                            )
                        cobranca.save()
                        self.stdout.write("PIX salvo no banco de dados")
                    else:
                        self.stdout.write("Erro ao gerar PIX")
                else:
                    self.stdout.write("PIX já existe na cobrança")
                    
            else:
                self.stdout.write("Erro ao consultar cobrança no Asaas")
                
        except CobrancaAsaas.DoesNotExist:
            self.stdout.write(f"Cobrança {cobranca_id} não encontrada")
        except Exception as e:
            self.stdout.write(f"Erro: {str(e)}")
            logger.error(f"Erro ao atualizar cobrança: {str(e)}")