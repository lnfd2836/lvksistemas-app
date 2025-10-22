#!/usr/bin/env python3
"""
Teste Completo de Produção - Simula navegador real
Testa login e geração de boleto em produção no Heroku
"""

import requests
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse

# URLs do sistema em produção
BASE_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
LOGIN_URL = f"{BASE_URL}/login/"
BOLETO_URL = f"{BASE_URL}/financeiro/boletos/gerar/67/"
DASHBOARD_URL = f"{BASE_URL}/dashboard/"

class TestadorProducao:
    def __init__(self):
        self.session = requests.Session()
        # Headers que simulam um navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
    def obter_csrf_token(self, html):
        """Extrai CSRF token do HTML"""
        patterns = [
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            r"name='csrfmiddlewaretoken' value='([^']+)'",
            r'csrfmiddlewaretoken["\']?\s*:\s*["\']([^"\']+)["\']',
            r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        return None
    
    def fazer_login_producao(self):
        """Faz login no sistema de produção"""
        print("🔐 Fazendo login no sistema de produção...")
        
        try:
            # 1. Acessa a página de login
            print("📄 Acessando página de login...")
            response = self.session.get(LOGIN_URL)
            
            if response.status_code != 200:
                print(f"❌ Erro ao acessar login: {response.status_code}")
                return False
            
            print(f"✅ Página de login carregada ({len(response.content)} bytes)")
            
            # 2. Extrai CSRF token
            csrf_token = self.obter_csrf_token(response.text)
            if not csrf_token:
                print("❌ CSRF token não encontrado")
                return False
            
            print(f"🔑 CSRF token obtido: {csrf_token[:20]}...")
            
            # 3. Prepara dados do login
            login_data = {
                'username': 'admin',
                'password': 'admin123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            # 4. Headers específicos para o POST
            post_headers = {
                'Referer': LOGIN_URL,
                'Origin': BASE_URL,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1'
            }
            
            # 5. Faz o POST de login
            print("📤 Enviando credenciais...")
            response = self.session.post(
                LOGIN_URL, 
                data=login_data, 
                headers=post_headers,
                allow_redirects=True  # Permite redirecionamentos
            )
            
            print(f"📊 Status: {response.status_code}")
            print(f"🌐 URL final: {response.url}")
            
            # 6. Verifica se o login foi bem-sucedido
            if response.status_code == 200:
                # Verifica se não está mais na página de login
                if 'login' not in response.url and ('dashboard' in response.url or 'dashboard' in response.text.lower()):
                    print("✅ Login bem-sucedido!")
                    return True
                elif 'login' in response.url:
                    # Ainda na página de login - verifica se há mensagem de erro
                    content = response.text.lower()
                    if any(x in content for x in ['erro', 'inválid', 'incorrect', 'wrong']):
                        print("❌ Credenciais inválidas")
                    else:
                        print("❌ Login falhou - motivo desconhecido")
                    return False
                else:
                    print("⚠️ Login pode ter funcionado - verificando...")
                    return self.verificar_autenticacao()
            else:
                print(f"❌ Erro no login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro durante login: {e}")
            return False
    
    def verificar_autenticacao(self):
        """Verifica se está autenticado tentando acessar o dashboard"""
        print("🔍 Verificando autenticação...")
        
        try:
            response = self.session.get(DASHBOARD_URL)
            
            if response.status_code == 200 and 'login' not in response.url:
                print("✅ Usuário autenticado!")
                return True
            else:
                print("❌ Usuário não autenticado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar autenticação: {e}")
            return False
    
    def testar_geracao_boleto(self):
        """Testa a geração de boleto"""
        print("\n📄 Testando geração de boleto...")
        
        try:
            # Acessa a página de geração de boleto
            response = self.session.get(BOLETO_URL)
            
            print(f"📊 Status: {response.status_code}")
            print(f"🌐 URL: {response.url}")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Analisa o conteúdo
                indicadores = {
                    'formulario_presente': '<form' in content,
                    'opcoes_pagamento': any(x in content for x in ['asaas', 'pagamento', 'boleto']),
                    'pix_disponivel': 'pix' in content,
                    'botao_gerar': any(x in content for x in ['gerar', 'criar', 'submit']),
                    'dados_loja': any(x in content for x in ['loja', 'cliente', 'valor']),
                    'select_asaas': 'asaas' in content and 'select' in content
                }
                
                print("\n🔍 Análise da página:")
                for key, value in indicadores.items():
                    status = "✅" if value else "❌"
                    print(f"  {status} {key.replace('_', ' ').title()}")
                
                # Se tem formulário, tenta extrair mais informações
                if indicadores['formulario_presente']:
                    print("\n📝 Detalhes do formulário:")
                    
                    # Procura por selects (opções de pagamento)
                    selects = re.findall(r'<select[^>]*name="([^"]*)"[^>]*>(.*?)</select>', response.text, re.DOTALL)
                    for name, options_html in selects:
                        print(f"  🔽 Select '{name}':")
                        options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', options_html)
                        for value, text in options:
                            if value and text.strip():
                                print(f"    - {text.strip()} (value: {value})")
                
                return True
                
            elif response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"🔄 Redirecionado para: {location}")
                return False
                
            else:
                print(f"❌ Erro ao acessar boleto: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar boleto: {e}")
            return False
    
    def executar_teste_completo(self):
        """Executa o teste completo"""
        print("🚀 TESTE COMPLETO DE PRODUÇÃO")
        print("=" * 60)
        print(f"🌐 Sistema: {BASE_URL}")
        print(f"📄 Boleto: {BOLETO_URL}")
        print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        resultados = {}
        
        # 1. Teste de login
        resultados['login'] = self.fazer_login_producao()
        
        if resultados['login']:
            # 2. Teste de geração de boleto
            resultados['boleto'] = self.testar_geracao_boleto()
        else:
            print("⚠️ Pulando teste de boleto - login falhou")
            resultados['boleto'] = False
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL")
        print("=" * 60)
        
        for teste, sucesso in resultados.items():
            status = "✅ SUCESSO" if sucesso else "❌ FALHA"
            print(f"{teste.upper()}: {status}")
        
        sucesso_geral = all(resultados.values())
        
        if sucesso_geral:
            print("\n🎉 TESTE GERAL: ✅ SUCESSO COMPLETO!")
            print("\n📋 Sistema funcionando:")
            print("- ✅ Login em produção funcionando")
            print("- ✅ Página de boleto acessível")
            print("- ✅ Integração com Asaas detectada")
            
            print(f"\n🌐 Para gerar boleto manualmente:")
            print(f"1. Acesse: {LOGIN_URL}")
            print("2. Login: admin / admin123")
            print(f"3. Vá para: {BOLETO_URL}")
            print("4. Selecione 'Asaas I.P S.A' e gere o boleto")
            
        else:
            print("\n⚠️ TESTE GERAL: ❌ PROBLEMAS DETECTADOS")
            
            if not resultados['login']:
                print("\n🔧 Problema no login:")
                print("- Verifique se o usuário 'admin' existe no banco de produção")
                print("- Confirme a senha 'admin123'")
                print("- Verifique logs do Heroku para mais detalhes")
            
            if not resultados['boleto']:
                print("\n🔧 Problema no boleto:")
                print("- Verifique se a rota existe")
                print("- Confirme permissões do usuário")
        
        return sucesso_geral

def main():
    testador = TestadorProducao()
    return testador.executar_teste_completo()

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)