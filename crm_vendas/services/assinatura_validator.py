"""
Serviço de validação e sanitização de dados para assinaturas digitais
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class AssinaturaDataValidator:
    """
    Serviço para validar e sanitizar dados de assinatura digital
    """
    
    # Limites de campos baseados no modelo AssinaturaDigital
    MAX_NOME_SIGNATARIO = 200
    MAX_CPF_SIGNATARIO = 14
    MAX_OBSERVACOES = 1000  # Assumindo um limite razoável
    
    @classmethod
    def validate_and_sanitize_company_data(cls, loja, documento, tipo_documento: str) -> Dict[str, Any]:
        """
        Valida e sanitiza dados da empresa para criação de assinatura digital
        
        Args:
            loja: Instância do modelo Loja
            documento: Instância do documento (Orcamento, Proposta ou Contrato)
            tipo_documento: Tipo do documento ('orcamento', 'proposta', 'contrato')
            
        Returns:
            Dict com dados validados e sanitizados
            
        Raises:
            ValueError: Se dados essenciais estão ausentes
        """
        try:
            # Validar dados essenciais
            if not loja:
                raise ValueError("Loja é obrigatória para criar assinatura da empresa")
            
            if not documento:
                raise ValueError("Documento é obrigatório para criar assinatura")
            
            if not hasattr(documento, 'lead') or not documento.lead:
                raise ValueError("Documento deve ter um lead associado")
            
            # Sanitizar nome da empresa
            nome_signatario = cls._sanitize_nome_signatario(loja.nome)
            
            # Sanitizar email
            email_signatario = cls._sanitize_email_signatario(loja.email)
            
            # Sanitizar CNPJ para campo CPF (limitado a 14 caracteres)
            cpf_signatario = cls._sanitize_cpf_signatario(loja.cnpj)
            
            # Criar observações
            observacoes = cls._create_observacoes(tipo_documento, documento.numero)
            
            # Calcular data de expiração (7 dias)
            data_expiracao = timezone.now() + timedelta(days=7)
            
            validated_data = {
                'tipo_documento': tipo_documento,
                'tipo_signatario': 'empresa',
                'lead': documento.lead,
                'nome_signatario': nome_signatario,
                'email_signatario': email_signatario,
                'cpf_signatario': cpf_signatario,
                'observacoes': observacoes,
                'data_expiracao': data_expiracao,
                'status': 'pendente'
            }
            
            # Associar documento específico
            if tipo_documento == 'orcamento':
                validated_data['orcamento'] = documento
            elif tipo_documento == 'proposta':
                validated_data['proposta'] = documento
            elif tipo_documento == 'contrato':
                validated_data['contrato'] = documento
            
            logger.info(f"Dados da empresa validados com sucesso para {tipo_documento} {documento.numero}")
            return validated_data
            
        except Exception as e:
            logger.error(f"Erro na validação de dados da empresa: {str(e)}")
            raise
    
    @classmethod
    def _sanitize_nome_signatario(cls, nome: str) -> str:
        """
        Sanitiza o nome do signatário
        """
        if not nome:
            return "Empresa"
        
        # Truncar se necessário
        nome_sanitizado = str(nome).strip()[:cls.MAX_NOME_SIGNATARIO]
        
        if len(str(nome)) > cls.MAX_NOME_SIGNATARIO:
            logger.warning(f"Nome da empresa truncado de {len(nome)} para {cls.MAX_NOME_SIGNATARIO} caracteres")
        
        return nome_sanitizado
    
    @classmethod
    def _sanitize_email_signatario(cls, email: str) -> str:
        """
        Sanitiza o email do signatário
        """
        if not email:
            logger.warning("Email da empresa não informado, usando email padrão")
            return "noreply@empresa.com"
        
        return str(email).strip().lower()
    
    @classmethod
    def _sanitize_cpf_signatario(cls, cnpj: str) -> str:
        """
        Sanitiza o CNPJ para o campo cpf_signatario (limitado a 14 caracteres)
        """
        if not cnpj:
            logger.warning("CNPJ da empresa não informado")
            return ""
        
        # Remover caracteres especiais
        cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
        
        # Truncar para 14 caracteres (limitação do campo)
        cnpj_truncado = cnpj_limpo[:cls.MAX_CPF_SIGNATARIO]
        
        if len(cnpj_limpo) > cls.MAX_CPF_SIGNATARIO:
            logger.warning(f"CNPJ truncado de {len(cnpj_limpo)} para {cls.MAX_CPF_SIGNATARIO} caracteres: {cnpj_limpo} -> {cnpj_truncado}")
        
        return cnpj_truncado
    
    @classmethod
    def _create_observacoes(cls, tipo_documento: str, numero_documento: str) -> str:
        """
        Cria observações padronizadas para a assinatura
        """
        observacao = f'Assinatura automática da empresa após aprovação do cliente para {tipo_documento} {numero_documento}'
        
        # Truncar se necessário
        if len(observacao) > cls.MAX_OBSERVACOES:
            observacao = observacao[:cls.MAX_OBSERVACOES - 3] + "..."
            logger.warning("Observações truncadas devido ao limite de caracteres")
        
        return observacao
    
    @classmethod
    def validate_client_signature_completion(cls, assinatura_digital) -> bool:
        """
        Valida se a assinatura do cliente foi realmente completada
        
        Args:
            assinatura_digital: Instância de AssinaturaDigital
            
        Returns:
            bool: True se a assinatura do cliente está completa
        """
        try:
            return (
                assinatura_digital.tipo_signatario == 'cliente' and
                assinatura_digital.status == 'assinado' and
                assinatura_digital.data_assinatura is not None
            )
        except Exception as e:
            logger.error(f"Erro na validação de assinatura do cliente: {str(e)}")
            return False
    
    @classmethod
    def check_company_signature_exists(cls, documento, tipo_documento: str) -> bool:
        """
        Verifica se já existe uma solicitação de assinatura da empresa para o documento
        
        Args:
            documento: Instância do documento
            tipo_documento: Tipo do documento
            
        Returns:
            bool: True se já existe assinatura da empresa
        """
        try:
            from crm_vendas.models import AssinaturaDigital
            
            filter_kwargs = {
                'tipo_signatario': 'empresa',
                'tipo_documento': tipo_documento,
                tipo_documento: documento
            }
            
            return AssinaturaDigital.objects.filter(**filter_kwargs).exists()
            
        except Exception as e:
            logger.error(f"Erro ao verificar assinatura da empresa existente: {str(e)}")
            return False