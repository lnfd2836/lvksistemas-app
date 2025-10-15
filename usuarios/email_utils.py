"""
Utilitários para envio de emails do sistema
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.template import TemplateDoesNotExist
from smtplib import SMTPException, SMTPAuthenticationError, SMTPConnectError
import logging
import traceback

logger = logging.getLogger(__name__)


def validar_configuracao_email():
    """
    Valida se todas as configurações necessárias para envio de email estão presentes
    
    Returns:
        tuple: (is_valid: bool, errors: list, warnings: list)
    """
    errors = []
    warnings = []
    
    # Verificar configurações obrigatórias
    required_settings = {
        'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
        'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
    }
    
    for setting_name, setting_value in required_settings.items():
        if not setting_value:
            errors.append(f"Configuração {setting_name} não está definida ou está vazia")
        elif setting_name in ['EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'] and 'your-' in str(setting_value):
            errors.append(f"Configuração {setting_name} contém valor de exemplo, configure com credenciais reais")
    
    # Verificar configurações específicas do Gmail
    if getattr(settings, 'EMAIL_HOST', '') == 'smtp.gmail.com':
        if getattr(settings, 'EMAIL_PORT', 0) != 587:
            warnings.append("Para Gmail, a porta recomendada é 587")
        
        if not getattr(settings, 'EMAIL_USE_TLS', False):
            warnings.append("Para Gmail, EMAIL_USE_TLS deve ser True")
        
        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        if email_user and not email_user.endswith('@gmail.com'):
            warnings.append("EMAIL_HOST_USER deve ser um endereço @gmail.com para usar smtp.gmail.com")
    
    # Verificar se templates existem
    template_paths = [
        'emails/credenciais_usuario.html',
        'emails/credenciais_loja.html',
        'emails/notificacao_admin.html',
        'emails/troca_senha_obrigatoria.html'
    ]
    
    for template_path in template_paths:
        try:
            render_to_string(template_path, {})
        except TemplateDoesNotExist:
            errors.append(f"Template {template_path} não encontrado")
        except Exception:
            # Template existe mas pode ter erro de renderização sem contexto, isso é OK
            pass
    
    is_valid = len(errors) == 0
    
    return is_valid, errors, warnings


def testar_conectividade_smtp():
    """
    Testa a conectividade com o servidor SMTP sem enviar email
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import smtplib
        
        host = getattr(settings, 'EMAIL_HOST', '')
        port = getattr(settings, 'EMAIL_PORT', 587)
        user = getattr(settings, 'EMAIL_HOST_USER', '')
        password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        
        if not all([host, port, user, password]):
            return False, "Configurações de email incompletas"
        
        logger.debug(f"Testando conectividade SMTP: {host}:{port}")
        
        # Conectar ao servidor
        server = smtplib.SMTP(host, port, timeout=10)
        
        if use_tls:
            server.starttls()
        
        # Tentar autenticar
        server.login(user, password)
        server.quit()
        
        return True, "Conectividade SMTP OK"
        
    except SMTPAuthenticationError as e:
        return False, f"Erro de autenticação: {e}. Verifique EMAIL_HOST_USER e EMAIL_HOST_PASSWORD"
    except SMTPConnectError as e:
        return False, f"Erro de conexão: {e}. Verifique EMAIL_HOST e EMAIL_PORT"
    except Exception as e:
        return False, f"Erro inesperado: {e}"


