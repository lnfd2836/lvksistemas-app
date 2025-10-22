from django.core.management.base import BaseCommand
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sincroniza cobranças do Asaas com o banco local'

    def handle(self, *args, **options):
        self.stdout.write("=== SINCRONIZAÇÃO ASAAS ===")
        
        try:
            # Inicializar serviço Asaas
            asaas_service = AsaasService()
            
            # Buscar todas as cobranças no Asaas
            self.stdout.write("Buscando cobranças no Asaas...")
            
            response = asaas_service._fazer_requisicao('GET', '/payments', params={
                'limit': 100,
                'offset': 0
            })
            
            if response and response.get('data'):
                cobrancas_asaas = response['data']
                self.stdout.write(f"Encontradas {len(cobrancas_asaas)} cobranças no Asaas")
                
                for cobranca_data in cobrancas_asaas:
                    asaas_id = cobranca_data['id']
                    self.stdout.write(f"\nProcessando cobrança: {asaas_id}")
                    
                    # Verificar se já existe no banco local
                    cobranca_local = CobrancaAsaas.objects.filter(asaas_id=asaas_id).first()
                    
                    if cobranca_local:
                        self.stdout.write(f"  ✓ Já existe no banco local")
                        
                        # Atualizar dados se necessário
                        if not cobranca_local.bank_slip_url and cobranca_data.get('bankSlipUrl'):
                            cobranca_local.bank_slip_url = cobranca_data['bankSlipUrl']
                            cobranca_local.save()
                            self.stdout.write(f"  ✓ Bank Slip URL atualizada")
                            
                        if not cobranca_local.invoice_url and cobranca_data.get('invoiceUrl'):
                            cobranca_local.invoice_url = cobranca_data['invoiceUrl']
                            cobranca_local.save()
                            self.stdout.write(f"  ✓ Invoice URL atualizada")
                            
                        # Tentar gerar PIX se não existir
                        if not cobranca_local.pix_qr_code:
                            self.stdout.write(f"  → Tentando gerar PIX...")
                            pix_data = asaas_service._gerar_pix_cobranca(asaas_id)
                            if pix_data:
                                cobranca_local.pix_qr_code = pix_data.get('qrCode', '')
                                cobranca_local.pix_copy_paste = pix_data.get('payload', '')
                                if pix_data.get('expirationDate'):
                                    cobranca_local.pix_expires_date = timezone.datetime.fromisoformat(
                                        pix_data['expirationDate'].replace('Z', '+00:00')
                                    )
                                cobranca_local.save()
                                self.stdout.write(f"  ✓ PIX gerado e salvo")
                            else:
                                self.stdout.write(f"  ✗ Erro ao gerar PIX")
                    else:
                        self.stdout.write(f"  ⚠ Cobrança não existe no banco local")
                        self.stdout.write(f"    Customer ID: {cobranca_data.get('customer')}")
                        self.stdout.write(f"    Valor: R$ {cobranca_data.get('value')}")
                        self.stdout.write(f"    Status: {cobranca_data.get('status')}")
                        self.stdout.write(f"    Data Vencimento: {cobranca_data.get('dueDate')}")
                        self.stdout.write(f"    Bank Slip URL: {cobranca_data.get('bankSlipUrl', 'N/A')}")
                        
                        # Tentar encontrar controle financeiro baseado na referência externa
                        external_ref = cobranca_data.get('externalReference', '')
                        if external_ref and external_ref.startswith('CF_'):
                            try:
                                controle_id = external_ref.split('_')[1]
                                controle = ControleFinanceiro.objects.get(id=controle_id)
                                
                                self.stdout.write(f"  → Criando cobrança no banco local...")
                                
                                # Criar cobrança no banco local
                                nova_cobranca = CobrancaAsaas.objects.create(
                                    asaas_id=cobranca_data['id'],
                                    controle_financeiro=controle,
                                    customer_id=cobranca_data['customer'],
                                    valor=cobranca_data['value'],
                                    data_vencimento=timezone.datetime.fromisoformat(cobranca_data['dueDate']).replace(tzinfo=timezone.utc),
                                    descricao=cobranca_data.get('description', ''),
                                    status=cobranca_data['status'],
                                    invoice_url=cobranca_data.get('invoiceUrl', ''),
                                    bank_slip_url=cobranca_data.get('bankSlipUrl', ''),
                                    invoice_number=cobranca_data.get('invoiceNumber', ''),
                                    external_reference=cobranca_data.get('externalReference', ''),
                                    api_response=cobranca_data
                                )
                                
                                self.stdout.write(f"  ✓ Cobrança criada no banco local")
                                
                                # Tentar gerar PIX
                                self.stdout.write(f"  → Tentando gerar PIX...")
                                pix_data = asaas_service._gerar_pix_cobranca(asaas_id)
                                if pix_data:
                                    nova_cobranca.pix_qr_code = pix_data.get('qrCode', '')
                                    nova_cobranca.pix_copy_paste = pix_data.get('payload', '')
                                    if pix_data.get('expirationDate'):
                                        nova_cobranca.pix_expires_date = timezone.datetime.fromisoformat(
                                            pix_data['expirationDate'].replace('Z', '+00:00')
                                        )
                                    nova_cobranca.save()
                                    self.stdout.write(f"  ✓ PIX gerado e salvo")
                                else:
                                    self.stdout.write(f"  ✗ Erro ao gerar PIX")
                                    
                            except ControleFinanceiro.DoesNotExist:
                                self.stdout.write(f"  ✗ Controle financeiro não encontrado: {controle_id}")
                            except Exception as e:
                                self.stdout.write(f"  ✗ Erro ao criar cobrança: {str(e)}")
                        else:
                            self.stdout.write(f"  ✗ Referência externa inválida: {external_ref}")
                
                self.stdout.write(f"\n=== SINCRONIZAÇÃO CONCLUÍDA ===")
                
            else:
                self.stdout.write("Nenhuma cobrança encontrada no Asaas")
                
        except Exception as e:
            self.stdout.write(f"Erro na sincronização: {str(e)}")
            logger.error(f"Erro na sincronização Asaas: {str(e)}")
    
    def _fazer_requisicao(self, asaas_service, method, endpoint, **kwargs):
        """Helper para fazer requisições à API do Asaas"""
        import requests
        
        url = f"{asaas_service.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=asaas_service.headers, **kwargs)
            elif method == 'POST':
                response = requests.post(url, headers=asaas_service.headers, **kwargs)
            else:
                return None
                
            if response.status_code == 200:
                return response.json()
            else:
                self.stdout.write(f"Erro na API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.stdout.write(f"Erro na requisição: {str(e)}")
            return None