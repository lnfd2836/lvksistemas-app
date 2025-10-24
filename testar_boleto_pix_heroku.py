#!/usr/bin/env python
"""
Script para testar emissão de boleto com PIX na API Asaas no Heroku
Testa o fluxo completo de geração de cobrança em produção
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
from controle_financeiro.models import ControleFinanceiro, CobrancaAsaas
from controle_financeiro.asaas_service import AsaasService

def testar_boleto_pix_producao():
    """
    Testa emissão de boleto com PIX na API Asaas em produção
    """
    print("=" * 80)
    print("🧪 TESTE: EMISSÃO DE BOLETO COM PIX - HEROKU PRODUÇÃO")
    print("=" * 80)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Ambiente: Heroku Produção")
    
    # 1. Verificar configuração do Asaas
    print("\n1. 🔍 VERIFICANDO CONFIGURAÇÃO ASAAS...")
    print(f"   API Key: {settings.ASAAS_API_KEY[:20]}..." if settings.ASAAS_API_KEY else "   ❌ API Key não configurada")
    print(f"   Environment: {settings.ASAAS_ENVIRONMENT}")
    print(f"   Site URL: {settings.SITE_URL}")
    
    if not settings.ASAAS_API_KEY:
        print("❌ ERRO: API Key do Asaas não configurada!")
        return False
    
    # 2. Inicializar serviço Asaas
    print("\n2. 🔧 INICIALIZANDO SERVIÇO ASAAS...")
    try:
        asaas_service = AsaasService()
        
        if asaas_service.validar_configuracao():
            print("   ✅ Serviço Asaas inicializado com sucesso!")
            print(f"   Base URL: {asaas_service.base_url}")
        else:
            print("   ❌ Falha na validação da configuração Asaas!")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao inicializar serviço: {str(e)}")
        return False
    
    # 3. Buscar controle financeiro para teste
    print("\n3. 🏪 BUSCANDO CONTROLE FINANCEIRO...")
    try:
        controle = ControleFinanceiro.objects.filter(
            status='ativo'
        ).select_related('loja', 'plano').first()
        
        if not controle:
            print("   ❌ Nenhum controle financeiro ativo encontrado!")
            return False
        
        print(f"   ✅ Controle encontrado:")
        print(f"     Loja: {controle.loja.nome}")
        print(f"     CNPJ: {controle.loja.cnpj}")
        print(f"     Plano: {controle.plano.nome}")
        print(f"     Valor: R$ {controle.valor_mensal}")
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar controle: {str(e)}")
        return False
    
    # 4. Gerar cobrança de teste
    print("\n4. 💰 GERANDO COBRANÇA COM BOLETO E PIX...")
    try:
        descricao = f"TESTE HEROKU - Boleto+PIX - {controle.loja.nome} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        print(f"   Descrição: {descricao}")
        print(f"   Valor: R$ {controle.valor_mensal}")
        print(f"   Vencimento: 30 dias")
        
        resultado = asaas_service.gerar_cobranca_com_pix(
            controle,
            dias_vencimento=30,
            descricao=descricao
        )
        
        if not resultado.get('success'):
            print(f"   ❌ Erro ao gerar cobrança: {resultado.get('error')}")
            return False
        
        cobranca_data = resultado['cobranca']
        pix_data = resultado.get('pix', {})
        
        print(f"   ✅ Cobrança gerada com sucesso!")
        print(f"     ID: {cobranca_data['id']}")
        print(f"     Valor: R$ {cobranca_data['value']}")
        print(f"     Vencimento: {cobranca_data['dueDate']}")
        print(f"     Status: {cobranca_data['status']}")
        print(f"     Customer: {cobranca_data['customer']}")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar cobrança: {str(e)}")
        return False
    
    # 5. Verificar dados do boleto
    print("\n5. 📄 VERIFICANDO DADOS DO BOLETO...")
    try:
        if cobranca_data.get('invoiceUrl'):
            print(f"   ✅ URL da Fatura: {cobranca_data['invoiceUrl']}")
        else:
            print(f"   ⚠️ URL da fatura não disponível ainda")
        
        if cobranca_data.get('bankSlipUrl'):
            print(f"   ✅ PDF do Boleto: {cobranca_data['bankSlipUrl']}")
        else:
            print(f"   ⚠️ PDF do boleto ainda sendo gerado")
        
        if cobranca_data.get('invoiceNumber'):
            print(f"   ✅ Número da Fatura: {cobranca_data['invoiceNumber']}")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao verificar dados do boleto: {str(e)}")
    
    # 6. Verificar dados do PIX
    print("\n6. 💳 VERIFICANDO DADOS DO PIX...")
    try:
        if pix_data:
            print(f"   ✅ PIX gerado com sucesso!")
            
            if pix_data.get('qrCode'):
                print(f"   ✅ QR Code disponível (tamanho: {len(pix_data['qrCode'])} chars)")
            
            if pix_data.get('payload'):
                print(f"   ✅ PIX Copia e Cola disponível")
                print(f"     Payload: {pix_data['payload'][:50]}...")
            
            if pix_data.get('expirationDate'):
                print(f"   ✅ Data de expiração: {pix_data['expirationDate']}")
        else:
            print(f"   ⚠️ Dados do PIX não disponíveis")
            
    except Exception as e:
        print(f"   ⚠️ Erro ao verificar PIX: {str(e)}")
    
    # 7. Salvar cobrança no banco de dados
    print("\n7. 💾 SALVANDO COBRANÇA NO BANCO...")
    try:
        cobranca = CobrancaAsaas.objects.create(
            asaas_id=cobranca_data['id'],
            controle_financeiro=controle,
            customer_id=cobranca_data['customer'],
            valor=Decimal(str(cobranca_data['value'])),
            data_vencimento=timezone.datetime.fromisoformat(cobranca_data['dueDate']).replace(tzinfo=timezone.get_current_timezone()),
            descricao=cobranca_data['description'],
            status=cobranca_data['status'],
            invoice_url=cobranca_data.get('invoiceUrl', ''),
            bank_slip_url=cobranca_data.get('bankSlipUrl', ''),
            invoice_number=cobranca_data.get('invoiceNumber', ''),
            external_reference=cobranca_data.get('externalReference', ''),
            api_response=cobranca_data
        )
        
        # Salvar dados do PIX
        if pix_data:
            cobranca.pix_qr_code = pix_data.get('qrCode', '')
            cobranca.pix_copy_paste = pix_data.get('payload', '')
            if pix_data.get('expirationDate'):
                cobranca.pix_expires_date = timezone.datetime.fromisoformat(
                    pix_data['expirationDate'].replace('Z', '+00:00')
                ).replace(tzinfo=timezone.get_current_timezone())
            cobranca.save()
        
        print(f"   ✅ Cobrança salva no banco com ID: {cobranca.id}")
        
    except Exception as e:
        print(f"   ❌ Erro ao salvar no banco: {str(e)}")
        return False
    
    # 8. Aguardar e verificar PDF do boleto
    print("\n8. ⏳ AGUARDANDO GERAÇÃO DO PDF...")
    try:
        import time
        
        for tentativa in range(3):
            print(f"   Tentativa {tentativa + 1}/3...")
            time.sleep(5)  # Aguardar 5 segundos
            
            # Consultar cobrança atualizada
            cobranca_atualizada = asaas_service.consultar_cobranca(cobranca_data['id'])
            
            if cobranca_atualizada and cobranca_atualizada.get('bankSlipUrl'):
                print(f"   ✅ PDF do boleto disponível!")
                print(f"     URL: {cobranca_atualizada['bankSlipUrl']}")
                
                # Atualizar no banco
                cobranca.bank_slip_url = cobranca_atualizada['bankSlipUrl']
                cobranca.save()
                break
            else:
                print(f"   ⏳ PDF ainda não disponível...")
        else:
            print(f"   ⚠️ PDF não foi gerado no tempo esperado")
            
    except Exception as e:
        print(f"   ⚠️ Erro ao verificar PDF: {str(e)}")
    
    # 9. Testar webhook (simulação)
    print("\n9. 🔗 TESTANDO WEBHOOK...")
    try:
        webhook_url = f"{settings.SITE_URL}/webhook/asaas/"
        print(f"   URL do Webhook: {webhook_url}")
        
        # Dados de teste do webhook
        webhook_test_data = {
            'event': 'PAYMENT_CREATED',
            'payment': {
                'id': cobranca_data['id'],
                'customer': cobranca_data['customer'],
                'value': cobranca_data['value'],
                'status': 'PENDING',
                'description': cobranca_data['description']
            }
        }
        
        # Testar webhook
        response = requests.post(
            webhook_url,
            json=webhook_test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"   ✅ Webhook respondeu corretamente!")
            print(f"     Status: {response.status_code}")
            print(f"     Resposta: {response.text}")
        else:
            print(f"   ⚠️ Webhook retornou status {response.status_code}")
            print(f"     Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ⚠️ Erro ao testar webhook: {str(e)}")
    
    # 10. Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DO TESTE")
    print("=" * 80)
    
    print(f"✅ Cobrança ID: {cobranca_data['id']}")
    print(f"✅ Valor: R$ {cobranca_data['value']}")
    print(f"✅ Vencimento: {cobranca_data['dueDate']}")
    print(f"✅ Status: {cobranca_data['status']}")
    
    if cobranca_data.get('bankSlipUrl'):
        print(f"✅ PDF Boleto: Disponível")
    else:
        print(f"⚠️ PDF Boleto: Sendo gerado")
    
    if pix_data and pix_data.get('payload'):
        print(f"✅ PIX: Disponível")
    else:
        print(f"⚠️ PIX: Não disponível")
    
    print(f"\n🔗 LINKS IMPORTANTES:")
    print(f"   Sistema: {settings.SITE_URL}")
    print(f"   Financeiro: {settings.SITE_URL}/financeiro/")
    print(f"   Cobrança: {settings.SITE_URL}/financeiro/asaas/cobrancas/{cobranca.id}/")
    
    if cobranca_data.get('bankSlipUrl'):
        print(f"   PDF Boleto: {cobranca_data['bankSlipUrl']}")
    
    return True

def main():
    """Função principal"""
    try:
        sucesso = testar_boleto_pix_producao()
        
        if sucesso:
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print("   Boleto com PIX gerado e funcionando no Heroku!")
        else:
            print("\n❌ TESTE FALHOU!")
            print("   Verifique os erros acima e tente novamente.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()