def enviar_email_credenciais_usuario(user, senha_provisoria, tipo_usuario='Super Administrador'):
    """
    Envia email com credenciais provisórias para novo usuário
    
    Args:
        user: Instância do User
        senha_provisoria: Senha provisória gerada
        tipo_usuario: Tipo do usuário (Super Administrador, Administrador de Loja)
    """
    email_destino = user.email if user else 'N/A'
    
    try:
        logger.info(f"Iniciando envio de email de credenciais para usuário: {user.username} ({email_destino})")
        
        # Validação de configuração
        is_valid, errors, warnings = validar_configuracao_email()
        if not is_valid:
            logger.error(f"Configuração de email inválida: {'; '.join(errors)}")
            return False
        
        if warnings:
            for warning in warnings:
                logger.warning(f"Aviso de configuração: {warning}")
        
        # Validação básica
        if not user or not user.email:
            logger.error(f"Usuário inválido ou sem email: user={user}, email={email_destino}")
            return False
            
        if not senha_provisoria:
            logger.error(f"Senha provisória não fornecida para usuário {user.username}")
            return False
        
        # Contexto para o template
        context = {
            'user': user,
            'senha_provisoria': senha_provisoria,
            'tipo_usuario': tipo_usuario,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br')}/login/",
        }
        
        logger.debug(f"Renderizando templates de email para {email_destino}")
        
        # Renderiza template HTML
        try:
            html_content = render_to_string('emails/credenciais_usuario.html', context)
        except TemplateDoesNotExist as e:
            logger.error(f"Template HTML não encontrado para credenciais de usuário: {e}")
            return False
        
        # Renderiza template texto
        try:
            text_content = render_to_string('emails/credenciais_usuario.txt', context)
        except TemplateDoesNotExist:
            logger.warning(f"Template de texto não encontrado, usando versão HTML convertida")
            text_content = strip_tags(html_content)
        
        # Assunto do email
        subject = f'🎉 Bem-vindo ao Sistema LVK - Credenciais de Acesso'
        
        logger.debug(f"Criando email para {email_destino} com assunto: {subject}")
        
        # Cria email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        # Anexa versão HTML
        email.attach_alternative(html_content, "text/html")
        
        logger.debug(f"Enviando email para {email_destino}")
        
        # Envia email
        email.send()
        
        logger.info(f"✅ Email de credenciais enviado com sucesso para {email_destino} (usuário: {user.username})")
        return True
        
    except SMTPAuthenticationError as e:
        logger.error(f"❌ Erro de autenticação SMTP ao enviar email para {email_destino}: {e}")
        logger.error("Verifique as credenciais EMAIL_HOST_USER e EMAIL_HOST_PASSWORD no arquivo .env")
        logger.error("Para Gmail, pode ser necessário usar uma 'Senha de App': https://myaccount.google.com/apppasswords")
        return False
        
    except SMTPConnectError as e:
        logger.error(f"❌ Erro de conexão SMTP ao enviar email para {email_destino}: {e}")
        logger.error("Verifique as configurações EMAIL_HOST e EMAIL_PORT no arquivo .env")
        return False
        
    except SMTPException as e:
        logger.error(f"❌ Erro SMTP ao enviar email para {email_destino}: {e}")
        logger.error(f"Configurações atuais: HOST={getattr(settings, 'EMAIL_HOST', 'N/A')}, PORT={getattr(settings, 'EMAIL_PORT', 'N/A')}")
        return False
        
    except TemplateDoesNotExist as e:
        logger.error(f"❌ Template de email não encontrado para {email_destino}: {e}")
        logger.error("Verifique se os templates estão no diretório correto: templates/emails/")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar email de credenciais para {email_destino}: {e}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def enviar_email_credenciais_loja(loja, senha_provisoria):
    """
    Envia email com credenciais provisórias para nova loja
    
    Args:
        loja: Instância da Loja
        senha_provisoria: Senha provisória gerada
    """
    email_destino = loja.email if loja else 'N/A'
    nome_loja = loja.nome if loja else 'N/A'
    
    try:
        logger.info(f"Iniciando envio de email de credenciais para loja: {nome_loja} ({email_destino})")
        
        # Validação de configuração
        is_valid, errors, warnings = validar_configuracao_email()
        if not is_valid:
            logger.error(f"Configuração de email inválida: {'; '.join(errors)}")
            return False
        
        if warnings:
            for warning in warnings:
                logger.warning(f"Aviso de configuração: {warning}")
        
        # Validação básica
        if not loja or not loja.email:
            logger.error(f"Loja inválida ou sem email: loja={loja}, email={email_destino}")
            return False
            
        if not senha_provisoria:
            logger.error(f"Senha provisória não fornecida para loja {nome_loja}")
            return False
        
        # Contexto para o template
        context = {
            'loja': loja,
            'senha_provisoria': senha_provisoria,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br')}/loja/login/",
        }
        
        logger.debug(f"Renderizando templates de email para loja {nome_loja}")
        
        # Renderiza template HTML
        try:
            html_content = render_to_string('emails/credenciais_loja.html', context)
        except TemplateDoesNotExist as e:
            logger.error(f"Template HTML não encontrado para credenciais de loja: {e}")
            return False
        
        # Renderiza template texto
        try:
            text_content = render_to_string('emails/credenciais_loja.txt', context)
        except TemplateDoesNotExist:
            logger.warning(f"Template de texto não encontrado para loja, usando versão HTML convertida")
            text_content = strip_tags(html_content)
        
        # Assunto do email
        subject = f'🏪 Sua Loja {loja.nome} foi Criada - Credenciais de Acesso'
        
        logger.debug(f"Criando email para loja {nome_loja} com assunto: {subject}")
        
        # Cria email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[loja.email]
        )
        
        # Anexa versão HTML
        email.attach_alternative(html_content, "text/html")
        
        logger.debug(f"Enviando email para loja {nome_loja} ({email_destino})")
        
        # Envia email
        email.send()
        
        logger.info(f"✅ Email de credenciais da loja enviado com sucesso para {email_destino} (loja: {nome_loja})")
        return True
        
    except SMTPAuthenticationError as e:
        logger.error(f"❌ Erro de autenticação SMTP ao enviar email para loja {nome_loja} ({email_destino}): {e}")
        logger.error("Verifique as credenciais EMAIL_HOST_USER e EMAIL_HOST_PASSWORD no arquivo .env")
        logger.error("Para Gmail, pode ser necessário usar uma 'Senha de App': https://myaccount.google.com/apppasswords")
        return False
        
    except SMTPConnectError as e:
        logger.error(f"❌ Erro de conexão SMTP ao enviar email para loja {nome_loja} ({email_destino}): {e}")
        logger.error("Verifique as configurações EMAIL_HOST e EMAIL_PORT no arquivo .env")
        return False
        
    except SMTPException as e:
        logger.error(f"❌ Erro SMTP ao enviar email para loja {nome_loja} ({email_destino}): {e}")
        logger.error(f"Configurações atuais: HOST={getattr(settings, 'EMAIL_HOST', 'N/A')}, PORT={getattr(settings, 'EMAIL_PORT', 'N/A')}")
        return False
        
    except TemplateDoesNotExist as e:
        logger.error(f"❌ Template de email não encontrado para loja {nome_loja}: {e}")
        logger.error("Verifique se os templates estão no diretório correto: templates/emails/")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar email de credenciais para loja {nome_loja} ({email_destino}): {e}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def enviar_email_notificacao_admin(admin_user, tipo_acao, detalhes):
    """
    Envia email de notificação para administradores do sistema
    
    Args:
        admin_user: Usuário administrador que receberá a notificação
        tipo_acao: Tipo da ação (criacao_usuario, criacao_loja)
        detalhes: Detalhes da ação
    """
    email_destino = admin_user.email if admin_user else 'N/A'
    username = admin_user.username if admin_user else 'N/A'
    
    try:
        logger.info(f"Iniciando envio de notificação admin para: {username} ({email_destino}) - Ação: {tipo_acao}")
        
        # Validação básica
        if not admin_user or not admin_user.email:
            logger.error(f"Admin inválido ou sem email: admin={admin_user}, email={email_destino}")
            return False
        
        # Contexto para o template
        context = {
            'admin_user': admin_user,
            'tipo_acao': tipo_acao,
            'detalhes': detalhes,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
        }
        
        logger.debug(f"Renderizando templates de notificação admin para {email_destino}")
        
        # Renderiza template HTML
        try:
            html_content = render_to_string('emails/notificacao_admin.html', context)
        except TemplateDoesNotExist as e:
            logger.error(f"Template HTML de notificação admin não encontrado: {e}")
            return False
        
        # Renderiza template texto
        try:
            text_content = render_to_string('emails/notificacao_admin.txt', context)
        except TemplateDoesNotExist:
            logger.warning(f"Template de texto de notificação admin não encontrado, usando versão HTML convertida")
            text_content = strip_tags(html_content)
        
        # Assunto do email
        subject = f'🔔 Notificação do Sistema - {tipo_acao.replace("_", " ").title()}'
        
        logger.debug(f"Criando email de notificação para {email_destino} com assunto: {subject}")
        
        # Cria email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_user.email]
        )
        
        # Anexa versão HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envia email
        email.send()
        
        logger.info(f"✅ Email de notificação enviado com sucesso para {email_destino} (admin: {username})")
        return True
        
    except SMTPAuthenticationError as e:
        logger.error(f"❌ Erro de autenticação SMTP ao enviar notificação para {email_destino}: {e}")
        return False
        
    except SMTPException as e:
        logger.error(f"❌ Erro SMTP ao enviar notificação para {email_destino}: {e}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar notificação para {email_destino}: {e}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        return False


def enviar_email_troca_senha_obrigatoria(user):
    """
    Envia email lembrando que é obrigatório trocar a senha
    
    Args:
        user: Instância do User
    """
    email_destino = user.email if user else 'N/A'
    username = user.username if user else 'N/A'
    
    try:
        logger.info(f"Iniciando envio de email de troca de senha obrigatória para: {username} ({email_destino})")
        
        # Validação básica
        if not user or not user.email:
            logger.error(f"Usuário inválido ou sem email: user={user}, email={email_destino}")
            return False
        
        # Contexto para o template
        context = {
            'user': user,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br')}/login/",
        }
        
        logger.debug(f"Renderizando templates de troca de senha para {email_destino}")
        
        # Renderiza template HTML
        try:
            html_content = render_to_string('emails/troca_senha_obrigatoria.html', context)
        except TemplateDoesNotExist as e:
            logger.error(f"Template HTML de troca de senha não encontrado: {e}")
            return False
        
        # Renderiza template texto
        try:
            text_content = render_to_string('emails/troca_senha_obrigatoria.txt', context)
        except TemplateDoesNotExist:
            logger.warning(f"Template de texto de troca de senha não encontrado, usando versão HTML convertida")
            text_content = strip_tags(html_content)
        
        # Assunto do email
        subject = f'🔐 Troca de Senha Obrigatória - {user.first_name}'
        
        logger.debug(f"Criando email de troca de senha para {email_destino} com assunto: {subject}")
        
        # Cria email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        # Anexa versão HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envia email
        email.send()
        
        logger.info(f"✅ Email de troca de senha obrigatória enviado com sucesso para {email_destino} (usuário: {username})")
        return True
        
    except SMTPAuthenticationError as e:
        logger.error(f"❌ Erro de autenticação SMTP ao enviar email de troca de senha para {email_destino}: {e}")
        return False
        
    except SMTPException as e:
        logger.error(f"❌ Erro SMTP ao enviar email de troca de senha para {email_destino}: {e}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar email de troca de senha para {email_destino}: {e}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        return False
