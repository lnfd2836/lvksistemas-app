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
        
        # Formato alternativo para teste (alguns endpoints podem usar Authorization)
        self.headers_alt = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'LVK Sistemas - Sistema de Gestão'
        }
        
        # Dados da conta Asaas (dados reais da conta)
        self.conta_dados = {
            'banco': '461',  # Asaas I.P S.A
            'agencia': '0001',
            'conta': '194116-2',
            'tipo_conta': 'Conta de Pagamento',
            'nome_completo': 'FELIX REPRESENTACOES E COMERCIO LTDA',
            'cnpj': '41.449.198/0001-72',
            'wallet_id': '5193cd6d-899f-4219-b45a-a8a2012eae05',
            'chave_pix': '0be79c1f-73f8-41d9-a795-3401856ce31b'
        }
    
    def validar_configuracao(self):
        """Valida se a configuração da API está correta"""
        if not self.api_key:
            raise ValueError("ASAAS_API_KEY não configurada nas settings")
        
        try:
            # Testar primeiro formato de header (access_token)
            response = requests.get(
                f"{self.base_url}/myAccount",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                account_data = response.json()
                logger.info(f"Conexão com Asaas estabelecida (access_token). Conta: {account_data.get('name', 'N/A')}")
                return True
            
            # Se falhou, testar formato alternativo (Authorization Bearer)
            logger.info("Testando formato alternativo de header (Authorization Bearer)")
            response = requests.get(
                f"{self.base_url}/myAccount",
                headers=self.headers_alt,
                timeout=30
            )
            
            if response.status_code == 200:
                account_data = response.json()
                logger.info(f"Conexão com Asaas estabelecida (Bearer). Conta: {account_data.get('name', 'N/A')}")
                # Usar headers alternativos daqui em diante
                self.headers = self.headers_alt
                return True
            else:
                logger.error(f"Erro na validação da API Asaas (ambos formatos): {response.status_code} - {response.text}")
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
            logger.info(f"Iniciando processamento do webhook: {webhook_data}")
            
            event = webhook_data.get('event')
            payment = webhook_data.get('payment', {})
            payment_id = payment.get('id')
            
            logger.info(f"Event: {event}, Payment ID: {payment_id}")
            
            if not payment_id:
                logger.error("Payment ID não encontrado no webhook")
                return {'success': False, 'error': 'Payment ID não encontrado'}
            
            # Para eventos de criação, usar dados do próprio webhook
            if event in ['PAYMENT_CREATED', 'PAYMENT_RECEIVED']:
                logger.info(f"Processando evento {event} com dados do webhook")
                
                # Processar diferentes tipos de eventos
                if event == 'PAYMENT_RECEIVED':
                    return self._processar_pagamento_recebido(payment)
                elif event == 'PAYMENT_CREATED':
                    logger.info(f"Pagamento criado: {payment_id}")
                    return {'success': True, 'message': f'Pagamento {payment_id} criado'}
                    
            # Para outros eventos, consultar dados completos
            else:
                logger.info(f"Consultando dados completos para evento {event}")
                cobranca_completa = self.consultar_cobranca(payment_id)
                
                if not cobranca_completa:
                    logger.warning(f"Não foi possível consultar cobrança {payment_id}, usando dados do webhook")
                    cobranca_completa = payment
                
                # Processar diferentes tipos de eventos
                if event == 'PAYMENT_OVERDUE':
                    return self._processar_pagamento_vencido(cobranca_completa)
                elif event == 'PAYMENT_DELETED':
                    return self._processar_pagamento_cancelado(cobranca_completa)
            
            # Evento não específico - apenas registrar
            logger.info(f"Evento {event} registrado mas não processado especificamente")
            return {'success': True, 'message': f'Evento {event} registrado'}
                
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}
    
    def _processar_pagamento_recebido(self, cobranca):
        """Processa pagamento recebido"""
        try:
            logger.info(f"Processando pagamento recebido: {cobranca}")
            
            payment_id = cobranca.get('id')
            valor_pago = Decimal(str(cobranca.get('value', 0)))
            
            # Tentar buscar pela CobrancaAsaas primeiro
            try:
                from .models import CobrancaAsaas
                cobranca_asaas = CobrancaAsaas.objects.get(asaas_id=payment_id)
                
                # Marcar como paga
                cobranca_asaas.marcar_como_paga()
                
                logger.info(f"Pagamento processado via CobrancaAsaas: {cobranca_asaas.controle_financeiro.loja.nome} - R$ {valor_pago}")
                return {'success': True, 'message': 'Pagamento processado via CobrancaAsaas'}
                
            except CobrancaAsaas.DoesNotExist:
                logger.info(f"CobrancaAsaas não encontrada para {payment_id}, tentando por referência externa")
            
            # Fallback: buscar por referência externa
            external_ref = cobranca.get('externalReference', '')
            logger.info(f"Referência externa: {external_ref}")
            
            if external_ref and external_ref.startswith('CF_'):
                cf_id = external_ref.split('_')[1]
                logger.info(f"Extraído CF ID: {cf_id}")
                
                from .models import ControleFinanceiro
                controle = ControleFinanceiro.objects.get(id=cf_id)
                
                # Processar pagamento
                controle.processar_pagamento(
                    valor_pago,
                    f"Pagamento via Asaas - ID: {payment_id}"
                )
                
                logger.info(f"Pagamento processado via referência externa: {controle.loja.nome} - R$ {valor_pago}")
                return {'success': True, 'message': 'Pagamento processado via referência externa'}
            
            # Se não encontrou nenhuma forma de processar
            logger.warning(f"Não foi possível processar pagamento {payment_id} - sem referência válida")
            return {'success': True, 'message': f'Pagamento {payment_id} registrado mas não processado (sem referência)'}
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento recebido: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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