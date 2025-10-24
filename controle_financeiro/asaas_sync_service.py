"""
Serviço de Sincronização em Tempo Real com API do Asaas
Sistema completo para manter boletos sempre atualizados entre os dois sistemas
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging
from typing import Dict, List, Optional, Tuple

from .models import CobrancaAsaas, ControleFinanceiro
from .asaas_service import AsaasService

logger = logging.getLogger(__name__)


class AsaasSyncService:
    """Serviço de sincronização em tempo real com Asaas"""
    
    def __init__(self):
        self.asaas_service = AsaasService()
        self.sync_interval = 300  # 5 minutos por padrão
        self.is_running = False
        self.sync_thread = None
        self.last_sync = None
        self.sync_stats = {
            'total_synced': 0,
            'updates_found': 0,
            'errors': 0,
            'last_error': None
        }
    
    def start_real_time_sync(self, interval_seconds: int = 300):
        """
        Inicia sincronização em tempo real
        
        Args:
            interval_seconds: Intervalo entre sincronizações em segundos
        """
        if self.is_running:
            logger.warning("Sincronização já está em execução")
            return False
        
        self.sync_interval = interval_seconds
        self.is_running = True
        
        # Iniciar thread de sincronização
        self.sync_thread = threading.Thread(
            target=self._sync_loop,
            daemon=True,
            name="AsaasSyncThread"
        )
        self.sync_thread.start()
        
        logger.info(f"Sincronização em tempo real iniciada (intervalo: {interval_seconds}s)")
        return True
    
    def stop_real_time_sync(self):
        """Para a sincronização em tempo real"""
        if not self.is_running:
            return False
        
        self.is_running = False
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=10)
        
        logger.info("Sincronização em tempo real parada")
        return True
    
    def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Executar sincronização completa
                result = self.sync_all_charges()
                
                # Atualizar estatísticas
                self.sync_stats['total_synced'] += result['total_processed']
                self.sync_stats['updates_found'] += result['updates_made']
                
                if result['errors']:
                    self.sync_stats['errors'] += len(result['errors'])
                    self.sync_stats['last_error'] = result['errors'][-1]
                
                self.last_sync = timezone.now()
                
                sync_time = time.time() - start_time
                logger.info(
                    f"Sincronização concluída em {sync_time:.2f}s - "
                    f"Processadas: {result['total_processed']}, "
                    f"Atualizadas: {result['updates_made']}, "
                    f"Erros: {len(result['errors'])}"
                )
                
                # Aguardar próximo ciclo
                time.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de sincronização: {str(e)}")
                self.sync_stats['errors'] += 1
                self.sync_stats['last_error'] = str(e)
                
                # Aguardar antes de tentar novamente
                time.sleep(min(self.sync_interval, 60))
    
    def sync_all_charges(self) -> Dict:
        """
        Sincroniza todas as cobranças com o Asaas
        
        Returns:
            Dict com resultado da sincronização
        """
        result = {
            'total_processed': 0,
            'updates_made': 0,
            'new_charges': 0,
            'errors': [],
            'details': []
        }
        
        try:
            # Validar configuração com retry
            validation_attempts = 3
            config_valid = False
            
            for attempt in range(validation_attempts):
                try:
                    if self.asaas_service.validar_configuracao():
                        config_valid = True
                        break
                    else:
                        logger.warning(f"Tentativa {attempt + 1} de validação falhou")
                        if attempt < validation_attempts - 1:
                            time.sleep(2)  # Aguardar 2 segundos antes de tentar novamente
                except Exception as e:
                    logger.error(f"Erro na tentativa {attempt + 1} de validação: {str(e)}")
                    if attempt < validation_attempts - 1:
                        time.sleep(2)
            
            if not config_valid:
                raise ValueError("Configuração do Asaas inválida após múltiplas tentativas")
            
            # 1. Sincronizar cobranças existentes no sistema
            try:
                local_result = self._sync_existing_charges()
                result['total_processed'] += local_result['processed']
                result['updates_made'] += local_result['updates']
                result['errors'].extend(local_result['errors'])
            except Exception as e:
                logger.error(f"Erro ao sincronizar cobranças existentes: {str(e)}")
                result['errors'].append(f"Erro cobranças existentes: {str(e)}")
            
            # 2. Buscar novas cobranças no Asaas
            try:
                remote_result = self._fetch_new_charges_from_asaas()
                result['new_charges'] += remote_result['new_charges']
                result['errors'].extend(remote_result['errors'])
            except Exception as e:
                logger.error(f"Erro ao buscar novas cobranças: {str(e)}")
                result['errors'].append(f"Erro novas cobranças: {str(e)}")
            
            # 3. Verificar cobranças vencidas
            try:
                overdue_result = self._check_overdue_charges()
                result['updates_made'] += overdue_result['updates']
                result['errors'].extend(overdue_result['errors'])
            except Exception as e:
                logger.error(f"Erro ao verificar cobranças vencidas: {str(e)}")
                result['errors'].append(f"Erro cobranças vencidas: {str(e)}")
            
            logger.info(f"Sincronização completa: {result}")
            
        except Exception as e:
            logger.error(f"Erro na sincronização completa: {str(e)}")
            result['errors'].append(str(e))
        
        return result
    
    def _sync_existing_charges(self) -> Dict:
        """Sincroniza cobranças já existentes no sistema"""
        result = {
            'processed': 0,
            'updates': 0,
            'errors': []
        }
        
        try:
            # Buscar cobranças pendentes ou recentes (últimos 30 dias)
            data_limite = timezone.now() - timedelta(days=30)
            cobrancas = CobrancaAsaas.objects.filter(
                data_criacao__gte=data_limite
            ).exclude(
                status__in=['RECEIVED', 'CONFIRMED', 'REFUNDED']
            )
            
            logger.info(f"Sincronizando {cobrancas.count()} cobranças existentes")
            
            for cobranca in cobrancas:
                try:
                    # Consultar status atual no Asaas com retry
                    dados_asaas = None
                    max_retries = 3
                    
                    for retry in range(max_retries):
                        try:
                            dados_asaas = self.asaas_service.consultar_cobranca(cobranca.asaas_id)
                            break  # Sucesso, sair do loop de retry
                        except requests.exceptions.ConnectionError as e:
                            if "Connection refused" in str(e) and retry < max_retries - 1:
                                logger.warning(f"Connection refused para cobrança {cobranca.asaas_id}, tentativa {retry + 1}/{max_retries}")
                                time.sleep(2 ** retry)  # Backoff exponencial
                                continue
                            else:
                                raise  # Re-raise se não for connection refused ou última tentativa
                        except Exception as e:
                            if retry < max_retries - 1:
                                logger.warning(f"Erro na tentativa {retry + 1} para cobrança {cobranca.asaas_id}: {str(e)}")
                                time.sleep(1)
                                continue
                            else:
                                raise
                    
                    if dados_asaas:
                        # Verificar se houve mudanças
                        status_anterior = cobranca.status
                        cobranca.atualizar_dados_asaas(dados_asaas)
                        
                        if cobranca.status != status_anterior:
                            result['updates'] += 1
                            logger.info(f"Cobrança {cobranca.asaas_id} atualizada: {status_anterior} → {cobranca.status}")
                            
                            # Processar pagamento se foi recebido
                            if cobranca.status in ['RECEIVED', 'CONFIRMED'] and status_anterior not in ['RECEIVED', 'CONFIRMED']:
                                cobranca.marcar_como_paga()
                    else:
                        logger.warning(f"Não foi possível obter dados da cobrança {cobranca.asaas_id}")
                    
                    result['processed'] += 1
                    
                except Exception as e:
                    error_msg = f"Erro ao sincronizar cobrança {cobranca.asaas_id}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    # Continuar com próxima cobrança mesmo com erro
        
        except Exception as e:
            error_msg = f"Erro ao buscar cobranças locais: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _fetch_new_charges_from_asaas(self) -> Dict:
        """Busca novas cobranças criadas no Asaas"""
        result = {
            'new_charges': 0,
            'errors': []
        }
        
        try:
            # Buscar cobranças dos últimos 7 dias
            data_inicio = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Fazer requisição para API do Asaas
            response = requests.get(
                f"{self.asaas_service.base_url}/payments",
                headers=self.asaas_service.headers,
                params={
                    'dateCreated[ge]': data_inicio,
                    'limit': 100
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('data', [])
                
                for payment in payments:
                    try:
                        # Verificar se já existe no sistema
                        if not CobrancaAsaas.objects.filter(asaas_id=payment['id']).exists():
                            # Tentar identificar o controle financeiro pela referência
                            external_ref = payment.get('externalReference', '')
                            
                            if external_ref and external_ref.startswith('CF_'):
                                cf_id = external_ref.split('_')[1]
                                
                                try:
                                    controle = ControleFinanceiro.objects.get(id=cf_id)
                                    
                                    # Criar nova cobrança no sistema
                                    self._create_charge_from_asaas_data(payment, controle)
                                    result['new_charges'] += 1
                                    
                                except ControleFinanceiro.DoesNotExist:
                                    logger.warning(f"Controle financeiro {cf_id} não encontrado para cobrança {payment['id']}")
                    
                    except Exception as e:
                        error_msg = f"Erro ao processar nova cobrança {payment.get('id', 'N/A')}: {str(e)}"
                        logger.error(error_msg)
                        result['errors'].append(error_msg)
            
            else:
                error_msg = f"Erro ao buscar cobranças no Asaas: {response.status_code}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        except Exception as e:
            error_msg = f"Erro ao buscar novas cobranças: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _check_overdue_charges(self) -> Dict:
        """Verifica e atualiza cobranças vencidas"""
        result = {
            'updates': 0,
            'errors': []
        }
        
        try:
            # Buscar cobranças pendentes que já venceram
            agora = timezone.now()
            cobrancas_vencidas = CobrancaAsaas.objects.filter(
                status='PENDING',
                data_vencimento__lt=agora
            )
            
            for cobranca in cobrancas_vencidas:
                try:
                    # Consultar status atual no Asaas
                    dados_asaas = self.asaas_service.consultar_cobranca(cobranca.asaas_id)
                    
                    if dados_asaas:
                        status_anterior = cobranca.status
                        cobranca.atualizar_dados_asaas(dados_asaas)
                        
                        # Se ainda está pendente, marcar como vencida
                        if cobranca.status == 'PENDING':
                            cobranca.status = 'OVERDUE'
                            cobranca.save()
                            result['updates'] += 1
                            logger.info(f"Cobrança {cobranca.asaas_id} marcada como vencida")
                
                except Exception as e:
                    error_msg = f"Erro ao verificar cobrança vencida {cobranca.asaas_id}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
        
        except Exception as e:
            error_msg = f"Erro ao verificar cobranças vencidas: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _create_charge_from_asaas_data(self, payment_data: Dict, controle: ControleFinanceiro):
        """Cria uma cobrança no sistema a partir dos dados do Asaas"""
        try:
            with transaction.atomic():
                cobranca = CobrancaAsaas.objects.create(
                    asaas_id=payment_data['id'],
                    controle_financeiro=controle,
                    customer_id=payment_data['customer'],
                    valor=Decimal(str(payment_data['value'])),
                    data_vencimento=datetime.fromisoformat(payment_data['dueDate']).replace(tzinfo=timezone.utc),
                    descricao=payment_data.get('description', ''),
                    status=payment_data['status'],
                    external_reference=payment_data.get('externalReference', ''),
                    api_response=payment_data
                )
                
                # Atualizar dados adicionais
                cobranca.atualizar_dados_asaas(payment_data)
                
                logger.info(f"Nova cobrança criada no sistema: {cobranca.asaas_id}")
                return cobranca
        
        except Exception as e:
            logger.error(f"Erro ao criar cobrança no sistema: {str(e)}")
            raise
    
    def sync_single_charge(self, asaas_id: str) -> Dict:
        """
        Sincroniza uma cobrança específica
        
        Args:
            asaas_id: ID da cobrança no Asaas
            
        Returns:
            Dict com resultado da sincronização
        """
        result = {
            'success': False,
            'updated': False,
            'error': None
        }
        
        try:
            # Buscar cobrança no sistema
            try:
                cobranca = CobrancaAsaas.objects.get(asaas_id=asaas_id)
            except CobrancaAsaas.DoesNotExist:
                result['error'] = f"Cobrança {asaas_id} não encontrada no sistema"
                return result
            
            # Consultar dados atuais no Asaas
            dados_asaas = self.asaas_service.consultar_cobranca(asaas_id)
            
            if not dados_asaas:
                result['error'] = f"Não foi possível consultar cobrança {asaas_id} no Asaas"
                return result
            
            # Verificar se houve mudanças
            status_anterior = cobranca.status
            cobranca.atualizar_dados_asaas(dados_asaas)
            
            if cobranca.status != status_anterior:
                result['updated'] = True
                logger.info(f"Cobrança {asaas_id} sincronizada: {status_anterior} → {cobranca.status}")
                
                # Processar pagamento se foi recebido
                if cobranca.status in ['RECEIVED', 'CONFIRMED'] and status_anterior not in ['RECEIVED', 'CONFIRMED']:
                    cobranca.marcar_como_paga()
            
            result['success'] = True
            
        except Exception as e:
            error_msg = f"Erro ao sincronizar cobrança {asaas_id}: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
        
        return result
    
    def get_sync_status(self) -> Dict:
        """Retorna status atual da sincronização"""
        return {
            'is_running': self.is_running,
            'sync_interval': self.sync_interval,
            'last_sync': self.last_sync,
            'stats': self.sync_stats.copy(),
            'thread_alive': self.sync_thread.is_alive() if self.sync_thread else False
        }
    
    def force_sync_now(self) -> Dict:
        """Força uma sincronização imediata"""
        logger.info("Iniciando sincronização forçada")
        return self.sync_all_charges()
    
    def reset_stats(self):
        """Reseta as estatísticas de sincronização"""
        self.sync_stats = {
            'total_synced': 0,
            'updates_found': 0,
            'errors': 0,
            'last_error': None
        }
        logger.info("Estatísticas de sincronização resetadas")


# Instância global do serviço de sincronização
sync_service = AsaasSyncService()


def start_sync_service(interval_seconds: int = 300):
    """Inicia o serviço de sincronização global"""
    return sync_service.start_real_time_sync(interval_seconds)


def stop_sync_service():
    """Para o serviço de sincronização global"""
    return sync_service.stop_real_time_sync()


def get_sync_service():
    """Retorna a instância do serviço de sincronização"""
    return sync_service