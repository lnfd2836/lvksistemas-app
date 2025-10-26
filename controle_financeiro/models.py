from django.db import models
from django.utils import timezone
from datetime import timedelta
from lojas.models import Loja
from django.contrib.auth.models import User
import uuid


class PlanoFinanceiro(models.Model):
    """Planos financeiros disponíveis para as lojas"""
    nome = models.CharField(max_length=100, verbose_name="Nome do Plano")
    descricao = models.TextField(verbose_name="Descrição")
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Mensal")
    dias_trial = models.IntegerField(default=30, verbose_name="Dias de Teste Grátis")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Plano Financeiro"
        verbose_name_plural = "Planos Financeiros"
        ordering = ['valor_mensal']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor_mensal}"


class ConfiguracaoBoleto(models.Model):
    """Configurações para geração de boletos"""
    nome_banco = models.CharField(max_length=100, verbose_name="Nome do Banco")
    codigo_banco = models.CharField(max_length=10, verbose_name="Código do Banco")
    agencia = models.CharField(max_length=10, verbose_name="Agência")
    conta = models.CharField(max_length=20, verbose_name="Conta")
    carteira = models.CharField(max_length=10, verbose_name="Carteira")
    codigo_cedente = models.CharField(max_length=20, verbose_name="Código do Cedente", help_text="Código do cedente/beneficiário no banco", blank=True, null=True)
    convenio = models.CharField(max_length=20, verbose_name="Número do Convênio", help_text="Número do convênio com o banco", blank=True, null=True)
    
    # Dados do beneficiário
    nome_beneficiario = models.CharField(max_length=200, verbose_name="Nome do Beneficiário")
    cnpj_beneficiario = models.CharField(max_length=20, verbose_name="CNPJ do Beneficiário")
    endereco_beneficiario = models.TextField(verbose_name="Endereço do Beneficiário")
    
    # Configurações
    instrucoes = models.TextField(blank=True, verbose_name="Instruções do Boleto")
    multa = models.DecimalField(max_digits=5, decimal_places=2, default=2.00, verbose_name="Multa (%)")
    juros = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name="Juros ao Mês (%)")
    desconto = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Desconto (%)")
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Boleto"
        verbose_name_plural = "Configurações de Boletos"
    
    def __str__(self):
        return f"{self.nome_banco} - {self.nome_beneficiario}"


