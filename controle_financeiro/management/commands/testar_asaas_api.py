"""
Comando para testar a API do Asaas
"""

from django.core.management.base import BaseCommand
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import ControleFinanceiro, ConfiguracaoBoleto
from django.conf import settings


class Command(BaseCommand):
    help = 'Testa a API do Asaas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-cobranca',
            action='store_true',
            help='Testa criação de cobrança',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== TESTE DA API ASAAS ==='))
        
        # Verificar configurações
        self.stdout.write(f'API Key: {settings.ASAAS_API_KEY[:10]}...' if settings.ASAAS_API_KEY else 'API Key: NÃO CONFIGURADA')
        self.stdout.write(f'Environment: {settings.ASAAS_ENVIRONMENT}')
        self.stdout.write(f'Site URL: {settings.SITE_URL}')
        
        # Criar serviço
        asaas_service = AsaasService()
        
        # Testar validação
        self.stdout.write('\n--- VALIDAÇÃO DA CONFIGURAÇÃO ---')
        if asaas_service.validar_configuracao():
            self.stdout.write(self.style.SUCCESS('✅ Configuração válida'))
        else:
            self.stdout.write(self.style.ERROR('❌ Configuração inválida'))
            return
        
        # Testar criação de cobrança se solicitado
        if options['test_cobranca']:
            self.stdout.write('\n--- TESTE DE CRIAÇÃO DE COBRANÇA ---')
            
            # Buscar um controle financeiro para teste
            controle = ControleFinanceiro.objects.first()
            if not controle:
                self.stdout.write(self.style.ERROR('❌ Nenhum controle financeiro encontrado'))
                return
            
            self.stdout.write(f'Testando com controle: {controle.id} - {controle.loja.nome}')
            
            try:
                resultado = asaas_service.gerar_cobranca_com_pix(controle, dias_vencimento=30)
                
                if resultado.get('success'):
                    self.stdout.write(self.style.SUCCESS('✅ Cobrança criada com sucesso!'))
                    cobranca = resultado['cobranca']
                    self.stdout.write(f'ID da cobrança: {cobranca["id"]}')
                    self.stdout.write(f'Valor: R$ {cobranca["value"]}')
                    self.stdout.write(f'Vencimento: {cobranca["dueDate"]}')
                    self.stdout.write(f'Status: {cobranca["status"]}')
                    
                    if resultado.get('pix'):
                        pix = resultado['pix']
                        self.stdout.write(f'PIX gerado: {pix.get("payload", "N/A")[:50]}...')
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Erro ao criar cobrança: {resultado.get("error")}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Exceção: {str(e)}'))
        
        self.stdout.write('\n=== TESTE CONCLUÍDO ===')
