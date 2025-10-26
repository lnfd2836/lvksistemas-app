#!/usr/bin/env python3
"""
Script para investigar as cobranças faltantes em detalhes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import ControleFinanceiro
from lojas.models import Loja
import requests
import json


def investigate_charges():
    """Investiga as cobranças faltantes em detalhes"""
    asaas_service = AsaasService()
    
    # IDs das cobranças faltantes
    missing_charges = [
        'pay_1k8i5vn1ujr8g6wa',
        'pay_skbidaq2qe30cr2l', 
        'pay_3b9ab8yhbhgf3b1p'
    ]
    
    print("🔍 Investigando cobranças faltantes em detalhes...\n")
    
    for payment_id in missing_charges:
        print(f"📋 COBRANÇA: {payment_id}")
        print("-" * 50)
        
        try:
            # Buscar dados da cobrança
            payment_response = requests.get(
                f"{asaas_service.base_url}/payments/{payment_id}",
                headers=asaas_service.headers,
                timeout=10
            )
            
            if payment_response.status_code == 200:
                payment = payment_response.json()
                
                print(f"Status: {payment['status']}")
                print(f"Valor: R$ {payment['value']}")
                print(f"Vencimento: {payment['dueDate']}")
                print(f"Descrição: {payment.get('description', 'N/A')}")
                print(f"Customer ID: {payment.get('customer', 'N/A')}")
                print(f"Referência Externa: {payment.get('externalReference', 'N/A')}")
                
                # Buscar dados do customer
                customer_id = payment.get('customer')
                if customer_id:
                    print(f"\n👤 CUSTOMER: {customer_id}")
                    
                    customer_response = requests.get(
                        f"{asaas_service.base_url}/customers/{customer_id}",
                        headers=asaas_service.headers,
                        timeout=10
                    )
                    
                    if customer_response.status_code == 200:
                        customer = customer_response.json()
                        
                        print(f"Nome: {customer.get('name', 'N/A')}")
                        print(f"Email: {customer.get('email', 'N/A')}")
                        print(f"CPF/CNPJ: {customer.get('cpfCnpj', 'N/A')}")
                        print(f"Telefone: {customer.get('phone', 'N/A')}")
                        print(f"Endereço: {customer.get('address', 'N/A')}")
                        print(f"Cidade: {customer.get('city', 'N/A')}")
                        print(f"Estado: {customer.get('state', 'N/A')}")
                        print(f"Referência Externa: {customer.get('externalReference', 'N/A')}")
                        
                        # Verificar se existe loja com esses dados
                        customer_email = customer.get('email', '')
                        customer_cnpj = customer.get('cpfCnpj', '')
                        
                        print(f"\n🏪 VERIFICAÇÃO DE LOJA EXISTENTE:")
                        
                        loja_por_email = None
                        loja_por_cnpj = None
                        
                        if customer_email:
                            loja_por_email = Loja.objects.filter(email=customer_email).first()
                            if loja_por_email:
                                print(f"✅ Loja encontrada por email: {loja_por_email.nome} (ID: {loja_por_email.id})")
                            else:
                                print(f"❌ Nenhuma loja encontrada com email: {customer_email}")
                        
                        if customer_cnpj:
                            loja_por_cnpj = Loja.objects.filter(cnpj=customer_cnpj).first()
                            if loja_por_cnpj:
                                print(f"✅ Loja encontrada por CNPJ: {loja_por_cnpj.nome} (ID: {loja_por_cnpj.id})")
                            else:
                                print(f"❌ Nenhuma loja encontrada com CNPJ: {customer_cnpj}")
                        
                        # Verificar controle financeiro
                        loja_encontrada = loja_por_email or loja_por_cnpj
                        if loja_encontrada:
                            controle = ControleFinanceiro.objects.filter(loja=loja_encontrada).first()
                            if controle:
                                print(f"✅ Controle financeiro encontrado: ID {controle.id}")
                            else:
                                print(f"❌ Nenhum controle financeiro para a loja {loja_encontrada.nome}")
                        
                    else:
                        print(f"❌ Erro ao buscar customer: {customer_response.status_code}")
                
            else:
                print(f"❌ Erro ao buscar cobrança: {payment_response.status_code}")
                
        except Exception as e:
            print(f"💥 Erro: {str(e)}")
        
        print("\n" + "="*60 + "\n")


def list_existing_lojas():
    """Lista lojas existentes no sistema"""
    print("🏪 LOJAS EXISTENTES NO SISTEMA:")
    print("-" * 50)
    
    lojas = Loja.objects.all()
    for loja in lojas:
        print(f"ID: {loja.id}")
        print(f"Nome: {loja.nome}")
        print(f"Email: {loja.email}")
        print(f"CNPJ: {loja.cnpj}")
        
        # Verificar controle financeiro
        controle = ControleFinanceiro.objects.filter(loja=loja).first()
        if controle:
            print(f"Controle Financeiro: ID {controle.id} - {controle.status}")
        else:
            print("Controle Financeiro: ❌ Não encontrado")
        
        print("-" * 30)


def main():
    print("🚀 Investigação detalhada das cobranças faltantes\n")
    
    # Listar lojas existentes
    list_existing_lojas()
    
    print("\n")
    
    # Investigar cobranças
    investigate_charges()


if __name__ == '__main__':
    main()