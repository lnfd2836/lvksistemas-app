"""
Comando para testar geração de boletos no Heroku
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import ControleFinanceiro, ConfiguracaoBoleto
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.pdf_service import BoletoPDFService
from django.conf import settings
from decimal import Decimal
from datetime import datetime
from django.utils import timezone


class Command(BaseCommand):
    help = 'Testa geração de boletos no Heroku'

    def add_arguments(self, parser):
        parser.add_argument(
            '--controle-id',
            type=int,
            help='ID do controle financeiro para testar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== TESTE DE GERAÇÃO DE BOLETOS ==='))
        
        # Verificar configurações
        self.stdout.write('\n--- CONFIGURAÇÕES ---')
        self.stdout.write(f'API Key: {settings.ASAAS_API_KEY[:10]}...' if settings.ASAAS_API_KEY else 'API Key: NÃO CONFIGURADA')
        self.stdout.write(f'Environment: {settings.ASAAS_ENVIRONMENT}')
        self.stdout.write(f'Site URL: {settings.SITE_URL}')
        
        # Buscar controle financeiro
        if options['controle_id']:
            try:
                controle = ControleFinanceiro.objects.get(id=options['controle_id'])
            except ControleFinanceiro.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Controle financeiro {options["controle_id"]} não encontrado'))
                return
        else:
            controle = ControleFinanceiro.objects.first()
            if not controle:
                self.stdout.write(self.style.ERROR('Nenhum controle financeiro encontrado'))
                return
        
        self.stdout.write(f'\nControle financeiro: {controle.id} - {controle.loja.nome}')
        self.stdout.write(f'Valor mensal: R$ {controle.valor_mensal}')
        
        # Buscar configuração do Asaas
        config = ConfiguracaoBoleto.objects.filter(codigo_banco="461", ativo=True).first()
        if not config:
            self.stdout.write(self.style.ERROR('Configuração do Asaas não encontrada'))
            return
        
        self.stdout.write(f'\nConfiguração: {config.codigo_banco} - {config.nome_banco}')
        
        # Testar API do Asaas
        self.stdout.write('\n--- TESTE DA API ASAAS ---')
        asaas_service = AsaasService()
        
        if not asaas_service.validar_configuracao():
            self.stdout.write(self.style.ERROR('❌ Configuração da API inválida'))
            return
        
        self.stdout.write('✅ Configuração da API válida')
        
        # Tentar gerar cobrança
        try:
            self.stdout.write('\nGerando cobrança...')
            dados_boleto = asaas_service.gerar_cobranca_com_pix(controle, dias_vencimento=30)
            
            if dados_boleto.get('success'):
                self.stdout.write(self.style.SUCCESS('✅ Cobrança criada com sucesso!'))
                cobranca = dados_boleto['cobranca']
                pix_data = dados_boleto.get('pix', {})
                
                self.stdout.write(f'ID da cobrança: {cobranca["id"]}')
                self.stdout.write(f'Valor: R$ {cobranca["value"]}')
                self.stdout.write(f'Status: {cobranca["status"]}')
                self.stdout.write(f'Vencimento: {cobranca["dueDate"]}')
                
                if pix_data:
                    self.stdout.write(f'PIX gerado: {bool(pix_data.get("encodedImage"))}')
                    self.stdout.write(f'PIX payload: {bool(pix_data.get("payload"))}')
                else:
                    self.stdout.write('❌ PIX não gerado')
                
                # Testar geração do PDF
                self.stdout.write('\n--- TESTE DE GERAÇÃO DE PDF ---')
                
                # Criar boleto temporário para teste
                from controle_financeiro.models import BoletoGerado, CobrancaAsaas
                
                boleto = BoletoGerado.objects.create(
                    controle_financeiro=controle,
                    configuracao=config,
                    numero_boleto=cobranca['id'],
                    linha_digitavel=cobranca.get('bankSlipUrl', ''),
                    codigo_barras=cobranca.get('bankSlipUrl', ''),
                    valor=Decimal(str(cobranca['value'])),
                    data_vencimento=datetime.strptime(cobranca['dueDate'], '%Y-%m-%d').date()
                )
                
                # Salvar dados do PIX
                if pix_data:
                    CobrancaAsaas.objects.create(
                        asaas_id=cobranca['id'],
                        controle_financeiro=controle,
                        customer_id=cobranca.get('customer', ''),
                        valor=Decimal(str(cobranca['value'])),
                        data_vencimento=datetime.strptime(cobranca['dueDate'], '%Y-%m-%d'),
                        descricao=cobranca.get('description', ''),
                        status=cobranca['status'],
                        invoice_url=cobranca.get('invoiceUrl', ''),
                        bank_slip_url=cobranca.get('bankSlipUrl', ''),
                        invoice_number=cobranca.get('invoiceNumber', ''),
                        pix_qr_code=pix_data.get('encodedImage', ''),
                        pix_copy_paste=pix_data.get('payload', ''),
                        external_reference=cobranca.get('externalReference', ''),
                        api_response=cobranca
                    )
                
                # Testar PDF
                pdf_service = BoletoPDFService()
                try:
                    pdf_response = pdf_service.gerar_pdf_boleto_asaas(boleto)
                    self.stdout.write(self.style.SUCCESS('✅ PDF gerado com sucesso!'))
                    self.stdout.write(f'Tamanho do PDF: {len(pdf_response.content)} bytes')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Erro ao gerar PDF: {str(e)}'))
                
                # Limpar boleto de teste
                boleto.delete()
                
            else:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao criar cobrança: {dados_boleto.get("error")}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Exceção: {str(e)}'))
            import traceback
            traceback.print_exc()
        
        self.stdout.write('\n=== TESTE CONCLUÍDO ===')
