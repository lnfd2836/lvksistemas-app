"""
Comando para testar a integração com a API do Asaas
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import ControleFinanceiro


class Command(BaseCommand):
    help = 'Testa a integração com a API do Asaas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--controle-id',
            type=int,
            help='ID do controle financeiro para testar geração de cobrança'
        )
        parser.add_argument(
            '--apenas-conexao',
            action='store_true',
            help='Testa apenas a conexão com a API'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Teste da Integração Asaas ===\n')
        )

        # Verificar configurações
        self.stdout.write('1. Verificando configurações...')
        
        api_key = getattr(settings, 'ASAAS_API_KEY', None)
        environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
        
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ ASAAS_API_KEY não configurada')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ API Key configurada (ambiente: {environment})')
        )

        # Testar conexão
        self.stdout.write('\n2. Testando conexão com a API...')
        
        try:
            asaas_service = AsaasService()
            
            if asaas_service.validar_configuracao():
                self.stdout.write(
                    self.style.SUCCESS('✅ Conexão estabelecida com sucesso!')
                )
                self.stdout.write(f'   URL Base: {asaas_service.base_url}')
                self.stdout.write(f'   Ambiente: {asaas_service.environment}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Falha na conexão com a API')
                )
                return
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na conexão: {str(e)}')
            )
            return

        # Se apenas teste de conexão, parar aqui
        if options['apenas_conexao']:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Teste de conexão concluído com sucesso!')
            )
            return

        # Testar geração de cobrança
        controle_id = options.get('controle_id')
        
        if controle_id:
            self.stdout.write(f'\n3. Testando geração de cobrança (ID: {controle_id})...')
            
            try:
                controle = ControleFinanceiro.objects.get(id=controle_id)
                self.stdout.write(f'   Loja: {controle.loja.nome}')
                self.stdout.write(f'   Valor: R$ {controle.valor_mensal}')
                
                # Gerar cobrança de teste
                resultado = asaas_service.gerar_cobranca_com_pix(
                    controle,
                    dias_vencimento=30,
                    descricao=f'Teste de cobrança - {controle.loja.nome}'
                )
                
                if resultado.get('success'):
                    cobranca = resultado['cobranca']
                    pix = resultado.get('pix', {})
                    
                    self.stdout.write(
                        self.style.SUCCESS('✅ Cobrança gerada com sucesso!')
                    )
                    self.stdout.write(f'   ID Asaas: {cobranca["id"]}')
                    self.stdout.write(f'   Status: {cobranca["status"]}')
                    self.stdout.write(f'   Valor: R$ {cobranca["value"]}')
                    self.stdout.write(f'   Vencimento: {cobranca["dueDate"]}')
                    
                    if cobranca.get('invoiceUrl'):
                        self.stdout.write(f'   URL Boleto: {cobranca["invoiceUrl"]}')
                    
                    if pix.get('qrCode'):
                        self.stdout.write('   ✅ PIX QR Code gerado')
                    
                    if pix.get('payload'):
                        self.stdout.write('   ✅ PIX Copia e Cola gerado')
                        
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erro na geração: {resultado.get("error")}')
                    )
                    
            except ControleFinanceiro.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Controle financeiro ID {controle_id} não encontrado')
                )
                return
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro na geração de cobrança: {str(e)}')
                )
                return
        else:
            self.stdout.write('\n3. Para testar geração de cobrança, use --controle-id=ID')

        # Informações da conta
        self.stdout.write('\n4. Dados da conta Asaas configurada:')
        conta_dados = asaas_service.conta_dados
        for key, value in conta_dados.items():
            self.stdout.write(f'   {key.replace("_", " ").title()}: {value}')

        self.stdout.write(
            self.style.SUCCESS('\n✅ Teste concluído com sucesso!')
        )
        
        # Dicas
        self.stdout.write('\n📋 Próximos passos:')
        self.stdout.write('   1. Configure o webhook no painel do Asaas')
        self.stdout.write(f'   2. URL do webhook: {settings.SITE_URL}/financeiro/asaas/webhook/')
        self.stdout.write('   3. Eventos recomendados: PAYMENT_RECEIVED, PAYMENT_OVERDUE')
        self.stdout.write('   4. Teste pagamentos no ambiente sandbox')