"""
Signals para automatizar criação de recursos quando uma loja é criada
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Loja
from .models_login import LoginPersonalizado

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Loja)
def criar_recursos_loja(sender, instance, created, **kwargs):
    """
    Signal executado após salvar uma loja.
    Cria automaticamente recursos necessários para a loja.
    """
    if created:
        # Verificar se já foi processado (evitar duplicação)
        if hasattr(instance, '_signal_processed'):
            logger.warning(f"Signal já processado para loja {instance.nome} - ignorando execução duplicada")
            return
        
        # Marcar como processado
        instance._signal_processed = True
        
        try:
            logger.info(f"🚀 INICIANDO processamento de signal para nova loja: {instance.nome}")
            
            # 1. Criar login personalizado para a loja
            login_personalizado = criar_login_personalizado(instance)
            
            # 2. Criar usuário admin se não existir
            admin_user = criar_admin_loja(instance)
            
            # 3. Associar admin à loja se foi criado
            if admin_user and not instance.admin_user:
                instance.admin_user = admin_user
                instance.save(update_fields=['admin_user'])
            
            # 4. Enviar email com credenciais e link personalizado (APENAS UMA VEZ)
            logger.info(f"📧 Enviando email único para loja {instance.nome}")
            email_enviado = enviar_email_credenciais_loja_personalizado(instance, login_personalizado)
            
            logger.info(f"✅ Recursos criados para loja {instance.nome}:")
            logger.info(f"- Login personalizado: {login_personalizado.get_login_url()}")
            if admin_user:
                logger.info(f"- Admin criado: {admin_user.username}")
            logger.info(f"- Senha provisória: {instance.senha_provisoria}")
            logger.info(f"- Email enviado: {'✅ SIM' if email_enviado else '❌ FALHOU'} para: {instance.email}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar recursos para loja {instance.nome}: {str(e)}")


def criar_login_personalizado(loja):
    """
    Cria login personalizado para a loja
    """
    try:
        # Verificar se já existe
        login_personalizado, created = LoginPersonalizado.objects.get_or_create(
            loja=loja,
            defaults={
                'titulo': f'Login - {loja.nome}',
                'subtitulo': f'Acesse o sistema da {loja.nome}',
                'mensagem_boas_vindas': f'Bem-vindo ao sistema da {loja.nome}',
                'mensagem_rodape': f'© {loja.nome} - Todos os direitos reservados',
                'ativo': True
            }
        )
        
        if created:
            logger.info(f"Login personalizado criado para {loja.nome}: {login_personalizado.get_login_url()}")
        else:
            logger.info(f"Login personalizado já existe para {loja.nome}")
        
        return login_personalizado
        
    except Exception as e:
        logger.error(f"Erro ao criar login personalizado para {loja.nome}: {str(e)}")
        raise


def criar_admin_loja(loja):
    """
    Cria usuário admin para a loja se não existir
    """
    try:
        # Se já tem admin, não criar outro
        if loja.admin_user:
            logger.info(f"Loja {loja.nome} já tem admin: {loja.admin_user.username}")
            return loja.admin_user
        
        # Gerar username único baseado no nome da loja
        username_base = gerar_username_loja(loja.nome)
        username = username_base
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{username_base}_{counter}"
            counter += 1
        
        # Criar usuário admin
        admin_user = User.objects.create_user(
            username=username,
            email=loja.email,
            password=loja.senha_provisoria,  # Usar senha provisória da loja
            first_name='Administrador',
            last_name=loja.nome,
            is_staff=False,  # Não é staff do Django admin
            is_active=True
        )
        
        logger.info(f"Admin criado para {loja.nome}: {admin_user.username}")
        return admin_user
        
    except Exception as e:
        logger.error(f"Erro ao criar admin para {loja.nome}: {str(e)}")
        return None


def gerar_username_loja(nome_loja):
    """
    Gera username baseado no nome da loja
    """
    import re
    from django.utils.text import slugify
    
    # Criar slug baseado no nome da loja
    username = slugify(nome_loja).replace('-', '_')
    
    # Remover caracteres especiais e limitar tamanho
    username = re.sub(r'[^a-z0-9_]', '', username)[:20]
    
    # Adicionar prefixo se necessário
    if not username:
        username = 'loja'
    
    return f"admin_{username}"


def enviar_email_credenciais_loja_personalizado(loja, login_personalizado):
    """
    Envia email com credenciais e link de login personalizado para a loja
    APENAS UMA VEZ por loja
    """
    # Verificar se já foi enviado (evitar duplicação)
    if hasattr(loja, '_email_enviado'):
        logger.warning(f"📧 Email já enviado para loja {loja.nome} - ignorando envio duplicado")
        return True
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        from django.template.loader import render_to_string
        
        logger.info(f"📧 ENVIANDO email único para loja {loja.nome} ({loja.email})")
        
        # URL completa do login personalizado
        site_url = getattr(settings, 'SITE_URL', 'https://www.lvksistemas.com.br')
        login_url_personalizada = f"{site_url}{login_personalizado.get_login_url()}"
        
        # Contexto para o template
        context = {
            'loja': loja,
            'senha_provisoria': loja.senha_provisoria,
            'login_personalizado': login_personalizado,
            'login_url_personalizada': login_url_personalizada,
            'site_url': site_url,
        }
        
        # Renderizar template HTML personalizado
        try:
            html_content = render_to_string('emails/credenciais_loja_personalizada.html', context)
        except:
            # Fallback para template padrão
            html_content = render_to_string('emails/credenciais_loja.html', context)
        
        # Assunto do email
        subject = f'🏪 Sua Loja {loja.nome} foi Criada - Acesso Personalizado'
        
        # Mensagem de texto simples
        message = f"""
