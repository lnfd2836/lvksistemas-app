#!/usr/bin/env python3
"""
Diagnóstico Específico do Erro 400 na API Asaas
Analisa e resolve problemas comuns que causam erro 400
"""

import requests
import json
from datetime import datetime, timedelta
import re

class DiagnosticadorErro400:
    def __init__(self):
        # Configurações padrão
        self.sandbox_url = "https://sandbox.asaas.com/api/v3"
        self.production_url = "https://www.asaas.com/api/v3"
        
        # API Keys de exemplo (você deve usar suas próprias)
        self.api_keys = {
            'sandbox': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDI2NzA6OiRhYWNoXzlmNzMwMjNkLTc4YzItNGY4Zi1hZGY2LTQyMzAzZGY5NzI4Nw==',
            'production': 'SUA_API_KEY_DE_PRODUCAO'
        }
    
    def validar_api_key(self, api_key):
        """Valida formato da API key"""
        print("🔑 Validando formato da API Key...")
        
        if not api_key:
            print("❌ API Key não fornecida")
            return False
        
        # Padrões válidos para API keys do Asaas
        patterns = [
            r'^\$aact_[a-zA-Z0-9]{32}::[0-9]{17}::\$aach_[a-zA-Z0-9\-]{36}$',  # Sandbox
            r'^\$aact_[a-zA-Z0-9]{32}$',  # Production (formato mais simples)
            r'^[a-zA-Z0-9\-_]{40,}$'  # Formato genérico
        ]
        
        for pattern in patterns:
            if re.match(pattern, api_key):
                print("✅ Formato da API Key válido")
                return True
        
        print("⚠️ Formato da API Key pode estar incorreto")
        print(f"   Tamanho: {len(api_key)} caracteres")
        print(f"   Início: {api_key[:10]}...")
        return True  # Permite continuar mesmo com formato suspeito
    
    def testar_conexao_basica(self, base_url, api_key):
        """Testa conexão básica com a API"""
        print(f"\n🔗 Testando conexão com {base_url}...")
        
        headers = {
            'access_token': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LVK-Sistemas-Debug/1.0'
        }
        
        try:
            response = requests.get(f"{base_url}/myAccount", headers=headers, timeout=15)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Conexão bem-sucedida!")
                print(f"👤 Conta: {data.get('name', 'N/A')}")
                return True, headers
                
            elif response.status_code == 401:
                print("❌ Erro 401 - API Key inválida ou expirada")
                return False, None
                
            else:
                print(f"❌ Erro {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Erro: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text[:200]}...")
                return False, None
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False, None
    
    def analisar_dados_cobranca(self, dados):
        """Analisa dados de cobrança para identificar problemas"""
        print("\n🔍 Analisando dados da cobrança...")
        
        problemas = []
        
        # Campos obrigatórios
        campos_obrigatorios = ['customer', 'billingType', 'dueDate', 'value']
        
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                problemas.append(f"Campo obrigatório '{campo}' ausente ou vazio")
        
        # Validações específicas
        if 'value' in dados:
            try:
                valor = float(dados['value'])
                if valor <= 0:
                    problemas.append("Valor deve ser maior que zero")
                if valor < 5.00:
                    problemas.append("Valor mínimo é R$ 5,00")
            except:
                problemas.append("Valor deve ser numérico")
        
        if 'dueDate' in dados:
            try:
                due_date = datetime.strptime(dados['dueDate'], '%Y-%m-%d')
                if due_date < datetime.now():
                    problemas.append("Data de vencimento não pode ser no passado")
            except:
                problemas.append("Data de vencimento deve estar no formato YYYY-MM-DD")
        
        if 'billingType' in dados:
            tipos_validos = ['BOLETO', 'CREDIT_CARD', 'PIX', 'UNDEFINED']
            if dados['billingType'] not in tipos_validos:
                problemas.append(f"billingType deve ser um de: {', '.join(tipos_validos)}")
        
        if 'customer' in dados:
            customer = dados['customer']
            if not customer.startswith('cus_'):
                problemas.append("ID do cliente deve começar com 'cus_'")
        
        # Reporta problemas
        if problemas:
            print("❌ Problemas encontrados:")
            for problema in problemas:
                print(f"  - {problema}")
            return False
        else:
            print("✅ Dados da cobrança parecem válidos")
            return True
    
    def testar_cobranca_simples(self, base_url, headers):
        """Testa criação de cobrança com dados mínimos"""
        print("\n📄 Testando cobrança com dados mínimos...")
        
        # Primeiro, cria um cliente de teste
        cliente_data = {
            "name": "Cliente Teste Debug",
            "email": f"teste.debug.{datetime.now().strftime('%Y%m%d%H%M%S')}@lvksistemas.com.br",
            "cpfCnpj": "12345678901"
        }
        
        try:
            # Cria cliente
            response = requests.post(f"{base_url}/customers", headers=headers, json=cliente_data, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Erro ao criar cliente: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                return False
            
            cliente = response.json()
            customer_id = cliente['id']
            print(f"✅ Cliente criado: {customer_id}")
            
            # Agora testa cobrança
            cobranca_data = {
                "customer": customer_id,
                "billingType": "BOLETO",
                "dueDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "value": 29.90,
                "description": "Teste de diagnóstico - Erro 400"
            }
            
            print("📤 Dados da cobrança:")
            print(json.dumps(cobranca_data, indent=2))
            
            # Valida dados antes de enviar
            if not self.analisar_dados_cobranca(cobranca_data):
                return False
            
            # Envia cobrança
            response = requests.post(f"{base_url}/payments", headers=headers, json=cobranca_data, timeout=15)
            
            print(f"\n📊 Status da cobrança: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Cobrança criada com sucesso!")
                print(f"🆔 ID: {data.get('id')}")
                print(f"💰 Valor: R$ {data.get('value')}")
                print(f"🔗 URL: {data.get('invoiceUrl', 'N/A')}")
                return True
                
            elif response.status_code == 400:
                print("❌ Erro 400 - Analisando detalhes...")
                try:
                    error_data = response.json()
                    
                    if 'errors' in error_data:
                        print("📋 Erros específicos:")
                        for error in error_data['errors']:
                            code = error.get('code', 'N/A')
                            description = error.get('description', str(error))
                            print(f"  - [{code}] {description}")
                    else:
                        print(f"📋 Resposta completa:")
                        print(json.dumps(error_data, indent=2))
                        
                except:
                    print(f"📋 Resposta raw: {response.text}")
                
                return False
                
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def diagnosticar_erro_400(self):
        """Executa diagnóstico completo do erro 400"""
        print("🚀 DIAGNÓSTICO DO ERRO 400 - API ASAAS")
        print("=" * 60)
        print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Testa sandbox primeiro
        print("🧪 TESTANDO AMBIENTE SANDBOX")
        print("-" * 30)
        
        api_key_sandbox = self.api_keys['sandbox']
        
        if self.validar_api_key(api_key_sandbox):
            conexao_ok, headers = self.testar_conexao_basica(self.sandbox_url, api_key_sandbox)
            
            if conexao_ok:
                sucesso_sandbox = self.testar_cobranca_simples(self.sandbox_url, headers)
            else:
                sucesso_sandbox = False
        else:
            sucesso_sandbox = False
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 DIAGNÓSTICO FINAL")
        print("=" * 60)
        
        if sucesso_sandbox:
            print("✅ SANDBOX: Funcionando corretamente!")
            print("\n🔧 Se o erro persiste em produção:")
            print("1. Verifique se está usando a API Key de PRODUÇÃO")
            print("2. Confirme se a conta está ativa em produção")
            print("3. Verifique se os dados enviados estão corretos")
            print("4. Confirme se não há caracteres especiais nos dados")
            
        else:
            print("❌ SANDBOX: Problemas detectados")
            print("\n🔧 Possíveis soluções:")
            print("1. Verifique a API Key do sandbox")
            print("2. Confirme se a conta Asaas está ativa")
            print("3. Verifique conectividade de rede")
            print("4. Confirme formato dos dados enviados")
        
        print(f"\n📋 Próximos passos:")
        print("1. Execute este diagnóstico")
        print("2. Corrija os problemas identificados")
        print("3. Teste novamente sua integração")
        print("4. Se persistir, contate o suporte do Asaas")
        
        return sucesso_sandbox

def main():
    diagnosticador = DiagnosticadorErro400()
    return diagnosticador.diagnosticar_erro_400()

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)