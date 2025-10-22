#!/usr/bin/env python
"""
Script para testar o webhook do Asaas localmente
"""
import requests
import json

def test_webhook():
    """Testa o webhook com dados de exemplo"""
    
    # Dados de exemplo do webhook do Asaas
    webhook_data = {
        "id": "evt_05b708f961d739ea7eba7e4db318f621&1100657670",
        "event": "PAYMENT_CREATED",
        "dateCreated": "2025-10-22 09:01:11",
        "payment": {
            "object": "payment",
            "id": "pay_skbidaq2qe30cr2l",
            "dateCreated": "2025-10-22",
            "customer": "cus_000140108244",
            "checkoutSession": None,
            "paymentLink": None,
            "value": 5500,
            "netValue": 5500,
            "originalValue": None,
            "interestValue": None,
            "description": "Cobrança gerada automaticamente a partir de Pix recebido.",
            "billingType": "PIX",
            "confirmedDate": "2025-10-22",
            "pixTransaction": "d8db17f3-021d-4df5-bab6-f0d4b213d0b0",
            "pixQrCodeId": None,
            "status": "RECEIVED",
            "dueDate": "2025-10-22",
            "originalDueDate": "2025-10-22",
            "paymentDate": "2025-10-22",
            "clientPaymentDate": "2025-10-22",
            "installmentNumber": None,
            "invoiceUrl": "https://www.asaas.com/i/skbidaq2qe30cr2l",
            "invoiceNumber": "659889241",
            "externalReference": None,
            "deleted": False,
            "anticipated": False,
            "anticipable": False,
            "creditDate": "2025-10-22",
            "estimatedCreditDate": "2025-10-22",
            "transactionReceiptUrl": "https://www.asaas.com/comprovantes/h/UEFZTUVOVF9SRUNFSVZFRDpwYXlfc2tiaWRhcTJxZTMwY3IybA%3D%3D",
            "nossoNumero": None,
            "bankSlipUrl": None,
            "lastInvoiceViewedDate": None,
            "lastBankSlipViewedDate": None,
            "discount": {
                "value": 0,
                "limitDate": None,
                "dueDateLimitDays": 0,
                "type": "FIXED"
            },
            "interest": {
                "value": 0,
                "type": "PERCENTAGE"
            },
            "postalService": False,
            "escrow": None,
            "refunds": None
        }
    }
    
    # URLs para testar
    urls = [
        'http://localhost:8000/webhook/asaas/',
        'http://localhost:8000/webhook/asaas/debug/',
        'http://localhost:8000/webhook/asaas/final/',
    ]
    
    for url in urls:
        print(f"\n🧪 Testando: {url}")
        try:
            response = requests.post(
                url,
                json=webhook_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Asaas-Webhook-Test'
                },
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("   ✅ Webhook funcionando!")
            elif response.status_code == 302:
                print(f"   🔄 Redirecionamento para: {response.headers.get('Location', 'N/A')}")
            else:
                print("   ❌ Erro no webhook")
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testando webhooks do Asaas...")
    test_webhook()