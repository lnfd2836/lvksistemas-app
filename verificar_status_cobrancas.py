#!/usr/bin/env python
"""
Script para verificar o status das cobranças Asaas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.models import CobrancaAsaas

def verificar_cobrancas():
    """Verifica o status das cobranças"""
    
    print("🔍 VERIFICANDO STATUS DAS COBRANÇAS ASAAS")
    print("=" * 60)
    
    cobrancas = CobrancaAsaas.objects.all().order_by('-data_criacao')
    
    if not cobrancas.exists():
        print("❌ Nenhuma cobrança encontrada!")
        print("💡 Crie uma cobrança primeiro para testar a exclusão")
        return False
    
    print(f"✅ {cobrancas.count()} cobranças encontradas:")
    print()
    
    status_count = {}
    
    for cobranca in cobrancas:
        status = cobranca.status
        status_count[status] = status_count.get(status, 0) + 1
        
        print(f"📋 ID: {cobranca.id}")
        print(f"   Asaas ID: {cobranca.asaas_id}")
        print(f"   Loja: {cobranca.controle_financeiro.loja.nome}")
        print(f"   Status: {status}")
        print(f"   Valor: R$ {cobranca.valor}")
        print(f"   Vencimento: {cobranca.data_vencimento}")
        print(f"   Criação: {cobranca.data_criacao}")
        
        # Verificar se botão apareceria
        if status == 'PENDING':
            print(f"   🗑️  BOTÃO DE EXCLUIR: ✅ APARECE")
        else:
            print(f"   🗑️  BOTÃO DE EXCLUIR: ❌ NÃO APARECE (status não é PENDING)")
        
        print("-" * 40)
    
    print("\n📊 RESUMO POR STATUS:")
    for status, count in status_count.items():
        emoji = "🗑️" if status == 'PENDING' else "🚫"
        print(f"   {emoji} {status}: {count} cobranças")
    
    print("\n💡 DICA:")
    print("   O botão de excluir só aparece para cobranças com status 'PENDING'")
    print("   Se não há botões, é porque todas as cobranças já foram processadas")
    
    return True

def main():
    """Executa verificação"""
    
    print("🚀 DIAGNÓSTICO DO BOTÃO DE EXCLUIR")
    print("=" * 60)
    print("Verificando por que o botão pode não estar aparecendo...")
    print()
    
    if verificar_cobrancas():
        print("\n✅ VERIFICAÇÃO CONCLUÍDA!")
        print()
        print("🔧 SOLUÇÕES:")
        print("1. Se não há cobranças PENDING:")
        print("   - Crie uma nova cobrança para testar")
        print("   - Acesse: /financeiro/asaas/cobrancas/criar/")
        print()
        print("2. Se há cobranças mas não são PENDING:")
        print("   - O botão só aparece para cobranças pendentes")
        print("   - Cobranças pagas/vencidas não podem ser excluídas")
        print()
        print("3. Para forçar exibição (teste):")
        print("   - Posso modificar temporariamente a condição")
        return True
    else:
        print("\n❌ PROBLEMA IDENTIFICADO")
        print("Não há cobranças no sistema")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)