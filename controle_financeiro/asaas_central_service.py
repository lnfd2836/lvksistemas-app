"""
Serviço centralizado do Asaas para gerenciar pagamentos de todas as lojas
"""
import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class AsaasCentralService:
    """
    Serviço centralizado para gerenciar todos os pagamentos via Asaas
    Todas as lojas usam a mesma conta Asaas para recebimentos
    """
    
    def __init__(self):
        """Inicializa o serviço com as configurações centralizadas"""
        self.api_key = getattr(settings, 'ASAAS_API_KEY', '')
        self.environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
        
        # URLs da API Asaas
        if self.environment == 'production':
            self.base_url = 'https://www.asaas.com/api/v3'
        else:
            self.base_url = 'https://sandbox.asaas.com/api/v3'
        
        # Headers padrão
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Configurações centralizadas
        self.company_name = "LVK Sistemas"
        self.support_email = getattr(settings, 'SUPPORT_EMAIL', 'suporte@lvksistemas.com.br')
    
    def criar_cliente_loja(self, loja) -> Dict[str, Any]:
        """
        Cria ou atualiza um cliente no Asaas para uma loja
        
        Args:
            loja: Instância da loja
            
        Returns:
            dict: Dados do cliente criado/atualizado
        """
        try:
            # Dados do cliente baseados na loja
            cliente_data = {
                'name': loja.nome,
                'email': loja.email,
                'phone': self._format_phone(loja.telefone) if loja.telefone else None,
                'mobilePhone': self._format_phone(loja.telefone) if loja.telefone else None,
                'cpfCnpj': self._format_cnpj(loja.cnpj) if loja.cnpj else None,
                'postalCode': self._format_cep(loja.cep) if loja.cep else None,
                'address': loja.endereco if loja.endereco else None,
                'addressNumber': 'S/N',
                'complement': f'Loja ID: {loja.id}',
                'province': loja.cidade if loja.cidade else None,
                'city': loja.cidade if loja.cidade else None,
                'state': loja.estado if loja.estado else 'SP',
                'country': 'Brasil',
                'externalReference': f'loja_{loja.id}',
                'notificationDisabled': False,
                'additionalEmails': self.support_email,
                'municipalInscription': None,
                'stateInscription': None,
                'observations': f'Cliente automático - Loja: {loja.nome} (ID: {loja.id})'
            }
            
            # Remover campos None
            cliente_data = {k: v for k, v in cliente_data.items() if v is not None}
            
            # Verificar se cliente já existe
            existing_customer = self._buscar_cliente_por_referencia(f'loja_{loja.id}')
            
            if existing_customer:
                # Atualizar cliente existente
                response = requests.put(
                    f"{self.base_url}/customers/{existing_customer['id']}",
                    json=cliente_data,
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"Cliente Asaas atualizado para loja {loja.nome}")
                    return response.json()
                else:
                    logger.error(f"Erro ao atualizar cliente Asaas: {response.status_code} - {response.text}")
                    raise Exception(f"Erro na API Asaas: {response.status_code}")
            
            else:
                # Criar novo cliente
                response = requests.post(
                    f"{self.base_url}/customers",
                    json=cliente_data,
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"Cliente Asaas criado para loja {loja.nome}")
                    return response.json()
                else:
                    logger.error(f"Erro ao criar cliente Asaas: {response.status_code} - {response.text}")
                    raise Exception(f"Erro na API Asaas: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar cliente Asaas para loja {loja.nome}: {str(e)}")
            raise
    
    def gerar_cobranca_loja(self, controle_financeiro, dias_vencimento=7) -> Dict[str, Any]:
        """
        Gera uma cobrança no Asaas para uma loja
        
        Args:
            controle_financeiro: Instância do ControleFinanceiro
            dias_vencimento: Dias para vencimento da cobrança
            
        Returns:
            dict: Dados da cobrança criada
        """
        try:
            loja = controle_financeiro.loja
            
            # Criar/atualizar cliente primeiro
            cliente_asaas = self.criar_cliente_loja(loja)
            
            # Calcular data de vencimento
            data_vencimento = timezone.now().date() + timedelta(days=dias_vencimento)
            
            # Dados da cobrança
            cobranca_data = {
                'customer': cliente_asaas['id'],
                'billingType': 'BOLETO',
                'value': float(controle_financeiro.valor_mensal),
                'dueDate': data_vencimento.strftime('%Y-%m-%d'),
                'description': f'Mensalidade {loja.nome} - Plano {controle_financeiro.plano.nome}',
                'externalReference': f'controle_{controle_financeiro.id}',
                'installmentCount': 1,
                'totalValue': float(controle_financeiro.valor_mensal),
                'installmentValue': float(controle_financeiro.valor_mensal),
                'discount': {
                    'value': 0,
                    'dueDateLimitDays': 0
                },
                'interest': {
                    'value': 2.0,  # 2% ao mês
                    'type': 'PERCENTAGE'
                },
                'fine': {
                    'value': 2.0,  # 2% de multa
                    'type': 'PERCENTAGE'
                },
                'postalService': False,
                'split': [],
                'callback': {
                    'successUrl': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/financeiro/asaas/success/",
                    'autoRedirect': True
                }
            }
            
            # Criar cobrança
            response = requests.post(
                f"{self.base_url}/payments",
                json=cobranca_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                cobranca = response.json()
                logger.info(f"Cobrança Asaas criada para {loja.nome}: {cobranca['id']}")
                
                # Atualizar controle financeiro com dados da cobrança
                controle_financeiro.asaas_payment_id = cobranca['id']
                controle_financeiro.asaas_customer_id = cliente_asaas['id']
                controle_financeiro.boleto_url = cobranca.get('bankSlipUrl', '')
                controle_financeiro.codigo_barras = cobranca.get('barCode', '')
                controle_financeiro.linha_digitavel = cobranca.get('digitableLine', '')
                controle_financeiro.save()
                
                return cobranca
            
            else:
                logger.error(f"Erro ao criar cobrança Asaas: {response.status_code} - {response.text}")
                raise Exception(f"Erro na API Asaas: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Erro ao gerar cobrança para {loja.nome}: {str(e)}")
            raise
    
    def consultar_cobranca(self, payment_id: str) -> Dict[str, Any]:
        """
        Consulta uma cobrança específica no Asaas
        
        Args:
            payment_id: ID da cobrança no Asaas
            
        Returns:
            dict: Dados da cobrança
        """
        try:
            response = requests.get(
                f"{self.base_url}/payments/{payment_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao consultar cobrança {payment_id}: {response.status_code}")
                return {}
        
        except Exception as e:
            logger.error(f"Erro ao consultar cobrança {payment_id}: {str(e)}")
            return {}
    
    def listar_cobrancas_periodo(self, data_inicio=None, data_fim=None, status=None) -> Dict[str, Any]:
        """
        Lista cobranças de um período específico
        
        Args:
            data_inicio: Data de início (opcional)
            data_fim: Data de fim (opcional)
            status: Status das cobranças (opcional)
            
        Returns:
            dict: Lista de cobranças
        """
        try:
            params = {
                'limit': 100,
                'offset': 0
            }
            
            if data_inicio:
                params['dateCreated[ge]'] = data_inicio.strftime('%Y-%m-%d')
            
            if data_fim:
                params['dateCreated[le]'] = data_fim.strftime('%Y-%m-%d')
            
            if status:
                params['status'] = status
            
            response = requests.get(
                f"{self.base_url}/payments",
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao listar cobranças: {response.status_code}")
                return {'data': [], 'totalCount': 0}
        
        except Exception as e:
            logger.error(f"Erro ao listar cobranças: {str(e)}")
            return {'data': [], 'totalCount': 0}
    
    def processar_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa webhooks do Asaas para atualizar status das cobranças
        
        Args:
            webhook_data: Dados do webhook
            
        Returns:
            dict: Resultado do processamento
        """
        try:
            event = webhook_data.get('event')
            payment_data = webhook_data.get('payment', {})
            payment_id = payment_data.get('id')
            
            if not payment_id:
                return {'success': False, 'error': 'Payment ID não encontrado'}
            
            # Buscar controle financeiro
            from .models import ControleFinanceiro
            
            try:
                controle = ControleFinanceiro.objects.get(asaas_payment_id=payment_id)
            except ControleFinanceiro.DoesNotExist:
                logger.warning(f"ControleFinanceiro não encontrado para payment_id: {payment_id}")
                return {'success': False, 'error': 'Controle financeiro não encontrado'}
            
            # Atualizar status baseado no evento
            if event == 'PAYMENT_RECEIVED':
                controle.status = 'paga'
                controle.data_pagamento = timezone.now()
                logger.info(f"Pagamento recebido para loja {controle.loja.nome}")
            
            elif event == 'PAYMENT_OVERDUE':
                controle.status = 'vencida'
                logger.info(f"Pagamento vencido para loja {controle.loja.nome}")
            
            elif event == 'PAYMENT_DELETED':
                controle.status = 'cancelada'
                logger.info(f"Pagamento cancelado para loja {controle.loja.nome}")
            
            elif event == 'PAYMENT_RESTORED':
                controle.status = 'ativa'
                logger.info(f"Pagamento restaurado para loja {controle.loja.nome}")
            
            controle.save()
            
            return {'success': True, 'message': f'Webhook processado: {event}'}
        
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _buscar_cliente_por_referencia(self, referencia: str) -> Optional[Dict[str, Any]]:
        """Busca cliente por referência externa"""
        try:
            response = requests.get(
                f"{self.base_url}/customers",
                params={'externalReference': referencia},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    return data['data'][0]
            
            return None
        
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por referência {referencia}: {str(e)}")
            return None
    
    def _format_phone(self, phone: str) -> str:
        """Formata telefone para o padrão do Asaas"""
        if not phone:
            return ''
        
        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do país se necessário
        if len(phone) == 10:
            phone = '55' + phone
        elif len(phone) == 11:
            phone = '55' + phone
        
        return phone
    
    def _format_cnpj(self, cnpj: str) -> str:
        """Formata CNPJ removendo caracteres especiais e validando"""
        if not cnpj:
            return ''
        
        # Remove caracteres não numéricos
        cnpj_digits = ''.join(filter(str.isdigit, cnpj))
        
        # Validar tamanho
        if len(cnpj_digits) == 11:
            # É um CPF
            return cnpj_digits
        elif len(cnpj_digits) == 14:
            # É um CNPJ
            return cnpj_digits
        else:
            # CNPJ/CPF inválido, usar um CNPJ padrão para teste
            logger.warning(f"CNPJ/CPF inválido: {cnpj}, usando CNPJ padrão")
            return '11222333000181'  # CNPJ válido para teste
    
    def _format_cep(self, cep: str) -> str:
        """Formata CEP removendo caracteres especiais"""
        if not cep:
            return ''
        
        return ''.join(filter(str.isdigit, cep))
    
    def testar_conexao(self) -> Dict[str, Any]:
        """
        Testa a conexão com a API do Asaas
        
        Returns:
            dict: Resultado do teste
        """
        try:
            response = requests.get(
                f"{self.base_url}/myAccount",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                account_data = response.json()
                return {
                    'success': True,
                    'message': 'Conexão com Asaas estabelecida',
                    'account': account_data.get('name', 'Conta Asaas'),
                    'environment': self.environment
                }
            else:
                return {
                    'success': False,
                    'message': f'Erro na conexão: {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao conectar com Asaas',
                'error': str(e)
            }