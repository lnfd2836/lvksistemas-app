"""
Comando para testar o envio de email em produção
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
    help = 'Testa o envio de email em produção'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de destino para teste',
            required=True
        )

    def handle(self, *args, **options):
        email_destino = options['email']
        
        self.stdout.write(f"🧪 Testando sistema de email em produção...")
        self.stdout.write(f"📧 Email de destino: {email_destino}")
        
        # Verificar configurações
        self.stdout.write("\n📋 Configurações:")
        self.stdout.write(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Não configurado')}")
        self.stdout.write(f"  EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Não configurado')}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Não configurado')}")
        
        # Teste 1: Email básico
        self.stdout.write("\n🔍 Teste 1: Email básico...")
        try:
            send_mail(
                subject='✅ Teste Sistema LVK - Email Funcionando',
                message=f'''
Olá!

Este é um email de teste do sistema LVK Sistemas.

✅ O sistema de envio de emails está funcionando corretamente!

Detalhes do teste:
- Data/Hora: {timezone.now().strftime('%d/%m/%Y às %H:%M')}
- Servidor: Heroku (Produção)
- Email de origem: {settings.DEFAULT_FROM_EMAIL}

Atenciosamente,
Sistema LVK
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_destino],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("✅ Email básico enviado com sucesso!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro no email básico: {e}"))
            return
        
        # Teste 2: Email de credenciais de usuário
        self.stdout.write("\n🔍 Teste 2: Email de credenciais de usuário...")
        try:
            from django.utils import timezone
            user_test = User(
                username='teste_usuario',
                email=email_destino,
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
                self.stdout.write(self.style.SUCCESS("✅ Email de credenciais de usuário enviado!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Falha no email de credenciais de usuário"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro no email de usuário: {e}"))
        
        # Teste 3: Email de credenciais de loja
        self.stdout.write("\n🔍 Teste 3: Email de credenciais de loja...")
        try:
            loja_test = Loja(
                nome='Loja Teste Sistema',
                email=email_destino,
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
                self.stdout.write(self.style.SUCCESS("✅ Email de credenciais de loja enviado!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Falha no email de credenciais de loja"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro no email de loja: {e}"))
        
        self.stdout.write(f"\n🎉 Teste concluído! Verifique a caixa de entrada de {email_destino}")
        self.stdout.write("📝 Nota: Verifique também a pasta de spam/lixo eletrônico")