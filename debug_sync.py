#!/usr/bin/env python
"""
Script para debugar a sincronização e verificar se os boletos estão no Asaas
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/uiz/Documentos/lvksistemas-app/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lvksistemas_app.settings')
django.setup()

import requests
from datetime import datetime, timedelta
from django.utils import timezone
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro

def debug_asaas_sync():
    """Debug da sincronização com Asaas"""
    print("🔍 INICIANDO DEBUG DA SINCRONIZAÇÃO ASAAS")
    print("=" * 50)
    
    try:
        # 1. Testar configuração
        asaas_service = AsaasService()
        print(f"🔧 Base URL: {asaas_service.base_url}")
        print(f"🔧 Environment: {asaas_service.environment}")
        
        # 2. Validar configuração
        print("\n📡 Testando conectividade...")
        if asaas_service.validar_configuracao():
            print("✅ Configuração válida!")
        else:
            print("❌ Configuração inválida!")
            return
        
        # 3. Buscar cobranças no Asaas (últimos 30 dias)
        print("\n🔍 Buscando cobranças no Asaas...")
        data_inicio = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{asaas_service.base_url}/payments",
            headers=asaas_service.headers,
            params={
                'dateCreated[ge]': data_inicio,
                'limit': 100
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            payments = data.get('data', [])
            
            print(f"📊 Encontradas {len(payments)} cobranças no Asaas")
            
            if payments:
                print("\n📋 COBRANÇAS ENCONTRADAS NO ASAAS:")
                print("-" * 80)
                for i, payment in enumerate(payments[:10]):  # Mostrar apenas as 10 primeiras
                    print(f"{i+1:2d}. ID: {payment['id']}")
                    print(f"    Status: {payment['status']}")
                    print(f"    Valor: R$ {payment['value']}")
                    print(f"    Vencimento: {payment['dueDate']}")
                    print(f"    Customer: {payment['customer']}")
                    print(f"    External Ref: {payment.get('externalReference', 'N/A')}")
                    print(f"    Descrição: {payment.get('description', 'N/A')}")
                    print()
            else:
                print("❌ Nenhuma cobrança encontrada no Asaas!")
        else:
            print(f"❌ Erro ao buscar cobranças: {response.status_code}")
            print(f"Response: {response.text}")
        
        # 4. Verificar cobranças no sistema local
        print("\n🗄️ Verificando cobranças no sistema local...")
        cobrancas_locais = CobrancaAsaas.objects.all().count()
        print(f"📊 Total de cobranças no sistema: {cobrancas_locais}")
        
        if cobrancas_locais > 0:
            print("\n📋 COBRANÇAS NO SISTEMA LOCAL:")
            print("-" * 80)
            for cobranca in CobrancaAsaas.objects.all()[:10]:
                print(f"ID Asaas: {cobranca.asaas_id}")
                print(f"Status: {cobranca.status}")
                print(f"Valor: R$ {cobranca.valor}")
                print(f"Loja: {cobranca.controle_financeiro.loja.nome}")
                print(f"Criado em: {cobranca.data_criacao}")
                print()
        
        # 5. Verificar controles financeiros
        print("\n🏪 Verificando controles financeiros...")
        controles = ControleFinanceiro.objects.all().count()
        print(f"📊 Total de controles financeiros: {controles}")
        
        if controles > 0:
            print("\n📋 CONTROLES FINANCEIROS:")
            print("-" * 80)
            for controle in ControleFinanceiro.objects.all()[:5]:
                print(f"ID: {controle.id}")
                print(f"Loja: {controle.loja.nome}")
                print(f"Email: {controle.loja.email}")
                print(f"Status: {controle.status}")
                print()
        
    except Exception as e:
        print(f"❌ Erro no debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_asaas_sync()