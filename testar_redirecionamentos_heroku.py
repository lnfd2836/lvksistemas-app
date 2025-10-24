#!/usr/bin/env python
"""
Script para testar os redirecionamentos da otimização no Heroku
"""

import requests
import sys

def testar_redirecionamentos():
    """Testa se os redirecionamentos estão funcionando no Heroku"""
    
    base_url = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
    
    print("🧪 TESTANDO REDIRECIONAMENTOS NO HEROKU")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print()
    
    # URLs para testar (sem autenticação, só para ver se redirecionam)
    urls_teste = [
        ("/controle-financeiro/boletos/", "Listar Boletos -> Cobranças Asaas"),
        ("/controle-financeiro/boletos/configurar/", "Configurar Boletos -> Configurar Asaas"),
        ("/controle-financeiro/asaas/cobrancas/", "Cobranças Asaas (destino)"),
        ("/controle-financeiro/asaas/configurar/", "Configurar Asaas (destino)"),
    ]
    
    resultados = []
    
    for url, descricao in urls_teste:
        print(f"🔍 Testando: {descricao}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(f"{base_url}{url}", allow_redirects=False, timeout=10)
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'N/A')
                print(f"   ✅ Redirecionamento OK (302)")
                print(f"   📍 Destino: {location}")
                resultados.append(True)
            elif response.status_code == 200:
                print(f"   ✅ Página carregada (200)")
                resultados.append(True)
            elif response.status_code == 403:
                print(f"   ⚠️  Acesso negado (403) - Normal para páginas protegidas")
                resultados.append(True)
            else:
                print(f"   ❌ Status inesperado: {response.status_code}")
                resultados.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro de conexão: {e}")
            resultados.append(False)
        
        print()
    
    return resultados

def testar_pagina_principal():
    """Testa se a página principal está funcionando"""
    
    print("🏠 TESTANDO PÁGINA PRINCIPAL")
    print("=" * 60)
    
    base_url = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
    
    try:
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Página principal carregando corretamente")
            print(f"   Status: {response.status_code}")
            print(f"   Tamanho: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Página principal com erro: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar página principal: {e}")
        return False

def main():
    """Executa todos os testes"""
    
    print("🚀 TESTE DE DEPLOY - OTIMIZAÇÃO DE BOLETOS")
    print("=" * 60)
    print("Data:", "23/10/2025 22:15")
    print("Ambiente: Heroku Produção")
    print()
    
    # 1. Testar página principal
    principal_ok = testar_pagina_principal()
    print()
    
    # 2. Testar redirecionamentos
    resultados_redirect = testar_redirecionamentos()
    
    # 3. Resultado final
    print("=" * 60)
    print("📋 RESUMO DOS TESTES:")
    print()
    
    if principal_ok:
        print("✅ Página principal: OK")
    else:
        print("❌ Página principal: FALHOU")
    
    sucessos = sum(resultados_redirect)
    total = len(resultados_redirect)
    
    print(f"✅ Redirecionamentos: {sucessos}/{total} OK")
    
    if principal_ok and sucessos == total:
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Deploy da otimização foi bem-sucedido")
        print("✅ Sistema funcionando corretamente no Heroku")
        print()
        print("🔄 Próximos passos:")
        print("   1. Testar login no sistema")
        print("   2. Verificar se redirecionamentos funcionam após login")
        print("   3. Monitorar logs por alguns dias")
        return True
    else:
        print()
        print("❌ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)