class BoletoGerado(models.Model):
    """Boletos gerados para as lojas"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    controle_financeiro = models.ForeignKey('ControleFinanceiro', on_delete=models.CASCADE, verbose_name="Controle Financeiro")
    configuracao = models.ForeignKey(ConfiguracaoBoleto, on_delete=models.CASCADE, verbose_name="Configuração")
    
    # Dados do boleto
    numero_boleto = models.CharField(max_length=50, verbose_name="Número do Boleto")
    linha_digitavel = models.CharField(max_length=54, verbose_name="Linha Digitável")
    codigo_barras = models.CharField(max_length=44, verbose_name="Código de Barras")
    
    # Valores
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data_vencimento = models.DateTimeField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Pagamento")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    
    # Metadados
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Boleto Gerado"
        verbose_name_plural = "Boletos Gerados"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Boleto {self.numero_boleto} - {self.controle_financeiro.loja.nome}"
    
    @property
    def dias_para_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        if self.data_vencimento:
            delta = self.data_vencimento - timezone.now()
            return delta.days
        return 0
    
    def validar_e_corrigir_codigo(self):
        """Valida e corrige automaticamente o código de barras/linha digitável"""
        try:
            from .boleto_simple_corrector import BoletoSimpleCorrector
            
            corrector = BoletoSimpleCorrector()
            
            # Tentar corrigir linha digitável se existir
            if self.linha_digitavel:
                result = corrector.correct_single_dv_error(self.linha_digitavel)
                
                if result['success'] and result.get('corrections'):
                    # Código foi corrigido
                    self.linha_digitavel = result['corrected_code']
                    
                    # Log da correção
                    corrections_info = []
                    for correction in result['corrections']:
                        corrections_info.append(f"Campo {correction['campo']}: DV {correction['dv_original']} → {correction['dv_correto']}")
                    
                    correction_log = f"Correção automática aplicada: {', '.join(corrections_info)}"
                    
                    if self.observacoes:
                        self.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: {correction_log}"
                    else:
                        self.observacoes = f"{timezone.now().strftime('%d/%m/%Y %H:%M')}: {correction_log}"
                    
                    return {
                        'corrected': True,
                        'message': correction_log,
                        'corrections': result['corrections']
                    }
            
            return {
                'corrected': False,
                'message': 'Código já está válido ou não precisa de correção'
            }
            
        except Exception as e:
            return {
                'corrected': False,
                'message': f'Erro na validação: {str(e)}'
            }
    
    def save(self, *args, **kwargs):
        """Override do save para aplicar correção automática"""
        # TEMPORARIAMENTE DESABILITADO: Correção automática estava removendo formatação da linha digitável
        # TODO: Corrigir o BoletoSimpleCorrector para preservar formatação
        
        # # Se é um novo boleto ou a linha digitável foi alterada, validar e corrigir
        # if not self.pk or 'linha_digitavel' in kwargs.get('update_fields', []):
        #     correction_result = self.validar_e_corrigir_codigo()
        #     
        #     # Se houve correção, não salvar ainda para evitar loop
        #     if correction_result['corrected']:
        #         # Salvar sem chamar validação novamente
        #         super().save(*args, **kwargs)
        #         return
        
        super().save(*args, **kwargs)
    
    def marcar_como_pago(self):
        """Marca o boleto como pago"""
        self.status = 'pago'
        self.data_pagamento = timezone.now()
        self.save()
        
        # Processa o pagamento no controle financeiro
        self.controle_financeiro.processar_pagamento(
            self.valor, 
            f"Pagamento via boleto {self.numero_boleto}"
        )


class ControleFinanceiro(models.Model):
    """Controle financeiro de cada loja"""
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('vencida', 'Vencida'),
        ('bloqueada', 'Bloqueada'),
        ('suspensa', 'Suspensa'),
    ]
    
    loja = models.OneToOneField(Loja, on_delete=models.CASCADE, verbose_name="Loja")
    plano = models.ForeignKey(PlanoFinanceiro, on_delete=models.CASCADE, verbose_name="Plano")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa', verbose_name="Status")
    
    # Datas importantes
    data_inicio = models.DateTimeField(default=timezone.now, verbose_name="Data de Início")
    data_vencimento = models.DateTimeField(verbose_name="Data de Vencimento")
    data_bloqueio = models.DateTimeField(null=True, blank=True, verbose_name="Data de Bloqueio")
    data_ultimo_pagamento = models.DateTimeField(null=True, blank=True, verbose_name="Último Pagamento")
    
    # Valores
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Mensal")
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Pago")
    valor_pendente = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Pendente")
    
    # Controle de acesso
    dias_grace_period = models.IntegerField(default=5, verbose_name="Dias de Tolerância")
    bloqueada = models.BooleanField(default=False, verbose_name="Bloqueada")
    motivo_bloqueio = models.TextField(blank=True, verbose_name="Motivo do Bloqueio")
    
    # Metadados
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Controle Financeiro"
        verbose_name_plural = "Controles Financeiros"
        ordering = ['-data_vencimento']
    
    def __str__(self):
        return f"{self.loja.nome} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Calcula data de vencimento baseada no plano
        if not self.data_vencimento:
            if self.plano.dias_trial > 0:
                self.data_vencimento = self.data_inicio + timedelta(days=self.plano.dias_trial)
            else:
                self.data_vencimento = self.data_inicio + timedelta(days=30)
        
        # Define valor mensal baseado no plano
        if not self.valor_mensal:
            self.valor_mensal = self.plano.valor_mensal
        
        super().save(*args, **kwargs)
    
    def verificar_status(self):
        """Verifica e atualiza o status financeiro da loja"""
        agora = timezone.now()
        
        if self.data_vencimento <= agora:
            # Verifica se está no período de tolerância
            if self.data_bloqueio is None:
                self.data_bloqueio = self.data_vencimento + timedelta(days=self.dias_grace_period)
            
            if agora <= self.data_bloqueio:
                self.status = 'vencida'
                self.bloqueada = False
            else:
                self.status = 'bloqueada'
                self.bloqueada = True
                self.motivo_bloqueio = f"Pagamento vencido em {self.data_vencimento.strftime('%d/%m/%Y')}"
        else:
            self.status = 'ativa'
            self.bloqueada = False
        
        self.save()
        return self.status
    
    def processar_pagamento(self, valor_pago, observacoes=""):
        """Processa um pagamento e atualiza o status"""
        self.valor_pago += valor_pago
        self.data_ultimo_pagamento = timezone.now()
        
        # Se pagou o valor mensal, renova por mais 30 dias
        if self.valor_pago >= self.valor_mensal:
            self.data_vencimento = timezone.now() + timedelta(days=30)
            self.valor_pendente = 0
            self.status = 'ativa'
            self.bloqueada = False
            self.motivo_bloqueio = ""
        else:
            self.valor_pendente = self.valor_mensal - self.valor_pago
        
        if observacoes:
            self.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: {observacoes}"
        
        self.save()
        return True
    
    @property
    def dias_para_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        if self.data_vencimento:
            delta = self.data_vencimento - timezone.now()
            return delta.days
        return 0
    
    @property
    def dias_bloqueada(self):
        """Retorna quantos dias a loja está bloqueada"""
        if self.data_bloqueio and self.bloqueada:
            delta = timezone.now() - self.data_bloqueio
            return delta.days
        return 0


class Pagamento(models.Model):
    """Registro de pagamentos das lojas"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    controle_financeiro = models.ForeignKey(ControleFinanceiro, on_delete=models.CASCADE, verbose_name="Controle Financeiro")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    
    # Dados do pagamento
    metodo_pagamento = models.CharField(max_length=50, verbose_name="Método de Pagamento")
    dados_pagamento = models.JSONField(default=dict, verbose_name="Dados do Pagamento")
    
    # Controle
    data_pagamento = models.DateTimeField(null=True, blank=True, verbose_name="Data do Pagamento")
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Aprovado por")
    
    # Metadados
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Pagamento {self.id} - {self.controle_financeiro.loja.nome} - R$ {self.valor}"
    
    def aprovar(self, usuario_aprovador, observacoes=""):
        """Aprova o pagamento"""
        self.status = 'aprovado'
        self.data_aprovacao = timezone.now()
        self.aprovado_por = usuario_aprovador
        if observacoes:
            self.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: {observacoes}"
        
        # Processa o pagamento no controle financeiro
        self.controle_financeiro.processar_pagamento(self.valor, f"Pagamento aprovado - {self.id}")
        
        self.save()
        return True
    
    def rejeitar(self, motivo, usuario_aprovador=""):
        """Rejeita o pagamento"""
        self.status = 'rejeitado'
        if motivo:
            self.observacoes += f"\n{timezone.now().strftime('%d/%m/%Y %H:%M')}: REJEITADO - {motivo}"
        self.save()
        return True


