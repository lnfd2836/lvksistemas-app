#!/usr/bin/env python
"""
Script para testar diferentes endpoints de nota fiscal do Asaas
"""

import os
import sys
import django
import requests

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.asaas_service import AsaasService

def testar_endpoints_nota_fiscal():
    """
    Testa diferentes endpoints para encontrar o correto para notas fiscais
    """
    print("=" * 80)
    print("TESTE: ENDPOINTS DE NOTA FISCAL DO ASAAS")
    print("=" * 80)
    
    asaas_service = AsaasService()
    
    # Lista de endpoints possíveis para testar
    endpoints_para_testar = [
        '/invoices',
        '/fiscalInvoices', 
        '/nfse',
        '/serviceInvoices',
        '/municipalInvoices',
        '/fiscalDocuments',
        '/myAccount/fiscalInfo',
        '/myAccount/municipalServices'
    ]
    
    print(f"\nTestando endpoints com base URL: {asaas_service.base_url}")
    print(f"Environment: {asaas_service.environment}")
    
    for endpoint in endpoints_para_testar:
        print(f"\n--- Testando: {endpoint} ---")
        
        try:
            # Testar GET primeiro
            response = requests.get(
                f"{asaas_service.base_url}{endpoint}",
                headers=asaas_service.headers,
                timeout=30
            )
            
            print(f"GET {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Endpoint disponível! Dados: {str(data)[:200]}...")
                except:
                    print(f"✅ Endpoint disponível! Resposta não-JSON")
                    
            elif response.status_code == 401:
                print(f"❌ Não autorizado - verifique API Key")
                
            elif response.status_code == 403:
                print(f"⚠️ Acesso negado - pode precisar de permissões especiais")
                
            elif response.status_code == 404:
                print(f"❌ Endpoint não encontrado")
                
            else:
                print(f"⚠️ Status: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
    
    # Testar endpoint específico para criar nota fiscal
    print(f"\n--- Testando POST em endpoints de criação ---")
    
    # Buscar uma cobrança paga para teste
    from controle_financeiro.models import CobrancaAsaas
    cobranca_paga = CobrancaAsaas.objects.filter(status='RECEIVED').first()
    
    if cobranca_paga:
        print(f"Usando cobrança paga para teste: {cobranca_paga.asaas_id}")
        
        # Dados de teste para nota fiscal
        test_data = {
            'payment': cobranca_paga.asaas_id,
            'serviceDescription': 'Teste de emissao de nota fiscal',
            'municipalServiceCode': '14.02'
        }
        
        endpoints_post = ['/invoices', '/fiscalInvoices', '/nfse']
        
        for endpoint in endpoints_post:
            try:
                response = requests.post(
                    f"{asaas_service.base_url}{endpoint}",
                    headers=asaas_service.headers,
                    json=test_data,
                    timeout=30
                )
                
                print(f"POST {endpoint}: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"✅ SUCESSO! Nota fiscal pode ser criada neste endpoint")
                    try:
                        result = response.json()
                        print(f"Resposta: {result}")
                    except:
                        print(f"Resposta não-JSON: {response.text[:200]}")
                        
                elif response.status_code == 400:
                    print(f"⚠️ Dados inválidos - endpoint existe mas dados incorretos")
                    try:
                        error = response.json()
                        print(f"Erro: {error}")
                    except:
                        print(f"Erro: {response.text[:200]}")
                        
                elif response.status_code == 404:
                    print(f"❌ Endpoint não existe")
                    
                else:
                    print(f"Status: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ Erro: {str(e)}")
    else:
        print("Nenhuma cobrança paga encontrada para teste")
    
    # Verificar documentação específica
    print(f"\n--- Verificando configuração da conta ---")
    
    try:
        # Verificar dados da conta
        account_response = requests.get(
            f"{asaas_service.base_url}/myAccount",
            headers=asaas_service.headers,
            timeout=30
        )
        
        if account_response.status_code == 200:
            account_data = account_response.json()
            print(f"✅ Conta: {account_data.get('name')}")
            print(f"   CNPJ: {account_data.get('cpfCnpj')}")
            print(f"   Email: {account_data.get('email')}")
            
            # Verificar se tem módulo fiscal habilitado
            if 'fiscalInfo' in str(account_data):
                print(f"✅ Módulo fiscal parece estar disponível")
            else:
                print(f"⚠️ Módulo fiscal pode não estar habilitado")
                
    except Exception as e:
        print(f"❌ Erro ao verificar conta: {str(e)}")

if __name__ == '__main__':
    testar_endpoints_nota_fiscal()