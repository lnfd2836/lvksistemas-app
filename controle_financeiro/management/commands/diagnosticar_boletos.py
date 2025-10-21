"""
Comando para diagnosticar problemas de geração de boletos no Heroku
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import BoletoGerado, ConfiguracaoBoleto, ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService
from django.conf import settings


class Command(BaseCommand):
    help = 'Diagnostica problemas de geração de boletos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--boleto-id',
            type=int,
            help='ID do boleto para diagnosticar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DIAGNÓSTICO DE BOLETOS ==='))
        
        # Verificar configurações
        self.stdout.write('\n--- CONFIGURAÇÕES ---')
        configs = ConfiguracaoBoleto.objects.all()
        self.stdout.write(f'Total de configurações: {configs.count()}')
        
        for config in configs:
            self.stdout.write(f'\nConfiguração ID {config.id}:')
            self.stdout.write(f'  Banco: {config.codigo_banco} - {config.nome_banco}')
            self.stdout.write(f'  Ativo: {config.ativo}')
            self.stdout.write(f'  Agência: {config.agencia}')
            self.stdout.write(f'  Conta: {config.conta}')
        
        # Verificar configuração ativa
        config_ativa = ConfiguracaoBoleto.objects.filter(ativo=True).first()
        if config_ativa:
            self.stdout.write(f'\n✅ Configuração ativa: {config_ativa.codigo_banco} - {config_ativa.nome_banco}')
            
            # Verificar se é Asaas
            if config_ativa.codigo_banco == "461":
                self.stdout.write('✅ Configuração é do Asaas')
            else:
                self.stdout.write(f'❌ Configuração não é do Asaas: {config_ativa.codigo_banco}')
        else:
            self.stdout.write('\n❌ Nenhuma configuração ativa encontrada')
        
        # Verificar API do Asaas
        self.stdout.write('\n--- API ASAAS ---')
        self.stdout.write(f'API Key: {settings.ASAAS_API_KEY[:10]}...' if settings.ASAAS_API_KEY else 'API Key: NÃO CONFIGURADA')
        self.stdout.write(f'Environment: {settings.ASAAS_ENVIRONMENT}')
        
        asaas_service = AsaasService()
        if asaas_service.validar_configuracao():
            self.stdout.write('✅ Configuração da API válida')
        else:
            self.stdout.write('❌ Configuração da API inválida')
        
        # Verificar boletos
        self.stdout.write('\n--- BOLETOS ---')
        boletos = BoletoGerado.objects.all().order_by('-id')[:10]
        self.stdout.write(f'Total de boletos: {BoletoGerado.objects.count()}')
        
        for boleto in boletos:
            self.stdout.write(f'\nBoleto ID {boleto.id}:')
            self.stdout.write(f'  Número: {boleto.numero_boleto}')
            self.stdout.write(f'  Banco: {boleto.configuracao.codigo_banco} - {boleto.configuracao.nome_banco}')
            self.stdout.write(f'  Valor: R$ {boleto.valor}')
            self.stdout.write(f'  Status: {boleto.status}')
            self.stdout.write(f'  Linha digitável: {boleto.linha_digitavel[:50]}...')
            
            # Verificar se tem PIX
            from controle_financeiro.models import CobrancaAsaas
            cobrancas = CobrancaAsaas.objects.filter(controle_financeiro=boleto.controle_financeiro)
            if cobrancas.exists():
                cobranca = cobrancas.first()
                self.stdout.write(f'  ✅ Tem CobrancaAsaas: {cobranca.asaas_id}')
                self.stdout.write(f'  PIX QR: {bool(cobranca.pix_qr_code)}')
                self.stdout.write(f'  PIX Copy: {bool(cobranca.pix_copy_paste)}')
            else:
                self.stdout.write(f'  ❌ Sem CobrancaAsaas')
        
        # Diagnosticar boleto específico se fornecido
        if options['boleto_id']:
            self.stdout.write(f'\n--- DIAGNÓSTICO BOLETO {options["boleto_id"]} ---')
            try:
                boleto = BoletoGerado.objects.get(id=options['boleto_id'])
                self.stdout.write(f'Boleto encontrado: {boleto.numero_boleto}')
                
                # Verificar se é boleto simulado
                if boleto.numero_boleto.startswith('BOL'):
                    self.stdout.write('❌ Este é um boleto simulado (não gerado via Asaas)')
                    self.stdout.write('Motivo: Número do boleto começa com "BOL"')
                else:
                    self.stdout.write('✅ Este parece ser um boleto do Asaas')
                
                # Verificar configuração usada
                if boleto.configuracao.codigo_banco == "461":
                    self.stdout.write('✅ Usou configuração do Asaas')
                else:
                    self.stdout.write(f'❌ Não usou configuração do Asaas: {boleto.configuracao.codigo_banco}')
                
            except BoletoGerado.DoesNotExist:
                self.stdout.write(f'❌ Boleto {options["boleto_id"]} não encontrado')
        
        self.stdout.write('\n=== DIAGNÓSTICO CONCLUÍDO ===')
