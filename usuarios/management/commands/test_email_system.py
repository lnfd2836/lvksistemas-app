"""
Comando para testar o sistema de envio de emails
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from usuarios.email_utils import (
    enviar_email_credenciais_usuario, 
    enviar_email_credenciais_loja,
    validar_configuracao_email,
    testar_conectividade_smtp
)
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
            choices=['basico', 'usuario', 'loja', 'diagnostico', 'conectividade'],
            help='Tipo de teste de email',
            default='diagnostico'
        )
        parser.add_argument(
            '--skip-send',
            action='store_true',
            help='Apenas valida configurações sem enviar emails'
        )

    def handle(self, *args, **options):
        email_destino = options['email']
        tipo_teste = options['tipo']
        skip_send = options['skip_send']
        
        self.stdout.write(self.style.HTTP_INFO("🧪 SISTEMA DE TESTE DE EMAIL - LVK"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"📧 Email de destino: {email_destino}")
        self.stdout.write(f"🔧 Tipo de teste: {tipo_teste}")
        if skip_send:
            self.stdout.write("⚠️  Modo: Apenas diagnóstico (sem envio)")
        
        # Executar diagnóstico
        self.executar_diagnostico()
        
        if skip_send:
            return
        
        # Executar testes específicos
        if tipo_teste == 'basico':
            self.testar_email_basico(email_destino)
        elif tipo_teste == 'usuario':
            self.testar_email_usuario(email_destino)
        elif tipo_teste == 'loja':
            self.testar_email_loja(email_destino)
        elif tipo_teste == 'conectividade':
            self.testar_conectividade()

    def executar_diagnostico(self):
        """Executa diagnóstico do sistema de email"""
        self.stdout.write(self.style.HTTP_INFO("\n🔍 DIAGNÓSTICO DO SISTEMA DE EMAIL"))
        self.stdout.write("-" * 40)
        
        # Verificar configurações
        self.stdout.write("\n📋 Verificando Configurações:")
        is_valid, errors, warnings = validar_configuracao_email()
        
        # Mostrar configurações
        self.stdout.write(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Não configurado')}")
        self.stdout.write(f"  EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Não configurado')}")
        self.stdout.write(f"  EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Não configurado')}")
        
        if errors:
            self.stdout.write(self.style.ERROR("\n❌ Erros:"))
            for error in errors:
                self.stdout.write(f"  • {error}")
        
        if warnings:
            self.stdout.write(self.style.WARNING("\n⚠️  Avisos:"))
            for warning in warnings:
                self.stdout.write(f"  • {warning}")
        
        if is_valid:
            self.stdout.write(self.style.SUCCESS("✅ Configurações válidas"))
        else:
            self.stdout.write(self.style.ERROR("❌ Configurações inválidas"))
        
        # Testar conectividade
        self.stdout.write("\n🌐 Testando Conectividade:")
        sucesso, mensagem = testar_conectividade_smtp()
        
        if sucesso:
            self.stdout.write(self.style.SUCCESS(f"✅ {mensagem}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ {mensagem}"))

    def testar_conectividade(self):
        """Testa conectividade SMTP"""
        sucesso, mensagem = testar_conectividade_smtp()
        if sucesso:
            self.stdout.write(self.style.SUCCESS(f"✅ {mensagem}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ {mensagem}"))

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