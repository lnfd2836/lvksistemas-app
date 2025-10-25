#!/usr/bin/env python
"""
Script específico para testar e diagnosticar Connection Refused
"""

import os
import sys
import django
import time
import requests

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.asaas_sync_service import get_sync_service
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_connection_refused():
    """Testa especificamente para connection refused"""
    print("🔍 TESTE ESPECÍFICO PARA CONNECTION REFUSED")
    print("=" * 50)
    
    asaas_service = AsaasService()
    
    # Teste 1: Conexão rápida
    print("\n1. 🚀 Teste de conexão rápida (3s timeout)...")
    try:
        result = asaas_service.test_connection_quick(timeout=3)
        
        if result['connection_refused']:
            print("❌ CONNECTION REFUSED DETECTADO!")
            print(f"   Erro: {result['error']}")
            print("   🕐 Recomendação: Aguarde 5-10 minutos")
            return False
        elif result['accessible']:
            print(f"✅ API acessível (Status: {result['status_code']})")
        else:
            print(f"⚠️ API não acessível: {result.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Erro no teste rápido: {str(e)}")
        return False
    
    # Teste 2: Múltiplas tentativas com delays
    print("\n2. 🔄 Teste com múltiplas tentativas...")
    for i in range(3):
        try:
            print(f"   Tentativa {i+1}/3...")
            
            response = requests.get(
                f"{asaas_service.base_url}/myAccount",
                headers=asaas_service.headers,
                timeout=5
            )
            
            print(f"   ✅ Sucesso! Status: {response.status_code}")
            break
            
        except requests.exceptions.ConnectionError as e:
            if "Connection refused" in str(e):
                print(f"   ❌ Connection refused na tentativa {i+1}")
                if i < 2:  # Não aguardar na última tentativa
                    print(f"   ⏳ Aguardando {(i+1)*2} segundos...")
                    time.sleep((i+1)*2)
            else:
                print(f"   ❌ Outro erro de conexão: {str(e)}")
                break
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            break
    
    # Teste 3: Teste do serviço de sincronização
    print("\n3. 🔧 Teste do serviço de sincronização...")
    try:
        sync_service = get_sync_service()
        result = sync_service.simple_sync_check()
        
        print(f"   API acessível: {result['api_accessible']}")
        print(f"   Configuração válida: {result['config_valid']}")
        print(f"   Cobranças testadas: {result['sample_charges_checked']}")
        
        if result['errors']:
            connection_refused_errors = [e for e in result['errors'] if 'Connection refused' in e]
            if connection_refused_errors:
                print("   ❌ CONNECTION REFUSED detectado no serviço!")
                for error in connection_refused_errors:
                    print(f"      - {error}")
            else:
                print("   ⚠️ Outros erros encontrados:")
                for error in result['errors'][:3]:
                    print(f"      - {error}")
        else:
            print("   ✅ Nenhum erro encontrado!")
            
    except Exception as e:
        print(f"   ❌ Erro no teste do serviço: {str(e)}")
    
    return True

def diagnosticar_ambiente():
    """Diagnostica o ambiente para connection refused"""
    print("\n🔍 DIAGNÓSTICO DO AMBIENTE")
    print("=" * 30)
    
    # Verificar configurações
    asaas_service = AsaasService()
    
    print(f"Base URL: {asaas_service.base_url}")
    print(f"Environment: {asaas_service.environment}")
    print(f"API Key configurada: {'Sim' if asaas_service.api_key else 'Não'}")
    
    if asaas_service.api_key:
        if asaas_service.api_key.startswith('$aact_'):
            print("Tipo de chave: Produção")
        else:
            print("Tipo de chave: Sandbox/Teste")
    
    # Testar DNS
    print("\n🌐 Teste de DNS...")
    try:
        import socket
        ip = socket.gethostbyname('api.asaas.com')
        print(f"✅ DNS OK - api.asaas.com resolve para {ip}")
    except Exception as e:
        print(f"❌ Erro de DNS: {str(e)}")
    
    # Testar conectividade básica
    print("\n🔌 Teste de conectividade básica...")
    try:
        response = requests.get('https://api.asaas.com', timeout=10)
        print(f"✅ Conectividade básica OK (Status: {response.status_code})")
    except requests.exceptions.ConnectionError as e:
        if "Connection refused" in str(e):
            print("❌ CONNECTION REFUSED na conectividade básica!")
        else:
            print(f"❌ Erro de conectividade: {str(e)}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def sugerir_solucoes():
    """Sugere soluções para connection refused"""
    print("\n💡 SOLUÇÕES PARA CONNECTION REFUSED")
    print("=" * 35)
    
    print("1. ⏰ AGUARDAR")
    print("   - Connection refused é geralmente temporário")
    print("   - Aguarde 5-10 minutos antes de tentar novamente")
    print("   - API pode estar em manutenção ou sobregregada")
    
    print("\n2. 🕐 HORÁRIOS")
    print("   - Tente em horários de menor movimento")
    print("   - Evite horários comerciais (9h-18h)")
    print("   - Madrugada e fins de semana têm menos tráfego")
    
    print("\n3. 🔧 CONFIGURAÇÕES")
    print("   - Verifique se a chave da API está correta")
    print("   - Confirme se está usando o ambiente correto")
    print("   - Teste com timeouts menores primeiro")
    
    print("\n4. 🚨 SE PERSISTIR")
    print("   - Pode ser problema na API Asaas")
    print("   - Verifique status da API no site do Asaas")
    print("   - Entre em contato com suporte se necessário")

def main():
    """Função principal"""
    print("🚫 DIAGNÓSTICO DE CONNECTION REFUSED - ASAAS")
    print("=" * 50)
    
    # Executar testes
    try:
        # Diagnóstico do ambiente
        diagnosticar_ambiente()
        
        # Teste específico
        if testar_connection_refused():
            print("\n✅ TESTES CONCLUÍDOS")
        else:
            print("\n❌ CONNECTION REFUSED DETECTADO")
            
        # Sugestões
        sugerir_solucoes()
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {str(e)}")
    
    print("\n" + "=" * 50)
    print("FIM DO DIAGNÓSTICO")

if __name__ == '__main__':
    main()