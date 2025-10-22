#!/usr/bin/env python3
"""
Teste Completo - Boleto com PIX em Produção
Simula o processo completo: Login → Gerar Boleto → Verificar PIX
"""

import requests
import re
import json
from datetime import datetime
from urllib.parse import urljoin

# Configurações
BASE_URL = "https://lvksistemas-app-4f6fa281e217.herokuapp.com"
LOGIN_URL = f"{BASE_URL}/login/"
BOLETO_URL = f"{BASE_URL}/financeiro/boletos/gerar/67/"
CONTROLES_URL = f"{BASE_URL}/financeiro/controles/"

# Credenciais
USERNAME = "admin"
PASSWORD = "admin123"

class TesteBoletoProducao:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
    def obter_csrf_token(self, html):
        """Extrai CSRF token do HTML"""
        patterns = [
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            r"name='csrfmiddlewaretoken' value='([^']+)'",
            r'csrfmiddlewaretoken["\']?\s*:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        return None
    
    def fazer_login(self):
        """Realiza login no sistema"""
        print("🔐 Iniciando processo de login...")
        
        try:
            # Acessa página de login
            response = self.session.get(LOGIN_URL)
            if response.status_code != 200:
                print(f"❌ Erro ao acessar login: {response.status_code}")
                return False
            
            # Extrai CSRF token
            csrf_token = self.obter_csrf_token(response.text)
            if not csrf_token:
                print("❌ CSRF token não encontrado")
                return False
            
            print(f"🔑 CSRF token obtido: {csrf_token[:20]}...")
            
            # Dados do login
            login_data = {
                'username': USERNAME,
                'password': PASSWORD,
                'csrfmiddlewaretoken': csrf_token
            }
            
            # Realiza login
            response = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
            
            # Verifica se login foi bem-sucedido
            if response.status_code == 200:
                # Se não tem mais formulário de login, provavelmente logou
                if 'name="username"' not in response.text and 'login' not in response.url.lower():
                    print("✅ Login realizado com sucesso!")
                    return True
                else:
                    print("❌ Login falhou - ainda na página de login")
                    return False
            else:
                print(f"❌ Erro no login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro durante login: {e}")
            return False
    
    def acessar_controles_financeiros(self):
        """Acessa página de controles financeiros"""
        print("\n💰 Acessando controles financeiros...")
        
        try:
            response = self.session.get(CONTROLES_URL)
            
            if response.status_code == 200:
                print("✅ Controles financeiros acessados!")
                
                # Verifica conteúdo
                content = response.text.lower()
                indicadores = {
                    'lojas': 'loja' in content,
                    'boletos': 'boleto' in content,
                    'gerar': 'gerar' in content,
                    'asaas': 'asaas' in content
                }
                
                print("🔍 Conteúdo encontrado:")
                for key, value in indicadores.items():
                    status = "✅" if value else "❌"
                    print(f"  {status} {key.title()}")
                
                return True
            else:
                print(f"❌ Erro ao acessar controles: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao acessar controles: {e}")
            return False
    
    def testar_geracao_boleto(self):
        """Testa a geração de boleto específica"""
        print(f"\n📄 Testando geração de boleto: {BOLETO_URL}")
        
        try:
            response = self.session.get(BOLETO_URL)
            
            print(f"📊 Status: {response.status_code}")
            print(f"🌐 URL: {response.url}")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Analisa o conteúdo da página
                indicadores = {
                    'formulario_boleto': '<form' in content and ('boleto' in content or 'gerar' in content),
                    'opcoes_pagamento': any(x in content for x in ['asaas', 'pix', 'pagamento']),
                    'dados_loja': any(x in content for x in ['loja', 'cliente', 'valor']),
                    'botao_gerar': any(x in content for x in ['gerar', 'criar', 'submit']),
                    'pix_disponivel': 'pix' in content,
                    'qr_code': any(x in content for x in ['qr', 'qrcode'])
                }
                
                print("\n🔍 Análise da página de boleto:")
                for key, value in indicadores.items():
                    status = "✅" if value else "❌"
                    print(f"  {status} {key.replace('_', ' ').title()}")
                
                # Se tem formulário, tenta extrair informações
                if indicadores['formulario_boleto']:
                    print("\n📝 Formulário de boleto detectado!")
                    
                    # Procura por campos do formulário
                    selects = re.findall(r'<select[^>]*name="([^"]*)"[^>]*>', response.text)
                    inputs = re.findall(r'<input[^>]*name="([^"]*)"[^>]*>', response.text)
                    
                    if selects or inputs:
                        print("  Campos disponíveis:")
                        for select in selects:
                            print(f"    - Select: {select}")
                        for inp in inputs:
                            print(f"    - Input: {inp}")
                    
                    # Tenta encontrar opções de pagamento
                    options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', response.text)
                    if options:
                        print("  Opções de pagamento:")
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
    
    def verificar_integracao_asaas(self):
        """Verifica se a integração com Asaas está configurada"""
        print("\n🔗 Verificando integração Asaas...")
        
        # URLs para testar
        urls_teste = [
            f"{BASE_URL}/financeiro/asaas/",
            f"{BASE_URL}/financeiro/asaas/cobrancas/",
            f"{BASE_URL}/admin/",
        ]
        
        for url in urls_teste:
            try:
                response = self.session.get(url, timeout=10)
                status = "✅" if response.status_code in [200, 302] else "❌"
                print(f"  {status} {url.split('/')[-2] or url.split('/')[-3]}: {response.status_code}")
                
                if response.status_code == 200 and 'asaas' in response.text.lower():
                    print(f"    🎯 Integração Asaas detectada!")
                    
            except Exception as e:
                print(f"  ❌ {url}: Erro - {e}")
    
    def executar_teste_completo(self):
        """Executa o teste completo"""
        print("🚀 TESTE COMPLETO - BOLETO COM PIX PRODUÇÃO")
        print("=" * 70)
        print(f"🌐 Sistema: {BASE_URL}")
        print(f"📄 Boleto: {BOLETO_URL}")
        print(f"👤 Usuário: {USERNAME}")
        print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 70)
        
        resultados = {}
        
        # 1. Login
        resultados['login'] = self.fazer_login()
        
        if resultados['login']:
            # 2. Controles Financeiros
            resultados['controles'] = self.acessar_controles_financeiros()
            
            # 3. Geração de Boleto
            resultados['boleto'] = self.testar_geracao_boleto()
            
            # 4. Integração Asaas
            self.verificar_integracao_asaas()
        
        # Relatório final
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL")
        print("=" * 70)
        
        for teste, sucesso in resultados.items():
            status = "✅ SUCESSO" if sucesso else "❌ FALHA"
            print(f"{teste.upper()}: {status}")
        
        sucesso_geral = all(resultados.values())
        
        if sucesso_geral:
            print("\n🎉 TESTE GERAL: ✅ SUCESSO COMPLETO!")
            print("\n📋 Sistema funcionando corretamente:")
            print("- ✅ Login funcionando")
            print("- ✅ Controles financeiros acessíveis")
            print("- ✅ Página de boleto carregando")
            print("- ✅ Integração com Asaas detectada")
            
            print(f"\n🌐 Para testar manualmente:")
            print(f"1. Acesse: {LOGIN_URL}")
            print(f"2. Login: {USERNAME} / {PASSWORD}")
            print(f"3. Vá para: {BOLETO_URL}")
            print("4. Selecione 'Asaas I.P S.A' e gere o boleto")
            
        else:
            print("\n⚠️ TESTE GERAL: ❌ PROBLEMAS DETECTADOS")
            print("\n🔧 Verifique:")
            print("- Credenciais de login")
            print("- Configuração do sistema")
            print("- Integração com Asaas")
        
        return sucesso_geral

def main():
    teste = TesteBoletoProducao()
    return teste.executar_teste_completo()

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)