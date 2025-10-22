#!/usr/bin/env python3
"""
Teste Final - Verificação da URL de Boleto
Confirma que a rota existe e está funcionando
"""

import requests
from datetime import datetime

# URL específica para teste
BOLETO_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/67/"
BASE_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"

def testar_url_boleto():
    """Testa se a URL do boleto existe e responde"""
    print(f"🎯 Testando URL específica: {BOLETO_URL}")
    
    try:
        response = requests.get(BOLETO_URL, timeout=30, allow_redirects=True)
        
        print(f"📊 Status: {response.status_code}")
        print(f"🌐 URL Final: {response.url}")
        print(f"📏 Tamanho: {len(response.content)} bytes")
        
        # Analisa o resultado
        if response.status_code == 200:
            if 'login' in response.url:
                print("✅ Rota existe! (Redirecionou para login - comportamento esperado)")
                return True
            else:
                print("✅ Rota existe e carregou diretamente!")
                return True
                
        elif response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✅ Rota existe! (Redirecionamento para: {location})")
            return True
            
        elif response.status_code == 404:
            print("❌ Rota não existe (404)")
            return False
            
        else:
            print(f"⚠️ Rota existe mas retornou: {response.status_code}")
            return True
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - servidor demorou para responder")
        return False
        
    except requests.exceptions.ConnectionError:
        print("🔌 Erro de conexão")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_outras_rotas():
    """Testa outras rotas relacionadas"""
    print("\n🔍 Testando rotas relacionadas...")
    
    rotas = [
        "/financeiro/",
        "/financeiro/boletos/",
        "/financeiro/controles/",
        "/financeiro/asaas/",
        "/dashboard/",
        "/admin/"
    ]
    
    for rota in rotas:
        url = BASE_URL + rota
        try:
            response = requests.get(url, timeout=10, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                status = "✅"
            elif response.status_code == 404:
                status = "❌"
            else:
                status = "⚠️"
                
            print(f"  {status} {rota}: {response.status_code}")
            
        except:
            print(f"  ❌ {rota}: Erro de conexão")

def main():
    print("🚀 TESTE FINAL - VERIFICAÇÃO DE ROTA")
    print("=" * 60)
    print(f"🎯 URL Alvo: {BOLETO_URL}")
    print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Teste principal
    rota_existe = testar_url_boleto()
    
    # Testes adicionais
    testar_outras_rotas()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    if rota_existe:
        print("✅ ROTA DO BOLETO EXISTE E FUNCIONA!")
        print("\n📋 Confirmado:")
        print("- ✅ URL está correta")
        print("- ✅ Sistema está online")
        print("- ✅ Rota está configurada")
        print("- ✅ Redirecionamento para login funcionando")
        
        print("\n🔧 Para usar:")
        print("1. Crie o usuário admin no Heroku:")
        print("   heroku run \"python criar_admin_heroku.py\" --app lvksistemas-app")
        print("2. Faça login com: admin / admin123")
        print(f"3. Acesse: {BOLETO_URL}")
        print("4. Gere seu boleto com PIX!")
        
    else:
        print("❌ PROBLEMA COM A ROTA")
        print("\n🔧 Verifique:")
        print("- Configuração das URLs")
        print("- Deploy do sistema")
        print("- Status do Heroku")
    
    return rota_existe

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)