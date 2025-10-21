"""
Comando para diagnosticar problemas com webhooks do Asaas
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import CobrancaAsaas, BoletoGerado
from controle_financeiro.asaas_service import AsaasService
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Diagnostica problemas com webhooks do Asaas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-webhook',
            action='store_true',
            help='Testa o endpoint do webhook',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DIAGNÓSTICO DO WEBHOOK ASAAS ==='))
        
        # Verificar configurações
        self.stdout.write('\n--- CONFIGURAÇÕES ---')
        self.stdout.write(f'API Key: {settings.ASAAS_API_KEY[:20]}...')
        self.stdout.write(f'Environment: {settings.ASAAS_ENVIRONMENT}')
        self.stdout.write(f'Site URL: {settings.SITE_URL}')
        
        # Verificar configuração da API
        asaas_service = AsaasService()
        if asaas_service.validar_configuracao():
            self.stdout.write('✅ API configurada corretamente')
        else:
            self.stdout.write('❌ Problema na configuração da API')
        
        # Verificar cobranças existentes
        self.stdout.write('\n--- COBRANÇAS NO BANCO ---')
        cobrancas = CobrancaAsaas.objects.all()
        self.stdout.write(f'Total de cobranças: {cobrancas.count()}')
        
        for cobranca in cobrancas[:5]:
            self.stdout.write(f'  ID: {cobranca.asaas_id}, Status: {cobranca.status}')
        
        # Verificar boletos
        self.stdout.write('\n--- BOLETOS NO BANCO ---')
        boletos = BoletoGerado.objects.all()
        self.stdout.write(f'Total de boletos: {boletos.count()}')
        
        for boleto in boletos[:5]:
            self.stdout.write(f'  ID: {boleto.id}, Número: {boleto.numero_boleto}, Banco: {boleto.configuracao.codigo_banco}')
        
        # Verificar endpoint do webhook
        self.stdout.write('\n--- ENDPOINT DO WEBHOOK ---')
        webhook_url = f"{settings.SITE_URL}/financeiro/asaas/webhook/"
        self.stdout.write(f'URL: {webhook_url}')
        
        if options['test_webhook']:
            self.stdout.write('\n--- TESTANDO WEBHOOK ---')
            try:
                # Teste básico de conectividade
                response = requests.get(webhook_url, timeout=10)
                self.stdout.write(f'Status HTTP: {response.status_code}')
                if response.status_code == 405:  # Method Not Allowed é esperado para GET
                    self.stdout.write('✅ Endpoint acessível (método GET não permitido é normal)')
                else:
                    self.stdout.write(f'⚠️ Resposta inesperada: {response.status_code}')
            except requests.exceptions.RequestException as e:
                self.stdout.write(f'❌ Erro ao acessar webhook: {str(e)}')
        
        # Verificar configuração no Asaas
        self.stdout.write('\n--- CONFIGURAÇÃO NO ASAAS ---')
        self.stdout.write('Para verificar se o webhook está configurado corretamente:')
        self.stdout.write('1. Acesse https://www.asaas.com')
        self.stdout.write('2. Vá em Configurações > Webhooks')
        self.stdout.write('3. Verifique se existe um webhook com:')
        self.stdout.write(f'   URL: {webhook_url}')
        self.stdout.write('   Eventos: PAYMENT_RECEIVED, PAYMENT_CONFIRMED, PAYMENT_OVERDUE')
        self.stdout.write('   Status: Ativo')
        
        # Verificar logs recentes
        self.stdout.write('\n--- LOGS RECENTES ---')
        self.stdout.write('Para ver logs detalhados, execute:')
        self.stdout.write('heroku logs --tail --app lvksistemas-app')
        
        self.stdout.write('\n=== DIAGNÓSTICO CONCLUÍDO ===')
