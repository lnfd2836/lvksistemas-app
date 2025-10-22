#!/usr/bin/env python3
"""
Configurar API Key de Produção e Testar
"""

import requests
import json
from datetime import datetime, timedelta

# API Key de produção fornecida
API_KEY_PRODUCAO = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl"

def testar_api_producao():
    """Testa a API Key de produção"""
    print("🚀 TESTANDO API KEY DE PRODUÇÃO")
    print("=" * 50)
    print(f"🔑 API Key: {API_KEY_PRODUCAO[:30]}...")
    print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    base_url = "https://www.asaas.com/api/v3"
    headers = {
        'access_token': API_KEY_PRODUCAO,
        'Content-Type': 'application/json',
        'User-Agent': 'LVK-Sistemas/1.0'
    }
    
    try:
        # Testa conexão
        print("🔗 Testando conexão...")
        response = requests.get(f"{base_url}/myAccount", headers=headers, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Key de produção funcionando!")
            print(f"👤 Conta: {data.get('name', 'N/A')}")
            print(f"📧 Email: {data.get('email', 'N/A')}")
            print(f"💰 Wallet ID: {data.get('walletId', 'N/A')}")
            
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Detalhes: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def gerar_comandos_heroku():
    """Gera comandos para configurar no Heroku"""
    print("\n🔧 COMANDOS PARA CONFIGURAR NO HEROKU:")
    print("=" * 50)
    
    print("# Configurar API Key de produção")
    print(f"heroku config:set ASAAS_API_KEY='{API_KEY_PRODUCAO}' --app lvksistemas-app")
    
    print("\n# Configurar ambiente como produção")
    print("heroku config:set ASAAS_ENVIRONMENT='production' --app lvksistemas-app")
    
    print("\n# Verificar configuração")
    print("heroku config --app lvksistemas-app")
    
    print("\n# Testar no Heroku")
    print('heroku run "python -c \\"')
    print('from controle_financeiro.asaas_service import AsaasService')
    print('asaas = AsaasService()')
    print('print(\\"✅ Testando API...\\")') 
    print('if asaas.validar_configuracao():')
    print('    print(\\"✅ API funcionando!\\")') 
    print('else:')
    print('    print(\\"❌ API com problemas\\")') 
    print('\\"" --app lvksistemas-app')

if __name__ == "__main__":
    # Testa a API
    api_funcionando = testar_api_producao()
    
    # Gera comandos
    gerar_comandos_heroku()
    
    print("\n" + "=" * 50)
    if api_funcionando:
        print("✅ API KEY VÁLIDA!")
        print("\n📋 Próximos passos:")
        print("1. Execute os comandos do Heroku acima")
        print("2. Teste a geração de boleto")
        print("3. Confirme se não há mais erro 400")
    else:
        print("❌ API KEY COM PROBLEMAS")
        print("Verifique se a chave está correta")