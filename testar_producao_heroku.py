#!/usr/bin/env python3
"""
Script para testar o login personalizado em produção no Heroku
"""

import requests
import time
from urllib.parse import urljoin

# URLs base do Heroku
HEROKU_URLS = [
    'https://lvksistemas.herokuapp.com',
    'https://lvksistemas-app-4f6fa281e217.herokuapp.com',
    'https://loja-conveniencia-pdv-7fed430df60a.herokuapp.com'
]

# URLs de login personalizado para testar
LOGIN_URLS = [
    '/login/felix-ribeirao-pretosp-clinica-de-estetica/',
    '/login/loja-felix/',
    '/login/fatesa-escola-de-ultrassonografia/'
]

def testar_url_heroku(base_url, path):
    """Testa uma URL específica no Heroku"""
    
    full_url = urljoin(base_url, path)
    
    try:
        print(f"   🧪 Testando: {full_url}")
        
        # Fazer requisição com timeout
        response = requests.get(full_url, timeout=30, allow_redirects=True)
        
        if response.status_code == 200:
            print(f"   ✅ Status 200 - Página carregou corretamente")
            
            # Verificar se contém elementos esperados
            content = response.text.lower()
            
            if 'login' in content:
                print(f"   ✅ Contém formulário de login")
            
            if 'csrf' in content:
                print(f"   ✅ CSRF token presente")
                
            if 'bootstrap' in content or 'css' in content:
                print(f"   ✅ CSS carregando")
                
            return True
            
        elif response.status_code == 302:
            print(f"   ↗️ Redirecionamento (302) para: {response.headers.get('Location', 'N/A')}")
            return True
            
        else:
            print(f"   ❌ Status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout - Heroku pode estar dormindo")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Erro de conexão")
        return False
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

def testar_dashboard_heroku(base_url):
    """Testa o dashboard principal"""
    
    dashboard_url = urljoin(base_url, '/dashboard/')
    
    try:
        print(f"   🧪 Testando dashboard: {dashboard_url}")
        
        response = requests.get(dashboard_url, timeout=30, allow_redirects=False)
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            if '/login/' in redirect_location:
                print(f"   ✅ Redirecionamento correto para login")
                return True
            else:
                print(f"   ⚠️ Redirecionamento inesperado: {redirect_location}")
                return False
        else:
            print(f"   ❌ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no dashboard: {str(e)}")
        return False

def acordar_heroku(base_url):
    """Acorda o Heroku se estiver dormindo"""
    
    try:
        print(f"   ⏰ Acordando Heroku...")
        response = requests.get(base_url, timeout=60)
        print(f"   ✅ Heroku acordado (Status: {response.status_code})")
        time.sleep(2)  # Aguardar um pouco
        return True
    except:
        print(f"   ❌ Erro ao acordar Heroku")
        return False

def main():
    """Função principal"""
    
    print("🚀 Testando Login Personalizado em Produção no Heroku...")
    print("=" * 60)
    
    for base_url in HEROKU_URLS:
        print(f"\n🌐 Testando: {base_url}")
        print("-" * 50)
        
        # Tentar acordar o Heroku primeiro
        if not acordar_heroku(base_url):
            continue
        
        # Testar dashboard principal
        testar_dashboard_heroku(base_url)
        
        # Testar URLs de login personalizado
        sucessos = 0
        total = len(LOGIN_URLS)
        
        for login_path in LOGIN_URLS:
            if testar_url_heroku(base_url, login_path):
                sucessos += 1
            print()  # Linha em branco
        
        # Resumo para esta URL base
        print(f"   📊 Resumo: {sucessos}/{total} URLs funcionando")
        
        if sucessos == total:
            print(f"   🎉 Todos os logins personalizados funcionando!")
        elif sucessos > 0:
            print(f"   ⚠️ Alguns logins funcionando, verificar logs")
        else:
            print(f"   ❌ Nenhum login funcionando, verificar deploy")
    
    print("\n" + "=" * 60)
    print("✅ Teste de produção concluído!")
    print("\n📋 Próximos passos se houver problemas:")
    print("1. Verificar logs: heroku logs --tail")
    print("2. Verificar variáveis: heroku config")
    print("3. Verificar build: heroku releases")
    print("4. Reiniciar se necessário: heroku restart")

if __name__ == "__main__":
    main()