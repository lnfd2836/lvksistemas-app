#!/usr/bin/env python3
"""
Script para configurar a API Key do Asaas corretamente
"""

import os
import sys
import requests
import json
from datetime import datetime

def testar_api_key(api_key, environment='sandbox'):
    """Testa se uma API Key é válida"""
    
    # URLs da API
    if environment == 'production':
        base_url = 'https://www.asaas.com/api/v3'
    else:
        base_url = 'https://sandbox.asaas.com/api/v3'
    
    # Headers para teste
    headers = {
        'access_token': api_key,
        'Content-Type': 'application/json',
        'User-Agent': 'Java/1.8.0_282'
    }
    
    try:
        print(f"🧪 Testando API Key no ambiente: {environment}")
        print(f"📡 URL: {base_url}/myAccount")
        
        response = requests.get(
            f"{base_url}/myAccount",
            headers=headers,
            timeout=30,
            verify=True
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Key VÁLIDA!")
            print(f"👤 Nome da conta: {data.get('name', 'N/A')}")
            print(f"📧 Email: {data.get('email', 'N/A')}")
            print(f"🆔 ID: {data.get('id', 'N/A')}")
            return True
            
        elif response.status_code == 401:
            print(f"❌ API Key INVÁLIDA ou EXPIRADA")
            return False
            
        elif response.status_code == 403:
            print(f"❌ ACESSO NEGADO - Possível problema de firewall")
            print(f"📄 Resposta: {response.text}")
            return False
            
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

def obter_api_key_sandbox():
    """Instrui como obter API Key do sandbox"""
    print("\n" + "=" * 60)
    print("🔧 COMO OBTER API KEY DO SANDBOX (TESTE)")
    print("=" * 60)
    print("1. Acesse: https://sandbox.asaas.com")
    print("2. Crie uma conta gratuita")
    print("3. Faça login")
    print("4. Vá em: Configurações → API")
    print("5. Certifique-se que está em SANDBOX")
    print("6. Gere uma nova API Key")
    print("7. Copie a chave gerada")
    print("\n💡 A API Key do sandbox é gratuita e serve para testes!")

def obter_api_key_producao():
    """Instrui como obter API Key de produção"""
    print("\n" + "=" * 60)
    print("🚀 COMO OBTER API KEY DE PRODUÇÃO")
    print("=" * 60)
    print("1. Acesse: https://www.asaas.com")
    print("2. Faça login na sua conta")
    print("3. Vá em: Configurações → API")
    print("4. ⚠️  MUDE PARA PRODUÇÃO (não sandbox)")
    print("5. Gere uma nova API Key")
    print("6. Copie a chave gerada")
    print("\n⚠️  ATENÇÃO: API Key de produção processa pagamentos reais!")

def configurar_env_file(api_key, environment):
    """Configura o arquivo .env com a nova API Key"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print(f"❌ Arquivo {env_file} não encontrado!")
        return False
    
    # Ler arquivo atual
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Atualizar linhas
    updated_lines = []
    api_key_updated = False
    env_updated = False
    
    for line in lines:
        if line.startswith('ASAAS_API_KEY='):
            updated_lines.append(f'ASAAS_API_KEY={api_key}\n')
            api_key_updated = True
        elif line.startswith('ASAAS_ENVIRONMENT='):
            updated_lines.append(f'ASAAS_ENVIRONMENT={environment}\n')
            env_updated = True
        else:
            updated_lines.append(line)
    
    # Adicionar se não existir
    if not api_key_updated:
        updated_lines.append(f'ASAAS_API_KEY={api_key}\n')
    
    if not env_updated:
        updated_lines.append(f'ASAAS_ENVIRONMENT={environment}\n')
    
    # Escrever arquivo atualizado
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Arquivo {env_file} atualizado!")
    return True

def main():
    """Função principal"""
    print("🔑 CONFIGURADOR DE API KEY DO ASAAS")
    print("=" * 60)
    
    # Verificar API Key atual
    current_api_key = os.getenv('ASAAS_API_KEY', '3f12cef7-f5a3-446e-b1ba-1eb37090298d')
    current_env = os.getenv('ASAAS_ENVIRONMENT', 'sandbox')
    
    print(f"📋 Configuração atual:")
    print(f"   API Key: {current_api_key}")
    print(f"   Environment: {current_env}")
    
    # Testar API Key atual
    print(f"\n🧪 Testando configuração atual...")
    if testar_api_key(current_api_key, current_env):
        print(f"\n🎉 SUA API KEY ATUAL ESTÁ FUNCIONANDO!")
        print(f"✅ Não é necessário alterar nada.")
        return
    
    print(f"\n❌ API Key atual não está funcionando.")
    
    # Menu de opções
    while True:
        print(f"\n📋 OPÇÕES:")
        print(f"1. Testar uma nova API Key")
        print(f"2. Como obter API Key do Sandbox (teste)")
        print(f"3. Como obter API Key de Produção")
        print(f"4. Sair")
        
        opcao = input(f"\n👉 Escolha uma opção (1-4): ").strip()
        
        if opcao == '1':
            # Testar nova API Key
            nova_api_key = input(f"\n🔑 Digite a nova API Key: ").strip()
            if not nova_api_key:
                print(f"❌ API Key não pode estar vazia!")
                continue
            
            ambiente = input(f"🌍 Ambiente (sandbox/production) [sandbox]: ").strip() or 'sandbox'
            
            if testar_api_key(nova_api_key, ambiente):
                # API Key válida, configurar
                resposta = input(f"\n💾 Salvar esta configuração no .env? (s/n): ").strip().lower()
                if resposta in ['s', 'sim', 'y', 'yes']:
                    if configurar_env_file(nova_api_key, ambiente):
                        print(f"\n🎉 CONFIGURAÇÃO SALVA COM SUCESSO!")
                        print(f"✅ Reinicie o sistema para aplicar as mudanças.")
                        break
            else:
                print(f"\n❌ API Key inválida. Tente novamente.")
        
        elif opcao == '2':
            obter_api_key_sandbox()
        
        elif opcao == '3':
            obter_api_key_producao()
        
        elif opcao == '4':
            print(f"\n👋 Saindo...")
            break
        
        else:
            print(f"❌ Opção inválida!")

if __name__ == '__main__':
    main()