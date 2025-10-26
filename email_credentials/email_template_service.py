"""
Serviço de templates de email para credenciais
"""
from django.template.loader import render_to_string
from django.conf import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmailTemplateService:
    """Gerenciador de templates de email para credenciais"""
    
    # Mapeamento de templates por tipo de usuário
    TEMPLATES = {
        'super_admin': 'email_credentials/super_admin_credentials.html',
        'loja_admin': 'email_credentials/loja_admin_credentials.html',
        'loja_user': 'email_credentials/loja_user_credentials.html',
        'recovery': 'email_credentials/password_recovery.html'
    }
    
    # Assuntos padrão dos emails
    DEFAULT_SUBJECTS = {
        'super_admin': 'Credenciais Super Admin - LVK Sistemas',
        'loja_admin': 'Credenciais Admin - {loja_nome}',
        'loja_user': 'Credenciais de Acesso - {loja_nome}',
        'recovery': 'Recuperação de Senha - LVK Sistemas'
    }
    
    def __init__(self):
        """Inicializa o serviço de templates"""
        self.config = getattr(settings, 'EMAIL_CREDENTIALS_CONFIG', {})
        self.templates = self.config.get('TEMPLATES', self.TEMPLATES)
        self.subjects = self.config.get('EMAIL_SUBJECTS', self.DEFAULT_SUBJECTS)
    
    def get_template_path(self, user_type: str, loja_type: Optional[str] = None) -> str:
        """
        Retorna o caminho do template apropriado
        
        Args:
            user_type: Tipo do usuário (super_admin, loja_admin, loja_user, recovery)
            loja_type: Tipo da loja para personalização adicional
            
        Returns:
            str: Caminho do template
        """
        # Template específico por tipo de loja (se existir)
        if loja_type and user_type in ['loja_admin', 'loja_user']:
            specific_template = f'email_credentials/{user_type}_{loja_type}.html'
            if self._template_exists(specific_template):
                return specific_template
        
        # Template padrão
        return self.templates.get(user_type, self.templates['loja_user'])
    
    def render_email(self, user_type: str, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Renderiza o email completo (HTML e texto)
        
        Args:
            user_type: Tipo do usuário
            context: Dados para renderização
            
        Returns:
            dict: {'html': html_content, 'text': text_content, 'subject': subject}
        """
        try:
            # Preparar contexto completo
            full_context = self._prepare_context(context)
            
            # Obter template
            loja_type = context.get('loja', {}).get('tipo_loja', {}).get('nome', None)
            template_path = self.get_template_path(user_type, loja_type)
            
            # Renderizar HTML
            html_content = render_to_string(template_path, full_context)
            
            # Renderizar versão texto (se existir)
            text_template = template_path.replace('.html', '.txt')
            text_content = ''
            if self._template_exists(text_template):
                text_content = render_to_string(text_template, full_context)
            else:
                text_content = self._html_to_text(html_content)
            
            # Gerar assunto
            subject = self._generate_subject(user_type, full_context)
            
            return {
                'html': html_content,
                'text': text_content,
                'subject': subject
            }
            
        except Exception as e:
            logger.error(f"Erro ao renderizar email para {user_type}: {str(e)}")
            return self._get_fallback_email(user_type, context)
    
    def _prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara o contexto completo para renderização
        """
        full_context = {
            'site_name': getattr(settings, 'SITE_NAME', 'LVK Sistemas'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'suporte@lvksistemas.com.br'),
            'company_name': 'LVK Sistemas',
            **context
        }
        
        # Adicionar URLs específicas
        if 'loja' in context:
            loja = context['loja']
            full_context['login_url'] = f"{full_context['site_url']}/login/{loja.id}/"
            full_context['loja_dashboard_url'] = f"{full_context['site_url']}/dashboard/loja/{loja.id}/"
        else:
            full_context['login_url'] = f"{full_context['site_url']}/login/"
            full_context['admin_dashboard_url'] = f"{full_context['site_url']}/dashboard/super-admin/"
        
        return full_context
    
    def _generate_subject(self, user_type: str, context: Dict[str, Any]) -> str:
        """
        Gera o assunto do email baseado no tipo e contexto
        """
        subject_template = self.subjects.get(user_type, 'Credenciais de Acesso - LVK Sistemas')
        
        try:
            # Substituir variáveis no assunto
            if 'loja' in context:
                loja = context['loja']
                subject = subject_template.format(
                    loja_nome=loja.nome,
                    loja_tipo=getattr(loja.tipo_loja, 'nome', 'Loja') if hasattr(loja, 'tipo_loja') else 'Loja'
                )
            else:
                subject = subject_template
            
            return subject
            
        except Exception as e:
            logger.warning(f"Erro ao gerar assunto para {user_type}: {str(e)}")
            return "Credenciais de Acesso - LVK Sistemas"
    
    def _template_exists(self, template_path: str) -> bool:
        """
        Verifica se um template existe
        """
        try:
            from django.template.loader import get_template
            get_template(template_path)
            return True
        except:
            return False
    
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
    
    def _get_fallback_email(self, user_type: str, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Retorna email de fallback em caso de erro
        """
        user = context.get('user')
        password = context.get('password', '[SENHA]')
        loja = context.get('loja')
        
        if user_type == 'super_admin':
            subject = "Credenciais Super Admin - LVK Sistemas"
            text = f"""
Olá {user.first_name or user.username},

Suas credenciais de Super Administrador foram criadas:

Usuário: {user.username}
Senha: {password}
Acesso: http://localhost:8000/dashboard/super-admin/

IMPORTANTE: Altere sua senha no primeiro acesso.

Atenciosamente,
Equipe LVK Sistemas
            """.strip()
        
        elif loja:
            subject = f"Credenciais de Acesso - {loja.nome}"
            text = f"""
Olá {user.first_name or user.username},

Suas credenciais para {loja.nome} foram criadas:

Usuário: {user.username}
Senha: {password}
Acesso: http://localhost:8000/login/{loja.id}/

IMPORTANTE: Altere sua senha no primeiro acesso.

Atenciosamente,
Equipe {loja.nome}
            """.strip()
        
        else:
            subject = "Credenciais de Acesso - LVK Sistemas"
            text = f"""
Olá {user.first_name or user.username},

Suas credenciais foram criadas:

Usuário: {user.username}
Senha: {password}

IMPORTANTE: Altere sua senha no primeiro acesso.

Atenciosamente,
Equipe LVK Sistemas
            """.strip()
        
        return {
            'html': f'<pre>{text}</pre>',
            'text': text,
            'subject': subject
        }
    
    def get_available_templates(self) -> Dict[str, str]:
        """
        Retorna lista de templates disponíveis
        """
        return self.templates.copy()
    
    def validate_template(self, user_type: str, context: Dict[str, Any]) -> bool:
        """
        Valida se um template pode ser renderizado com o contexto fornecido
        """
        try:
            self.render_email(user_type, context)
            return True
        except Exception as e:
            logger.error(f"Validação de template falhou para {user_type}: {str(e)}")
            return False