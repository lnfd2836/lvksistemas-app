#!/usr/bin/env python
"""
Teste específico para verificar a API Key da Asaas
"""

import os
import sys
import django
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.conf import settings

def testar_api_key_asaas():
    print("🎯 TESTE DE VALIDAÇÃO DA API KEY ASAAS")
    print("=" * 50)
    
    # 1. Verificar configurações
    api_key = getattr(settings, 'ASAAS_API_KEY', None)
    environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
    
    print(f"✅ API Key configurada: {'Sim' if api_key else 'Não'}")
    print(f"✅ Ambiente: {environment}")
    print(f"✅ Formato da chave: {api_key[:20]}..." if api_key else "N/A")
    
    if not api_key:
        print("❌ API Key não configurada!")
        return False
    
    # 2. Determinar URL base
    if environment == 'production':
        base_url = 'https://www.asaas.com/api/v3'
    else:
        base_url = 'https://sandbox.asaas.com/api/v3'
    
    print(f"✅ URL base: {base_url}")
    
    # 3. Testar diferentes formatos de header
    headers_formats = [
        ("access_token", {'access_token': api_key, 'Content-Type': 'application/json'}),
        ("Authorization Bearer", {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}),
        ("Authorization direto", {'Authorization': api_key, 'Content-Type': 'application/json'}),
    ]
    
    endpoints_to_test = [
        "/myAccount",
        "/customers?limit=1",
        "/payments?limit=1"
    ]
    
    for header_name, headers in headers_formats:
        print(f"\n🔍 Testando formato: {header_name}")
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                print(f"   Testando: {endpoint}")
                
                response = requests.get(url, headers=headers, timeout=30)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ SUCESSO! Formato {header_name} funciona!")
                    data = response.json()
                    if endpoint == "/myAccount":
                        print(f"   Conta: {data.get('name', 'N/A')}")
                    return True
                elif response.status_code == 401:
                    print(f"   ❌ Não autorizado")
                elif response.status_code == 403:
                    print(f"   ❌ Acesso negado")
                else:
                    print(f"   ⚠️ Status {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
    
    print("\n❌ Nenhum formato de header funcionou")
    return False

if __name__ == "__main__":
    success = testar_api_key_asaas()
    if success:
        print("\n✅ API Key válida!")
    else:
        print("\n❌ API Key inválida ou expirada!")
        print("\n🔧 SOLUÇÕES:")
        print("1. Verifique se a API Key está correta na conta Asaas")
        print("2. Gere uma nova API Key se necessário")
        print("3. Atualize a variável ASAAS_API_KEY no Heroku")
