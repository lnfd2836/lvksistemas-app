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
        try:
            from .models_sync import SyncStatus
            db_status = SyncStatus.get_current()
            
            if db_status.is_running:
                logger.warning("Sincronização já está marcada como ativa no banco")
                return False
            
            # Marcar como ativo no banco
            db_status.start_sync(interval_seconds)
            
            # Atualizar também em memória
            self.sync_interval = interval_seconds
            self.is_running = True
            self.last_sync = timezone.now()
            
            logger.info(f"Sincronização marcada como ativa (intervalo: {interval_seconds}s)")
            logger.info("HEROKU MODE: Use execução manual ou Celery para sincronização contínua")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar sincronização: {str(e)}")
            return False
    
    def stop_real_time_sync(self):
        """Para a sincronização em tempo real"""
        try:
            from .models_sync import SyncStatus
            db_status = SyncStatus.get_current()
            
            if not db_status.is_running:
                return False
            
            # Marcar como parado no banco
            db_status.stop_sync()
            
            # Atualizar também em memória
            self.is_running = False
            self.sync_thread = None
            
            logger.info("Sincronização em tempo real parada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar sincronização: {str(e)}")
            return False
    
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
            
            # 1. Buscar novas cobranças do Asaas
            try:
                new_result = self._fetch_new_charges_from_asaas()
                result['new_charges'] += new_result['new_charges']
                result['errors'].extend(new_result['errors'])
                logger.info(f"Novas cobranças sincronizadas: {new_result['new_charges']}")
            except requests.exceptions.ConnectionError as e:
                if "Connection refused" in str(e):
                    logger.warning("Connection refused durante busca de novas cobranças - continuando")
                    result['errors'].append("Connection refused durante busca de novas cobranças")
                else:
                    raise
            except Exception as e:
                logger.error(f"Erro ao buscar novas cobranças: {str(e)}")
                result['errors'].append(f"Erro novas cobranças: {str(e)}")
            
            # 2. Sincronizar apenas algumas cobranças existentes (máximo 10)
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
            

            # 3. Verificar cobranças excluídas (se API estiver acessível)
            try:
                deleted_result = self._check_deleted_charges()
                result['deleted_found'] = deleted_result['deleted_found']
                result['deleted_removed'] = deleted_result['deleted_removed']
                result['errors'].extend(deleted_result['errors'])
                logger.info(f"Verificação de exclusões: {deleted_result['deleted_found']} encontradas, {deleted_result['deleted_removed']} removidas")
            except Exception as e:
                logger.error(f"Erro ao verificar cobranças excluídas: {str(e)}")
                result['errors'].append(f"Erro verificação exclusões: {str(e)}")
            
            logger.info(f"Sincronização limitada concluída: {result}")
            
        except Exception as e:
            logger.error(f"Erro na sincronização completa: {str(e)}")
            result['errors'].append(str(e))
        
        return result
    
    def _create_loja_and_controle_from_customer(self, customer_data, payment_data):
        """
        Cria automaticamente uma loja e controle financeiro para cobranças órfãs
        
        Args:
            customer_data: Dados do customer do Asaas
            payment_data: Dados do payment do Asaas
            
        Returns:
            ControleFinanceiro: Controle financeiro criado ou None se falhar
        """
        try:
            from lojas.models import Loja
            from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro
            from django.utils import timezone
            from datetime import timedelta
            
            # Extrair dados do customer
            customer_name = customer_data.get('name', 'Loja Importada do Asaas')
            customer_email = customer_data.get('email', '')
            customer_cnpj = customer_data.get('cpfCnpj', '')
            customer_phone = customer_data.get('phone', '')
            customer_address = customer_data.get('address', '')
            customer_city = customer_data.get('city', '')
            customer_state = customer_data.get('state', '')
            
            # Verificar se já existe loja com esses dados
            loja_existente = None
            if customer_email:
                loja_existente = Loja.objects.filter(email=customer_email).first()
            if not loja_existente and customer_cnpj:
                loja_existente = Loja.objects.filter(cnpj=customer_cnpj).first()
            
            if loja_existente:
                logger.info(f"Loja existente encontrada: {loja_existente.nome}")
                loja = loja_existente
            else:
                # Criar nova loja
                loja = Loja.objects.create(
                    nome=customer_name,
                    email=customer_email,
                    cnpj=customer_cnpj,
                    telefone=customer_phone,
                    endereco=customer_address or 'Endereço não informado',
                    cidade=customer_city or 'Cidade não informada',
                    estado=customer_state or 'Estado não informado',
                    cep='00000000',  # Valor padrão
                    status='ativa'
                )
                logger.info(f"Nova loja criada: {loja.nome} (ID: {loja.id})")
            
            # Verificar se já existe controle financeiro para esta loja
            controle_existente = ControleFinanceiro.objects.filter(loja=loja).first()
            if controle_existente:
                logger.info(f"Controle financeiro existente encontrado: {controle_existente.id}")
                return controle_existente
            
            # Buscar plano financeiro padrão
            plano_padrao = PlanoFinanceiro.objects.filter(nome='Básico').first()
            if not plano_padrao:
                # Criar plano básico se não existir
                plano_padrao = PlanoFinanceiro.objects.create(
                    nome='Básico',
                    descricao='Plano básico para lojas importadas',
                    valor_mensal=29.90,
                    status='ativo'
                )
                logger.info(f"Plano básico criado: {plano_padrao.nome}")
            
            # Criar controle financeiro
            controle_financeiro = ControleFinanceiro.objects.create(
                loja=loja,
                plano=plano_padrao,
                status='ativa',
                valor_mensal=plano_padrao.valor_mensal,
                data_inicio=timezone.now(),
                data_vencimento=timezone.now() + timedelta(days=30)
            )
            
            logger.info(f"Controle financeiro criado: {controle_financeiro.id} para loja {loja.nome}")
            return controle_financeiro
            
        except Exception as e:
            logger.error(f"Erro ao criar loja e controle financeiro: {str(e)}")
            return None
    
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
                                    
                                    # Tentar criar loja e controle financeiro automaticamente para cobrança órfã
                                    customer_id = payment.get('customer')
                                    if customer_id:
                                        try:
                                            # Buscar dados do customer no Asaas
                                            customer_response = requests.get(
                                                f"{self.asaas_service.base_url}/customers/{customer_id}",
                                                headers=self.asaas_service.headers,
                                                timeout=10
                                            )
                                            
                                            if customer_response.status_code == 200:
                                                customer_data = customer_response.json()
                                                logger.info(f"Criando loja e controle financeiro para cobrança órfã {payment['id']}")
                                                controle_criado = self._create_loja_and_controle_from_customer(customer_data, payment)
                                                if controle_criado:
                                                    self._create_charge_from_asaas_data(payment, controle_criado)
                                                    result['new_charges'] += 1
                                                    logger.info(f"Cobrança órfã {payment['id']} associada ao controle criado {controle_criado.id}")
                                                else:
                                                    logger.warning(f"Não foi possível criar controle financeiro para cobrança órfã {payment['id']}")
                                            else:
                                                logger.warning(f"Erro ao buscar customer {customer_id} para cobrança órfã: {customer_response.status_code}")
                                                
                                        except Exception as e:
                                            logger.warning(f"Erro ao processar cobrança órfã {payment['id']}: {str(e)}")
                            
                            else:
                                # Cobrança sem externalReference - tentar associar por dados do customer
                                customer_id = payment.get('customer')
                                if customer_id:
                                    try:
                                        # Buscar dados do customer no Asaas
                                        customer_response = requests.get(
                                            f"{self.asaas_service.base_url}/customers/{customer_id}",
                                            headers=self.asaas_service.headers,
                                            timeout=10
                                        )
                                        
                                        if customer_response.status_code == 200:
                                            customer_data = customer_response.json()
                                            customer_email = customer_data.get('email', '')
                                            customer_cnpj = customer_data.get('cpfCnpj', '')
                                            
                                            # Buscar controle financeiro por email ou CNPJ
                                            controle = None
                                            if customer_email:
                                                controle = ControleFinanceiro.objects.filter(
                                                    loja__email=customer_email
                                                ).first()
                                            
                                            if not controle and customer_cnpj:
                                                controle = ControleFinanceiro.objects.filter(
                                                    loja__cnpj=customer_cnpj
                                                ).first()
                                            
                                            if controle:
                                                # Criar nova cobrança no sistema
                                                self._create_charge_from_asaas_data(payment, controle)
                                                result['new_charges'] += 1
                                                logger.info(f"Cobrança órfã {payment['id']} associada ao controle {controle.id} via {customer_email or customer_cnpj}")
                                            else:
                                                # Tentar criar loja e controle financeiro automaticamente
                                                logger.info(f"Criando loja e controle financeiro para customer {customer_id} - cobrança {payment['id']}")
                                                controle_criado = self._create_loja_and_controle_from_customer(customer_data, payment)
                                                if controle_criado:
                                                    self._create_charge_from_asaas_data(payment, controle_criado)
                                                    result['new_charges'] += 1
                                                    logger.info(f"Cobrança órfã {payment['id']} associada ao controle criado {controle_criado.id}")
                                                else:
                                                    logger.warning(f"Não foi possível criar controle financeiro para customer {customer_id} - cobrança {payment['id']}")
                                        else:
                                            logger.warning(f"Erro ao buscar customer {customer_id}: {customer_response.status_code}")
                                    
                                    except Exception as e:
                                        logger.warning(f"Erro ao associar cobrança órfã {payment['id']}: {str(e)}")
                    
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
                    data_vencimento=datetime.fromisoformat(payment_data['dueDate']).replace(tzinfo=timezone.get_current_timezone()),
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
        """Retorna status atual da sincronização (persistente)"""
        try:
            from .models_sync import SyncStatus
            db_status = SyncStatus.get_current()
            return db_status.to_dict()
        except Exception as e:
            # Fallback para status em memória
            return {
                'is_running': self.is_running,
                'sync_interval': self.sync_interval,
                'last_sync': self.last_sync,
                'stats': self.sync_stats.copy(),
                'thread_alive': False
            }
    
    def force_sync_now(self) -> Dict:
        """Força uma sincronização imediata (versão Heroku otimizada)"""
        logger.info("Iniciando sincronização forçada")
        try:
            from .models_sync import SyncStatus
            
            result = self.sync_all_charges()
            self.last_sync = timezone.now()
            
            # Atualizar estatísticas em memória
            self.sync_stats['total_synced'] += result['total_processed']
            self.sync_stats['updates_found'] += result['updates_made']
            
            if result['errors']:
                self.sync_stats['errors'] += len(result['errors'])
                self.sync_stats['last_error'] = result['errors'][-1] if result['errors'] else None
            
            # Atualizar no banco
            try:
                db_status = SyncStatus.get_current()
                db_status.update_last_sync()
                db_status.update_stats({
                    'total_synced': db_status.stats.get('total_synced', 0) + result['total_processed'],
                    'updates_found': db_status.stats.get('updates_found', 0) + result['updates_made'],
                    'errors': db_status.stats.get('errors', 0) + len(result['errors']),
                    'last_error': result['errors'][-1] if result['errors'] else db_status.stats.get('last_error')
                })
            except Exception as db_error:
                logger.warning(f"Erro ao atualizar banco: {str(db_error)}")
            
            return result
        except Exception as e:
            logger.error(f"Erro na sincronização forçada: {str(e)}")
            self.sync_stats['errors'] += 1
            self.sync_stats['last_error'] = str(e)
            
            # Atualizar erro no banco
            try:
                from .models_sync import SyncStatus
                db_status = SyncStatus.get_current()
                db_status.update_stats({
                    'errors': db_status.stats.get('errors', 0) + 1,
                    'last_error': str(e)
                })
            except:
                pass
            
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


    def _check_deleted_charges(self) -> Dict:
        """Verifica cobranças que foram excluídas no Asaas"""
        result = {
            'deleted_found': 0,
            'deleted_removed': 0,
            'errors': []
        }
        
        try:
            # Buscar cobranças locais dos últimos 30 dias
            data_limite = timezone.now() - timedelta(days=30)
            cobrancas_locais = CobrancaAsaas.objects.filter(
                data_criacao__gte=data_limite
            ).exclude(
                status__in=['RECEIVED', 'CONFIRMED', 'REFUNDED']
            )
            
            logger.info(f"Verificando {len(cobrancas_locais)} cobranças locais para exclusões...")
            
            for cobranca in cobrancas_locais:
                try:
                    # Tentar consultar a cobrança no Asaas
                    response = requests.get(
                        f"{self.asaas_service.base_url}/payments/{cobranca.asaas_id}",
                        headers=self.asaas_service.headers,
                        timeout=10
                    )
                    
                    if response.status_code == 404:
                        # Cobrança foi excluída do Asaas
                        logger.warning(f"Cobrança {cobranca.asaas_id} foi excluída do Asaas")
                        result['deleted_found'] += 1
                        
                        # Adicionar observação e excluir
                        cobranca.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: Cobrança excluída do Asaas - removida automaticamente"
                        cobranca.save()
                        cobranca.delete()
                        
                        result['deleted_removed'] += 1
                        logger.info(f"Cobrança {cobranca.asaas_id} removida do sistema local")
                        
                    elif response.status_code == 401:
                        logger.error("Erro de autenticação - verificar API key")
                        break
                        
                except requests.exceptions.ConnectionError as e:
                    if "Connection refused" in str(e):
                        logger.warning("Connection refused - parando verificação de exclusões")
                        break
                    else:
                        logger.warning(f"Erro de conexão para {cobranca.asaas_id}: {str(e)}")
                        result['errors'].append(f"Conexão falhou para {cobranca.asaas_id}")
                        
                except Exception as e:
                    logger.warning(f"Erro ao verificar cobrança {cobranca.asaas_id}: {str(e)}")
                    result['errors'].append(f"Erro em {cobranca.asaas_id}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Erro ao verificar cobranças excluídas: {str(e)}")
            result['errors'].append(f"Erro geral: {str(e)}")
        
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