🎉 Parabéns! Sua loja "{loja.nome}" foi criada com sucesso!

🏪 DADOS DA LOJA:
Nome: {loja.nome}
CNPJ: {loja.cnpj}
Email: {loja.email}
Telefone: {loja.telefone}

🔑 CREDENCIAIS DE ACESSO:
URL de Login Personalizada: {login_url_personalizada}
Usuário: {loja.email}
Senha Provisória: {loja.senha_provisoria}

⚠️ INSTRUÇÕES IMPORTANTES:
1. Acesse seu link personalizado: {login_url_personalizada}
2. Use o EMAIL DA LOJA como usuário: {loja.email}
3. Use a senha provisória fornecida acima
4. Você será obrigado a alterar a senha no primeiro acesso
5. Mantenha suas credenciais em local seguro

📧 Este é seu link exclusivo de acesso. Salve nos favoritos!

Em caso de dúvidas, entre em contato conosco:
📞 Suporte: suporte@lvksistemas.com.br

Atenciosamente,
Equipe LVK Sistemas
        """
        
        # Enviar email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [loja.email],
            html_message=html_content,
            fail_silently=False,
        )
        
        # Marcar como enviado
        loja._email_enviado = True
        
        logger.info(f"✅ Email ÚNICO com login personalizado enviado para {loja.email}")
        logger.info(f"🔗 Link personalizado: {login_url_personalizada}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar email personalizado para loja {loja.nome}: {str(e)}")
        return False


@receiver(post_save, sender=User)
def configurar_usuario_loja(sender, instance, created, **kwargs):
    """
    Configura usuário quando é criado para uma loja
    """
    if created:
        try:
            # Verificar se é admin de alguma loja
            loja = Loja.objects.filter(admin_user=instance).first()
            
            if loja:
                logger.info(f"Usuário {instance.username} configurado como admin da loja {loja.nome}")
                
                # Criar perfil de usuário se necessário
                from usuarios.models import PerfilUsuario
                perfil, created = PerfilUsuario.objects.get_or_create(
                    user=instance,
                    defaults={
                        'requires_password_change': True,  # Forçar troca de senha na primeira vez
                        'tipo_usuario': 'admin_loja'
                    }
                )
                
                if created:
                    logger.info(f"Perfil criado para admin {instance.username}")
                
        except Exception as e:
            logger.error(f"Erro ao configurar usuário {instance.username}: {str(e)}")