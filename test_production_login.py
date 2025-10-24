#!/usr/bin/env python
"""
Script para testar login no servidor de produção
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_production_login():
    """Testa login no servidor de produção"""
    
    # URL de produção
    base_url = "https://www.lvksistemas.com.br"
    login_url = f"{base_url}/login/"
    
    print("🔍 TESTANDO LOGIN NO SERVIDOR DE PRODUÇÃO")
    print(f"URL: {login_url}")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Acessar página de login para obter CSRF token
        print("1. Acessando página de login...")
        response = session.get(login_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página de login: {response.status_code}")
            return False
        
        print(f"✅ Página de login acessada: {response.status_code}")
        
        # 2. Extrair CSRF token
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = None
        
        # Procurar token CSRF no HTML
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"✅ CSRF token encontrado: {csrf_token[:20]}...")
        else:
            print("⚠️ CSRF token não encontrado no HTML")
        
        # 3. Testar diferentes credenciais
        credenciais_teste = [
            ('admin', 'admin123'),
            ('teste', '123'),
            ('lvkadmin', 'lvk2024'),
            ('superadmin', 'super123')
        ]
        
        for username, password in credenciais_teste:
            print(f"\n2. Testando login: {username}/{password}")
            
            # Dados do POST
            login_data = {
                'username': username,
                'password': password,
            }
            
            if csrf_token:
                login_data['csrfmiddlewaretoken'] = csrf_token
            
            # Headers
            headers = {
                'Referer': login_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Fazer POST
            response = session.post(login_url, data=login_data, headers=headers, allow_redirects=False, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 302:
                # Redirecionamento = sucesso
                redirect_url = response.headers.get('Location', '')
                print(f"✅ LOGIN FUNCIONANDO! Redirecionado para: {redirect_url}")
                
                # Seguir redirecionamento para confirmar
                if redirect_url:
                    final_response = session.get(f"{base_url}{redirect_url}" if redirect_url.startswith('/') else redirect_url, timeout=10)
                    print(f"   Página final: {final_response.status_code}")
                
                return True
                
            elif response.status_code == 200:
                # Mesma página = erro de login
                if 'incorretos' in response.text or 'incorreta' in response.text:
                    print(f"❌ Credenciais incorretas")
                else:
                    print(f"⚠️ Resposta inesperada (200)")
                    
            else:
                print(f"❌ Erro inesperado: {response.status_code}")
            
            # Reset da sessão para próximo teste
            session = requests.Session()
            response = session.get(login_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
        
        print(f"\n❌ Nenhuma credencial funcionou no servidor de produção")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout na conexão com o servidor")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão com o servidor")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False


def check_server_status():
    """Verifica se o servidor está respondendo"""
    
    urls_teste = [
        "https://www.lvksistemas.com.br/",
        "https://www.lvksistemas.com.br/login/",
        "https://www.lvksistemas.com.br/admin/"
    ]
    
    print("\n🌐 VERIFICANDO STATUS DO SERVIDOR")
    print("=" * 60)
    
    for url in urls_teste:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Erro: {str(e)}")


if __name__ == "__main__":
    print("🔧 TESTE DE LOGIN NO SERVIDOR DE PRODUÇÃO")
    print("=" * 60)
    
    # Verificar status do servidor
    check_server_status()
    
    # Testar login
    success = test_production_login()
    
    if success:
        print("\n🎉 SUCESSO! Login funcionando no servidor de produção")
    else:
        print("\n❌ FALHA! Login não está funcionando no servidor de produção")
        print("\n💡 POSSÍVEIS CAUSAS:")
        print("1. Banco de dados diferente entre local e produção")
        print("2. Configurações de ambiente diferentes")
        print("3. Middleware ou autenticação customizada")
        print("4. Cache ou sessões não sincronizadas")
        
        print("\n🔧 SOLUÇÕES RECOMENDADAS:")
        print("1. Verificar se o banco de produção tem os usuários")
        print("2. Resetar senhas diretamente no servidor de produção")
        print("3. Verificar logs do servidor de produção")
        print("4. Limpar cache e sessões")