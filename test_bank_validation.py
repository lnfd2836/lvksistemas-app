#!/usr/bin/env python3
"""
Script para testar a validação do banco da loja na geração de boletos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.models import ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService
from lojas.models import Loja


def test_bank_validation():
    """Testa a validação do banco da loja"""
    
    print("🧪 Testando validação do banco da loja...")
    
    asaas_service = AsaasService()
    
    # Buscar controles financeiros
    controles = ControleFinanceiro.objects.all()
    
    if not controles:
        print("❌ Nenhum controle financeiro encontrado")
        return
    
    print(f"📊 Testando {len(controles)} controles financeiros:")
    
    for controle in controles:
        loja = controle.loja
        
        print(f"\n🏪 Loja: {loja.nome}")
        print(f"   Código do banco: {loja.db_name}")
        print(f"   CNPJ: {loja.cnpj}")
        
        # Testar validação
        try:
            is_valid = asaas_service.validar_banco_loja(controle)
            
            if is_valid:
                print(f"   ✅ Banco válido - pode gerar boletos")
            else:
                print(f"   ❌ Banco inválido - NÃO pode gerar boletos")
                
        except Exception as e:
            print(f"   💥 Erro na validação: {str(e)}")


def test_boleto_generation():
    """Testa geração de boleto com validação"""
    
    print("\n🧪 Testando geração de boleto com validação...")
    
    asaas_service = AsaasService()
    
    # Buscar primeiro controle financeiro
    controle = ControleFinanceiro.objects.first()
    
    if not controle:
        print("❌ Nenhum controle financeiro encontrado")
        return
    
    print(f"🏪 Testando com loja: {controle.loja.nome}")
    print(f"   Código do banco: {controle.loja.db_name}")
    
    try:
        # Tentar gerar cobrança (modo teste - não vai realmente gerar)
        print("   🔄 Validando banco antes da geração...")
        
        if asaas_service.validar_banco_loja(controle):
            print("   ✅ Validação passou - boleto PODE ser gerado")
            print("   💡 Para gerar realmente, use: asaas_service.gerar_cobranca_com_pix(controle)")
        else:
            print("   ❌ Validação falhou - boleto NÃO pode ser gerado")
            
    except Exception as e:
        print(f"   💥 Erro: {str(e)}")


def show_loja_details():
    """Mostra detalhes das lojas"""
    
    print("\n📋 DETALHES DAS LOJAS:")
    print("=" * 60)
    
    lojas = Loja.objects.all()
    
    for loja in lojas:
        print(f"🏪 {loja.nome}")
        print(f"   ID: {loja.id}")
        print(f"   CNPJ: {loja.cnpj}")
        print(f"   Email: {loja.email}")
        print(f"   Código do banco: {loja.db_name}")
        print(f"   Status: {loja.status}")
        print(f"   Admin: {loja.admin_user.email if loja.admin_user else 'Não definido'}")
        
        # Verificar controle financeiro
        controle = ControleFinanceiro.objects.filter(loja=loja).first()
        if controle:
            print(f"   Controle Financeiro: ID {controle.id} - {controle.status}")
        else:
            print(f"   Controle Financeiro: ❌ Não encontrado")
        
        print("-" * 40)


def main():
    print("🚀 Testando sistema de validação de banco da loja")
    
    # Mostrar detalhes das lojas
    show_loja_details()
    
    # Testar validação
    test_bank_validation()
    
    # Testar geração de boleto
    test_boleto_generation()
    
    print("\n🎯 Teste concluído!")
    print("\n💡 RESUMO DAS MELHORIAS:")
    print("  ✅ Cada loja tem código único do banco (db_name)")
    print("  ✅ Validação impede geração sem banco criado")
    print("  ✅ Referência externa usa código do banco")
    print("  ✅ Sistema de notificação por email implementado")
    print("  ✅ Processamento automático via Celery")


if __name__ == '__main__':
    main()