"""
Comando para testar o sistema de envio de emails
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from usuarios.email_utils import enviar_email_credenciais_usuario, enviar_email_credenciais_loja
from lojas.models import Loja
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Testa o sistema de envio de emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de destino para teste',
            default='test@example.com'
        )
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['basico', 'usuario', 'loja'],
            help='Tipo de teste de email',
            default='basico'
        )

    def handle(self, *args, **options):
        email_destino = options['email']
        tipo_teste = options['tipo']
        
        self.stdout.write(f"🧪 Testando sistema de email...")
        self.stdout.write(f"📧 Email de destino: {email_destino}")
        self.stdout.write(f"🔧 Tipo de teste: {tipo_teste}")
        
        # Verificar configurações de email
        self.stdout.write("\n📋 Configurações de Email:")
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Não configurado')}")
        self.stdout.write(f"  EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Não configurado')}")
        self.stdout.write(f"  EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Não configurado')}")
        self.stdout.write(f"  EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Não configurado')}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Não configurado')}")
        
        if tipo_teste == 'basico':
            self.testar_email_basico(email_destino)
        elif tipo_teste == 'usuario':
            self.testar_email_usuario(email_destino)
        elif tipo_teste == 'loja':
            self.testar_email_loja(email_destino)

    def testar_email_basico(self, email_destino):
        """Testa envio de email básico"""
        self.stdout.write("\n🔍 Testando envio de email básico...")
        
        try:
            send_mail(
                subject='Teste de Email - Sistema LVK',
                message='Este é um email de teste do sistema LVK.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_destino],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("✅ Email básico enviado com sucesso!"))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao enviar email básico: {e}"))
            return False

    def testar_email_usuario(self, email_destino):
        """Testa envio de email de credenciais de usuário"""
        self.stdout.write("\n🔍 Testando envio de email de credenciais de usuário...")
        
        try:
            # Criar usuário temporário para teste
            user_test = User(
                username='test_user',
                email=email_destino,
                first_name='Usuário',
                last_name='Teste',
                is_superuser=True
            )
            
            sucesso = enviar_email_credenciais_usuario(
                user=user_test,
                senha_provisoria='senha123teste',
                tipo_usuario='Super Administrador'
            )
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS("✅ Email de credenciais de usuário enviado com sucesso!"))
                return True
            else:
                self.stdout.write(self.style.ERROR("❌ Falha ao enviar email de credenciais de usuário"))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao enviar email de credenciais de usuário: {e}"))
            return False

    def testar_email_loja(self, email_destino):
        """Testa envio de email de credenciais de loja"""
        self.stdout.write("\n🔍 Testando envio de email de credenciais de loja...")
        
        try:
            # Criar loja temporária para teste
            loja_test = Loja(
                nome='Loja Teste',
                email=email_destino,
                cnpj='12.345.678/0001-90',
                endereco='Rua Teste, 123',
                cidade='São Paulo',
                estado='SP',
                cep='01234-567',
                telefone='(11) 99999-9999',
                senha_provisoria='loja123teste'
            )
            
            sucesso = enviar_email_credenciais_loja(
                loja=loja_test,
                senha_provisoria='loja123teste'
            )
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS("✅ Email de credenciais de loja enviado com sucesso!"))
                return True
            else:
                self.stdout.write(self.style.ERROR("❌ Falha ao enviar email de credenciais de loja"))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao enviar email de credenciais de loja: {e}"))
            return False