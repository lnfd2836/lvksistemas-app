#!/usr/bin/env python3
"""
Verificar e Corrigir Configuração no Heroku
"""

import subprocess
import sys

def executar_comando(comando):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def verificar_heroku_cli():
    """Verifica se Heroku CLI está instalado"""
    print("🔧 Verificando Heroku CLI...")
    sucesso, stdout, stderr = executar_comando("heroku --version")
    
    if sucesso:
        print(f"✅ Heroku CLI instalado: {stdout.strip()}")
        return True
    else:
        print("❌ Heroku CLI não encontrado")
        print("📋 Instale com: npm install -g heroku")
        return False

def verificar_config_atual():
    """Verifica configuração atual no Heroku"""
    print("\n🔍 Verificando configuração atual...")
    sucesso, stdout, stderr = executar_comando("heroku config --app lvksistemas-app")
    
    if sucesso:
        print("✅ Configurações atuais:")
        print(stdout)
        
        # Verifica se ASAAS_API_KEY está configurada
        if "ASAAS_API_KEY" in stdout:
            print("✅ ASAAS_API_KEY encontrada")
            return True
        else:
            print("❌ ASAAS_API_KEY não encontrada")
            return False
    else:
        print(f"❌ Erro ao verificar config: {stderr}")
        return False

def configurar_api_key():
    """Configura a API Key no Heroku"""
    api_key = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl"
    
    print("\n🔧 Configurando API Key...")
    
    # Comando para configurar API Key
    comando_api = f'heroku config:set ASAAS_API_KEY="{api_key}" --app lvksistemas-app'
    sucesso, stdout, stderr = executar_comando(comando_api)
    
    if sucesso:
        print("✅ API Key configurada")
    else:
        print(f"❌ Erro ao configurar API Key: {stderr}")
        return False
    
    # Comando para configurar ambiente
    comando_env = 'heroku config:set ASAAS_ENVIRONMENT="production" --app lvksistemas-app'
    sucesso, stdout, stderr = executar_comando(comando_env)
    
    if sucesso:
        print("✅ Ambiente configurado como produção")
        return True
    else:
        print(f"❌ Erro ao configurar ambiente: {stderr}")
        return False

def testar_no_heroku():
    """Testa a configuração no Heroku"""
    print("\n🧪 Testando configuração no Heroku...")
    
    comando_teste = '''heroku run "python -c \\"
import os
from controle_financeiro.asaas_service import AsaasService
print('🔑 API Key:', os.environ.get('ASAAS_API_KEY', 'NÃO CONFIGURADA')[:30] + '...')
print('🌐 Environment:', os.environ.get('ASAAS_ENVIRONMENT', 'NÃO CONFIGURADO'))
asaas = AsaasService()
print('📡 Base URL:', asaas.base_url)
if asaas.validar_configuracao():
    print('✅ API funcionando!')
else:
    print('❌ API com problemas')
\\"" --app lvksistemas-app'''
    
    sucesso, stdout, stderr = executar_comando(comando_teste)
    
    if sucesso:
        print("✅ Teste executado:")
        print(stdout)
        return "✅ API funcionando!" in stdout
    else:
        print(f"❌ Erro no teste: {stderr}")
        return False

def main():
    print("🚀 VERIFICAR E CORRIGIR CONFIGURAÇÃO HEROKU")
    print("=" * 60)
    
    # 1. Verifica Heroku CLI
    if not verificar_heroku_cli():
        print("\n❌ Instale o Heroku CLI primeiro")
        return False
    
    # 2. Verifica configuração atual
    config_ok = verificar_config_atual()
    
    # 3. Configura se necessário
    if not config_ok:
        print("\n🔧 Configurando API Key...")
        if not configurar_api_key():
            print("\n❌ Falha na configuração")
            return False
    
    # 4. Testa configuração
    if testar_no_heroku():
        print("\n✅ CONFIGURAÇÃO OK!")
        print("\n📋 Agora teste:")
        print("1. Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/")
        print("2. Login: admin / admin123")
        print("3. Gere um boleto - deve funcionar!")
        return True
    else:
        print("\n❌ CONFIGURAÇÃO COM PROBLEMAS")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)