class CobrancaAsaas(models.Model):
    """Cobranças geradas via API do Asaas"""
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('RECEIVED', 'Recebido'),
        ('CONFIRMED', 'Confirmado'),
        ('OVERDUE', 'Vencido'),
        ('REFUNDED', 'Estornado'),
        ('RECEIVED_IN_CASH', 'Recebido em Dinheiro'),
        ('REFUND_REQUESTED', 'Estorno Solicitado'),
        ('CHARGEBACK_REQUESTED', 'Chargeback Solicitado'),
        ('CHARGEBACK_DISPUTE', 'Disputa de Chargeback'),
        ('AWAITING_CHARGEBACK_REVERSAL', 'Aguardando Reversão'),
        ('DUNNING_REQUESTED', 'Cobrança Solicitada'),
        ('DUNNING_RECEIVED', 'Cobrança Recebida'),
        ('AWAITING_RISK_ANALYSIS', 'Aguardando Análise'),
    ]
    
    # Identificadores
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asaas_id = models.CharField(max_length=100, unique=True, verbose_name="ID no Asaas")
    controle_financeiro = models.ForeignKey(ControleFinanceiro, on_delete=models.CASCADE, verbose_name="Controle Financeiro")
    
    # Dados da cobrança
    customer_id = models.CharField(max_length=100, verbose_name="ID do Cliente no Asaas")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data_vencimento = models.DateTimeField(verbose_name="Data de Vencimento")
    descricao = models.TextField(verbose_name="Descrição")
    
    # Status e controle
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING', verbose_name="Status")
    data_pagamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Pagamento")
    
    # URLs e dados do boleto
    invoice_url = models.URLField(blank=True, verbose_name="URL do Boleto")
    bank_slip_url = models.URLField(blank=True, verbose_name="URL do PDF")
    invoice_number = models.CharField(max_length=100, blank=True, verbose_name="Número da Fatura")
    
    # Dados do PIX
    pix_qr_code = models.TextField(blank=True, verbose_name="QR Code PIX")
    pix_copy_paste = models.TextField(blank=True, verbose_name="PIX Copia e Cola")
    pix_expires_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Expiração do PIX")
    
    # Dados de resposta da API
    api_response = models.JSONField(default=dict, verbose_name="Resposta da API")
    
    # Metadados
    external_reference = models.CharField(max_length=200, blank=True, verbose_name="Referência Externa")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cobrança Asaas"
        verbose_name_plural = "Cobranças Asaas"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Cobrança {self.asaas_id} - {self.controle_financeiro.loja.nome} - R$ {self.valor}"
    
    @property
    def dias_para_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        if self.data_vencimento:
            delta = self.data_vencimento - timezone.now()
            return delta.days
        return 0
    
    @property
    def esta_vencida(self):
        """Verifica se a cobrança está vencida"""
        return self.data_vencimento < timezone.now() and self.status == 'PENDING'
    
    def marcar_como_paga(self, data_pagamento=None):
        """Marca a cobrança como paga"""
        self.status = 'RECEIVED'
        self.data_pagamento = data_pagamento or timezone.now()
        self.save()
        
        # Processar pagamento no controle financeiro
        self.controle_financeiro.processar_pagamento(
            self.valor,
            f"Pagamento via Asaas - Cobrança {self.asaas_id}"
        )
    
    def atualizar_dados_asaas(self, dados_asaas):
        """Atualiza dados com resposta da API do Asaas"""
        self.status = dados_asaas.get('status', self.status)
        self.invoice_url = dados_asaas.get('invoiceUrl', self.invoice_url)
        self.bank_slip_url = dados_asaas.get('bankSlipUrl', self.bank_slip_url)
        self.invoice_number = dados_asaas.get('invoiceNumber', self.invoice_number)
        
        # Atualizar dados do PIX se disponível
        if 'pix' in dados_asaas:
            pix_data = dados_asaas['pix']
            self.pix_qr_code = pix_data.get('qrCode', self.pix_qr_code)
            self.pix_copy_paste = pix_data.get('payload', self.pix_copy_paste)
            if pix_data.get('expirationDate'):
                self.pix_expires_date = datetime.fromisoformat(pix_data['expirationDate'].replace('Z', '+00:00'))
        
        # Salvar resposta completa da API
        self.api_response = dados_asaas
        self.save()


class NotificacaoFinanceira(models.Model):
    """Notificações financeiras para as lojas"""
    TIPO_CHOICES = [
        ('vencimento', 'Aviso de Vencimento'),
        ('bloqueio', 'Aviso de Bloqueio'),
        ('pagamento', 'Confirmação de Pagamento'),
        ('renovacao', 'Renovação Automática'),
    ]
    
    controle_financeiro = models.ForeignKey(ControleFinanceiro, on_delete=models.CASCADE, verbose_name="Controle Financeiro")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    
    # Controle
    enviada = models.BooleanField(default=False, verbose_name="Enviada")
    data_envio = models.DateTimeField(null=True, blank=True, verbose_name="Data de Envio")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notificação Financeira"
        verbose_name_plural = "Notificações Financeiras"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.controle_financeiro.loja.nome}"
# Importar modelos de sincronização
from .models_sync import SyncStatus