"""
Utilitários para envio de emails do sistema
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def enviar_email_credenciais_usuario(user, senha_provisoria, tipo_usuario='Super Administrador'):
    """
    Envia email com credenciais provisórias para novo usuário
    
    Args:
        user: Instância do User
        senha_provisoria: Senha provisória gerada
        tipo_usuario: Tipo do usuário (Super Administrador, Administrador de Loja)
    """
    try:
        # Contexto para o template
        context = {
            'user': user,
            'senha_provisoria': senha_provisoria,
            'tipo_usuario': tipo_usuario,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br')}/login/",
        }
        
        # Renderiza template HTML
        html_content = render_to_string('emails/credenciais_usuario.html', context)
        
        # Renderiza template texto
        text_content = render_to_string('emails/credenciais_usuario.txt', context)
        
        # Assunto do email
        subject = f'🎉 Bem-vindo ao Sistema LVK - Credenciais de Acesso'
        
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
        
        logger.info(f"Email de credenciais enviado para {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de credenciais para {user.email}: {e}")
        return False


def enviar_email_credenciais_loja(loja, senha_provisoria):
    """
    Envia email com credenciais provisórias para nova loja
    
    Args:
        loja: Instância da Loja
        senha_provisoria: Senha provisória gerada
    """
    try:
        # Contexto para o template
        context = {
            'loja': loja,
            'senha_provisoria': senha_provisoria,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br')}/login/",
        }
        
        # Renderiza template HTML
        html_content = render_to_string('emails/credenciais_loja.html', context)
        
        # Renderiza template texto
        text_content = render_to_string('emails/credenciais_loja.txt', context)
        
        # Assunto do email
        subject = f'🏪 Sua Loja {loja.nome} foi Criada - Credenciais de Acesso'
        
        # Cria email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[loja.email]
        )
        
        # Anexa versão HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envia email
        email.send()
        
        logger.info(f"Email de credenciais da loja enviado para {loja.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de credenciais da loja para {loja.email}: {e}")
        return False


def enviar_email_notificacao_admin(admin_user, tipo_acao, detalhes):
    """
    Envia email de notificação para administradores do sistema
    
    Args:
        admin_user: Usuário administrador que receberá a notificação
        tipo_acao: Tipo da ação (criacao_usuario, criacao_loja)
        detalhes: Detalhes da ação
    """
    try:
        # Contexto para o template
        context = {
            'admin_user': admin_user,
            'tipo_acao': tipo_acao,
            'detalhes': detalhes,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
        }
        
        # Renderiza template HTML
        html_content = render_to_string('emails/notificacao_admin.html', context)
        
        # Renderiza template texto
        text_content = render_to_string('emails/notificacao_admin.txt', context)
        
        # Assunto do email
        subject = f'🔔 Notificação do Sistema - {tipo_acao.replace("_", " ").title()}'
        
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
        
        logger.info(f"Email de notificação enviado para {admin_user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de notificação para {admin_user.email}: {e}")
        return False


def enviar_email_troca_senha_obrigatoria(user):
    """
    Envia email lembrando que é obrigatório trocar a senha
    
    Args:
        user: Instância do User
    """
    try:
        # Contexto para o template
        context = {
            'user': user,
            'site_url': getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://lvksistemas.com.br')}/login/",
        }
        
        # Renderiza template HTML
        html_content = render_to_string('emails/troca_senha_obrigatoria.html', context)
        
        # Renderiza template texto
        text_content = render_to_string('emails/troca_senha_obrigatoria.txt', context)
        
        # Assunto do email
        subject = f'🔐 Troca de Senha Obrigatória - {user.first_name}'
        
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
        
        logger.info(f"Email de troca de senha obrigatória enviado para {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de troca de senha para {user.email}: {e}")
        return False
