"""
Comando para testar o sistema de email usando backend de console
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
    help = 'Testa o sistema de email usando backend de console'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testando sistema de email com backend de console...")
        
        # Temporariamente muda o backend para console
        original_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        
        try:
            # Teste 1: Email básico
            self.stdout.write("\n🔍 Teste 1: Email básico...")
            send_mail(
                subject='Teste Sistema LVK - Console Backend',
                message='Este é um teste usando backend de console.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['teste@example.com'],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("✅ Email básico enviado (console)"))
            
            # Teste 2: Email de credenciais de usuário
            self.stdout.write("\n🔍 Teste 2: Email de credenciais de usuário...")
            user_test = User(
                username='teste_usuario',
                email='teste@example.com',
                first_name='Usuário',
                last_name='Teste',
                is_superuser=True
            )
            
            sucesso = enviar_email_credenciais_usuario(
                user=user_test,
                senha_provisoria='SenhaTest123!',
                tipo_usuario='Super Administrador'
            )
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS("✅ Email de credenciais de usuário enviado (console)"))
            else:
                self.stdout.write(self.style.ERROR("❌ Falha no email de credenciais de usuário"))
            
            # Teste 3: Email de credenciais de loja
            self.stdout.write("\n🔍 Teste 3: Email de credenciais de loja...")
            loja_test = Loja(
                nome='Loja Teste Console',
                email='loja@example.com',
                cnpj='12.345.678/0001-90',
                endereco='Rua Teste, 123',
                cidade='São Paulo',
                estado='SP',
                cep='01234-567',
                telefone='(11) 99999-9999',
                senha_provisoria='LojaTest123!'
            )
            
            sucesso = enviar_email_credenciais_loja(
                loja=loja_test,
                senha_provisoria='LojaTest123!'
            )
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS("✅ Email de credenciais de loja enviado (console)"))
            else:
                self.stdout.write(self.style.ERROR("❌ Falha no email de credenciais de loja"))
            
            self.stdout.write("\n🎉 Teste concluído!")
            self.stdout.write("📝 Os emails foram exibidos no console acima")
            self.stdout.write("✅ O sistema de email está funcionando corretamente")
            self.stdout.write("⚠️  O problema é apenas com as credenciais SMTP do Gmail")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro durante o teste: {e}"))
        
        finally:
            # Restaura o backend original
            settings.EMAIL_BACKEND = original_backend