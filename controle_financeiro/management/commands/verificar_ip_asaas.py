"""
Comando para verificar o problema de IP com a API do Asaas
"""

from django.core.management.base import BaseCommand
import requests
import json

class Command(BaseCommand):
    help = 'Verifica o IP atual do Heroku e testa a API do Asaas'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("🔍 VERIFICAÇÃO DE IP - ASAAS API")
        self.stdout.write("=" * 60)
        
        # Verificar IP atual
        try:
            self.stdout.write("📡 Verificando IP atual do Heroku...")
            response = requests.get('https://api.ipify.org', timeout=10)
            current_ip = response.text.strip()
            self.stdout.write(f"🌐 IP atual: {current_ip}")
        except Exception as e:
            self.stdout.write(f"❌ Erro ao verificar IP: {str(e)}")
            current_ip = "Desconhecido"
        
        # Verificar múltiplos IPs (Heroku usa vários)
        self.stdout.write("\n📊 Testando variação de IPs...")
        ips_encontrados = set()
        
        for i in range(3):
            try:
                response = requests.get('https://api.ipify.org', timeout=5)
                ip = response.text.strip()
                ips_encontrados.add(ip)
                self.stdout.write(f"   Teste {i+1}: {ip}")
            except:
                self.stdout.write(f"   Teste {i+1}: Falhou")
        
        self.stdout.write(f"\n📋 Total de IPs diferentes encontrados: {len(ips_encontrados)}")
        
        # Testar API do Asaas
        self.stdout.write("\n🧪 Testando API do Asaas...")
        
        from django.conf import settings
        from controle_financeiro.asaas_service import AsaasService
        
        api_key = getattr(settings, 'ASAAS_API_KEY', None)
        environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
        
        if not api_key:
            self.stdout.write("❌ API Key não configurada")
            return
        
        # URL da API
        if environment == 'production':
            base_url = 'https://www.asaas.com/api/v3'
        else:
            base_url = 'https://sandbox.asaas.com/api/v3'
        
        # Headers
        headers = {
            'access_token': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'Java/1.8.0_282'
        }
        
        try:
            response = requests.get(
                f"{base_url}/myAccount",
                headers=headers,
                timeout=30
            )
            
            self.stdout.write(f"📊 Status da API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(self.style.SUCCESS("✅ API FUNCIONANDO!"))
                self.stdout.write(f"👤 Conta: {data.get('name', 'N/A')}")
                self.stdout.write(f"📧 Email: {data.get('email', 'N/A')}")
                
            elif response.status_code == 403:
                self.stdout.write(self.style.ERROR("❌ ERRO 403 - ACESSO NEGADO"))
                self.stdout.write("🔧 CAUSA: Restrição de IP na API do Asaas")
                self.stdout.write(f"📍 IP atual ({current_ip}) não está autorizado")
                self.stdout.write("\n💡 SOLUÇÃO:")
                self.stdout.write("1. Acesse: https://www.asaas.com")
                self.stdout.write("2. Vá em: Configurações → API")
                self.stdout.write("3. REMOVA todos os IPs da lista de 'Endereços IP autorizados'")
                self.stdout.write("4. DEIXE A LISTA VAZIA")
                self.stdout.write("5. Salve as alterações")
                
            elif response.status_code == 401:
                self.stdout.write(self.style.ERROR("❌ ERRO 401 - API KEY INVÁLIDA"))
                self.stdout.write("🔧 Verifique se a API Key está correta")
                
            else:
                self.stdout.write(f"❌ Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro na requisição: {str(e)}")
        
        # Resumo
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📋 RESUMO")
        self.stdout.write("=" * 60)
        self.stdout.write(f"🌐 IP atual: {current_ip}")
        self.stdout.write(f"📊 IPs diferentes detectados: {len(ips_encontrados)}")
        self.stdout.write(f"🔑 API Key: {'Configurada' if api_key else 'Não configurada'}")
        self.stdout.write(f"🌍 Ambiente: {environment}")
        
        if len(ips_encontrados) > 1:
            self.stdout.write("\n⚠️  HEROKU USA IPs DINÂMICOS!")
            self.stdout.write("💡 Recomendação: Remover restrição de IP no Asaas")
        
        self.stdout.write("\n📖 Documentação completa: SOLUCAO_IP_ASAAS.md")
        self.stdout.write("=" * 60)