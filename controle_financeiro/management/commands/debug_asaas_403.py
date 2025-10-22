"""
Comando para debugar erro 403 do Asaas
"""
from django.core.management.base import BaseCommand
from controle_financeiro.asaas_service import AsaasService
import requests
from django.conf import settings


class Command(BaseCommand):
    help = 'Debug específico para erro 403 do Asaas'

    def handle(self, *args, **options):
        try:
            self.stdout.write("🔍 Debug específico para erro 403 - Asaas")
            self.stdout.write("=" * 60)
            
            # Verificar configurações
            api_key = getattr(settings, 'ASAAS_API_KEY', None)
            environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
            
            self.stdout.write(f"🔑 API Key: {api_key[:20] if api_key else 'NÃO CONFIGURADA'}...")
            self.stdout.write(f"🌐 Environment: {environment}")
            
            if environment == 'production':
                base_url = 'https://www.asaas.com/api/v3'
            else:
                base_url = 'https://sandbox.asaas.com/api/v3'
            
            self.stdout.write(f"🔗 Base URL: {base_url}")
            
            # Testar diferentes combinações de headers
            headers_tests = [
                {
                    'name': 'Formato 1: access_token + User-Agent Java',
                    'headers': {
                        'access_token': api_key,
                        'Content-Type': 'application/json',
                        'User-Agent': 'Java/1.8.0_282'
                    }
                },
                {
                    'name': 'Formato 2: Authorization Bearer + User-Agent Java',
                    'headers': {
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                        'User-Agent': 'Java/1.8.0_282'
                    }
                },
                {
                    'name': 'Formato 3: access_token + Accept + User-Agent Java',
                    'headers': {
                        'access_token': api_key,
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'User-Agent': 'Java/1.8.0_282'
                    }
                },
                {
                    'name': 'Formato 4: access_token + User-Agent personalizado',
                    'headers': {
                        'access_token': api_key,
                        'Content-Type': 'application/json',
                        'User-Agent': 'LVK-Sistemas/1.0'
                    }
                }
            ]
            
            for i, test in enumerate(headers_tests, 1):
                self.stdout.write(f"\n{i}️⃣ {test['name']}")
                self.stdout.write("-" * 50)
                
                try:
                    response = requests.get(
                        f"{base_url}/myAccount",
                        headers=test['headers'],
                        timeout=60
                    )
                    
                    self.stdout.write(f"   📊 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.stdout.write(f"   ✅ SUCESSO! Conta: {data.get('name', 'N/A')}")
                        self.stdout.write(f"   📧 Email: {data.get('email', 'N/A')}")
                        break
                    elif response.status_code == 401:
                        self.stdout.write("   ❌ 401 - API Key inválida ou expirada")
                    elif response.status_code == 403:
                        self.stdout.write("   ❌ 403 - Acesso negado (firewall/bloqueio)")
                        self.stdout.write(f"   📄 Resposta: {response.text[:100]}")
                    else:
                        self.stdout.write(f"   ❌ {response.status_code} - {response.text[:100]}")
                        
                except requests.exceptions.Timeout:
                    self.stdout.write("   ⏰ TIMEOUT - Conexão demorou mais de 60s")
                except requests.exceptions.ConnectionError as e:
                    self.stdout.write(f"   🔌 ERRO DE CONEXÃO: {str(e)}")
                except Exception as e:
                    self.stdout.write(f"   ❌ ERRO: {str(e)}")
            
            # Testar endpoint simples
            self.stdout.write(f"\n🧪 Teste adicional - endpoint /customers")
            self.stdout.write("-" * 50)
            
            try:
                response = requests.get(
                    f"{base_url}/customers",
                    headers={
                        'access_token': api_key,
                        'Content-Type': 'application/json',
                        'User-Agent': 'Java/1.8.0_282'
                    },
                    params={'limit': 1},
                    timeout=60
                )
                
                self.stdout.write(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    total = data.get('totalCount', 0)
                    self.stdout.write(f"   ✅ SUCESSO! Total clientes: {total}")
                else:
                    self.stdout.write(f"   ❌ Erro: {response.text[:100]}")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ ERRO: {str(e)}")
            
            # Recomendações
            self.stdout.write(f"\n💡 Recomendações baseadas na documentação Asaas:")
            self.stdout.write("   1. Verificar se firewall está bloqueando IPs do Asaas")
            self.stdout.write("   2. Liberar User-Agent 'Java/1.8.0_282'")
            self.stdout.write("   3. Se usar Cloudflare, verificar configurações específicas")
            self.stdout.write("   4. Contatar suporte Asaas se problema persistir")
            
            self.stdout.write(f"\n✅ Debug concluído")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro geral: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())