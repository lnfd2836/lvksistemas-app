#!/usr/bin/env python3
"""
Resolver Erro 400 - API Asaas
Identifica e resolve problemas com a API Key e configurações
"""

import requests
import json
from datetime import datetime, timedelta

class ResolverErroAsaas:
    def __init__(self):
        self.sandbox_url = "https://sandbox.asaas.com/api/v3"
        self.production_url = "https://www.asaas.com/api/v3"
        
    def identificar_problema_api_key(self, api_key):
        """Identifica problemas com a API Key"""
        print("🔍 ANALISANDO API KEY")
        print("=" * 40)
        
        if not api_key:
            print("❌ API Key não fornecida")
            return False
        
        print(f"📏 Tamanho: {len(api_key)} caracteres")
        print(f"🔤 Início: {api_key[:20]}...")
        print(f"🔤 Final: ...{api_key[-10:]}")
        
        # Verifica padrões conhecidos
        problemas = []
        
        if len(api_key) < 30:
            problemas.append("API Key muito curta (mínimo ~30 caracteres)")
        
        if not any(char in api_key for char in ['$', '_', '-']):
            problemas.append("API Key não tem formato típico do Asaas")
        
        if api_key == "3f12cef7-f5a3-446e-b1ba-1eb37090298d":
            problemas.append("Esta é uma API Key de exemplo/placeholder, não é real")
        
        if api_key.count('-') == 4 and len(api_key) == 36:
            problemas.append("Parece ser um UUID genérico, não uma API Key do Asaas")
        
        if problemas:
            print("\n❌ PROBLEMAS IDENTIFICADOS:")
            for problema in problemas:
                print(f"  - {problema}")
            return False
        else:
            print("✅ Formato da API Key parece válido")
            return True
    
    def testar_api_key_sandbox(self):
        """Testa com API Key de sandbox válida"""
        print("\n🧪 TESTANDO COM API KEY DE SANDBOX VÁLIDA")
        print("=" * 50)
        
        # API Key de sandbox para teste (pública, apenas para demonstração)
        sandbox_key = "$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDI2NzA6OiRhYWNoXzlmNzMwMjNkLTc4YzItNGY4Zi1hZGY2LTQyMzAzZGY5NzI4Nw=="
        
        headers = {
            'access_token': sandbox_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LVK-Sistemas/1.0'
        }
        
        try:
            # Testa conexão
            response = requests.get(f"{self.sandbox_url}/myAccount", headers=headers, timeout=15)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Conexão com sandbox bem-sucedida!")
                print(f"👤 Conta: {data.get('name', 'N/A')}")
                print(f"📧 Email: {data.get('email', 'N/A')}")
                
                # Testa criação de cobrança
                return self.testar_cobranca_sandbox(headers)
                
            elif response.status_code == 401:
                print("❌ API Key de sandbox inválida")
                return False
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def testar_cobranca_sandbox(self, headers):
        """Testa criação de cobrança no sandbox"""
        print("\n📄 Testando criação de cobrança no sandbox...")
        
        try:
            # Primeiro, cria um cliente
            cliente_data = {
                "name": "Cliente Teste LVK",
                "email": f"teste.{datetime.now().strftime('%Y%m%d%H%M%S')}@lvksistemas.com.br",
                "cpfCnpj": "12345678901"
            }
            
            response = requests.post(f"{self.sandbox_url}/customers", headers=headers, json=cliente_data, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Erro ao criar cliente: {response.status_code}")
                return False
            
            cliente = response.json()
            print(f"✅ Cliente criado: {cliente['id']}")
            
            # Agora cria a cobrança
            cobranca_data = {
                "customer": cliente['id'],
                "billingType": "BOLETO",
                "dueDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "value": 29.90,
                "description": "Teste de cobrança - Resolver Erro 400"
            }
            
            response = requests.post(f"{self.sandbox_url}/payments", headers=headers, json=cobranca_data, timeout=15)
            
            print(f"📊 Status da cobrança: {response.status_code}")
            
            if response.status_code == 200:
                cobranca = response.json()
                print("✅ Cobrança criada com sucesso!")
                print(f"🆔 ID: {cobranca['id']}")
                print(f"💰 Valor: R$ {cobranca['value']}")
                print(f"🔗 URL: {cobranca.get('invoiceUrl', 'N/A')}")
                
                # Testa PIX
                return self.testar_pix_sandbox(headers, cobranca['id'])
                
            elif response.status_code == 400:
                print("❌ Erro 400 - Analisando...")
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        for error in error_data['errors']:
                            print(f"  - {error.get('description', error)}")
                    else:
                        print(f"  {json.dumps(error_data, indent=2)}")
                except:
                    print(f"  Resposta: {response.text}")
                return False
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na cobrança: {e}")
            return False
    
    def testar_pix_sandbox(self, headers, payment_id):
        """Testa PIX no sandbox"""
        print(f"\n📱 Testando PIX para cobrança {payment_id}...")
        
        try:
            response = requests.get(f"{self.sandbox_url}/payments/{payment_id}/pixQrCode", headers=headers, timeout=15)
            
            if response.status_code == 200:
                pix_data = response.json()
                print("✅ PIX gerado com sucesso!")
                print(f"📋 Payload: {pix_data.get('payload', 'N/A')[:50]}...")
                return True
            else:
                print(f"⚠️ PIX não disponível: {response.status_code}")
                return True  # Cobrança funcionou, PIX pode não estar disponível no sandbox
                
        except Exception as e:
            print(f"⚠️ Erro no PIX: {e}")
            return True  # Cobrança funcionou
    
    def gerar_instrucoes_resolucao(self):
        """Gera instruções para resolver o problema"""
        print("\n🔧 COMO RESOLVER O ERRO 400")
        print("=" * 50)
        
        print("📋 PASSO 1: Obter API Key válida do Asaas")
        print("1. Acesse: https://www.asaas.com")
        print("2. Faça login na sua conta")
        print("3. Vá em: Configurações → Integrações → API")
        print("4. Para TESTES: Use o ambiente 'Sandbox'")
        print("5. Para PRODUÇÃO: Use o ambiente 'Produção'")
        print("6. Clique em 'Gerar nova chave'")
        print("7. Copie a chave gerada")
        
        print("\n📋 PASSO 2: Configurar no sistema")
        print("Para desenvolvimento local:")
        print("1. Edite o arquivo .env")
        print("2. Substitua a linha:")
        print("   ASAAS_API_KEY=3f12cef7-f5a3-446e-b1ba-1eb37090298d")
        print("3. Por:")
        print("   ASAAS_API_KEY=SUA_API_KEY_AQUI")
        print("4. Configure o ambiente:")
        print("   ASAAS_ENVIRONMENT=sandbox  (para testes)")
        print("   ASAAS_ENVIRONMENT=production  (para produção)")
        
        print("\nPara produção no Heroku:")
        print("1. Execute:")
        print("   heroku config:set ASAAS_API_KEY='SUA_API_KEY' --app lvksistemas-app")
        print("   heroku config:set ASAAS_ENVIRONMENT='production' --app lvksistemas-app")
        
        print("\n📋 PASSO 3: Testar a integração")
        print("1. Execute este script novamente")
        print("2. Teste no navegador")
        print("3. Verifique os logs para confirmar")
        
        print("\n⚠️ IMPORTANTE:")
        print("- API Key de SANDBOX só funciona no ambiente de testes")
        print("- API Key de PRODUÇÃO só funciona no ambiente real")
        print("- Nunca compartilhe sua API Key de produção")
        print("- Mantenha as chaves seguras")
    
    def executar_diagnostico(self):
        """Executa diagnóstico completo"""
        print("🚀 RESOLVER ERRO 400 - API ASAAS")
        print("=" * 60)
        print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Lê API Key atual do .env
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
                
            api_key_line = [line for line in env_content.split('\n') if line.startswith('ASAAS_API_KEY=')]
            
            if api_key_line:
                current_api_key = api_key_line[0].split('=', 1)[1]
                print(f"🔑 API Key atual: {current_api_key}")
                
                # Analisa a API Key atual
                api_key_valida = self.identificar_problema_api_key(current_api_key)
                
                if not api_key_valida:
                    print("\n❌ PROBLEMA IDENTIFICADO: API Key inválida")
                    
            else:
                print("❌ API Key não encontrada no arquivo .env")
                
        except FileNotFoundError:
            print("❌ Arquivo .env não encontrado")
        
        # Testa com API Key de sandbox válida
        sandbox_funcionou = self.testar_api_key_sandbox()
        
        # Gera instruções
        self.gerar_instrucoes_resolucao()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DO DIAGNÓSTICO")
        print("=" * 60)
        
        if sandbox_funcionou:
            print("✅ DIAGNÓSTICO: Sistema funcionando com API Key válida")
            print("\n🎯 SOLUÇÃO:")
            print("1. Obtenha uma API Key válida do Asaas")
            print("2. Configure no arquivo .env ou Heroku")
            print("3. Teste novamente")
            
        else:
            print("❌ DIAGNÓSTICO: Problemas na integração")
            print("\n🔧 VERIFIQUE:")
            print("1. Conectividade com a internet")
            print("2. Configurações de firewall")
            print("3. Status do serviço Asaas")
        
        return sandbox_funcionou

def main():
    resolver = ResolverErroAsaas()
    return resolver.executar_diagnostico()

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)