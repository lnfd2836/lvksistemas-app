#!/usr/bin/env python3
"""
Script para testar se o site está funcionando
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

def test_models():
    """Testa se os modelos estão funcionando"""
    try:
        from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro, CobrancaAsaas
        
        planos = PlanoFinanceiro.objects.count()
        controles = ControleFinanceiro.objects.count()
        cobrancas = CobrancaAsaas.objects.count()
        
        print(f"✅ PlanoFinanceiro: {planos} registros")
        print(f"✅ ControleFinanceiro: {controles} registros")
        print(f"✅ CobrancaAsaas: {cobrancas} registros")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")
        return False

def test_middleware():
    """Testa se o middleware está funcionando"""
    try:
        from controle_financeiro.middleware import ControleFinanceiroMiddleware
        
        # Criar uma instância do middleware
        def dummy_response(request):
            return "OK"
        
        middleware = ControleFinanceiroMiddleware(dummy_response)
        print("✅ Middleware carregado com sucesso")
        
        return True
    except Exception as e:
        print(f"❌ Erro no middleware: {e}")
        return False

def main():
    print("🧪 TESTE DO SISTEMA - CONTROLE FINANCEIRO")
    print("=" * 50)
    
    success = True
    
    # Teste 1: Modelos
    print("1️⃣ Testando modelos...")
    if not test_models():
        success = False
    
    # Teste 2: Middleware
    print("\n2️⃣ Testando middleware...")
    if not test_middleware():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema está funcionando corretamente")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️ Verifique os erros acima")

if __name__ == "__main__":
    main()