#!/usr/bin/env python
"""
Teste simples de sincronização no Heroku
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.asaas_sync_service import get_sync_service

def main():
    print("🔄 TESTE DE SINCRONIZAÇÃO HEROKU")
    print("=" * 35)
    
    try:
        sync_service = get_sync_service()
        
        # Executar teste de conectividade
        print("1. Testando conectividade...")
        result = sync_service.simple_sync_check()
        
        print(f"   API acessível: {result['api_accessible']}")
        print(f"   Config válida: {result['config_valid']}")
        print(f"   Cobranças testadas: {result['sample_charges_checked']}")
        
        if result['errors']:
            print(f"   Erros: {len(result['errors'])}")
            for error in result['errors'][:2]:
                print(f"     • {error}")
        
        # Executar sincronização limitada
        print("\n2. Executando sincronização limitada...")
        sync_result = sync_service._sync_existing_charges_limited()
        
        print(f"   Processadas: {sync_result['processed']}")
        print(f"   Atualizadas: {sync_result['updates']}")
        print(f"   Erros: {len(sync_result['errors'])}")
        
        if sync_result['errors']:
            print("   Erros encontrados:")
            for error in sync_result['errors'][:2]:
                print(f"     • {error}")
        
        # Status final
        if result['api_accessible'] and sync_result['processed'] > 0:
            print("\n✅ SINCRONIZAÇÃO FUNCIONANDO!")
            print("🌐 A API Asaas está acessível")
            print("📊 Cobranças foram processadas")
        else:
            print("\n⚠️  SINCRONIZAÇÃO COM LIMITAÇÕES")
            print("🔍 Verifique os erros acima")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")

if __name__ == '__main__':
    main()