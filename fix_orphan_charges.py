#!/usr/bin/env python3
"""
Script para corrigir cobranças órfãs e associá-las às lojas corretas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro, PlanoFinanceiro
from controle_financeiro.asaas_service import AsaasService
from lojas.models import Loja
from decimal import Decimal
import requests
import re


class OrphanChargesFixer:
    """Corrige cobranças órfãs"""
    
    def __init__(self):
        self.asaas_service = AsaasService()
        self.fixed_charges = []
        self.errors = []
    
    def fix_specific_charges(self):
        """Corrige cobranças específicas identificadas"""
        charges_to_fix = [
            {
                'payment_id': 'pay_1k8i5vn1ujr8g6wa',
                'strategy': 'reference_mismatch',
                'expected_loja': 'Fatesa Escola de Ultrassonografia'  # CNPJ similar
            },
            {
                'payment_id': 'pay_skbidaq2qe30cr2l',
                'strategy': 'pix_automatic',
                'expected_loja': 'Loja Felix'  # Nome similar "Felix"
            },
            {
                'payment_id': 'pay_3b9ab8yhbhgf3b1p',
                'strategy': 'pix_automatic', 
                'expected_loja': 'Loja Felix'  # Nome similar "Felix"
            }
        ]
        
        print("🔧 Corrigindo cobranças órfãs específicas...")
        
        for charge_info in charges_to_fix:
            try:
                self._fix_single_charge(charge_info)
            except Exception as e:
                print(f"💥 Erro ao corrigir {charge_info['payment_id']}: {str(e)}")
                self.errors.append(f"Erro em {charge_info['payment_id']}: {str(e)}")
    
    def _fix_single_charge(self, charge_info):
        """Corrige uma cobrança específica"""
        payment_id = charge_info['payment_id']
        strategy = charge_info['strategy']
        expected_loja_name = charge_info['expected_loja']
        
        print(f"\n🔧 Corrigindo cobrança {payment_id} (estratégia: {strategy})")
        
        # Buscar dados da cobrança no Asaas
        payment_response = requests.get(
            f"{self.asaas_service.base_url}/payments/{payment_id}",
            headers=self.asaas_service.headers,
            timeout=10
        )
        
        if payment_response.status_code != 200:
            raise Exception(f"Erro ao buscar cobrança: {payment_response.status_code}")
        
        payment = payment_response.json()
        
        # Encontrar loja apropriada
        loja = self._find_appropriate_loja(payment, expected_loja_name, strategy)
        
        if not loja:
            raise Exception(f"Não foi possível encontrar loja apropriada")
        
        print(f"✅ Loja encontrada: {loja.nome}")
        
        # Encontrar ou criar controle financeiro
        controle = ControleFinanceiro.objects.filter(loja=loja).first()
        
        if not controle:
            # Criar controle financeiro
            plano_basico = PlanoFinanceiro.objects.filter(nome='Básico').first()
            if not plano_basico:
                plano_basico = PlanoFinanceiro.objects.create(
                    nome='Básico',
                    descricao='Plano básico',
                    valor_mensal=29.90,
                    ativo=True
                )
            
            controle = ControleFinanceiro.objects.create(
                loja=loja,
                plano=plano_basico,
                status='ativa',
                valor_mensal=Decimal(str(payment['value'])),
                data_inicio=timezone.now(),
                data_vencimento=timezone.now() + timedelta(days=30)
            )
            print(f"✅ Controle financeiro criado: ID {controle.id}")
        else:
            print(f"✅ Controle financeiro existente: ID {controle.id}")
        
        # Criar cobrança no sistema
        with transaction.atomic():
            cobranca = CobrancaAsaas.objects.create(
                asaas_id=payment_id,
                controle_financeiro=controle,
                customer_id=payment.get('customer', ''),
                valor=Decimal(str(payment['value'])),
                data_vencimento=timezone.now().replace(
                    year=int(payment['dueDate'][:4]),
                    month=int(payment['dueDate'][5:7]),
                    day=int(payment['dueDate'][8:10])
                ),
                descricao=payment.get('description', ''),
                status=payment['status'],
                external_reference=payment.get('externalReference') or '',
                invoice_url=payment.get('invoiceUrl', ''),
                bank_slip_url=payment.get('bankSlipUrl', ''),
                invoice_number=payment.get('invoiceNumber', ''),
                api_response=payment,
                observacoes=f"Cobrança órfã corrigida automaticamente - Estratégia: {strategy}"
            )
            
            # Atualizar dados adicionais
            cobranca.atualizar_dados_asaas(payment)
            
            # Se já foi paga, processar pagamento
            if payment['status'] in ['RECEIVED', 'CONFIRMED']:
                cobranca.marcar_como_paga()
                print(f"✅ Pagamento processado automaticamente")
            
            print(f"✅ Cobrança {payment_id} criada com sucesso")
            
            self.fixed_charges.append({
                'payment_id': payment_id,
                'loja': loja.nome,
                'controle_id': controle.id,
                'valor': payment['value'],
                'status': payment['status'],
                'strategy': strategy
            })
    
    def _find_appropriate_loja(self, payment, expected_loja_name, strategy):
        """Encontra a loja apropriada para a cobrança"""
        
        if strategy == 'reference_mismatch':
            # Para cobranças com referência externa mas controle inexistente
            # Usar loja com CNPJ similar
            customer_id = payment.get('customer')
            if customer_id:
                customer_response = requests.get(
                    f"{self.asaas_service.base_url}/customers/{customer_id}",
                    headers=self.asaas_service.headers,
                    timeout=10
                )
                
                if customer_response.status_code == 200:
                    customer = customer_response.json()
                    customer_cnpj = customer.get('cpfCnpj', '')
                    
                    if customer_cnpj:
                        # Limpar CNPJ
                        cnpj_limpo = re.sub(r'[^0-9]', '', customer_cnpj)
                        
                        # Buscar loja com CNPJ similar (primeiros dígitos)
                        if cnpj_limpo.startswith('24758458'):
                            return Loja.objects.filter(nome__icontains='Fatesa').first()
            
            # Fallback: buscar por nome esperado
            return Loja.objects.filter(nome__icontains=expected_loja_name.split()[0]).first()
        
        elif strategy == 'pix_automatic':
            # Para cobranças automáticas de PIX
            # Usar loja com nome similar ao customer
            customer_id = payment.get('customer')
            if customer_id:
                customer_response = requests.get(
                    f"{self.asaas_service.base_url}/customers/{customer_id}",
                    headers=self.asaas_service.headers,
                    timeout=10
                )
                
                if customer_response.status_code == 200:
                    customer = customer_response.json()
                    customer_name = customer.get('name', '')
                    
                    if 'Felix' in customer_name:
                        return Loja.objects.filter(nome__icontains='Felix').first()
            
            # Fallback: usar primeira loja disponível
            return Loja.objects.first()
        
        return None
    
    def generate_report(self):
        """Gera relatório da correção"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE CORREÇÃO DE COBRANÇAS ÓRFÃS")
        print("="*60)
        
        print(f"✅ Cobranças corrigidas: {len(self.fixed_charges)}")
        print(f"❌ Erros: {len(self.errors)}")
        
        if self.fixed_charges:
            print("\n✅ COBRANÇAS CORRIGIDAS:")
            for charge in self.fixed_charges:
                print(f"  • {charge['payment_id']} → {charge['loja']}")
                print(f"    Controle: {charge['controle_id']} | R$ {charge['valor']} | {charge['status']}")
                print(f"    Estratégia: {charge['strategy']}")
                print()
        
        if self.errors:
            print("\n❌ ERROS:")
            for error in self.errors:
                print(f"  • {error}")
        
        print("="*60)


def main():
    print("🚀 Iniciando correção de cobranças órfãs...")
    
    fixer = OrphanChargesFixer()
    
    # Corrigir cobranças específicas
    fixer.fix_specific_charges()
    
    # Gerar relatório
    fixer.generate_report()
    
    print("\n🎯 Correção concluída!")
    print("💡 Verifique a interface web para confirmar que as cobranças apareceram")


if __name__ == '__main__':
    main()