#!/usr/bin/env python3
"""
Verificar Status Atual no Heroku
"""

import subprocess
import sys
import json

def executar_comando(comando):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def verificar_config_heroku():
    """Verifica configuração atual no Heroku"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO ATUAL NO HEROKU")
    print("=" * 60)
    
    sucesso, stdout, stderr = executar_comando("heroku config --app lvksistemas-app")
    
    if sucesso:
        print("📋 Configurações atuais:")
        print(stdout)
        
        # Verifica se as variáveis estão configuradas
        config_ok = True
        
        if "ASAAS_API_KEY" not in stdout:
            print("❌ ASAAS_API_KEY não encontrada")
            config_ok = False
        else:
            print("✅ ASAAS_API_KEY encontrada")
        
        if "ASAAS_ENVIRONMENT" not in stdout:
            print("❌ ASAAS_ENVIRONMENT não encontrada")
            config_ok = False
        else:
            print("✅ ASAAS_ENVIRONMENT encontrada")
        
        return config_ok
    else:
        print(f"❌ Erro ao verificar config: {stderr}")
        return False

def configurar_variaveis():
    """Configura as variáveis no Heroku"""
    print("\n🔧 CONFIGURANDO VARIÁVEIS NO HEROKU")
    print("=" * 60)
    
    api_key = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl"
    
    # Configura API Key
    print("🔑 Configurando ASAAS_API_KEY...")
    comando_api = f'heroku config:set ASAAS_API_KEY="{api_key}" --app lvksistemas-app'
    sucesso, stdout, stderr = executar_comando(comando_api)
    
    if sucesso:
        print("✅ ASAAS_API_KEY configurada")
    else:
        print(f"❌ Erro ao configurar API Key: {stderr}")
        return False
    
    # Configura Environment
    print("🌐 Configurando ASAAS_ENVIRONMENT...")
    comando_env = 'heroku config:set ASAAS_ENVIRONMENT="production" --app lvksistemas-app'
    sucesso, stdout, stderr = executar_comando(comando_env)
    
    if sucesso:
        print("✅ ASAAS_ENVIRONMENT configurada")
    else:
        print(f"❌ Erro ao configurar environment: {stderr}")
        return False
    
    return True

def testar_no_heroku():
    """Testa a configuração no Heroku"""
    print("\n🧪 TESTANDO CONFIGURAÇÃO NO HEROKU")
    print("=" * 60)
    
    comando_teste = '''heroku run "python -c \\"
import os
print('🔑 ASAAS_API_KEY:', 'Configurada' if os.environ.get('ASAAS_API_KEY') else 'NÃO CONFIGURADA')
print('🌐 ASAAS_ENVIRONMENT:', os.environ.get('ASAAS_ENVIRONMENT', 'NÃO CONFIGURADO'))
try:
    from controle_financeiro.asaas_service import AsaasService
    asaas = AsaasService()
    print('📡 Service URL:', asaas.base_url)
    print('🔧 Service API Key:', 'Configurada' if asaas.api_key else 'NÃO CONFIGURADA')
    if asaas.validar_configuracao():
        print('✅ VALIDAÇÃO: OK')
    else:
        print('❌ VALIDAÇÃO: ERRO')
except Exception as e:
    print('❌ ERRO:', str(e))
\\"" --app lvksistemas-app'''
    
    print("Executando teste...")
    sucesso, stdout, stderr = executar_comando(comando_teste)
    
    if sucesso:
        print("📊 Resultado do teste:")
        print(stdout)
        return "✅ VALIDAÇÃO: OK" in stdout
    else:
        print(f"❌ Erro no teste: {stderr}")
        return False

def fazer_deploy():
    """Faz deploy das alterações"""
    print("\n🚀 FAZENDO DEPLOY DAS ALTERAÇÕES")
    print("=" * 60)
    
    # Add arquivos
    print("📁 Adicionando arquivos...")
    sucesso, stdout, stderr = executar_comando("git add .")
    if not sucesso:
        print(f"❌ Erro no git add: {stderr}")
        return False
    
    # Commit
    print("💾 Fazendo commit...")
    sucesso, stdout, stderr = executar_comando('git commit -m "Fix: Configura API Asaas de produção e corrige settings"')
    if not sucesso and "nothing to commit" not in stderr:
        print(f"❌ Erro no commit: {stderr}")
        return False
    
    # Push para Heroku
    print("🚀 Fazendo push para Heroku...")
    sucesso, stdout, stderr = executar_comando("git push heroku main")
    if sucesso:
        print("✅ Deploy realizado com sucesso!")
        return True
    else:
        print(f"❌ Erro no deploy: {stderr}")
        return False

def main():
    """Função principal"""
    print("🚀 CONFIGURAÇÃO COMPLETA DO HEROKU")
    print("=" * 70)
    
    # 1. Verifica configuração atual
    config_ok = verificar_config_heroku()
    
    # 2. Configura variáveis se necessário
    if not config_ok:
        if not configurar_variaveis():
            print("\n❌ Falha na configuração das variáveis")
            return False
    
    # 3. Faz deploy
    if not fazer_deploy():
        print("\n❌ Falha no deploy")
        return False
    
    # 4. Testa configuração
    print("\n⏳ Aguardando deploy... (30 segundos)")
    import time
    time.sleep(30)
    
    if testar_no_heroku():
        print("\n🎉 SUCESSO COMPLETO!")
        print("\n📋 Agora teste:")
        print("1. Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/")
        print("2. Login: admin / admin123")
        print("3. Gere boleto: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/15/")
        print("4. Deve funcionar sem erro 400!")
        return True
    else:
        print("\n❌ AINDA COM PROBLEMAS")
        print("Verifique os logs: heroku logs --tail --app lvksistemas-app")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)