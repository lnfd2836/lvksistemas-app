#!/usr/bin/env python3
"""
Debug Direto das Settings
"""

import os
import sys
from pathlib import Path

# Remove .env para simular Heroku
if os.path.exists('.env'):
    os.rename('.env', '.env.backup')
    print("📁 .env renomeado temporariamente")

# Configura variáveis como no Heroku
os.environ['ASAAS_API_KEY'] = '$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl'
os.environ['ASAAS_ENVIRONMENT'] = 'production'
os.environ['DYNO'] = 'web.1'
os.environ['SECRET_KEY'] = 'test-key'
os.environ['DEBUG'] = 'False'

print("🔧 VARIÁVEIS DE AMBIENTE:")
print(f"ASAAS_API_KEY: {os.environ.get('ASAAS_API_KEY', 'NÃO DEFINIDA')[:30]}...")
print(f"ASAAS_ENVIRONMENT: {os.environ.get('ASAAS_ENVIRONMENT', 'NÃO DEFINIDA')}")

# Configura Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    
    print(f"\n📋 SETTINGS DJANGO:")
    print(f"ASAAS_API_KEY: {getattr(settings, 'ASAAS_API_KEY', 'NÃO DEFINIDA')[:30] if getattr(settings, 'ASAAS_API_KEY', None) else 'NÃO DEFINIDA'}...")
    print(f"ASAAS_ENVIRONMENT: {getattr(settings, 'ASAAS_ENVIRONMENT', 'NÃO DEFINIDA')}")
    
    # Testa diretamente
    api_key = getattr(settings, 'ASAAS_API_KEY', None)
    
    if api_key:
        print(f"\n✅ API Key encontrada nas settings!")
        print(f"📏 Tamanho: {len(api_key)} caracteres")
        print(f"🔤 Formato: {'Válido' if api_key.startswith('$aact_') else 'Inválido'}")
        
        # Testa conexão direta
        import requests
        
        headers = {
            'access_token': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LVK-Sistemas/1.0'
        }
        
        print(f"\n🔗 Testando conexão direta...")
        response = requests.get("https://www.asaas.com/api/v3/myAccount", headers=headers, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexão funcionando!")
            print(f"👤 Conta: {data.get('name', 'N/A')}")
        else:
            print(f"❌ Erro na conexão")
            
    else:
        print(f"\n❌ API Key NÃO encontrada nas settings!")
        print("🔍 Verificando environ...")
        
        # Verifica se está no environ
        env_key = os.environ.get('ASAAS_API_KEY')
        if env_key:
            print(f"✅ Encontrada no environ: {env_key[:30]}...")
        else:
            print(f"❌ Não encontrada no environ")
            
        # Verifica se django-environ está funcionando
        try:
            import environ
            env = environ.Env()
            test_key = env('ASAAS_API_KEY', default='NOT_FOUND')
            print(f"🧪 django-environ test: {test_key[:30] if test_key != 'NOT_FOUND' else 'NOT_FOUND'}...")
        except Exception as e:
            print(f"❌ Erro no django-environ: {e}")

finally:
    # Restaura .env
    if os.path.exists('.env.backup'):
        os.rename('.env.backup', '.env')
        print(f"\n📁 .env restaurado")