#!/usr/bin/env python3
"""
Debug Específico - Geração de Boleto
Analisa problemas nos dados enviados para criar boleto/cobrança
"""

import requests
import json
from datetime import datetime, timedelta
import re

class DebugGeracaoBoleto:
    def __init__(self, api_key, environment='sandbox'):
        self.api_key = api_key
        self.environment = environment
        
        if environment == 'production':
            self.base_url = 'https://www.asaas.com/api/v3'
        else:
            self.base_url = 'https://sandbox.asaas.com/api/v3'
        
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LVK-Sistemas/1.0'
        }
    
    def testar_conexao(self):
        """Testa se a API Key está funcionando"""
        print("🔗 Testando conexão com API Asaas...")
        
        try:
            response = requests.get(f"{self.base_url}/myAccount", headers=self.headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API Key funcionando!")
                print(f"👤 Conta: {data.get('name', 'N/A')}")
                print(f"📧 Email: {data.get('email', 'N/A')}")
                print(f"💰 Wallet ID: {data.get('walletId', 'N/A')}")
                return True
            else:
                print(f"❌ Erro na API: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def analisar_dados_boleto(self, dados_boleto):
        """Analisa dados do boleto para identificar problemas"""
        print("\n🔍 ANALISANDO DADOS DO BOLETO")
        print("=" * 40)
        
        print("📤 Dados enviados:")
        print(json.dumps(dados_boleto, indent=2, ensure_ascii=False))
        
        problemas = []
        avisos = []
        
        # Campos obrigatórios
        campos_obrigatorios = ['customer', 'billingType', 'dueDate', 'value']
        
        for campo in campos_obrigatorios:
            if campo not in dados_boleto:
                problemas.append(f"Campo obrigatório '{campo}' ausente")
            elif not dados_boleto[campo]:
                problemas.append(f"Campo obrigatório '{campo}' vazio")
        
        # Validações específicas
        if 'customer' in dados_boleto:
            customer = dados_boleto['customer']
            if not isinstance(customer, str):
                problemas.append("Campo 'customer' deve ser string")
            elif not customer.startswith('cus_'):
                problemas.append("ID do cliente deve começar com 'cus_'")
            elif len(customer) < 10:
                problemas.append("ID do cliente muito curto")
        
        if 'value' in dados_boleto:
            try:
                valor = float(dados_boleto['value'])
                if valor <= 0:
                    problemas.append("Valor deve ser maior que zero")
                elif valor < 5.00:
                    problemas.append("Valor mínimo para boleto é R$ 5,00")
                elif valor > 1000000:
                    avisos.append("Valor muito alto, pode ter limite na conta")
            except (ValueError, TypeError):
                problemas.append("Valor deve ser numérico")
        
        if 'dueDate' in dados_boleto:
            try:
                due_date = datetime.strptime(dados_boleto['dueDate'], '%Y-%m-%d')
                hoje = datetime.now().date()
                if due_date.date() < hoje:
                    problemas.append("Data de vencimento não pode ser no passado")
                elif due_date.date() == hoje:
                    avisos.append("Data de vencimento é hoje - pode causar problemas")
                elif (due_date.date() - hoje).days > 365:
                    avisos.append("Data de vencimento muito distante (>1 ano)")
            except ValueError:
                problemas.append("Data de vencimento deve estar no formato YYYY-MM-DD")
        
        if 'billingType' in dados_boleto:
            tipos_validos = ['BOLETO', 'CREDIT_CARD', 'PIX', 'UNDEFINED']
            if dados_boleto['billingType'] not in tipos_validos:
                problemas.append(f"billingType deve ser: {', '.join(tipos_validos)}")
        
        if 'description' in dados_boleto:
            desc = dados_boleto['description']
            if len(desc) > 500:
                problemas.append("Descrição muito longa (máximo 500 caracteres)")
            elif len(desc) == 0:
                avisos.append("Descrição vazia - recomendado preencher")
        
        # Campos problemáticos comuns
        campos_problematicos = {
            'installmentCount': 'Pode causar erro se não for boleto parcelado',
            'installmentValue': 'Só usar se for parcelado',
            'totalValue': 'Pode conflitar com value',
            'callback': 'URL de callback pode estar inválida'
        }
        
        for campo, problema in campos_problematicos.items():
            if campo in dados_boleto:
                avisos.append(f"Campo '{campo}': {problema}")
        
        # Reporta problemas
        if problemas:
            print("\n❌ PROBLEMAS CRÍTICOS:")
            for problema in problemas:
                print(f"  - {problema}")
        
        if avisos:
            print("\n⚠️ AVISOS:")
            for aviso in avisos:
                print(f"  - {aviso}")
        
        if not problemas and not avisos:
            print("\n✅ Dados do boleto parecem válidos")
        
        return len(problemas) == 0
    
    def testar_cliente_existe(self, customer_id):
        """Verifica se o cliente existe no Asaas"""
        print(f"\n👤 Verificando cliente: {customer_id}")
        
        try:
            response = requests.get(f"{self.base_url}/customers/{customer_id}", headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                cliente = response.json()
                print("✅ Cliente encontrado!")
                print(f"📛 Nome: {cliente.get('name', 'N/A')}")
                print(f"📧 Email: {cliente.get('email', 'N/A')}")
                print(f"📱 Telefone: {cliente.get('mobilePhone', 'N/A')}")
                return True
            elif response.status_code == 404:
                print("❌ Cliente não encontrado!")
                print("🔧 Solução: Criar o cliente antes de gerar o boleto")
                return False
            else:
                print(f"❌ Erro ao consultar cliente: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar cliente: {e}")
            return False
    
    def criar_cliente_teste(self):
        """Cria um cliente de teste"""
        print("\n👤 Criando cliente de teste...")
        
        cliente_data = {
            "name": "Cliente Teste Debug",
            "email": f"debug.{datetime.now().strftime('%Y%m%d%H%M%S')}@lvksistemas.com.br",
            "cpfCnpj": "12345678901",
            "mobilePhone": "11999999999"
        }
        
        try:
            response = requests.post(f"{self.base_url}/customers", headers=self.headers, json=cliente_data, timeout=30)
            
            if response.status_code == 200:
                cliente = response.json()
                print(f"✅ Cliente criado: {cliente['id']}")
                return cliente['id']
            else:
                print(f"❌ Erro ao criar cliente: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao criar cliente: {e}")
            return None
    
    def testar_boleto_simples(self, customer_id):
        """Testa geração de boleto com dados mínimos"""
        print(f"\n📄 Testando boleto simples para cliente: {customer_id}")
        
        # Dados mínimos para boleto
        boleto_data = {
            "customer": customer_id,
            "billingType": "BOLETO",
            "dueDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "value": 29.90,
            "description": "Teste de boleto - Debug"
        }
        
        # Analisa dados antes de enviar
        dados_validos = self.analisar_dados_boleto(boleto_data)
        
        if not dados_validos:
            print("❌ Dados inválidos - não enviando requisição")
            return False
        
        try:
            print("\n📤 Enviando requisição...")
            response = requests.post(f"{self.base_url}/payments", headers=self.headers, json=boleto_data, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                boleto = response.json()
                print("✅ Boleto criado com sucesso!")
                print(f"🆔 ID: {boleto['id']}")
                print(f"💰 Valor: R$ {boleto['value']}")
                print(f"📅 Vencimento: {boleto['dueDate']}")
                print(f"🔗 URL: {boleto.get('invoiceUrl', 'N/A')}")
                
                # Testa PIX
                self.testar_pix_boleto(boleto['id'])
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
                            
                            # Sugestões baseadas no erro
                            if 'customer' in description.lower():
                                print("    💡 Sugestão: Verifique se o cliente existe")
                            elif 'value' in description.lower():
                                print("    💡 Sugestão: Verifique o formato do valor")
                            elif 'date' in description.lower():
                                print("    💡 Sugestão: Verifique o formato da data")
                    else:
                        print(f"📋 Resposta completa:")
                        print(json.dumps(error_data, indent=2))
                        
                except:
                    print(f"📋 Resposta raw: {response.text}")
                
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
    
    def testar_pix_boleto(self, payment_id):
        """Testa geração de PIX para o boleto"""
        print(f"\n📱 Testando PIX para boleto: {payment_id}")
        
        try:
            response = requests.get(f"{self.base_url}/payments/{payment_id}/pixQrCode", headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                pix_data = response.json()
                print("✅ PIX gerado com sucesso!")
                print(f"📋 Payload: {pix_data.get('payload', 'N/A')[:50]}...")
                if 'encodedImage' in pix_data:
                    print("🖼️ QR Code: Disponível")
                return True
            else:
                print(f"⚠️ PIX não disponível: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no PIX: {e}")
            return False
    
    def executar_debug_completo(self, api_key):
        """Executa debug completo da geração de boleto"""
        print("🚀 DEBUG COMPLETO - GERAÇÃO DE BOLETO")
        print("=" * 60)
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"🌐 Ambiente: {self.environment}")
        print(f"📡 URL Base: {self.base_url}")
        print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # 1. Testa conexão
        if not self.testar_conexao():
            print("\n❌ Falha na conexão - abortando debug")
            return False
        
        # 2. Cria cliente de teste
        customer_id = self.criar_cliente_teste()
        if not customer_id:
            print("\n❌ Falha ao criar cliente - abortando debug")
            return False
        
        # 3. Testa boleto simples
        boleto_ok = self.testar_boleto_simples(customer_id)
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RESULTADO DO DEBUG")
        print("=" * 60)
        
        if boleto_ok:
            print("✅ SUCESSO: Boleto gerado sem problemas!")
            print("\n📋 Confirmado:")
            print("- ✅ API Key funcionando")
            print("- ✅ Cliente criado")
            print("- ✅ Boleto gerado")
            print("- ✅ PIX disponível")
            
            print("\n🔧 Se o erro persiste no seu sistema:")
            print("1. Compare os dados que você está enviando")
            print("2. Verifique se o cliente existe antes de gerar boleto")
            print("3. Confirme formato dos campos (datas, valores)")
            print("4. Verifique se não há campos extras problemáticos")
            
        else:
            print("❌ PROBLEMA: Erro na geração do boleto")
            print("\n🔧 Próximos passos:")
            print("1. Analise os erros específicos mostrados acima")
            print("2. Corrija os dados conforme sugestões")
            print("3. Execute este debug novamente")
            print("4. Se persistir, contate suporte do Asaas")
        
        return boleto_ok

def main():
    print("Digite sua API Key do Asaas:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key não fornecida")
        return False
    
    print("\nEscolha o ambiente:")
    print("1. Sandbox (testes)")
    print("2. Produção")
    
    try:
        escolha = input("Digite 1 ou 2: ").strip()
        environment = 'sandbox' if escolha == '1' else 'production'
    except:
        environment = 'sandbox'
    
    debugger = DebugGeracaoBoleto(api_key, environment)
    return debugger.executar_debug_completo(api_key)

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)