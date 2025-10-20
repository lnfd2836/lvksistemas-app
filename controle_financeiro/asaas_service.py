"""
Serviço de integração com a API do Asaas para geração de boletos com PIX
Documentação: https://docs.asaas.com/docs/guia-de-cobrancas
"""

import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AsaasService:
    """Serviço para integração com a API do Asaas"""
    
    def __init__(self):
        # Configurações da conta Asaas
        self.api_key = getattr(settings, 'ASAAS_API_KEY', None)
        self.environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')  # sandbox ou production
        
        # URLs da API
        if self.environment == 'production':
            self.base_url = 'https://www.asaas.com/api/v3'
        else:
            self.base_url = 'https://sandbox.asaas.com/api/v3'
        
        # Headers padrão - Formato correto conforme documentação Asaas
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LVK Sistemas - Sistema de Gestão'
        }
        
        # Dados da conta Asaas (configuração padrão)
        self.conta_dados = {
            'banco': '461',  # Asaas I.P S.A
            'agencia': '0001',
            'conta': 'Configurada automaticamente pelo Asaas',
            'tipo_conta': 'Conta de Pagamento Digital',
            'nome_completo': 'Configurado no painel do Asaas',
            'cnpj': 'Configurado no painel do Asaas'
        }
    
    def validar_configuracao(self):
        """Valida se a configuração da API está correta"""
        if not self.api_key:
            raise ValueError("ASAAS_API_KEY não configurada nas settings")
        
        try:
            # Testar conexão com a API
            response = requests.get(
                f"{self.base_url}/myAccount",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                account_data = response.json()
                logger.info(f"Conexão com Asaas estabelecida. Conta: {account_data.get('name', 'N/A')}")
                return True
            else:
                logger.error(f"Erro na validação da API Asaas: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao conectar com a API Asaas: {str(e)}")
            return False
    
    def criar_cliente(self, controle_financeiro):
        """
        Cria ou atualiza cliente no Asaas
        
        Args:
            controle_financeiro: Instância do ControleFinanceiro
            
        Returns:
            dict: Dados do cliente criado/atualizado
        """
        loja = controle_financeiro.loja
        
        # Dados do cliente (loja)
        cliente_data = {
            'name': loja.nome,
            'email': loja.email,
            'phone': self._limpar_telefone(loja.telefone),
            'mobilePhone': self._limpar_telefone(loja.telefone),
            'cpfCnpj': self._limpar_cnpj(loja.cnpj),
            'postalCode': self._limpar_cep(loja.cep),
            'address': loja.endereco,
            'addressNumber': self._extrair_numero_endereco(loja.endereco),
            'complement': '',
            'province': loja.cidade,
            'city': loja.cidade,
            'state': loja.estado,
            'country': 'Brasil',
            'externalReference': str(loja.id),  # Referência externa para identificar
            'notificationDisabled': False,
            'additionalEmails': '',
            'municipalInscription': '',
            'stateInscription': '',
            'observations': f'Cliente criado automaticamente - Sistema LVK - Loja ID: {loja.id}'
        }
        
        try:
            # Verificar se cliente já existe
            cliente_existente = self._buscar_cliente_por_referencia(str(loja.id))
            
            if cliente_existente:
                # Atualizar cliente existente
                response = requests.put(
                    f"{self.base_url}/customers/{cliente_existente['id']}",
                    headers=self.headers,
                    json=cliente_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"Cliente atualizado no Asaas: {loja.nome}")
                    return response.json()
                else:
                    logger.error(f"Erro ao atualizar cliente no Asaas: {response.status_code} - {response.text}")
                    return None
            else:
                # Criar novo cliente
                response = requests.post(
                    f"{self.base_url}/customers",
                    headers=self.headers,
                    json=cliente_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"Cliente criado no Asaas: {loja.nome}")
                    return response.json()
                else:
                    logger.error(f"Erro ao criar cliente no Asaas: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao processar cliente no Asaas: {str(e)}")
            return None
    
    def gerar_cobranca_com_pix(self, controle_financeiro, dias_vencimento=30, descricao=None):
        """
        Gera cobrança no Asaas com boleto e PIX
        
        Args:
            controle_financeiro: Instância do ControleFinanceiro
            dias_vencimento: Dias para vencimento (padrão 30)
            descricao: Descrição personalizada da cobrança
            
        Returns:
            dict: Dados da cobrança criada
        """
        
        # Validar configuração
        if not self.validar_configuracao():
            raise ValueError("Configuração da API Asaas inválida")
        
        # Criar/atualizar cliente
        cliente = self.criar_cliente(controle_financeiro)
        if not cliente:
            raise ValueError("Erro ao criar/atualizar cliente no Asaas")
        
        # Calcular data de vencimento
        data_vencimento = timezone.now().date() + timedelta(days=dias_vencimento)
        
        # Preparar descrição
        if not descricao:
            descricao = f"Mensalidade {controle_financeiro.plano.nome} - {controle_financeiro.loja.nome}"
        
        # Dados da cobrança
        cobranca_data = {
            'customer': cliente['id'],
            'billingType': 'BOLETO',  # Tipo de cobrança: boleto
            'value': float(controle_financeiro.valor_mensal),
            'dueDate': data_vencimento.strftime('%Y-%m-%d'),
            'description': descricao,
            'externalReference': f"CF_{controle_financeiro.id}_{int(timezone.now().timestamp())}",
            
            # Configurações do boleto
            'installmentCount': 1,
            'installmentValue': float(controle_financeiro.valor_mensal),
            
            # Multa e juros
            'fine': {
                'value': 2.00,  # 2% de multa
                'type': 'PERCENTAGE'
            },
            'interest': {
                'value': 1.00,  # 1% ao mês de juros
                'type': 'PERCENTAGE'
            },
            
            # Desconto (se aplicável)
            'discount': {
                'value': 0.00,
                'dueDateLimitDays': 0,
                'type': 'PERCENTAGE'
            },
            
            # Configurações de notificação
            'postalService': False,  # Não enviar pelos correios
            
            # Callback/Webhook
            'callback': {
                'successUrl': f"{getattr(settings, 'SITE_URL', '')}/financeiro/asaas/callback/success/",
                'autoRedirect': True
            }
        }
        
        try:
            # Criar cobrança
            response = requests.post(
                f"{self.base_url}/payments",
                headers=self.headers,
                json=cobranca_data,
                timeout=30
            )
            
            if response.status_code == 200:
                cobranca = response.json()
                logger.info(f"Cobrança criada no Asaas: {cobranca['id']}")
                
                # Gerar PIX para a cobrança
                pix_data = self._gerar_pix_cobranca(cobranca['id'])
                
                # Combinar dados da cobrança com PIX
                resultado = {
                    'cobranca': cobranca,
                    'pix': pix_data,
                    'cliente': cliente,
                    'success': True
                }
                
                return resultado
                
            else:
                logger.error(f"Erro ao criar cobrança no Asaas: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Erro na API: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar cobrança no Asaas: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _gerar_pix_cobranca(self, payment_id):
        """
        Gera PIX para uma cobrança específica
        
        Args:
            payment_id: ID da cobrança no Asaas
            
        Returns:
            dict: Dados do PIX gerado
        """
        try:
            # Gerar QR Code PIX
            response = requests.get(
                f"{self.base_url}/payments/{payment_id}/pixQrCode",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                pix_data = response.json()
                logger.info(f"PIX gerado para cobrança {payment_id}")
                return pix_data
            else:
                logger.error(f"Erro ao gerar PIX: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar PIX: {str(e)}")
            return None
    
    def consultar_cobranca(self, payment_id):
        """
        Consulta status de uma cobrança
        
        Args:
            payment_id: ID da cobrança no Asaas
            
        Returns:
            dict: Dados atualizados da cobrança
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
                logger.error(f"Erro ao consultar cobrança: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao consultar cobrança: {str(e)}")
            return None
    
    def processar_webhook(self, webhook_data):
        """
        Processa webhook recebido do Asaas
        
        Args:
            webhook_data: Dados do webhook
            
        Returns:
            dict: Resultado do processamento
        """
        try:
            event = webhook_data.get('event')
            payment = webhook_data.get('payment', {})
            payment_id = payment.get('id')
            
            if not payment_id:
                return {'success': False, 'error': 'Payment ID não encontrado'}
            
            # Consultar dados completos da cobrança
            cobranca_completa = self.consultar_cobranca(payment_id)
            
            if not cobranca_completa:
                return {'success': False, 'error': 'Erro ao consultar cobrança'}
            
            # Processar diferentes tipos de eventos
            if event == 'PAYMENT_RECEIVED':
                return self._processar_pagamento_recebido(cobranca_completa)
            elif event == 'PAYMENT_OVERDUE':
                return self._processar_pagamento_vencido(cobranca_completa)
            elif event == 'PAYMENT_DELETED':
                return self._processar_pagamento_cancelado(cobranca_completa)
            else:
                logger.info(f"Evento não processado: {event}")
                return {'success': True, 'message': f'Evento {event} registrado'}
                
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _processar_pagamento_recebido(self, cobranca):
        """Processa pagamento recebido"""
        try:
            # Buscar controle financeiro pela referência externa
            external_ref = cobranca.get('externalReference', '')
            if external_ref.startswith('CF_'):
                cf_id = external_ref.split('_')[1]
                
                from .models import ControleFinanceiro
                controle = ControleFinanceiro.objects.get(id=cf_id)
                
                # Processar pagamento
                valor_pago = Decimal(str(cobranca.get('value', 0)))
                controle.processar_pagamento(
                    valor_pago,
                    f"Pagamento via Asaas - ID: {cobranca['id']}"
                )
                
                logger.info(f"Pagamento processado: {controle.loja.nome} - R$ {valor_pago}")
                return {'success': True, 'message': 'Pagamento processado com sucesso'}
            
            return {'success': False, 'error': 'Referência externa inválida'}
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento recebido: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _processar_pagamento_vencido(self, cobranca):
        """Processa pagamento vencido"""
        # Implementar lógica para pagamentos vencidos
        logger.info(f"Pagamento vencido: {cobranca['id']}")
        return {'success': True, 'message': 'Pagamento vencido registrado'}
    
    def _processar_pagamento_cancelado(self, cobranca):
        """Processa pagamento cancelado"""
        # Implementar lógica para pagamentos cancelados
        logger.info(f"Pagamento cancelado: {cobranca['id']}")
        return {'success': True, 'message': 'Pagamento cancelado registrado'}
    
    def _buscar_cliente_por_referencia(self, external_reference):
        """Busca cliente pela referência externa"""
        try:
            response = requests.get(
                f"{self.base_url}/customers",
                headers=self.headers,
                params={'externalReference': external_reference},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    return data['data'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente: {str(e)}")
            return None
    
    def _limpar_telefone(self, telefone):
        """Remove formatação do telefone"""
        if not telefone:
            return ''
        import re
        return re.sub(r'[^0-9]', '', str(telefone))
    
    def _limpar_cnpj(self, cnpj):
        """Remove formatação do CNPJ"""
        if not cnpj:
            return ''
        import re
        return re.sub(r'[^0-9]', '', str(cnpj))
    
    def _limpar_cep(self, cep):
        """Remove formatação do CEP"""
        if not cep:
            return ''
        import re
        return re.sub(r'[^0-9]', '', str(cep))
    
    def _extrair_numero_endereco(self, endereco):
        """Extrai número do endereço"""
        if not endereco:
            return ''
        import re
        numeros = re.findall(r'\d+', endereco)
        return numeros[0] if numeros else 'S/N'