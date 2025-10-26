#!/usr/bin/env python3
"""
Script para sincronizar cobranças que estão no Asaas mas não no sistema local
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from django.db import transaction
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService
from lojas.models import Loja
from decimal import Decimal
import logging
import requests

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MissingChargesSync:
    """Sincroniza cobranças que estão no Asaas mas não no sistema local"""
    
    def __init__(self):
        self.asaas_service = AsaasService()
        self.missing_charges = []
        self.synced_charges = []
        self.errors = []
        
    def find_missing_charges(self):
        """Encontra cobranças que estão no Asaas mas não no sistema local"""
        logger.info("🔍 Buscando cobranças no Asaas...")
        
        try:
            # Buscar cobranças dos últimos 60 dias
            data_inicio = (timezone.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{self.asaas_service.base_url}/payments",
                headers=self.asaas_service.headers,
                params={
                    'dateCreated[ge]': data_inicio,
                    'limit': 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('data', [])
                
                logger.info(f"📊 Encontradas {len(payments)} cobranças no Asaas")
                
                # Verificar quais não existem no sistema local
                for payment in payments:
                    payment_id = payment['id']
                    
                    if not CobrancaAsaas.objects.filter(asaas_id=payment_id).exists():
                        logger.info(f"❌ Cobrança {payment_id} não existe no sistema local")
                        self.missing_charges.append(payment)
                    else:
                        logger.info(f"✅ Cobrança {payment_id} já existe no sistema local")
                
                logger.info(f"🔍 Encontradas {len(self.missing_charges)} cobranças faltando no sistema local")
                return len(self.missing_charges)
                
            else:
                logger.error(f"❌ Erro na API: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            logger.error(f"💥 Erro ao buscar cobranças: {str(e)}")
            return 0
    
    def sync_missing_charges(self, confirm=False):
        """Sincroniza cobranças faltantes"""
        if not self.missing_charges:
            logger.info("✅ Nenhuma cobrança faltante encontrada")
            return 0
        
        logger.info(f"🔄 Preparando para sincronizar {len(self.missing_charges)} cobranças:")
        
        for payment in self.missing_charges:
            logger.info(f"  - {payment['id']} | R$ {payment['value']} | {payment['status']} | {payment.get('description', 'N/A')}")
        
        if not confirm:
            logger.warning("⚠️ Execute com confirm=True para sincronizar as cobranças")
            return 0
        
        # Sincronizar cobranças
        synced_count = 0
        for payment in self.missing_charges:
            try:
                if self._sync_single_charge(payment):
                    synced_count += 1
                    
            except Exception as e:
                logger.error(f"💥 Erro ao sincronizar cobrança {payment['id']}: {str(e)}")
                self.errors.append(f"Erro em {payment['id']}: {str(e)}")
        
        return synced_count
    
    def _sync_single_charge(self, payment):
        """Sincroniza uma cobrança específica"""
        payment_id = payment['id']
        logger.info(f"🔄 Sincronizando cobrança {payment_id}...")
        
        try:
            with transaction.atomic():
                # Tentar identificar o controle financeiro
                controle = self._identify_controle_financeiro(payment)
                
                if not controle:
                    logger.warning(f"⚠️ Não foi possível identificar controle financeiro para {payment_id}")
                    # Criar controle financeiro automático se necessário
                    controle = self._create_automatic_controle(payment)
                    
                    if not controle:
                        logger.error(f"❌ Não foi possível criar controle financeiro para {payment_id}")
                        return False
                
                # Criar cobrança no sistema
                cobranca = CobrancaAsaas.objects.create(
                    asaas_id=payment_id,
                    controle_financeiro=controle,
                    customer_id=payment['customer'],
                    valor=Decimal(str(payment['value'])),
                    data_vencimento=datetime.fromisoformat(payment['dueDate']).replace(tzinfo=timezone.get_current_timezone()),
                    descricao=payment.get('description', ''),
                    status=payment['status'],
                    external_reference=payment.get('externalReference', ''),
                    api_response=payment
                )
                
                # Atualizar dados adicionais
                cobranca.atualizar_dados_asaas(payment)
                
                # Se a cobrança já foi paga, processar pagamento
                if payment['status'] in ['RECEIVED', 'CONFIRMED']:
                    cobranca.marcar_como_paga()
                
                logger.info(f"✅ Cobrança {payment_id} sincronizada com sucesso")
                self.synced_charges.append({
                    'payment_id': payment_id,
                    'controle': controle.id,
                    'loja': controle.loja.nome,
                    'valor': payment['value'],
                    'status': payment['status']
                })
                
                return True
                
        except Exception as e:
            logger.error(f"💥 Erro ao criar cobrança {payment_id}: {str(e)}")
            return False
    
    def _identify_controle_financeiro(self, payment):
        """Identifica o controle financeiro para uma cobrança"""
        # Método 1: Por referência externa
        external_ref = payment.get('externalReference', '')
        if external_ref and external_ref.startswith('CF_'):
            try:
                cf_id = external_ref.split('_')[1]
                return ControleFinanceiro.objects.get(id=cf_id)
            except (IndexError, ControleFinanceiro.DoesNotExist):
                pass
        
        # Método 2: Buscar dados do customer no Asaas
        customer_id = payment.get('customer')
        if customer_id:
            try:
                customer_response = requests.get(
                    f"{self.asaas_service.base_url}/customers/{customer_id}",
                    headers=self.asaas_service.headers,
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
                        controle = ControleFinanceiro.objects.filter(
                            loja__cnpj=customer_cnpj
                        ).first()
                        if controle:
                            return controle
                            
            except Exception as e:
                logger.warning(f"Erro ao buscar customer {customer_id}: {str(e)}")
        
        return None
    
    def _create_automatic_controle(self, payment):
        """Cria controle financeiro automático para cobrança órfã"""
        try:
            customer_id = payment.get('customer')
            if not customer_id:
                return None
            
            # Buscar dados do customer
            customer_response = requests.get(
                f"{self.asaas_service.base_url}/customers/{customer_id}",
                headers=self.asaas_service.headers,
                timeout=10
            )
            
            if customer_response.status_code != 200:
                return None
            
            customer_data = customer_response.json()
            
            # Criar loja automática
            from controle_financeiro.models import PlanoFinanceiro
            
            # Buscar plano básico
            plano_basico = PlanoFinanceiro.objects.filter(nome='Básico').first()
            if not plano_basico:
                plano_basico = PlanoFinanceiro.objects.create(
                    nome='Básico',
                    descricao='Plano básico para cobranças importadas',
                    valor_mensal=29.90,
                    ativo=True
                )
            
            # Criar loja
            loja = Loja.objects.create(
                nome=customer_data.get('name', 'Loja Importada do Asaas'),
                email=customer_data.get('email', ''),
                cnpj=customer_data.get('cpfCnpj', ''),
                telefone=customer_data.get('phone', ''),
                endereco=customer_data.get('address', 'Endereço não informado'),
                cidade=customer_data.get('city', 'Cidade não informada'),
                estado=customer_data.get('state', 'Estado não informado'),
                cep='00000000',
                status='ativa'
            )
            
            # Criar controle financeiro
            controle = ControleFinanceiro.objects.create(
                loja=loja,
                plano=plano_basico,
                status='ativa',
                valor_mensal=Decimal(str(payment['value'])),
                data_inicio=timezone.now(),
                data_vencimento=timezone.now() + timedelta(days=30)
            )
            
            logger.info(f"✅ Controle financeiro criado automaticamente: {controle.id} para {loja.nome}")
            return controle
            
        except Exception as e:
            logger.error(f"💥 Erro ao criar controle automático: {str(e)}")
            return None
    
    def generate_report(self):
        """Gera relatório da sincronização"""
        logger.info("\n" + "="*60)
        logger.info("📋 RELATÓRIO DE SINCRONIZAÇÃO")
        logger.info("="*60)
        
        logger.info(f"🔍 Cobranças faltantes encontradas: {len(self.missing_charges)}")
        logger.info(f"✅ Cobranças sincronizadas: {len(self.synced_charges)}")
        logger.info(f"❌ Erros durante sincronização: {len(self.errors)}")
        
        if self.missing_charges:
            logger.info("\n📋 COBRANÇAS FALTANTES:")
            for payment in self.missing_charges:
                logger.info(f"  • {payment['id']} - R$ {payment['value']} - {payment['status']}")
        
        if self.synced_charges:
            logger.info("\n✅ COBRANÇAS SINCRONIZADAS:")
            for charge in self.synced_charges:
                logger.info(f"  • {charge['payment_id']} - {charge['loja']} - R$ {charge['valor']} - {charge['status']}")
        
        if self.errors:
            logger.info("\n❌ ERROS:")
            for error in self.errors:
                logger.info(f"  • {error}")
        
        logger.info("\n" + "="*60)


def main():
    """Função principal"""
    print("🚀 Iniciando sincronização de cobranças faltantes...")
    
    sync = MissingChargesSync()
    
    # Encontrar cobranças faltantes
    missing_count = sync.find_missing_charges()
    
    if missing_count > 0:
        print(f"\n⚠️ Encontradas {missing_count} cobranças no Asaas que não estão no sistema local")
        print("💡 Para sincronizar essas cobranças, execute:")
        print("   python sync_missing_charges.py --sync")
        
        # Verificar se foi solicitada sincronização
        if len(sys.argv) > 1 and sys.argv[1] == '--sync':
            print("\n🔄 Sincronizando cobranças faltantes...")
            synced = sync.sync_missing_charges(confirm=True)
            print(f"✅ {synced} cobranças sincronizadas com sucesso")
    else:
        print("✅ Todas as cobranças do Asaas já estão no sistema local")
    
    # Gerar relatório
    sync.generate_report()
    
    print("\n🎯 Sincronização concluída!")


if __name__ == '__main__':
    main()