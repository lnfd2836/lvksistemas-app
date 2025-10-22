"""
Comando para testar conexão com Asaas
"""
from django.core.management.base import BaseCommand
from controle_financeiro.asaas_service import AsaasService
import requests


class Command(BaseCommand):
    help = 'Testa conexão com a API do Asaas'

    def handle(self, *args, **options):
        try:
            self.stdout.write("🔧 Testando conexão com Asaas...")
            
            # Inicializar serviço
            asaas_service = AsaasService()
            
            self.stdout.write(f"🌐 Environment: {asaas_service.environment}")
            self.stdout.write(f"🔗 Base URL: {asaas_service.base_url}")
            self.stdout.write(f"🔑 API Key: {asaas_service.api_key[:20]}...")
            
            # Teste básico de conexão
            self.stdout.write("\n📡 Testando endpoint /myAccount...")
            
            try:
                response = requests.get(
                    f"{asaas_service.base_url}/myAccount",
                    headers=asaas_service.headers,
                    timeout=30
                )
                
                self.stdout.write(f"📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    account_data = response.json()
                    self.stdout.write("✅ Conexão bem-sucedida!")
                    self.stdout.write(f"👤 Nome da conta: {account_data.get('name', 'N/A')}")
                    self.stdout.write(f"📧 Email: {account_data.get('email', 'N/A')}")
                    self.stdout.write(f"💰 Wallet ID: {account_data.get('walletId', 'N/A')}")
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Erro na API: {response.status_code}"))
                    self.stdout.write(f"📄 Resposta: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"❌ Erro de conexão: {str(e)}"))
            
            # Teste de listagem de clientes
            self.stdout.write("\n📡 Testando endpoint /customers...")
            
            try:
                response = requests.get(
                    f"{asaas_service.base_url}/customers",
                    headers=asaas_service.headers,
                    params={'limit': 1},
                    timeout=30
                )
                
                self.stdout.write(f"📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    customers_data = response.json()
                    total = customers_data.get('totalCount', 0)
                    self.stdout.write(f"✅ Clientes encontrados: {total}")
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Erro ao listar clientes: {response.status_code}"))
                    self.stdout.write(f"📄 Resposta: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"❌ Erro ao listar clientes: {str(e)}"))
            
            self.stdout.write("\n✅ Teste de conexão concluído")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro geral: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())