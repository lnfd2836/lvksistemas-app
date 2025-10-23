#!/usr/bin/env python
"""
Script para sincronizar cobranças do Asaas com o sistema local
"""

import os
import sys
import django
import requests
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.conf import settings
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService
from lojas.models import Loja

def sincronizar_cobrancas():
    """Sincroniza cobranças do Asaas com o sistema local"""
    
    try:
        print("🔄 Iniciando sincronização com Asaas...")
        
        # Inicializar serviço Asaas
        asaas_service = AsaasService()
        
        # Verificar configuração
        if not asaas_service.validar_configuracao():
            print("❌ API Asaas não configurada")
            return
        
        print("✅ Conexão com Asaas estabelecida")
        
        # Buscar cobranças no Asaas
        url = f"{asaas_service.base_url}/payments"
        headers = asaas_service.headers
        
        # Buscar cobranças recentes (últimos 30 dias)
        params = {
            'limit': 100,
            'offset': 0
        }
        
        print(f"📡 Buscando cobranças no Asaas...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"❌ Erro ao buscar cobranças: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return
        
        data = response.json()
        cobrancas_asaas = data.get('data', [])
        
        print(f"📊 Encontradas {len(cobrancas_asaas)} cobranças no Asaas")
        
        # Processar cada cobrança
        cobrancas_sincronizadas = 0
        cobrancas_ignoradas = 0
        
        for cobranca_data in cobrancas_asaas:
            asaas_id = cobranca_data.get('id')
            customer_id = cobranca_data.get('customer')
            valor = float(cobranca_data.get('value', 0))
            status = cobranca_data.get('status')
            descricao = cobranca_data.get('description', '')
            
            print(f"\n🔍 Processando cobrança {asaas_id}")
            print(f"   Cliente: {customer_id}")
            print(f"   Valor: R$ {valor}")
            print(f"   Status: {status}")
            print(f"   Descrição: {descricao}")
            
            # Verificar se já existe no sistema
            cobranca_existente = CobrancaAsaas.objects.filter(asaas_id=asaas_id).first()
            
            if cobranca_existente:
                print(f"   ✅ Cobrança já existe no sistema")
                cobrancas_ignoradas += 1
                continue
            
            # Tentar encontrar controle financeiro relacionado
            # Buscar por descrição ou outros critérios
            controle = None
            
            # Tentar encontrar pela descrição
            if 'Loja Exemplo' in descricao:
                nome_loja = descricao.split(' - ')[1] if ' - ' in descricao else descricao
                loja = Loja.objects.filter(nome__icontains=nome_loja.replace('Primeira mensalidade - ', '')).first()
                if loja:
                    controle = ControleFinanceiro.objects.filter(loja=loja).first()
            
            # Se não encontrou, usar o primeiro controle disponível (para teste)
            if not controle:
                controle = ControleFinanceiro.objects.first()
                print(f"   ⚠️  Usando controle padrão: {controle.loja.nome if controle else 'Nenhum'}")
            
            if controle:
                # Criar cobrança no sistema
                try:
                    nova_cobranca = CobrancaAsaas.objects.create(
                        asaas_id=asaas_id,
                        controle_financeiro=controle,
                        customer_id=customer_id,
                        valor=valor,
                        data_vencimento=datetime.now(),
                        descricao=descricao,
                        status=status,
                        api_response=cobranca_data
                    )
                    
                    print(f"   ✅ Cobrança criada no sistema: {nova_cobranca.id}")
                    cobrancas_sincronizadas += 1
                    
                except Exception as e:
                    print(f"   ❌ Erro ao criar cobrança: {str(e)}")
            else:
                print(f"   ❌ Controle financeiro não encontrado")
        
        print(f"\n📊 Sincronização concluída:")
        print(f"   ✅ Sincronizadas: {cobrancas_sincronizadas}")
        print(f"   ⏭️  Ignoradas: {cobrancas_ignoradas}")
        print(f"   📊 Total no Asaas: {len(cobrancas_asaas)}")
        
        # Mostrar cobranças no sistema
        total_sistema = CobrancaAsaas.objects.count()
        print(f"   💾 Total no sistema: {total_sistema}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na sincronização: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        sucesso = sincronizar_cobrancas()
        if sucesso:
            print(f"\n🎉 Sincronização concluída com sucesso!")
        else:
            print(f"\n❌ Falha na sincronização")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        sys.exit(1)