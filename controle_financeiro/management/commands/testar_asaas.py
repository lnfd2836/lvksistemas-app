"""
Comando Django para testar a integração com Asaas
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from controle_financeiro.asaas_service import AsaasService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Testa a integração com a API do Asaas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apenas-conexao',
            action='store_true',
            help='Testa apenas a conexão com a API',
        )
        parser.add_argument(
            '--detalhado',
            action='store_true',
            help='Mostra informações detalhadas',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("🔍 TESTE DA INTEGRAÇÃO ASAAS")
        self.stdout.write("=" * 60)
        
        # Mostrar configurações
        api_key = getattr(settings, 'ASAAS_API_KEY', None)
        environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
        
        self.stdout.write(f"📋 Configurações:")
        self.stdout.write(f"   Environment: {environment}")
        self.stdout.write(f"   API Key: {'✅ Configurada' if api_key else '❌ Não configurada'}")
        
        if options['detalhado'] and api_key:
            # Mostrar apenas os primeiros e últimos caracteres da API Key
            masked_key = f"{api_key[:10]}...{api_key[-10:]}" if len(api_key) > 20 else api_key
            self.stdout.write(f"   API Key (mascarada): {masked_key}")
        
        self.stdout.write("")
        
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ ASAAS_API_KEY não configurada!"))
            return
        
        try:
            # Instanciar serviço
            service = AsaasService()
            self.stdout.write("✅ AsaasService instanciado com sucesso")
            
            # Testar validação
            self.stdout.write("🔍 Testando validação de configuração...")
            
            if service.validar_configuracao():
                self.stdout.write(self.style.SUCCESS("✅ CONFIGURAÇÃO VÁLIDA!"))
                self.stdout.write("🎉 A API do Asaas está funcionando corretamente")
                
                if not options['apenas_conexao']:
                    self.stdout.write("\n📊 Testando funcionalidades adicionais...")
                    
                    # Testar busca de clientes (sem criar)
                    try:
                        import requests
                        response = requests.get(
                            f"{service.base_url}/customers?limit=1",
                            headers=service.headers,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            total_clientes = data.get('totalCount', 0)
                            self.stdout.write(f"👥 Total de clientes: {total_clientes}")
                        
                    except Exception as e:
                        self.stdout.write(f"⚠️ Erro ao buscar clientes: {str(e)}")
                    
                    # Testar busca de pagamentos (sem criar)
                    try:
                        response = requests.get(
                            f"{service.base_url}/payments?limit=1",
                            headers=service.headers,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            total_pagamentos = data.get('totalCount', 0)
                            self.stdout.write(f"💰 Total de pagamentos: {total_pagamentos}")
                        
                    except Exception as e:
                        self.stdout.write(f"⚠️ Erro ao buscar pagamentos: {str(e)}")
                
            else:
                self.stdout.write(self.style.ERROR("❌ CONFIGURAÇÃO INVÁLIDA!"))
                self.stdout.write("🔧 Verifique:")
                self.stdout.write("   - API Key do Asaas")
                self.stdout.write("   - Configurações de rede/firewall")
                self.stdout.write("   - Status do serviço Asaas")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro inesperado: {str(e)}"))
            
            if options['detalhado']:
                import traceback
                self.stdout.write(traceback.format_exc())
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🏁 Teste finalizado")
        self.stdout.write("=" * 60)