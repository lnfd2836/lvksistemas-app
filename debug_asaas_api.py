#!/usr/bin/env python3
"""
Debug da API Asaas - Diagnóstico do Erro 400
Testa e diagnostica problemas na integração com a API Asaas
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações da API Asaas
ASAAS_BASE_URL = "https://www.asaas.com/api/v3"
ASAAS_SANDBOX_URL = "https://sandbox.asaas.com/api/v3"

# API Keys (você precisa configurar a correta)
API_KEYS = {
    'sandbox': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDI2NzA6OiRhYWNoXzlmNzMwMjNkLTc4YzItNGY4Zi1hZGY2LTQyMzAzZGY5NzI4Nw==',
    'production': 'SUA_API_KEY_DE_PRODUCAO_AQUI'
}

class AsaasDebugger:
    def __init__(self, environment='sandbox'):
        self.environment = environment
        self.base_url = ASAAS_SANDBOX_URL if environment == 'sandbox' else ASAAS_BASE_URL
        self.api_key = API_KEYS.get(environment)
        
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LVK-Sistemas/1.0'
        }
    
    def testar_conexao(self):
        """Testa conexão básica com a API"""
        print(f"🔗 Testando conexão com API Asaas ({self.environment})...")
        print(f"🌐 URL: {self.base_url}")
        
        try:
            # Testa endpoint básico
            response = requests.get(f"{self.base_url}/myAccount", headers=self.headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Conexão bem-sucedida!")
                print(f"👤 Nome: {data.get('name', 'N/A')}")
                print(f"📧 Email: {data.get('email', 'N/A')}")
                print(f"💰 Wallet ID: {data.get('walletId', 'N/A')}")
                return True
                
            elif response.status_code == 401:
                print("❌ Erro de autenticação - API Key inválida")
                print("🔧 Verifique se a API Key está correta")
                return False
                
            elif response.status_code == 403:
                print("❌ Acesso negado - Verifique permissões")
                return False
                
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout - API demorou para responder")
            return False
            
        except requests.exceptions.ConnectionError:
            print("🔌 Erro de conexão com a API")
            return False
            
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False
    
    def testar_criacao_cobranca(self):
        """Testa criação de cobrança com dados mínimos"""
        print("\n📄 Testando criação de cobrança...")
        
        # Dados mínimos para teste
        cobranca_data = {
            "customer": "cus_000005928840",  # ID de cliente de teste
            "billingType": "BOLETO",
            "dueDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "value": 29.90,
            "description": "Teste de cobrança - LVK Sistemas"
        }
        
        print(f"📤 Dados enviados:")
        print(json.dumps(cobranca_data, indent=2))
        
        try:
            response = requests.post(
                f"{self.base_url}/payments",
                headers=self.headers,
                json=cobranca_data,
                timeout=30
            )
            
            print(f"\n📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Cobrança criada com sucesso!")
                print(f"🆔 ID: {data.get('id')}")
                print(f"💰 Valor: R$ {data.get('value')}")
                print(f"📅 Vencimento: {data.get('dueDate')}")
                print(f"🔗 URL: {data.get('invoiceUrl')}")
                return True
                
            elif response.status_code == 400:
                print("❌ Erro 400 - Dados inválidos")
                try:
                    error_data = response.json()
                    print("📋 Detalhes do erro:")
                    
                    if 'errors' in error_data:
                        for error in error_data['errors']:
                            print(f"  - {error.get('description', error)}")
                    else:
                        print(f"  {json.dumps(error_data, indent=2)}")
                        
                except:
                    print(f"📋 Resposta: {response.text}")
                
                return False
                
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def testar_criacao_cliente(self):
        """Testa criação de cliente primeiro"""
        print("\n👤 Testando criação de cliente...")
        
        cliente_data = {
            "name": "Cliente Teste LVK",
            "email": "teste@lvksistemas.com.br",
            "cpfCnpj": "12345678901",
            "mobilePhone": "11999999999"
        }
        
        print(f"📤 Dados do cliente:")
        print(json.dumps(cliente_data, indent=2))
        
        try:
            response = requests.post(
                f"{self.base_url}/customers",
                headers=self.headers,
                json=cliente_data,
                timeout=30
            )
            
            print(f"\n📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Cliente criado com sucesso!")
                print(f"🆔 ID: {data.get('id')}")
                print(f"👤 Nome: {data.get('name')}")
                print(f"📧 Email: {data.get('email')}")
                
                # Agora testa cobrança com este cliente
                return self.testar_cobranca_com_cliente(data.get('id'))
                
            elif response.status_code == 400:
                print("❌ Erro 400 - Dados do cliente inválidos")
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        for error in error_data['errors']:
                            print(f"  - {error.get('description', error)}")
                    else:
                        print(f"  {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                return False
                
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na criação do cliente: {e}")
            return False
    
    def testar_cobranca_com_cliente(self, customer_id):
        """Testa cobrança com cliente específico"""
        print(f"\n📄 Testando cobrança com cliente {customer_id}...")
        
        cobranca_data = {
            "customer": customer_id,
            "billingType": "BOLETO",
            "dueDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "value": 29.90,
            "description": "Teste de cobrança com PIX - LVK Sistemas",
            "externalReference": f"LVK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "postalService": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/payments",
                headers=self.headers,
                json=cobranca_data,
                timeout=30
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Cobrança criada com sucesso!")
                print(f"🆔 ID: {data.get('id')}")
                print(f"💰 Valor: R$ {data.get('value')}")
                print(f"📅 Vencimento: {data.get('dueDate')}")
                
                # Testa PIX para esta cobrança
                return self.testar_pix_cobranca(data.get('id'))
                
            else:
                print(f"❌ Erro: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na cobrança: {e}")
            return False
    
    def testar_pix_cobranca(self, payment_id):
        """Testa geração de PIX para cobrança"""
        print(f"\n📱 Testando PIX para cobrança {payment_id}...")
        
        try:
            response = requests.get(
                f"{self.base_url}/payments/{payment_id}/pixQrCode",
                headers=self.headers,
                timeout=30
            )
            
            print(f"📊 Status PIX: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ PIX gerado com sucesso!")
                print(f"🔗 QR Code: {data.get('encodedImage', 'N/A')[:50]}...")
                print(f"📋 Payload: {data.get('payload', 'N/A')[:50]}...")
                return True
            else:
                print(f"❌ Erro no PIX: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no PIX: {e}")
            return False
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo"""
        print("🚀 DIAGNÓSTICO COMPLETO - API ASAAS")
        print("=" * 60)
        print(f"🌐 Ambiente: {self.environment}")
        print(f"🔑 API Key: {self.api_key[:20] if self.api_key else 'NÃO CONFIGURADA'}...")
        print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        resultados = {}
        
        # 1. Teste de conexão
        resultados['conexao'] = self.testar_conexao()
        
        if resultados['conexao']:
            # 2. Teste de criação de cliente e cobrança
            resultados['cobranca'] = self.testar_criacao_cliente()
        else:
            print("⚠️ Pulando testes de cobrança - conexão falhou")
            resultados['cobranca'] = False
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE DIAGNÓSTICO")
        print("=" * 60)
        
        for teste, sucesso in resultados.items():
            status = "✅ SUCESSO" if sucesso else "❌ FALHA"
            print(f"{teste.upper()}: {status}")
        
        if all(resultados.values()):
            print("\n🎉 DIAGNÓSTICO: ✅ API FUNCIONANDO!")
            print("\n📋 Tudo está configurado corretamente:")
            print("- ✅ Conexão com API")
            print("- ✅ Criação de clientes")
            print("- ✅ Geração de cobranças")
            print("- ✅ PIX funcionando")
            
        else:
            print("\n⚠️ DIAGNÓSTICO: ❌ PROBLEMAS DETECTADOS")
            
            if not resultados['conexao']:
                print("\n🔧 Problema na conexão:")
                print("- Verifique a API Key")
                print("- Confirme o ambiente (sandbox/production)")
                print("- Teste conectividade de rede")
            
            if not resultados['cobranca']:
                print("\n🔧 Problema nas cobranças:")
                print("- Verifique dados obrigatórios")
                print("- Confirme formato dos campos")
                print("- Verifique limites da conta")
        
        return all(resultados.values())

def main():
    print("Escolha o ambiente para teste:")
    print("1. Sandbox (recomendado para testes)")
    print("2. Produção")
    
    try:
        escolha = input("Digite 1 ou 2: ").strip()
        environment = 'sandbox' if escolha == '1' else 'production'
    except:
        environment = 'sandbox'
    
    debugger = AsaasDebugger(environment)
    return debugger.executar_diagnostico_completo()

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)