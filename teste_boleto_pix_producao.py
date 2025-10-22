#!/usr/bin/env python3
"""
Teste de Geração de Boleto com PIX - Produção Heroku
Testa a URL específica: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/67/
"""

import requests
import json
import sys
from datetime import datetime

# Configurações
BASE_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
BOLETO_URL = f"{BASE_URL}/financeiro/boletos/gerar/67/"
LOGIN_URL = f"{BASE_URL}/login/"

# Credenciais (conforme documentação)
USERNAME = "admin"
PASSWORD = "admin123"

def fazer_login(session):
    """Faz login no sistema"""
    print("🔐 Fazendo login no sistema...")
    
    # Primeiro, pega o CSRF token
    response = session.get(LOGIN_URL)
    if response.status_code != 200:
        print(f"❌ Erro ao acessar página de login: {response.status_code}")
        return False
    
    # Extrai CSRF token
    csrf_token = None
    if 'csrfmiddlewaretoken' in response.text:
        import re
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
    
    if not csrf_token:
        print("❌ Não foi possível obter CSRF token")
        return False
    
    # Faz login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200 and 'login' not in response.url:
        print("✅ Login realizado com sucesso!")
        return True
    else:
        print(f"❌ Falha no login. Status: {response.status_code}")
        return False

def testar_geracao_boleto(session):
    """Testa a geração de boleto com PIX"""
    print(f"\n📄 Testando geração de boleto: {BOLETO_URL}")
    
    try:
        # Acessa a página de geração de boleto
        response = session.get(BOLETO_URL)
        
        print(f"Status da resposta: {response.status_code}")
        print(f"URL final: {response.url}")
        
        if response.status_code == 200:
            print("✅ Página de geração de boleto acessada com sucesso!")
            
            # Verifica se tem conteúdo relacionado a boleto/PIX
            content = response.text.lower()
            
            indicadores = {
                'boleto': 'boleto' in content,
                'pix': 'pix' in content,
                'asaas': 'asaas' in content,
                'gerar': 'gerar' in content,
                'qr_code': 'qr' in content or 'qrcode' in content,
                'codigo_barras': 'código' in content or 'barras' in content
            }
            
            print("\n🔍 Análise do conteúdo da página:")
            for indicador, presente in indicadores.items():
                status = "✅" if presente else "❌"
                print(f"  {status} {indicador.replace('_', ' ').title()}: {'Presente' if presente else 'Ausente'}")
            
            # Verifica se é uma página de formulário
            if '<form' in content:
                print("\n📝 Formulário detectado na página")
                
                # Procura por campos de formulário
                import re
                inputs = re.findall(r'<input[^>]*name="([^"]*)"[^>]*>', content)
                selects = re.findall(r'<select[^>]*name="([^"]*)"[^>]*>', content)
                
                if inputs or selects:
                    print("  Campos encontrados:")
                    for inp in inputs:
                        print(f"    - Input: {inp}")
                    for sel in selects:
                        print(f"    - Select: {sel}")
            
            return True
            
        elif response.status_code == 302:
            print(f"🔄 Redirecionamento para: {response.headers.get('Location', 'URL não informada')}")
            return False
            
        elif response.status_code == 403:
            print("❌ Acesso negado (403) - Verifique permissões")
            return False
            
        elif response.status_code == 404:
            print("❌ Página não encontrada (404)")
            return False
            
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def testar_api_asaas():
    """Testa se a API do Asaas está respondendo"""
    print("\n🔗 Testando conectividade com API Asaas...")
    
    try:
        # Testa apenas conectividade (sem API key)
        response = requests.get("https://www.asaas.com/api/v3/", timeout=10)
        
        if response.status_code in [401, 403]:
            print("✅ API Asaas está online (resposta de autenticação esperada)")
            return True
        elif response.status_code == 200:
            print("✅ API Asaas está online")
            return True
        else:
            print(f"⚠️ API Asaas respondeu com status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com API Asaas: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE DE BOLETO COM PIX - PRODUÇÃO HEROKU")
    print("=" * 60)
    print(f"🌐 URL Base: {BASE_URL}")
    print(f"📄 URL Boleto: {BOLETO_URL}")
    print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Testa API Asaas primeiro
    testar_api_asaas()
    
    # Cria sessão para manter cookies
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # Faz login
        if not fazer_login(session):
            print("\n❌ Não foi possível fazer login. Teste abortado.")
            return False
        
        # Testa geração de boleto
        sucesso = testar_geracao_boleto(session)
        
        print("\n" + "=" * 60)
        if sucesso:
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("\n📋 Próximos passos:")
            print("1. Acesse a URL no navegador para testar manualmente")
            print("2. Verifique se o formulário de geração aparece")
            print("3. Teste a geração completa do boleto com PIX")
        else:
            print("❌ TESTE FALHOU!")
            print("\n🔧 Possíveis soluções:")
            print("1. Verifique se o sistema está online")
            print("2. Confirme as credenciais de login")
            print("3. Verifique se a URL está correta")
        
        return sucesso
        
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)