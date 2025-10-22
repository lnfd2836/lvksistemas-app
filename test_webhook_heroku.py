#!/usr/bin/env python
"""
Script para testar o webhook do Asaas no Heroku
"""
import requests
import json
import time

def test_webhook_heroku():
    """Testa o webhook no Heroku"""
    
    # URLs do Heroku para testar
    base_url = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
    
    urls = [
        f"{base_url}/webhook/asaas/test/",  # Teste simples
        f"{base_url}/webhook/asaas/",       # Webhook principal
        f"{base_url}/webhook/asaas/debug/", # Debug
    ]
    
    # Dados de teste do webhook
    webhook_data = {
        "id": "evt_test_heroku",
        "event": "PAYMENT_RECEIVED",
        "dateCreated": "2025-10-22 12:00:00",
        "payment": {
            "object": "payment",
            "id": "pay_test_heroku",
            "dateCreated": "2025-10-22",
            "customer": "cus_test",
            "value": 100.00,
            "status": "RECEIVED",
            "description": "Teste webhook Heroku",
            "billingType": "PIX",
            "externalReference": "CF_1_test"
        }
    }
    
    print("🚀 Testando webhooks no Heroku...")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    for i, url in enumerate(urls, 1):
        print(f"\n{i}️⃣ Testando: {url}")
        
        try:
            # Teste GET primeiro
            print("   📡 GET request...")
            response = requests.get(url, timeout=30)
            print(f"   GET Status: {response.status_code}")
            print(f"   GET Response: {response.text[:100]}")
            
            # Teste POST com dados
            print("   📡 POST request...")
            response = requests.post(
                url,
                json=webhook_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Asaas-Webhook-Test-Heroku',
                    'X-Forwarded-For': '54.232.1.1',  # IP do Asaas
                },
                timeout=30
            )
            
            print(f"   POST Status: {response.status_code}")
            print(f"   POST Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("   ✅ Webhook funcionando!")
            elif response.status_code == 302:
                location = response.headers.get('Location', 'N/A')
                print(f"   🔄 Redirecionamento para: {location}")
                print("   ❌ Ainda há problema de redirecionamento")
            elif response.status_code == 405:
                print("   ⚠️ Método não permitido")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout - Heroku pode estar dormindo")
            print("   💡 Aguardando 30s para o dyno acordar...")
            time.sleep(30)
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro na requisição: {str(e)}")
        
        except Exception as e:
            print(f"   ❌ Erro inesperado: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Teste concluído!")
    print("\n💡 Para monitorar logs no Heroku:")
    print("   heroku logs --tail --app lvksistemas-app-4f6fa281e217")
    print("\n🔧 Para configurar no Asaas:")
    print(f"   URL: {base_url}/webhook/asaas/")
    print("   Método: POST")
    print("   Content-Type: application/json")

if __name__ == "__main__":
    test_webhook_heroku()