#!/usr/bin/env python3
"""
Script para verificar todas as cobranças no Asaas e comparar com o sistema local
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from controle_financeiro.models import CobrancaAsaas
from controle_financeiro.asaas_service import AsaasService
import logging
import requests

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_asaas_payments():
    """Verifica todas as cobranças no Asaas"""
    asaas_service = AsaasService()
    
    print("🔍 Consultando cobranças no Asaas...")
    
    try:
        # Buscar cobranças dos últimos 30 dias
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
            
            print(f"📊 Encontradas {len(payments)} cobranças no Asaas (últimos 30 dias)")
            print("\n=== COBRANÇAS NO ASAAS ===")
            
            for payment in payments:
                print(f"ID: {payment['id']}")
                print(f"Status: {payment['status']}")
                print(f"Valor: R$ {payment['value']}")
                print(f"Vencimento: {payment['dueDate']}")
                print(f"Descrição: {payment.get('description', 'N/A')}")
                print(f"Cliente: {payment.get('customer', 'N/A')}")
                print(f"Referência: {payment.get('externalReference', 'N/A')}")
                print("-" * 50)
            
            # Comparar com sistema local
            print("\n🔄 Comparando com sistema local...")
            cobrancas_locais = CobrancaAsaas.objects.all()
            
            asaas_ids = {p['id'] for p in payments}
            local_ids = {c.asaas_id for c in cobrancas_locais}
            
            # Cobranças que existem no Asaas mas não no sistema local
            missing_local = asaas_ids - local_ids
            if missing_local:
                print(f"\n⚠️ Cobranças no Asaas mas não no sistema local ({len(missing_local)}):")
                for payment_id in missing_local:
                    payment = next(p for p in payments if p['id'] == payment_id)
                    print(f"  - {payment_id} | R$ {payment['value']} | {payment['status']}")
            
            # Cobranças que existem no sistema local mas não no Asaas
            missing_asaas = local_ids - asaas_ids
            if missing_asaas:
                print(f"\n❌ Cobranças no sistema local mas não no Asaas ({len(missing_asaas)}):")
                for payment_id in missing_asaas:
                    cobranca = CobrancaAsaas.objects.get(asaas_id=payment_id)
                    print(f"  - {payment_id} | R$ {cobranca.valor} | {cobranca.status} | {cobranca.controle_financeiro.loja.nome}")
            
            if not missing_local and not missing_asaas:
                print("✅ Sistema local e Asaas estão sincronizados")
            
        elif response.status_code == 401:
            print("🔐 Erro de autenticação - verificar API key")
            
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        if "Connection refused" in str(e):
            print("🚫 Connection refused - API Asaas indisponível")
        else:
            print(f"🌐 Erro de conexão: {str(e)}")
            
    except Exception as e:
        print(f"💥 Erro: {str(e)}")


def check_specific_payments():
    """Verifica cobranças específicas mencionadas pelo usuário"""
    asaas_service = AsaasService()
    
    # IDs das cobranças locais
    local_payments = ['pay_o8er5tm3rzu26drx', 'pay_jpn0w57kgnp7n7ja']
    
    print("\n🔍 Verificando cobranças específicas no Asaas...")
    
    for payment_id in local_payments:
        try:
            response = requests.get(
                f"{asaas_service.base_url}/payments/{payment_id}",
                headers=asaas_service.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                payment = response.json()
                print(f"✅ {payment_id} existe no Asaas:")
                print(f"   Status: {payment['status']}")
                print(f"   Valor: R$ {payment['value']}")
                print(f"   Vencimento: {payment['dueDate']}")
                
            elif response.status_code == 404:
                print(f"❌ {payment_id} NÃO existe no Asaas (foi excluído)")
                
            else:
                print(f"⚠️ {payment_id} - Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"💥 Erro ao verificar {payment_id}: {str(e)}")


def main():
    print("🚀 Verificando cobranças no Asaas vs Sistema Local...")
    
    # Verificar todas as cobranças
    check_asaas_payments()
    
    # Verificar cobranças específicas
    check_specific_payments()
    
    print("\n🎯 Verificação concluída!")


if __name__ == '__main__':
    main()