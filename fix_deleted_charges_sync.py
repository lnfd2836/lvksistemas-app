#!/usr/bin/env python3
"""
Script para corrigir sincronização de cobranças excluídas do Asaas
Identifica cobranças que foram excluídas no Asaas mas ainda existem no sistema local
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from controle_financeiro.models import CobrancaAsaas
from controle_financeiro.asaas_service import AsaasService
import logging
import requests

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeletedChargesSyncFixer:
    """Corrige sincronização de cobranças excluídas"""
    
    def __init__(self):
        self.asaas_service = AsaasService()
        self.deleted_charges = []
        self.errors = []
        
    def check_deleted_charges(self):
        """Verifica cobranças que foram excluídas no Asaas"""
        logger.info("🔍 Iniciando verificação de cobranças excluídas...")
        
        # Buscar cobranças locais dos últimos 30 dias
        data_limite = timezone.now() - timedelta(days=30)
        cobrancas_locais = CobrancaAsaas.objects.filter(
            data_criacao__gte=data_limite
        ).exclude(
            status__in=['RECEIVED', 'CONFIRMED', 'REFUNDED']
        )
        
        logger.info(f"📊 Verificando {len(cobrancas_locais)} cobranças locais...")
        
        for cobranca in cobrancas_locais:
            try:
                # Tentar consultar a cobrança no Asaas
                logger.info(f"🔎 Verificando cobrança {cobranca.asaas_id}...")
                
                response = requests.get(
                    f"{self.asaas_service.base_url}/payments/{cobranca.asaas_id}",
                    headers=self.asaas_service.headers,
                    timeout=10
                )
                
                if response.status_code == 404:
                    # Cobrança não existe mais no Asaas
                    logger.warning(f"❌ Cobrança {cobranca.asaas_id} foi excluída do Asaas")
                    self.deleted_charges.append({
                        'cobranca': cobranca,
                        'asaas_id': cobranca.asaas_id,
                        'loja': cobranca.controle_financeiro.loja.nome,
                        'valor': cobranca.valor,
                        'data_criacao': cobranca.data_criacao
                    })
                    
                elif response.status_code == 200:
                    # Cobrança ainda existe
                    logger.info(f"✅ Cobrança {cobranca.asaas_id} ainda existe no Asaas")
                    
                elif response.status_code == 401:
                    logger.error("🔐 Erro de autenticação - verificar API key")
                    break
                    
                else:
                    logger.warning(f"⚠️ Status inesperado {response.status_code} para cobrança {cobranca.asaas_id}")
                    
            except requests.exceptions.ConnectionError as e:
                if "Connection refused" in str(e):
                    logger.error("🚫 Connection refused - API Asaas indisponível")
                    break
                else:
                    logger.error(f"🌐 Erro de conexão: {str(e)}")
                    self.errors.append(f"Conexão falhou para {cobranca.asaas_id}: {str(e)}")
                    
            except Exception as e:
                logger.error(f"💥 Erro ao verificar cobrança {cobranca.asaas_id}: {str(e)}")
                self.errors.append(f"Erro em {cobranca.asaas_id}: {str(e)}")
        
        return len(self.deleted_charges)
    
    def remove_deleted_charges(self, confirm=False):
        """Remove cobranças excluídas do sistema local"""
        if not self.deleted_charges:
            logger.info("✅ Nenhuma cobrança excluída encontrada")
            return 0
        
        logger.info(f"🗑️ Encontradas {len(self.deleted_charges)} cobranças excluídas:")
        
        for item in self.deleted_charges:
            cobranca = item['cobranca']
            logger.info(f"  - {item['asaas_id']} | {item['loja']} | R$ {item['valor']} | {item['data_criacao'].strftime('%d/%m/%Y')}")
        
        if not confirm:
            logger.warning("⚠️ Execute com confirm=True para remover as cobranças")
            return 0
        
        # Remover cobranças excluídas
        removed_count = 0
        for item in self.deleted_charges:
            try:
                cobranca = item['cobranca']
                logger.info(f"🗑️ Removendo cobrança {cobranca.asaas_id}...")
                
                # Adicionar observação antes de excluir
                cobranca.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: Cobrança excluída do Asaas - removida automaticamente"
                cobranca.save()
                
                # Excluir cobrança
                cobranca.delete()
                removed_count += 1
                
                logger.info(f"✅ Cobrança {cobranca.asaas_id} removida com sucesso")
                
            except Exception as e:
                logger.error(f"💥 Erro ao remover cobrança {cobranca.asaas_id}: {str(e)}")
                self.errors.append(f"Erro ao remover {cobranca.asaas_id}: {str(e)}")
        
        return removed_count
    
    def update_sync_service(self):
        """Atualiza o serviço de sincronização para verificar cobranças excluídas"""
        logger.info("🔧 Verificando se o serviço de sincronização precisa ser atualizado...")
        
        # Verificar se já existe método para verificar cobranças excluídas
        sync_file_path = 'controle_financeiro/asaas_sync_service.py'
        
        try:
            with open(sync_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '_check_deleted_charges' in content:
                logger.info("✅ Método _check_deleted_charges já existe no serviço de sincronização")
                return True
            else:
                logger.warning("⚠️ Método _check_deleted_charges não encontrado - será necessário atualizar o serviço")
                return False
                
        except Exception as e:
            logger.error(f"💥 Erro ao verificar arquivo de sincronização: {str(e)}")
            return False
    
    def generate_report(self):
        """Gera relatório da verificação"""
        logger.info("\n" + "="*60)
        logger.info("📋 RELATÓRIO DE COBRANÇAS EXCLUÍDAS")
        logger.info("="*60)
        
        logger.info(f"🔍 Cobranças excluídas encontradas: {len(self.deleted_charges)}")
        logger.info(f"❌ Erros durante verificação: {len(self.errors)}")
        
        if self.deleted_charges:
            logger.info("\n📋 COBRANÇAS EXCLUÍDAS:")
            total_valor = 0
            for item in self.deleted_charges:
                logger.info(f"  • {item['asaas_id']} - {item['loja']} - R$ {item['valor']}")
                total_valor += item['valor']
            logger.info(f"\n💰 Valor total das cobranças excluídas: R$ {total_valor}")
        
        if self.errors:
            logger.info("\n❌ ERROS ENCONTRADOS:")
            for error in self.errors:
                logger.info(f"  • {error}")
        
        logger.info("\n" + "="*60)


def main():
    """Função principal"""
    print("🚀 Iniciando correção de sincronização de cobranças excluídas...")
    
    fixer = DeletedChargesSyncFixer()
    
    # Verificar cobranças excluídas
    deleted_count = fixer.check_deleted_charges()
    
    # Gerar relatório
    fixer.generate_report()
    
    if deleted_count > 0:
        print(f"\n⚠️ Encontradas {deleted_count} cobranças que foram excluídas no Asaas")
        print("💡 Para remover essas cobranças do sistema local, execute:")
        print("   python fix_deleted_charges_sync.py --remove")
        
        # Verificar se foi solicitada remoção
        if len(sys.argv) > 1 and sys.argv[1] == '--remove':
            print("\n🗑️ Removendo cobranças excluídas...")
            removed = fixer.remove_deleted_charges(confirm=True)
            print(f"✅ {removed} cobranças removidas com sucesso")
    else:
        print("✅ Nenhuma cobrança excluída encontrada - sistema sincronizado")
    
    # Verificar se o serviço de sincronização precisa ser atualizado
    fixer.update_sync_service()
    
    print("\n🎯 Correção concluída!")


if __name__ == '__main__':
    main()