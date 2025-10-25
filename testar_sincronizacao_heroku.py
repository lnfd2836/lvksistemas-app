#!/usr/bin/env python
"""
Script para testar a sincronização otimizada para Heroku
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.asaas_sync_service import get_sync_service
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import CobrancaAsaas
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_conectividade_basica():
    """Testa conectividade básica com a API Asaas"""
    print("=== TESTE DE CONECTIVIDADE BÁSICA ===")
    
    try:
        asaas_service = AsaasService()
        
        # Teste 1: Validar configuração
        print("1. Testando configuração da API...")
        if asaas_service.validar_configuracao():
            print("✅ Configuração válida")
        else:
            print("❌ Configuração inválida")
            return False
        
        # Teste 2: Verificar se há cobranças para testar
        print("2. Verificando cobranças existentes...")
        cobrancas = CobrancaAsaas.objects.all()[:5]
        print(f"   Encontradas {len(cobrancas)} cobranças para teste")
        
        # Teste 3: Testar consulta de uma cobrança
        if cobrancas:
            print("3. Testando consulta de cobrança...")
            cobranca = cobrancas[0]
            try:
                dados = asaas_service.consultar_cobranca(cobranca.asaas_id, timeout=10)
                if dados:
                    print(f"✅ Cobrança {cobranca.asaas_id} consultada com sucesso")
                    print(f"   Status: {dados.get('status', 'N/A')}")
                else:
                    print(f"❌ Falha ao consultar cobrança {cobranca.asaas_id}")
            except Exception as e:
                print(f"❌ Erro ao consultar cobrança: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de conectividade: {str(e)}")
        return False

def testar_sincronizacao_simples():
    """Testa sincronização simplificada"""
    print("\n=== TESTE DE SINCRONIZAÇÃO SIMPLES ===")
    
    try:
        sync_service = get_sync_service()
        
        # Teste 1: Verificação simples
        print("1. Executando verificação simples...")
        result = sync_service.simple_sync_check()
        
        print(f"   API acessível: {result['api_accessible']}")
        print(f"   Configuração válida: {result['config_valid']}")
        print(f"   Cobranças testadas: {result['sample_charges_checked']}")
        
        if result['errors']:
            print("   Erros encontrados:")
            for error in result['errors'][:3]:
                print(f"   - {error}")
        
        # Teste 2: Sincronização completa (se conectividade OK)
        if result['api_accessible']:
            print("2. Executando sincronização completa...")
            sync_result = sync_service.force_sync_now()
            
            print(f"   Processadas: {sync_result['total_processed']}")
            print(f"   Atualizadas: {sync_result['updates_made']}")
            print(f"   Novas: {sync_result['new_charges']}")
            print(f"   Erros: {len(sync_result['errors'])}")
            
            if sync_result['errors']:
                print("   Primeiros erros:")
                for error in sync_result['errors'][:3]:
                    print(f"   - {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de sincronização: {str(e)}")
        return False

def testar_status_servico():
    """Testa status do serviço"""
    print("\n=== TESTE DE STATUS DO SERVIÇO ===")
    
    try:
        sync_service = get_sync_service()
        
        # Obter status
        status = sync_service.get_sync_status()
        
        print(f"Sincronização ativa: {status['is_running']}")
        print(f"Intervalo: {status['sync_interval']} segundos")
        print(f"Última sincronização: {status['last_sync']}")
        print(f"Total sincronizadas: {status['stats']['total_synced']}")
        print(f"Atualizações encontradas: {status['stats']['updates_found']}")
        print(f"Erros: {status['stats']['errors']}")
        
        if status['stats']['last_error']:
            print(f"Último erro: {status['stats']['last_error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de status: {str(e)}")
        return False

def main():
    """Função principal"""
    print("TESTE DE SINCRONIZAÇÃO ASAAS - VERSÃO HEROKU")
    print("=" * 50)
    
    # Executar testes
    testes = [
        ("Conectividade Básica", testar_conectividade_basica),
        ("Status do Serviço", testar_status_servico),
        ("Sincronização Simples", testar_sincronizacao_simples),
    ]
    
    resultados = []
    
    for nome, teste in testes:
        print(f"\n🔄 Executando: {nome}")
        try:
            resultado = teste()
            resultados.append((nome, resultado))
            if resultado:
                print(f"✅ {nome}: PASSOU")
            else:
                print(f"❌ {nome}: FALHOU")
        except Exception as e:
            print(f"❌ {nome}: ERRO - {str(e)}")
            resultados.append((nome, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    passou = 0
    total = len(resultados)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome}: {status}")
        if resultado:
            passou += 1
    
    print(f"\nResultado: {passou}/{total} testes passaram")
    
    if passou == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    elif passou > 0:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
    else:
        print("🚨 Todos os testes falharam. Verifique a configuração.")

if __name__ == '__main__':
    main()