"""
Serviço de envio de emails com tratamento robusto de erros
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    """Exceção para erros de envio de email"""
    pass


class EmailSender:
    """Serviço robusto para envio de emails"""
    
    def __init__(self):
        """Inicializa o serviço de email"""
        self.config = getattr(settings, 'EMAIL_CREDENTIALS_CONFIG', {})
        self.enabled = self.config.get('ENABLED', True)
        self.fallback_to_screen = self.config.get('FALLBACK_TO_SCREEN', True)
        self.max_retries = self.config.get('MAX_RETRIES', 3)
        self.retry_delay = self.config.get('RETRY_DELAY', 1)  # segundos
        
        # Configurações de email
        self.from_email = getattr(settings, 'EMAIL_CREDENTIALS_FROM', 
                                 getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@lvksistemas.com.br'))
        self.reply_to = getattr(settings, 'EMAIL_CREDENTIALS_REPLY_TO', None)
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Envia email com tratamento robusto de erros
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML
            text_content: Conteúdo em texto (opcional)
            context: Contexto adicional para logs
            
        Returns:
            dict: Resultado do envio {'success': bool, 'message': str, 'error': str}
        """
        if not self.enabled:
            logger.info(f"Envio de email desabilitado. Email para {to_email} não foi enviado.")
            return {
                'success': False,
                'message': 'Envio de email desabilitado',
                'error': 'EMAIL_DISABLED',
                'fallback_used': False
            }
        
        # Validar dados
        if not to_email or not subject or not html_content:
            error_msg = "Dados obrigatórios faltando para envio de email"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'error': 'MISSING_DATA',
                'fallback_used': False
            }
        
        # Tentar enviar com retry
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = self._send_email_attempt(to_email, subject, html_content, text_content)
                
                # Log de sucesso
                self._log_email_attempt(to_email, subject, True, context=context)
                
                return {
                    'success': True,
                    'message': f'Email enviado com sucesso para {to_email}',
                    'error': None,
                    'fallback_used': False,
                    'attempts': attempt + 1
                }
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Tentativa {attempt + 1} de envio falhou para {to_email}: {last_error}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # Todas as tentativas falharam
        error_msg = f"Falha ao enviar email após {self.max_retries} tentativas: {last_error}"
        logger.error(error_msg)
        
        # Log de falha
        self._log_email_attempt(to_email, subject, False, error=last_error, context=context)
        
        # Usar fallback se habilitado
        fallback_used = False
        if self.fallback_to_screen:
            self._display_credentials_fallback(to_email, subject, html_content, text_content, context)
            fallback_used = True
        
        return {
            'success': False,
            'message': error_msg,
            'error': last_error,
            'fallback_used': fallback_used,
            'attempts': self.max_retries
        }
    
    def _send_email_attempt(self, to_email: str, subject: str, html_content: str, 
                           text_content: Optional[str] = None) -> bool:
        """
        Tentativa única de envio de email
        """
        # Criar email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content or self._html_to_text(html_content),
            from_email=self.from_email,
            to=[to_email]
        )
        
        # Adicionar versão HTML
        email.attach_alternative(html_content, "text/html")
        
        # Adicionar reply-to se configurado
        if self.reply_to:
            email.reply_to = [self.reply_to]
        
        # Enviar
        email.send()
        
        logger.info(f"Email enviado com sucesso para {to_email}")
        return True
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Converte HTML para texto simples
        """
        import re
        
        # Remove tags HTML
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Limpa espaços extras
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _display_credentials_fallback(self, to_email: str, subject: str, html_content: str, 
                                    text_content: Optional[str], context: Optional[Dict[str, Any]]):
        """
        Exibe credenciais na tela como fallback
        """
        print("\n" + "="*80)
        print("FALLBACK: CREDENCIAIS NÃO ENVIADAS POR EMAIL")
        print("="*80)
        print(f"Para: {to_email}")
        print(f"Assunto: {subject}")
        print("-"*80)
        
        if context and 'user' in context and 'password' in context:
            user = context['user']
            password = context['password']
            loja = context.get('loja')
            
            print(f"USUÁRIO: {user.username}")
            print(f"SENHA: {password}")
            
            if loja:
                print(f"LOJA: {loja.nome}")
                print(f"ACESSO: http://localhost:8000/login/{loja.id}/")
            else:
                print(f"ACESSO: http://localhost:8000/login/")
        else:
            print(text_content or self._html_to_text(html_content))
        
        print("="*80)
        print("IMPORTANTE: Informe essas credenciais ao usuário manualmente!")
        print("="*80 + "\n")
    
    def _log_email_attempt(self, to_email: str, subject: str, success: bool, 
                          error: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Registra tentativa de envio de email para auditoria
        """
        try:
            # Importar aqui para evitar dependência circular
            from .models import EmailLog
            
            # Extrair informações do contexto
            user_id = None
            loja_id = None
            if context:
                if 'user' in context:
                    user_id = context['user'].id
                if 'loja' in context:
                    loja_id = context['loja'].id
            
            # Criar log
            EmailLog.objects.create(
                to_email=to_email,
                subject=subject,
                success=success,
                error_message=error or '',
                user_id=user_id,
                loja_id=loja_id,
                email_type='credentials'
            )
            
        except Exception as e:
            # Não falhar se não conseguir logar
            logger.warning(f"Erro ao criar log de email: {str(e)}")
    
    def send_bulk_emails(self, email_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envia múltiplos emails
        
        Args:
            email_list: Lista de dicts com dados dos emails
            
        Returns:
            dict: Estatísticas do envio
        """
        results = {
            'total': len(email_list),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for email_data in email_list:
            try:
                result = self.send_email(
                    to_email=email_data['to_email'],
                    subject=email_data['subject'],
                    html_content=email_data['html_content'],
                    text_content=email_data.get('text_content'),
                    context=email_data.get('context')
                )
                
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'email': email_data['to_email'],
                        'error': result['error']
                    })
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'email': email_data.get('to_email', 'unknown'),
                    'error': str(e)
                })
        
        logger.info(f"Envio em lote concluído: {results['success']}/{results['total']} sucessos")
        return results
    
    def test_email_configuration(self) -> Dict[str, Any]:
        """
        Testa a configuração de email
        """
        try:
            from django.core.mail import get_connection
            
            connection = get_connection()
            connection.open()
            connection.close()
            
            return {
                'success': True,
                'message': 'Configuração de email OK',
                'from_email': self.from_email,
                'backend': settings.EMAIL_BACKEND
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro na configuração de email: {str(e)}',
                'error': str(e)
            }
    
    def get_email_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de envio de email
        """
        try:
            from .models import EmailLog
            from django.db.models import Count
            from datetime import timedelta
            from django.utils import timezone
            
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            
            stats = {
                'total_emails': EmailLog.objects.count(),
                'successful_emails': EmailLog.objects.filter(success=True).count(),
                'failed_emails': EmailLog.objects.filter(success=False).count(),
                'last_24h': EmailLog.objects.filter(sent_at__gte=last_24h).count(),
                'last_7d': EmailLog.objects.filter(sent_at__gte=last_7d).count(),
                'success_rate': 0
            }
            
            if stats['total_emails'] > 0:
                stats['success_rate'] = (stats['successful_emails'] / stats['total_emails']) * 100
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de email: {str(e)}")
            return {
                'error': str(e)
            }