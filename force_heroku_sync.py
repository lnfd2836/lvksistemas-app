#!/usr/bin/env python3
"""
Script para forçar sincronização no Heroku e diagnosticar problemas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro
from controle_financeiro.asaas_sync_service import get_sync_service
from controle_financeiro.asaas_service import AsaasService
from lojas.models import Loja
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def diagnose_heroku_environment():
    """Diagnostica o ambiente Heroku"""
    
    print("🔍 DIAGNÓSTICO DO AMBIENTE HEROKU")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    env_vars = [
        'ASAAS_API_KEY',
        'ASAAS_ENVIRONMENT',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'REDIS_URL',
        'DATABASE_URL'
    ]
    
    print("📋 Variáveis de Ambiente:")
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'PASSWORD' in var or 'KEY' in var:
                print(f"  ✅ {var}: ***configurado***")
            else:
                print(f"  ✅ {var}: {value[:50]}...")
        else:
            print(f"  ❌ {var}: NÃO CONFIGURADO")
    
    # Verificar configuração do Asaas
    print("\n🔧 Configuração do Asaas:")
    try:
        asaas_service = AsaasService()
        if asaas_service.validar_configuracao():
            print("  ✅ API do Asaas configurada corretamente")
        else:
            print("  ❌ Problema na configuração da API do Asaas")
    except Exception as e:
        print(f"  ❌ Erro na validação do Asaas: {str(e)}")
    
    # Verificar banco de dados
    print("\n💾 Banco de Dados:")
    try:
        lojas_count = Loja.objects.count()
        controles_count = ControleFinanceiro.objects.count()
        cobrancas_count = CobrancaAsaas.objects.count()
        
        print(f"  📊 Lojas: {lojas_count}")
        print(f"  📊 Controles Financeiros: {controles_count}")
        print(f"  📊 Cobranças: {cobrancas_count}")
        
    except Exception as e:
        print(f"  ❌ Erro ao acessar banco: {str(e)}")


def force_sync_with_asaas():
    """Força sincronização completa com Asaas"""
    
    print("\n🔄 FORÇANDO SINCRONIZAÇÃO COM ASAAS")
    print("=" * 50)
    
    try:
        # Obter serviço de sincronização
        sync_service = get_sync_service()
        
        print("📡 Iniciando sincronização forçada...")
        
        # Executar sincronização
        result = sync_service.force_sync_now()
        
        print(f"📊 Resultado da Sincronização:")
        print(f"  • Total processado: {result.get('total_processed', 0)}")
        print(f"  • Atualizações feitas: {result.get('updates_made', 0)}")
        print(f"  • Novas cobranças: {result.get('new_charges', 0)}")
        print(f"  • Erros: {len(result.get('errors', []))}")
        
        if result.get('errors'):
            print(f"\n❌ Erros encontrados:")
            for error in result['errors']:
                print(f"  • {error}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro na sincronização: {str(e)}")
        return None


def check_asaas_api_directly():
    """Verifica API do Asaas diretamente"""
    
    print("\n🌐 VERIFICAÇÃO DIRETA DA API ASAAS")
    print("=" * 50)
    
    try:
        import requests
        from datetime import timedelta
        
        asaas_service = AsaasService()
        
        # Buscar cobranças dos últimos 30 dias
        data_inicio = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"📡 Consultando cobranças desde {data_inicio}...")
        
        response = requests.get(
            f"{asaas_service.base_url}/payments",
            headers=asaas_service.headers,
            params={
                'dateCreated[ge]': data_inicio,
                'limit': 100
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            payments = data.get('data', [])
            
            print(f"✅ API respondeu com {len(payments)} cobranças")
            
            print("\n📋 Cobranças no Asaas:")
            for payment in payments:
                print(f"  • {payment['id']} | R$ {payment['value']} | {payment['status']} | {payment.get('description', 'N/A')}")
            
            return payments
            
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao consultar API: {str(e)}")
        return None


def sync_missing_charges_heroku(asaas_payments):
    """Sincroniza cobranças faltantes no Heroku"""
    
    if not asaas_payments:
        print("❌ Nenhuma cobrança do Asaas para sincronizar")
        return
    
    print("\n🔄 SINCRONIZANDO COBRANÇAS FALTANTES")
    print("=" * 50)
    
    # Verificar quais cobranças estão faltando
    local_ids = set(CobrancaAsaas.objects.values_list('asaas_id', flat=True))
    asaas_ids = {p['id'] for p in asaas_payments}
    
    missing_ids = asaas_ids - local_ids
    
    if not missing_ids:
        print("✅ Todas as cobranças já estão sincronizadas")
        return
    
    print(f"📊 Encontradas {len(missing_ids)} cobranças faltantes:")
    
    synced_count = 0
    
    for payment in asaas_payments:
        if payment['id'] in missing_ids:
            try:
                print(f"🔄 Sincronizando {payment['id']}...")
                
                # Tentar identificar controle financeiro
                controle = identify_controle_financeiro(payment)
                
                if controle:
                    # Criar cobrança
                    create_cobranca_from_payment(payment, controle)
                    synced_count += 1
                    print(f"  ✅ Sincronizada com {controle.loja.nome}")
                else:
                    print(f"  ⚠️ Controle financeiro não identificado")
                    
            except Exception as e:
                print(f"  ❌ Erro: {str(e)}")
    
    print(f"\n🎯 Sincronização concluída: {synced_count} cobranças adicionadas")


def identify_controle_financeiro(payment):
    """Identifica controle financeiro para uma cobrança"""
    
    # Método 1: Por referência externa
    external_ref = payment.get('externalReference', '')
    if external_ref and external_ref.startswith('CF_'):
        try:
            cf_id = external_ref.split('_')[1]
            return ControleFinanceiro.objects.get(id=cf_id)
        except (IndexError, ControleFinanceiro.DoesNotExist):
            pass
    
    # Método 2: Por dados do customer
    customer_id = payment.get('customer')
    if customer_id:
        try:
            import requests
            asaas_service = AsaasService()
            
            customer_response = requests.get(
                f"{asaas_service.base_url}/customers/{customer_id}",
                headers=asaas_service.headers,
                timeout=10
            )
            
            if customer_response.status_code == 200:
                customer_data = customer_response.json()
                customer_email = customer_data.get('email', '')
                customer_cnpj = customer_data.get('cpfCnpj', '')
                
                # Buscar por email
                if customer_email:
                    controle = ControleFinanceiro.objects.filter(
                        loja__email=customer_email
                    ).first()
                    if controle:
                        return controle
                
                # Buscar por CNPJ
                if customer_cnpj:
                    cnpj_limpo = customer_cnpj.replace('.', '').replace('/', '').replace('-', '')
                    controle = ControleFinanceiro.objects.filter(
                        loja__cnpj__contains=cnpj_limpo[:8]  # Primeiros 8 dígitos
                    ).first()
                    if controle:
                        return controle
                        
        except Exception as e:
            logger.warning(f"Erro ao buscar customer {customer_id}: {str(e)}")
    
    # Método 3: Usar primeiro controle disponível (fallback)
    return ControleFinanceiro.objects.first()


def create_cobranca_from_payment(payment, controle):
    """Cria cobrança a partir dos dados do Asaas"""
    
    from decimal import Decimal
    from datetime import datetime
    
    cobranca = CobrancaAsaas.objects.create(
        asaas_id=payment['id'],
        controle_financeiro=controle,
        customer_id=payment.get('customer', ''),
        valor=Decimal(str(payment['value'])),
        data_vencimento=datetime.fromisoformat(payment['dueDate']).replace(tzinfo=timezone.get_current_timezone()),
        descricao=payment.get('description', ''),
        status=payment['status'],
        external_reference=payment.get('externalReference', ''),
        invoice_url=payment.get('invoiceUrl', ''),
        bank_slip_url=payment.get('bankSlipUrl', ''),
        invoice_number=payment.get('invoiceNumber', ''),
        api_response=payment,
        observacoes=f"Sincronizada automaticamente no Heroku - {timezone.now().strftime('%d/%m/%Y %H:%M')}"
    )
    
    # Se já foi paga, processar pagamento
    if payment['status'] in ['RECEIVED', 'CONFIRMED']:
        cobranca.marcar_como_paga()
    
    return cobranca


def show_final_status():
    """Mostra status final após sincronização"""
    
    print("\n📊 STATUS FINAL")
    print("=" * 50)
    
    cobrancas = CobrancaAsaas.objects.all().order_by('-data_criacao')
    
    print(f"📋 Total de cobranças no sistema: {len(cobrancas)}")
    
    if cobrancas:
        print("\n🏷️ Cobranças por status:")
        status_count = {}
        for cobranca in cobrancas:
            status = cobranca.status
            status_count[status] = status_count.get(status, 0) + 1
        
        for status, count in status_count.items():
            print(f"  • {status}: {count}")
        
        print(f"\n📋 Últimas 5 cobranças:")
        for cobranca in cobrancas[:5]:
            print(f"  • {cobranca.asaas_id} | {cobranca.controle_financeiro.loja.nome} | R$ {cobranca.valor} | {cobranca.status}")


def main():
    print("🚀 SINCRONIZAÇÃO FORÇADA NO HEROKU")
    print("=" * 60)
    
    # 1. Diagnosticar ambiente
    diagnose_heroku_environment()
    
    # 2. Verificar API do Asaas
    asaas_payments = check_asaas_api_directly()
    
    # 3. Forçar sincronização
    sync_result = force_sync_with_asaas()
    
    # 4. Sincronizar cobranças faltantes
    if asaas_payments:
        sync_missing_charges_heroku(asaas_payments)
    
    # 5. Mostrar status final
    show_final_status()
    
    print("\n🎯 SINCRONIZAÇÃO CONCLUÍDA!")
    print("\n💡 Se ainda houver problemas:")
    print("  1. Verifique as variáveis de ambiente no Heroku")
    print("  2. Confirme se a API key do Asaas está correta")
    print("  3. Execute: heroku run python manage.py shell")
    print("  4. Verifique logs: heroku logs --tail")


if __name__ == '__main__':
    main()