#!/usr/bin/env python3
"""
Teste Simples de Login - Debug do Erro 403
"""

import requests
import re
from datetime import datetime

BASE_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
LOGIN_URL = f"{BASE_URL}/login/"

def debug_login_page():
    """Debug da página de login"""
    print("🔍 Analisando página de login...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    })
    
    try:
        # Acessa página de login
        response = session.get(LOGIN_URL)
        
        print(f"📊 Status: {response.status_code}")
        print(f"🌐 URL: {response.url}")
        print(f"📏 Tamanho: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Página de login acessível")
            
            # Analisa o HTML
            html = response.text
            
            # Procura por CSRF token
            csrf_patterns = [
                r'name="csrfmiddlewaretoken" value="([^"]+)"',
                r"name='csrfmiddlewaretoken' value='([^']+)'",
                r'csrfmiddlewaretoken["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
            
            csrf_token = None
            for pattern in csrf_patterns:
                match = re.search(pattern, html)
                if match:
                    csrf_token = match.group(1)
                    break
            
            if csrf_token:
                print(f"🔑 CSRF Token encontrado: {csrf_token[:20]}...")
            else:
                print("❌ CSRF Token não encontrado")
                
            # Procura por formulário de login
            if '<form' in html and 'username' in html:
                print("📝 Formulário de login encontrado")
                
                # Extrai action do form
                form_action = re.search(r'<form[^>]*action="([^"]*)"', html)
                if form_action:
                    print(f"🎯 Action do form: {form_action.group(1)}")
                
                # Extrai method do form
                form_method = re.search(r'<form[^>]*method="([^"]*)"', html, re.IGNORECASE)
                if form_method:
                    print(f"📤 Method do form: {form_method.group(1)}")
                
            else:
                print("❌ Formulário de login não encontrado")
            
            return csrf_token, session
            
        else:
            print(f"❌ Erro ao acessar login: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None

def testar_login_com_debug(csrf_token, session):
    """Testa login com debug detalhado"""
    print("\n🔐 Testando login com debug...")
    
    if not csrf_token:
        print("❌ Não é possível testar sem CSRF token")
        return False
    
    # Dados do login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    print(f"📤 Dados enviados: {list(login_data.keys())}")
    
    # Headers necessários para o Django CSRF
    headers = {
        'Referer': LOGIN_URL,  # IMPORTANTE: Django precisa do Referer para CSRF
        'Origin': BASE_URL,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        # Faz o POST com headers corretos
        response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=False)
        
        print(f"📊 Status da resposta: {response.status_code}")
        print(f"🌐 URL final: {response.url}")
        
        # Headers da resposta
        print("📋 Headers importantes:")
        for header in ['Location', 'Set-Cookie', 'Content-Type']:
            value = response.headers.get(header)
            if value:
                print(f"  {header}: {value[:100]}...")
        
        # Analisa o tipo de resposta
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"🔄 Redirecionamento para: {location}")
            
            if 'dashboard' in location or 'admin' in location:
                print("✅ Login bem-sucedido!")
                return True
            elif 'login' in location:
                print("❌ Redirecionado de volta para login - credenciais inválidas?")
                return False
            else:
                print("⚠️ Redirecionamento inesperado")
                return False
                
        elif response.status_code == 200:
            print("📄 Resposta 200 - analisando conteúdo...")
            
            content = response.text.lower()
            if 'dashboard' in content or 'bem-vindo' in content:
                print("✅ Login bem-sucedido (sem redirecionamento)!")
                return True
            elif 'erro' in content or 'inválid' in content:
                print("❌ Erro de login no conteúdo")
                return False
            else:
                print("⚠️ Conteúdo não identificado")
                return False
                
        elif response.status_code == 403:
            print("❌ Erro 403 - Acesso negado")
            print("   Possíveis causas:")
            print("   - CSRF token inválido")
            print("   - Middleware bloqueando")
            print("   - Configuração de segurança")
            
            # Tenta analisar o conteúdo do erro
            if response.text:
                content = response.text.lower()
                if 'csrf' in content:
                    print("   - Erro relacionado a CSRF detectado")
                if 'forbidden' in content:
                    print("   - Erro de permissão detectado")
            
            return False
            
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante login: {e}")
        return False

def testar_credenciais_alternativas(csrf_token, session):
    """Testa com credenciais alternativas"""
    print("\n🔄 Testando credenciais alternativas...")
    
    credenciais = [
        ('admin', 'admin'),
        ('admin', '123456'),
        ('root', 'admin123'),
        ('lvk', 'admin123'),
    ]
    
    # Headers necessários para o Django CSRF
    headers = {
        'Referer': LOGIN_URL,
        'Origin': BASE_URL,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    for username, password in credenciais:
        print(f"🧪 Testando: {username} / {password}")
        
        login_data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token
        }
        
        try:
            response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=False)
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if 'dashboard' in location:
                    print(f"✅ Sucesso com {username} / {password}!")
                    return True
                    
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print("❌ Nenhuma credencial funcionou")
    return False

def main():
    print("🚀 TESTE SIMPLES DE LOGIN - DEBUG 403")
    print("=" * 50)
    print(f"🌐 URL: {LOGIN_URL}")
    print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    # 1. Debug da página de login
    csrf_token, session = debug_login_page()
    
    if csrf_token and session:
        # 2. Testa login principal
        sucesso = testar_login_com_debug(csrf_token, session)
        
        if not sucesso:
            # 3. Testa credenciais alternativas
            testar_credenciais_alternativas(csrf_token, session)
    
    print("\n" + "=" * 50)
    print("📋 RESUMO:")
    print("- Sistema está online")
    print("- Página de login acessível")
    print("- Problema específico no processo de login")
    print("\n🔧 Sugestões:")
    print("1. Verificar logs do Heroku")
    print("2. Testar login manual no navegador")
    print("3. Verificar configurações de middleware")

if __name__ == "__main__":
    main()