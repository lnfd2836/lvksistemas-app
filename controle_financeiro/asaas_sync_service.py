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
        Inicia sincronização em tempo real (modo Heroku - sem threading)
        
        Args:
            interval_seconds: Intervalo entre sincronizações em segundos
        """
        if self.is_running:
            logger.warning("Sincronização já está marcada como ativa")
            return False
        
        # Marcar como ativo (sem threading no Heroku)
        self.sync_interval = interval_seconds
        self.is_running = True
        self.last_sync = timezone.now()
        
        logger.info(f"Sincronização marcada como ativa (intervalo: {interval_seconds}s)")
        logger.info("HEROKU MODE: Use execução manual ou Celery para sincronização contínua")
        
        return True
    
    def stop_real_time_sync(self):
        """Para a sincronização em tempo real"""
        if not self.is_running:
            return False
        
        self.is_running = False
        self.sync_thread = None
        
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
        Sincroniza todas as cobranças com o Asaas (versão anti-connection refused)
        
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
            # Estratégia 1: Validação com timeout muito baixo
            logger.info("Iniciando validação com timeout reduzido...")
            config_valid = False
            
            try:
                # Usar timeout de apenas 5 segundos para validação inicial
                config_valid = self._validate_with_short_timeout()
            except Exception as e:
                logger.warning(f"Validação rápida falhou: {str(e)}")
                result['errors'].append(f"Validação rápida: {str(e)}")
            
            if not config_valid:
                # Estratégia 2: Tentar validação com delay progressivo
                logger.info("Tentando validação com delay progressivo...")
                for attempt in range(3):
                    try:
                        time.sleep(attempt * 2)  # 0s, 2s, 4s
                        if self.asaas_service.validar_configuracao():
                            config_valid = True
                            logger.info(f"Validação bem-sucedida na tentativa {attempt + 1}")
                            break
                    except requests.exceptions.ConnectionError as e:
                        if "Connection refused" in str(e):
                            logger.warning(f"Connection refused na tentativa {attempt + 1}")
                            result['errors'].append(f"Connection refused tentativa {attempt + 1}")
                        else:
                            raise
                    except Exception as e:
                        logger.warning(f"Erro na tentativa {attempt + 1}: {str(e)}")
                        result['errors'].append(f"Tentativa {attempt + 1}: {str(e)}")
            
            if not config_valid:
                # Estratégia 3: Modo degradado - apenas verificar cobranças locais
                logger.info("Modo degradado: verificando apenas dados locais")
                return self._sync_local_only_mode()
            
            # Se chegou aqui, API está acessível - prosseguir com sincronização limitada
            logger.info("API acessível - iniciando sincronização limitada")
            
            # 1. Sincronizar apenas algumas cobranças existentes (máximo 10)
            try:
                local_result = self._sync_existing_charges_limited()
                result['total_processed'] += local_result['processed']
                result['updates_made'] += local_result['updates']
                result['errors'].extend(local_result['errors'])
            except requests.exceptions.ConnectionError as e:
                if "Connection refused" in str(e):
                    logger.warning("Connection refused durante sincronização - parando")
                    result['errors'].append("Connection refused durante sincronização")
                    return result
                else:
                    raise
            except Exception as e:
                logger.error(f"Erro ao sincronizar cobranças existentes: {str(e)}")
                result['errors'].append(f"Erro cobranças existentes: {str(e)}")
            
            logger.info(f"Sincronização limitada concluída: {result}")
            
        except Exception as e:
            logger.error(f"Erro na sincronização completa: {str(e)}")
            result['errors'].append(str(e))
        
        return result
    
    def _sync_existing_charges(self) -> Dict:
        """Sincroniza cobranças já existentes no sistema (versão Heroku otimizada)"""
        result = {
            'processed': 0,
            'updates': 0,
            'errors': []
        }
        
        try:
            # Buscar apenas cobranças mais recentes para evitar timeout
            data_limite = timezone.now() - timedelta(days=7)  # Reduzido para 7 dias
            cobrancas = CobrancaAsaas.objects.filter(
                data_criacao__gte=data_limite
            ).exclude(
                status__in=['RECEIVED', 'CONFIRMED', 'REFUNDED']
            )[:50]  # Limitar a 50 cobranças por execução
            
            logger.info(f"Sincronizando {len(cobrancas)} cobranças existentes (últimos 7 dias)")
            
            for cobranca in cobrancas:
                try:
                    # Consultar status atual no Asaas com timeout reduzido
                    dados_asaas = None
                    
                    try:
                        # Usar timeout mais baixo para evitar connection refused
                        dados_asaas = self.asaas_service.consultar_cobranca(
                            cobranca.asaas_id, 
                            timeout=15  # Timeout reduzido
                        )
                    except requests.exceptions.RequestException as e:
                        # Log do erro mas continuar com próxima cobrança
                        logger.warning(f"Erro de conexão para cobrança {cobranca.asaas_id}: {str(e)}")
                        result['errors'].append(f"Conexão falhou para {cobranca.asaas_id}")
                        continue
                    
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
                    
                    result['processed'] += 1
                    
                except Exception as e:
                    error_msg = f"Erro ao sincronizar cobrança {cobranca.asaas_id}: {str(e)}"
                    logger.warning(error_msg)  # Warning em vez de error
                    result['errors'].append(error_msg)
                    # Continuar com próxima cobrança mesmo com erro
        
        except Exception as e:
            error_msg = f"Erro ao buscar cobranças locais: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _fetch_new_charges_from_asaas(self) -> Dict:
        """Busca novas cobranças criadas no Asaas (versão Heroku otimizada)"""
        result = {
            'new_charges': 0,
            'errors': []
        }
        
        try:
            # Buscar cobranças dos últimos 3 dias apenas
            data_inicio = (timezone.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            
            # Fazer requisição para API do Asaas com timeout reduzido
            response = requests.get(
                f"{self.asaas_service.base_url}/payments",
                headers=self.asaas_service.headers,
                params={
                    'dateCreated[ge]': data_inicio,
                    'limit': 50  # Reduzido para 50
                },
                timeout=20  # Timeout reduzido
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
            'thread_alive': False  # No Heroku, usar Celery em vez de threads
        }
    
    def force_sync_now(self) -> Dict:
        """Força uma sincronização imediata (versão Heroku otimizada)"""
        logger.info("Iniciando sincronização forçada")
        try:
            result = self.sync_all_charges()
            self.last_sync = timezone.now()
            
            # Atualizar estatísticas
            self.sync_stats['total_synced'] += result['total_processed']
            self.sync_stats['updates_found'] += result['updates_made']
            
            if result['errors']:
                self.sync_stats['errors'] += len(result['errors'])
                self.sync_stats['last_error'] = result['errors'][-1] if result['errors'] else None
            
            return result
        except Exception as e:
            logger.error(f"Erro na sincronização forçada: {str(e)}")
            self.sync_stats['errors'] += 1
            self.sync_stats['last_error'] = str(e)
            return {
                'total_processed': 0,
                'updates_made': 0,
                'new_charges': 0,
                'errors': [str(e)],
                'details': []
            }
    
    def _validate_with_short_timeout(self) -> bool:
        """Validação com timeout muito curto para detectar connection refused rapidamente"""
        try:
            # Criar uma instância temporária com timeout muito baixo
            temp_service = AsaasService()
            
            # Fazer uma requisição muito simples com timeout de 3 segundos
            response = requests.get(
                f"{temp_service.base_url}/myAccount",
                headers=temp_service.headers,
                timeout=3
            )
            
            return response.status_code in [200, 401, 403]  # Qualquer resposta é boa
            
        except requests.exceptions.ConnectionError as e:
            if "Connection refused" in str(e):
                logger.warning("Connection refused detectado na validação rápida")
                return False
            raise
        except requests.exceptions.Timeout:
            logger.warning("Timeout na validação rápida")
            return False
        except Exception as e:
            logger.warning(f"Erro na validação rápida: {str(e)}")
            return False
    
    def _sync_local_only_mode(self) -> Dict:
        """Modo degradado - apenas verificações locais sem API"""
        result = {
            'total_processed': 0,
            'updates_made': 0,
            'new_charges': 0,
            'errors': ['Modo degradado: API inacessível'],
            'details': ['Executando apenas verificações locais']
        }
        
        try:
            # Verificar cobranças que deveriam estar vencidas
            agora = timezone.now()
            cobrancas_para_vencer = CobrancaAsaas.objects.filter(
                status='PENDING',
                data_vencimento__lt=agora
            )
            
            for cobranca in cobrancas_para_vencer:
                if cobranca.status == 'PENDING':
                    cobranca.status = 'OVERDUE'
                    cobranca.save()
                    result['updates_made'] += 1
                    result['total_processed'] += 1
            
            logger.info(f"Modo degradado: {result['updates_made']} cobranças marcadas como vencidas")
            
        except Exception as e:
            result['errors'].append(f"Erro no modo degradado: {str(e)}")
        
        return result
    
    def _sync_existing_charges_limited(self) -> Dict:
        """Sincroniza apenas algumas cobranças existentes (máximo 10)"""
        result = {
            'processed': 0,
            'updates': 0,
            'errors': []
        }
        
        try:
            # Buscar apenas cobranças reais (excluir exemplos e testes)
            cobrancas = CobrancaAsaas.objects.filter(
                status__in=['PENDING', 'OVERDUE']
            ).exclude(
                asaas_id__contains='exemplo'
            ).exclude(
                asaas_id__contains='TESTE'
            ).exclude(
                asaas_id__startswith='test_'
            ).order_by('-data_criacao')[:10]
            
            logger.info(f"Sincronizando {len(cobrancas)} cobranças (modo limitado)")
            
            for cobranca in cobrancas:
                try:
                    # Usar timeout muito baixo para detectar connection refused rapidamente
                    dados_asaas = self.asaas_service.consultar_cobranca(
                        cobranca.asaas_id, 
                        timeout=5  # Timeout muito baixo
                    )
                    
                    if dados_asaas:
                        status_anterior = cobranca.status
                        cobranca.atualizar_dados_asaas(dados_asaas)
                        
                        if cobranca.status != status_anterior:
                            result['updates'] += 1
                            logger.info(f"Cobrança {cobranca.asaas_id} atualizada: {status_anterior} → {cobranca.status}")
                            
                            # Processar pagamento se foi recebido
                            if cobranca.status in ['RECEIVED', 'CONFIRMED'] and status_anterior not in ['RECEIVED', 'CONFIRMED']:
                                cobranca.marcar_como_paga()
                    
                    result['processed'] += 1
                    
                    # Pequeno delay entre requisições para evitar sobrecarga
                    time.sleep(0.5)
                    
                except requests.exceptions.ConnectionError as e:
                    if "Connection refused" in str(e):
                        logger.warning(f"Connection refused para cobrança {cobranca.asaas_id} - parando sincronização")
                        result['errors'].append(f"Connection refused em {cobranca.asaas_id}")
                        break  # Parar imediatamente se connection refused
                    else:
                        raise
                except Exception as e:
                    error_msg = f"Erro ao sincronizar cobrança {cobranca.asaas_id}: {str(e)}"
                    logger.warning(error_msg)
                    result['errors'].append(error_msg)
                    # Continuar com próxima cobrança
        
        except Exception as e:
            error_msg = f"Erro ao buscar cobranças locais: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result

    def simple_sync_check(self) -> Dict:
        """Verificação de conectividade anti-connection refused"""
        result = {
            'api_accessible': False,
            'config_valid': False,
            'sample_charges_checked': 0,
            'errors': []
        }
        
        try:
            # 1. Teste rápido de conectividade
            logger.info("Executando teste rápido de conectividade...")
            if self._validate_with_short_timeout():
                result['api_accessible'] = True
                result['config_valid'] = True
                logger.info("✅ Teste rápido passou - API acessível")
                
                # 2. Testar com UMA cobrança apenas
                cobrancas_teste = CobrancaAsaas.objects.filter(
                    status='PENDING'
                ).order_by('-data_criacao')[:1]  # Apenas 1 cobrança
                
                for cobranca in cobrancas_teste:
                    try:
                        dados = self.asaas_service.consultar_cobranca(cobranca.asaas_id, timeout=5)
                        if dados:
                            result['sample_charges_checked'] += 1
                            logger.info(f"✅ Cobrança {cobranca.asaas_id} testada com sucesso")
                        break  # Testar apenas uma
                    except requests.exceptions.ConnectionError as e:
                        if "Connection refused" in str(e):
                            result['errors'].append(f"Connection refused ao testar {cobranca.asaas_id}")
                            result['api_accessible'] = False
                            break
                        else:
                            result['errors'].append(f"Erro de conexão: {str(e)}")
                    except Exception as e:
                        result['errors'].append(f"Erro ao consultar {cobranca.asaas_id}: {str(e)}")
                        
            else:
                result['errors'].append("Teste rápido de conectividade falhou")
                
        except Exception as e:
            result['errors'].append(f"Erro na verificação: {str(e)}")
        
        return result
    
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