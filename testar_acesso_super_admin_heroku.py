#!/usr/bin/env python
"""
Script para testar se o super admin pode acessar as lojas no Heroku
"""

import requests
import sys

def testar_acesso_heroku():
    """
    Testa o acesso às URLs do Heroku
    """
    print("🧪 TESTANDO ACESSO DO SUPER ADMIN NO HEROKU")
    print("=" * 60)
    
    base_url = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
    
    urls_teste = [
        "/",
        "/admin/",
        "/lojas/",
    ]
    
    for url in urls_teste:
        full_url = base_url + url
        print(f"🔍 Testando: {full_url}")
        
        try:
            response = requests.get(full_url, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {url} - Status: {response.status_code} (OK)")
            elif response.status_code == 302:
                print(f"🔄 {url} - Status: {response.status_code} (Redirecionamento)")
                if 'location' in response.headers:
                    print(f"   → Redirecionando para: {response.headers['location']}")
            elif response.status_code == 403:
                print(f"❌ {url} - Status: {response.status_code} (BLOQUEADO)")
            elif response.status_code == 404:
                print(f"⚠️ {url} - Status: {response.status_code} (Não encontrado)")
            elif response.status_code == 500:
                print(f"🚨 {url} - Status: {response.status_code} (Erro interno)")
            else:
                print(f"⚠️ {url} - Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ {url} - Timeout (servidor pode estar lento)")
        except requests.exceptions.RequestException as e:
            print(f"❌ {url} - Erro de conexão: {e}")
    
    print("=" * 60)
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
    print("2. Faça login como super admin")
    print("3. Teste o acesso a: https://lvksistemas-app-4f6fa281e217.herokuapp.com/lojas/")
    print("=" * 60)

if __name__ == '__main__':
    testar_acesso_heroku()