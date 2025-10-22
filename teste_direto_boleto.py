#!/usr/bin/env python3
"""
Teste Direto da URL de Boleto - Sem Login
Testa diretamente: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/67/
"""

import requests
import json
from datetime import datetime

# URL específica para teste
BOLETO_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/67/"
BASE_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"

def testar_url_direta():
    """Testa acesso direto à URL do boleto"""
    print(f"🔗 Testando acesso direto: {BOLETO_URL}")
    
    try:
        # Headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(BOLETO_URL, headers=headers, timeout=30, allow_redirects=True)
        
        print(f"📊 Status: {response.status_code}")
        print(f"🌐 URL Final: {response.url}")
        print(f"📏 Tamanho da resposta: {len(response.content)} bytes")
        
        # Analisa o tipo de resposta
        content_type = response.headers.get('content-type', '').lower()
        print(f"📄 Content-Type: {content_type}")
        
        if response.status_code == 200:
            print("✅ Acesso bem-sucedido!")
            
            # Analisa o conteúdo
            if 'text/html' in content_type:
                content = response.text.lower()
                
                # Verifica indicadores importantes
                indicadores = {
                    'login_required': any(x in content for x in ['login', 'entrar', 'usuário', 'senha']),
                    'boleto_page': any(x in content for x in ['boleto', 'cobrança', 'gerar']),
                    'pix_support': any(x in content for x in ['pix', 'qr code', 'qrcode']),
                    'asaas_integration': any(x in content for x in ['asaas', 'api']),
                    'form_present': '<form' in content,
                    'error_page': any(x in content for x in ['erro', 'error', '404', '500'])
                }
                
                print("\n🔍 Análise do conteúdo:")
                for key, value in indicadores.items():
                    status = "✅" if value else "❌"
                    print(f"  {status} {key.replace('_', ' ').title()}: {'Sim' if value else 'Não'}")
                
                # Se parece ser página de login
                if indicadores['login_required']:
                    print("\n🔐 Página requer autenticação")
                    return testar_sistema_base()
                
                # Se parece ser página de boleto
                elif indicadores['boleto_page']:
                    print("\n📄 Página de boleto detectada!")
                    return True
                
                else:
                    print("\n⚠️ Tipo de página não identificado")
                    
            elif 'application/json' in content_type:
                try:
                    data = response.json()
                    print(f"📋 Resposta JSON: {json.dumps(data, indent=2)}")
                except:
                    print("📋 Resposta JSON inválida")
            
            return True
            
        elif response.status_code == 302:
            location = response.headers.get('Location', 'Não informado')
            print(f"🔄 Redirecionamento para: {location}")
            
            if 'login' in location.lower():
                print("🔐 Redirecionado para login - autenticação necessária")
                return testar_sistema_base()
            
            return False
            
        elif response.status_code == 403:
            print("❌ Acesso negado (403)")
            print("   Possíveis causas:")
            print("   - Autenticação necessária")
            print("   - Permissões insuficientes")
            print("   - Bloqueio de IP/User-Agent")
            return False
            
        elif response.status_code == 404:
            print("❌ Página não encontrada (404)")
            print("   A URL pode estar incorreta ou a rota não existe")
            return False
            
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - O servidor demorou para responder")
        return False
        
    except requests.exceptions.ConnectionError:
        print("🔌 Erro de conexão - Verifique sua internet ou se o servidor está online")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de requisição: {e}")
        return False

def testar_sistema_base():
    """Testa se o sistema base está funcionando"""
    print(f"\n🏠 Testando sistema base: {BASE_URL}")
    
    try:
        response = requests.get(BASE_URL, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sistema base está online!")
            
            content = response.text.lower()
            if 'login' in content:
                print("🔐 Sistema requer autenticação")
            
            return True
        else:
            print(f"❌ Sistema base com problema: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar sistema base: {e}")
        return False

def testar_endpoints_relacionados():
    """Testa outros endpoints relacionados"""
    print("\n🔍 Testando endpoints relacionados...")
    
    endpoints = [
        "/financeiro/",
        "/financeiro/boletos/",
        "/financeiro/controles/",
        "/login/",
        "/admin/"
    ]
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=10)
            status = "✅" if response.status_code in [200, 302] else "❌"
            print(f"  {status} {endpoint}: {response.status_code}")
        except:
            print(f"  ❌ {endpoint}: Erro de conexão")

def main():
    """Função principal"""
    print("🚀 TESTE DIRETO - BOLETO COM PIX")
    print("=" * 60)
    print(f"🎯 URL Alvo: {BOLETO_URL}")
    print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Teste principal
    sucesso = testar_url_direta()
    
    # Testes adicionais
    testar_endpoints_relacionados()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ TESTE CONCLUÍDO!")
        print("\n📋 Resultado:")
        print("- A URL foi acessada com sucesso")
        print("- Verifique os detalhes acima para mais informações")
    else:
        print("❌ TESTE COM PROBLEMAS!")
        print("\n🔧 Próximos passos:")
        print("1. Verifique se você tem acesso ao sistema")
        print("2. Tente fazer login manualmente no navegador")
        print("3. Confirme se a URL está correta")
    
    print(f"\n🌐 Para teste manual, acesse: {BOLETO_URL}")
    
    return sucesso

if __name__ == "__main__":
    main()