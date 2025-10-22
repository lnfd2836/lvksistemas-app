#!/usr/bin/env python3
"""
Script de debug para testar a API do Asaas e resolver erro 403
Testa diferentes formatos de headers e endpoints
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Configurar Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.conf import settings
from controle_financeiro.asaas_service import AsaasService
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def testar_configuracao_detalhada():
    """Testa configuração da API Asaas com detalhes"""
    print("=" * 60)
    print("🔍 TESTE DETALHADO DA API ASAAS")
    print("=" * 60)
    
    # Verificar configurações
    api_key = getattr(settings, 'ASAAS_API_KEY', None)
    environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
    
    print(f"📋 Configurações:")
    print(f"   API Key: {'✅ Configurada' if api_key else '❌ Não configurada'}")
    print(f"   Environment: {environment}")
    
    if not api_key:
        print("❌ ASAAS_API_KEY não configurada!")
        return False
    
    # URLs da API
    if environment == 'production':
        base_url = 'https://www.asaas.com/api/v3'
    else:
        base_url = 'https://sandbox.asaas.com/api/v3'
    
    print(f"   Base URL: {base_url}")
    print()
    
    # Diferentes formatos de headers para testar
    headers_formats = [
        {
            'name': 'access_token padrão',
            'headers': {
                'access_token': api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'Java/1.8.0_282'
            }
        },
        {
            'name': 'Authorization Bearer',
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Java/1.8.0_282'
            }
        },
        {
            'name': 'access_token com Accept',
            'headers': {
                'access_token': api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'Java/1.8.0_282',
                'Accept': 'application/json'
            }
        },
        {
            'name': 'Authorization com $aact_',
            'headers': {
                'Authorization': f'$aact_{api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Java/1.8.0_282'
            }
        }
    ]
    
    # Endpoints para testar
    endpoints = [
        {'path': '/myAccount', 'name': 'Minha Conta'},
        {'path': '/customers?limit=1', 'name': 'Clientes'},
        {'path': '/payments?limit=1', 'name': 'Pagamentos'},
        {'path': '/finance/balance', 'name': 'Saldo'}
    ]
    
    sucesso = False
    
    for header_format in headers_formats:
        print(f"🧪 Testando formato: {header_format['name']}")
        print(f"   Headers: {json.dumps(header_format['headers'], indent=6)}")
        
        for endpoint in endpoints:
            try:
                print(f"   📡 Testando endpoint: {endpoint['name']} ({endpoint['path']})")
                
                response = requests.get(
                    f"{base_url}{endpoint['path']}",
                    headers=header_format['headers'],
                    timeout=90,
                    verify=True,
                    allow_redirects=True
                )
                
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"      ✅ SUCESSO! Resposta válida recebida")
                        
                        if endpoint['path'] == '/myAccount':
                            print(f"      👤 Nome da conta: {data.get('name', 'N/A')}")
                            print(f"      📧 Email: {data.get('email', 'N/A')}")
                            print(f"      🆔 ID: {data.get('id', 'N/A')}")
                        
                        sucesso = True
                        print(f"      🎉 CONFIGURAÇÃO FUNCIONANDO!")
                        break
                        
                    except json.JSONDecodeError:
                        print(f"      ⚠️ Resposta não é JSON válido")
                        
                elif response.status_code == 401:
                    print(f"      ❌ API Key inválida ou expirada")
                    break  # Não testar outros endpoints
                    
                elif response.status_code == 403:
                    print(f"      ❌ Acesso negado (403)")
                    print(f"      📄 Resposta: {response.text[:200]}...")
                    
                elif response.status_code == 404:
                    print(f"      ⚠️ Endpoint não encontrado (404)")
                    
                else:
                    print(f"      ❌ Erro {response.status_code}")
                    print(f"      📄 Resposta: {response.text[:200]}...")
                
            except requests.exceptions.Timeout:
                print(f"      ⏰ Timeout na requisição")
            except requests.exceptions.ConnectionError as e:
                print(f"      🔌 Erro de conexão: {str(e)}")
            except requests.exceptions.SSLError as e:
                print(f"      🔒 Erro SSL: {str(e)}")
            except Exception as e:
                print(f"      ❌ Erro inesperado: {str(e)}")
        
        if sucesso:
            break
        
        print()
    
    return sucesso

def testar_asaas_service():
    """Testa o AsaasService diretamente"""
    print("\n" + "=" * 60)
    print("🔧 TESTE DO ASAAS SERVICE")
    print("=" * 60)
    
    try:
        service = AsaasService()
        print("✅ AsaasService instanciado com sucesso")
        
        print("🔍 Testando validação de configuração...")
        resultado = service.validar_configuracao()
        
        if resultado:
            print("✅ Configuração válida!")
            return True
        else:
            print("❌ Configuração inválida!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar AsaasService: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print(f"🚀 Iniciando teste da API Asaas - {datetime.now()}")
    
    # Teste 1: Configuração detalhada
    sucesso_config = testar_configuracao_detalhada()
    
    # Teste 2: AsaasService
    sucesso_service = testar_asaas_service()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    if sucesso_config and sucesso_service:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A API Asaas está funcionando corretamente")
    elif sucesso_config:
        print("⚠️ Configuração manual OK, mas AsaasService com problema")
    elif sucesso_service:
        print("⚠️ AsaasService OK, mas configuração manual com problema")
    else:
        print("❌ TODOS OS TESTES FALHARAM!")
        print("🔧 Verifique:")
        print("   - API Key do Asaas")
        print("   - Configurações de rede/firewall")
        print("   - Status do serviço Asaas")
    
    print(f"\n🏁 Teste finalizado - {datetime.now()}")

if __name__ == '__main__':
    main()