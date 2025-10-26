#!/usr/bin/env python3
"""
Script de correção imediata para sincronização no Heroku
Execute: heroku run python fix_heroku_sync_now.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro, PlanoFinanceiro
from controle_financeiro.asaas_service import AsaasService
from lojas.models import Loja
from decimal import Decimal
from datetime import datetime, timedelta
import requests


def main():
    print("🚀 CORREÇÃO IMEDIATA - SINCRONIZAÇÃO HEROKU")
    print("=" * 60)
    
    try:
        # 1. Verificar configuração básica
        print("🔧 Verificando configuração...")
        
        asaas_service = AsaasService()
        if not asaas_service.api_key:
            print("❌ ASAAS_API_KEY não configurada!")
            return
        
        print(f"✅ API Key configurada: {asaas_service.api_key[:10]}...")
        print(f"✅ Ambiente: {asaas_service.environment}")
        
        # 2. Verificar lojas e controles
        print("\n🏪 Verificando lojas...")
        
        lojas = Loja.objects.all()
        print(f"📊 Lojas encontradas: {len(lojas)}")
        
        for loja in lojas:
            print(f"  • {loja.nome} | {loja.db_name}")
            
            # Verificar/criar controle financeiro
            controle = ControleFinanceiro.objects.filter(loja=loja).first()
            if not controle:
                print(f"    ⚠️ Criando controle financeiro...")
                
                plano = PlanoFinanceiro.objects.first()
                if not plano:
                    plano = PlanoFinanceiro.objects.create(
                        nome='Básico',
                        descricao='Plano básico',
                        valor_mensal=29.90,
                        ativo=True
                    )
                
                controle = ControleFinanceiro.objects.create(
                    loja=loja,
                    plano=plano,
                    status='ativa',
                    valor_mensal=plano.valor_mensal,
                    data_inicio=timezone.now(),
                    data_vencimento=timezone.now() + timedelta(days=30)
                )
                print(f"    ✅ Controle criado: ID {controle.id}")
            else:
                print(f"    ✅ Controle existe: ID {controle.id}")
        
        # 3. Buscar cobranças no Asaas
        print("\n📡 Buscando cobranças no Asaas...")
        
        data_inicio = (timezone.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{asaas_service.base_url}/payments",
            headers=asaas_service.headers,
            params={
                'dateCreated[ge]': data_inicio,
                'limit': 100
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        payments = data.get('data', [])
        
        print(f"✅ Encontradas {len(payments)} cobranças no Asaas")
        
        # 4. Sincronizar cobranças
        print("\n🔄 Sincronizando cobranças...")
        
        local_ids = set(CobrancaAsaas.objects.values_list('asaas_id', flat=True))
        synced_count = 0
        
        for payment in payments:
            payment_id = payment['id']
            
            if payment_id not in local_ids:
                print(f"  🔄 Sincronizando {payment_id}...")
                
                # Identificar controle financeiro
                controle = identify_controle(payment, asaas_service)
                
                if controle:
                    # Criar cobrança
                    try:
                        cobranca = CobrancaAsaas.objects.create(
                            asaas_id=payment_id,
                            controle_financeiro=controle,
                            customer_id=payment.get('customer', ''),
                            valor=Decimal(str(payment['value'])),
                            data_vencimento=datetime.fromisoformat(payment['dueDate']).replace(tzinfo=timezone.get_current_timezone()),
                            descricao=payment.get('description', ''),
                            status=payment['status'],
                            external_reference=payment.get('externalReference', ''),
                            invoice_url=payment.get('invoiceUrl', ''),
                            bank_slip_url=payment.get('bankSlipUrl', ''),
                            invoice_number=payment.get('invoiceNumber', ''),
                            api_response=payment,
                            observacoes=f"Sincronizada automaticamente - {timezone.now().strftime('%d/%m/%Y %H:%M')}"
                        )
                        
                        # Se já foi paga, processar
                        if payment['status'] in ['RECEIVED', 'CONFIRMED']:
                            cobranca.marcar_como_paga()
                        
                        synced_count += 1
                        print(f"    ✅ Criada para {controle.loja.nome}")
                        
                    except Exception as e:
                        print(f"    ❌ Erro: {str(e)}")
                else:
                    print(f"    ⚠️ Controle não identificado")
            else:
                print(f"  ✅ {payment_id} já existe")
        
        # 5. Mostrar resultado final
        print(f"\n🎯 RESULTADO:")
        print(f"  • Cobranças sincronizadas: {synced_count}")
        print(f"  • Total no sistema: {CobrancaAsaas.objects.count()}")
        
        # Mostrar por status
        status_count = {}
        for cobranca in CobrancaAsaas.objects.all():
            status = cobranca.status
            status_count[status] = status_count.get(status, 0) + 1
        
        print(f"\n📊 Por status:")
        for status, count in status_count.items():
            print(f"  • {status}: {count}")
        
        print(f"\n✅ SINCRONIZAÇÃO CONCLUÍDA!")
        print(f"🌐 Verifique: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/cobrancas/")
        
    except Exception as e:
        print(f"💥 ERRO: {str(e)}")
        import traceback
        traceback.print_exc()


def identify_controle(payment, asaas_service):
    """Identifica controle financeiro para cobrança"""
    
    # Método 1: Por referência externa
    external_ref = payment.get('externalReference', '')
    if external_ref and external_ref.startswith('CF_'):
        try:
            cf_id = external_ref.split('_')[1]
            return ControleFinanceiro.objects.get(id=cf_id)
        except (IndexError, ControleFinanceiro.DoesNotExist):
            pass
    
    # Método 2: Por customer
    customer_id = payment.get('customer')
    if customer_id:
        try:
            customer_response = requests.get(
                f"{asaas_service.base_url}/customers/{customer_id}",
                headers=asaas_service.headers,
                timeout=10
            )
            
            if customer_response.status_code == 200:
                customer_data = customer_response.json()
                customer_email = customer_data.get('email', '')
                customer_cnpj = customer_data.get('cpfCnpj', '')
                
                # Buscar por email
                if customer_email:
                    controle = ControleFinanceiro.objects.filter(
                        loja__email=customer_email
                    ).first()
                    if controle:
                        return controle
                
                # Buscar por CNPJ
                if customer_cnpj:
                    cnpj_limpo = customer_cnpj.replace('.', '').replace('/', '').replace('-', '')
                    controle = ControleFinanceiro.objects.filter(
                        loja__cnpj__contains=cnpj_limpo[:8]
                    ).first()
                    if controle:
                        return controle
                        
        except Exception:
            pass
    
    # Método 3: Primeiro controle disponível
    return ControleFinanceiro.objects.first()


if __name__ == '__main__':
    main()