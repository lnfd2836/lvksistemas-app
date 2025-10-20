"""
Comando para verificar se o sistema está pronto para produção
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import requests


class Command(BaseCommand):
    help = 'Verifica se o sistema está configurado corretamente para produção'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Verificação de Produção - Asaas ===\n')
        )

        errors = []
        warnings = []
        success = []

        # 1. Verificar ambiente
        self.stdout.write('1. Verificando ambiente...')
        
        if 'DYNO' in os.environ:
            success.append('✅ Executando no Heroku')
        else:
            warnings.append('⚠️  Não está executando no Heroku')

        # 2. Verificar configurações Django
        self.stdout.write('\n2. Verificando configurações Django...')
        
        if not settings.DEBUG:
            success.append('✅ DEBUG=False (produção)')
        else:
            errors.append('❌ DEBUG=True (deve ser False em produção)')

        if settings.SECRET_KEY and len(settings.SECRET_KEY) > 20:
            success.append('✅ SECRET_KEY configurada')
        else:
            errors.append('❌ SECRET_KEY não configurada ou muito simples')

        # 3. Verificar configurações Asaas
        self.stdout.write('\n3. Verificando configurações Asaas...')
        
        api_key = getattr(settings, 'ASAAS_API_KEY', None)
        if api_key and len(api_key) > 10:
            success.append('✅ ASAAS_API_KEY configurada')
        else:
            errors.append('❌ ASAAS_API_KEY não configurada')

        environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
        if environment == 'production':
            success.append('✅ ASAAS_ENVIRONMENT=production')
        else:
            warnings.append('⚠️  ASAAS_ENVIRONMENT=sandbox (ambiente de teste)')

        site_url = getattr(settings, 'SITE_URL', '')
        if site_url.startswith('https://'):
            success.append('✅ SITE_URL com HTTPS')
        else:
            errors.append('❌ SITE_URL deve usar HTTPS em produção')

        # 4. Testar conexão com Asaas
        self.stdout.write('\n4. Testando conexão com Asaas...')
        
        if api_key:
            try:
                from controle_financeiro.asaas_service import AsaasService
                asaas_service = AsaasService()
                
                if asaas_service.validar_configuracao():
                    success.append('✅ Conexão com Asaas funcionando')
                else:
                    errors.append('❌ Falha na conexão com Asaas')
                    
            except Exception as e:
                errors.append(f'❌ Erro ao testar Asaas: {str(e)}')

        # 5. Verificar URL do webhook
        self.stdout.write('\n5. Verificando URL do webhook...')
        
        webhook_url = f"{site_url}/financeiro/asaas/webhook/"
        if site_url:
            try:
                # Testar se a URL está acessível
                response = requests.get(site_url, timeout=10)
                if response.status_code < 500:
                    success.append('✅ Site acessível')
                    success.append(f'✅ URL do webhook: {webhook_url}')
                else:
                    errors.append(f'❌ Site retornou erro {response.status_code}')
                    
            except Exception as e:
                warnings.append(f'⚠️  Não foi possível testar o site: {str(e)}')

        # 6. Verificar banco de dados
        self.stdout.write('\n6. Verificando banco de dados...')
        
        try:
            from controle_financeiro.models import ConfiguracaoBoleto
            config_count = ConfiguracaoBoleto.objects.count()
            
            if config_count > 0:
                success.append(f'✅ {config_count} configuração(ões) de boleto encontrada(s)')
            else:
                warnings.append('⚠️  Nenhuma configuração de boleto encontrada')
                
        except Exception as e:
            errors.append(f'❌ Erro no banco de dados: {str(e)}')

        # 7. Verificar configurações de segurança
        self.stdout.write('\n7. Verificando segurança...')
        
        if hasattr(settings, 'SECURE_SSL_REDIRECT') and settings.SECURE_SSL_REDIRECT:
            success.append('✅ SSL redirect ativado')
        else:
            warnings.append('⚠️  SSL redirect não configurado')

        if hasattr(settings, 'SECURE_PROXY_SSL_HEADER'):
            success.append('✅ Proxy SSL header configurado')
        else:
            warnings.append('⚠️  Proxy SSL header não configurado')

        # Mostrar resultados
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESULTADO DA VERIFICAÇÃO')
        self.stdout.write('='*50)

        if success:
            self.stdout.write('\n✅ SUCESSOS:')
            for item in success:
                self.stdout.write(f'   {item}')

        if warnings:
            self.stdout.write(f'\n⚠️  AVISOS ({len(warnings)}):')
            for item in warnings:
                self.stdout.write(f'   {item}')

        if errors:
            self.stdout.write(f'\n❌ ERROS ({len(errors)}):')
            for item in errors:
                self.stdout.write(f'   {item}')

        # Conclusão
        self.stdout.write('\n' + '='*50)
        
        if errors:
            self.stdout.write(
                self.style.ERROR('❌ SISTEMA NÃO ESTÁ PRONTO PARA PRODUÇÃO')
            )
            self.stdout.write('Corrija os erros acima antes de usar em produção.')
        elif warnings:
            self.stdout.write(
                self.style.WARNING('⚠️  SISTEMA PARCIALMENTE PRONTO')
            )
            self.stdout.write('Verifique os avisos acima para melhor segurança.')
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ SISTEMA PRONTO PARA PRODUÇÃO!')
            )

        # Instruções finais
        self.stdout.write('\n📋 PRÓXIMOS PASSOS:')
        
        if environment != 'production':
            self.stdout.write('   1. Configure ASAAS_ENVIRONMENT=production')
            self.stdout.write('   2. Obtenha API Key de produção do Asaas')
        
        self.stdout.write('   3. Configure webhook no painel do Asaas:')
        self.stdout.write(f'      URL: {webhook_url}')
        self.stdout.write('      Eventos: PAYMENT_RECEIVED, PAYMENT_CONFIRMED, PAYMENT_OVERDUE')
        
        self.stdout.write('   4. Teste com uma cobrança real')
        self.stdout.write('   5. Monitore logs: heroku logs --tail')

        return len(errors) == 0