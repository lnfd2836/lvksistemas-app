#!/usr/bin/env python3
"""
Script para inserir cobranças diretamente via SQL, contornando as restrições do Django ORM
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import connection
from django.utils import timezone
from controle_financeiro.asaas_service import AsaasService
import requests
import uuid
import json


def insert_charges_directly():
    """Insere cobranças diretamente via SQL"""
    
    asaas_service = AsaasService()
    
    # Dados das cobranças para inserir
    charges_data = [
        {
            'payment_id': 'pay_1k8i5vn1ujr8g6wa',
            'controle_id': 75,  # Fatesa
            'strategy': 'reference_mismatch'
        },
        {
            'payment_id': 'pay_skbidaq2qe30cr2l',
            'controle_id': 83,  # Loja Felix
            'strategy': 'pix_automatic'
        },
        {
            'payment_id': 'pay_3b9ab8yhbhgf3b1p',
            'controle_id': 83,  # Loja Felix
            'strategy': 'pix_automatic'
        }
    ]
    
    cursor = connection.cursor()
    inserted_count = 0
    
    for charge_data in charges_data:
        payment_id = charge_data['payment_id']
        controle_id = charge_data['controle_id']
        strategy = charge_data['strategy']
        
        print(f"🔄 Inserindo cobrança {payment_id}...")
        
        try:
            # Buscar dados da cobrança no Asaas
            payment_response = requests.get(
                f"{asaas_service.base_url}/payments/{payment_id}",
                headers=asaas_service.headers,
                timeout=10
            )
            
            if payment_response.status_code != 200:
                print(f"❌ Erro ao buscar cobrança {payment_id}: {payment_response.status_code}")
                continue
            
            payment = payment_response.json()
            
            # Preparar dados para inserção
            cobranca_id = str(uuid.uuid4()).replace('-', '')
            customer_id = payment.get('customer', '')
            valor = payment['value']
            data_vencimento = payment['dueDate'] + ' 23:59:59'
            descricao = payment.get('description', '')
            status = payment['status']
            external_reference = payment.get('externalReference') or ''
            invoice_url = payment.get('invoiceUrl', '')
            bank_slip_url = payment.get('bankSlipUrl', '')
            invoice_number = payment.get('invoiceNumber', '')
            api_response = json.dumps(payment)
            observacoes = f'Cobrança órfã corrigida automaticamente - Estratégia: {strategy}'
            data_criacao = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            data_atualizacao = data_criacao
            
            # Inserir via SQL direto
            sql = """
                INSERT INTO controle_financeiro_cobrancaasaas (
                    id, asaas_id, customer_id, valor, data_vencimento, descricao,
                    status, data_pagamento, invoice_url, bank_slip_url, invoice_number,
                    pix_qr_code, pix_copy_paste, pix_expires_date, api_response,
                    external_reference, observacoes, data_criacao, data_atualizacao,
                    controle_financeiro_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            cursor.execute(sql, [
                cobranca_id,
                payment_id,
                customer_id,
                valor,
                data_vencimento,
                descricao,
                status,
                None,  # data_pagamento
                invoice_url,
                bank_slip_url,
                invoice_number,
                '',  # pix_qr_code
                '',  # pix_copy_paste
                None,  # pix_expires_date
                api_response,
                external_reference,
                observacoes,
                data_criacao,
                data_atualizacao,
                controle_id
            ])
            
            print(f"✅ Cobrança {payment_id} inserida com sucesso")
            inserted_count += 1
            
            # Se a cobrança já foi paga, processar pagamento
            if status in ['RECEIVED', 'CONFIRMED']:
                print(f"💰 Processando pagamento para cobrança {payment_id}...")
                
                # Buscar controle financeiro e processar pagamento
                from controle_financeiro.models import ControleFinanceiro
                from decimal import Decimal
                
                try:
                    controle = ControleFinanceiro.objects.get(id=controle_id)
                    controle.processar_pagamento(
                        Decimal(str(valor)),
                        f"Pagamento via Asaas - Cobrança {payment_id} (corrigida automaticamente)"
                    )
                    print(f"✅ Pagamento processado para {payment_id}")
                except Exception as e:
                    print(f"⚠️ Erro ao processar pagamento para {payment_id}: {str(e)}")
            
        except Exception as e:
            print(f"💥 Erro ao inserir cobrança {payment_id}: {str(e)}")
    
    print(f"\n🎯 Inserção concluída: {inserted_count} cobranças inseridas")
    return inserted_count


def verify_insertions():
    """Verifica se as inserções foram bem-sucedidas"""
    print("\n🔍 Verificando cobranças inseridas...")
    
    from controle_financeiro.models import CobrancaAsaas
    
    payment_ids = [
        'pay_1k8i5vn1ujr8g6wa',
        'pay_skbidaq2qe30cr2l', 
        'pay_3b9ab8yhbhgf3b1p'
    ]
    
    for payment_id in payment_ids:
        try:
            cobranca = CobrancaAsaas.objects.get(asaas_id=payment_id)
            print(f"✅ {payment_id} - {cobranca.controle_financeiro.loja.nome} - R$ {cobranca.valor} - {cobranca.status}")
        except CobrancaAsaas.DoesNotExist:
            print(f"❌ {payment_id} - Não encontrada")


def main():
    print("🚀 Inserindo cobranças órfãs diretamente via SQL...")
    
    # Inserir cobranças
    inserted = insert_charges_directly()
    
    if inserted > 0:
        # Verificar inserções
        verify_insertions()
        
        print(f"\n🎉 Sucesso! {inserted} cobranças foram inseridas")
        print("💡 Agora verifique a interface web - as cobranças devem aparecer")
        print("🔄 A sincronização deve funcionar normalmente a partir de agora")
    else:
        print("\n❌ Nenhuma cobrança foi inserida")


if __name__ == '__main__':
    main()