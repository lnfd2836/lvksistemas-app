#!/usr/bin/env python
"""
Teste para verificar se a criação de cobrança funciona sem callback
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.models import ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService

def testar_cobranca_sem_callback():
    print("🎯 TESTE DE CRIAÇÃO DE COBRANÇA SEM CALLBACK")
    print("=" * 50)
    
    try:
        # 1. Buscar um controle financeiro existente
        controle = ControleFinanceiro.objects.first()
        
        if not controle:
            print("❌ Nenhum controle financeiro encontrado")
            return False
        
        print(f"✅ Controle encontrado: {controle.loja.nome}")
        print(f"   Valor: R$ {controle.valor_mensal}")
        
        # 2. Testar criação de cobrança
        print("\n🔄 Testando criação de cobrança...")
        asaas_service = AsaasService()
        
        if not asaas_service.validar_configuracao():
            print("❌ API do Asaas não configurada")
            return False
        
        resultado = asaas_service.gerar_cobranca_com_pix(controle, dias_vencimento=30)
        
        if resultado.get('success'):
            cobranca = resultado['cobranca']
            pix_data = resultado['pix']
            
            print("✅ Cobrança criada com sucesso!")
            print(f"   ID: {cobranca['id']}")
            print(f"   Valor: R$ {cobranca['value']}")
            print(f"   Vencimento: {cobranca['dueDate']}")
            print(f"   Status: {cobranca['status']}")
            
            if pix_data:
                print("✅ PIX gerado com sucesso!")
                print(f"   Tem QR Code: {'Sim' if pix_data.get('encodedImage') else 'Não'}")
                print(f"   Tem Copy Paste: {'Sim' if pix_data.get('payload') else 'Não'}")
            else:
                print("⚠️ PIX não foi gerado")
            
            return True
        else:
            print(f"❌ Erro ao criar cobrança: {resultado.get('error')}")
            if 'details' in resultado:
                print(f"   Detalhes: {resultado['details']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = testar_cobranca_sem_callback()
    if success:
        print("\n✅ Teste passou - Cobrança criada sem callback!")
    else:
        print("\n❌ Teste falhou - Ainda há problemas")
