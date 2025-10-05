"""
Comando para testar o sistema de emails
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.email_utils import enviar_email_credenciais_usuario, enviar_email_credenciais_loja
from lojas.models import Loja
import secrets
import string


class Command(BaseCommand):
    help = 'Testa o sistema de envio de emails'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email para teste')
        parser.add_argument('--tipo', type=str, choices=['usuario', 'loja'], help='Tipo de teste')

    def handle(self, *args, **options):
        email = options.get('email', 'teste@lvksistemas.com.br')
        tipo = options.get('tipo', 'usuario')
        
        if tipo == 'usuario':
            self.testar_email_usuario(email)
        elif tipo == 'loja':
            self.testar_email_loja(email)

    def testar_email_usuario(self, email):
        """Testa envio de email para usuário"""
        try:
            # Cria usuário temporário para teste
            user = User.objects.create_user(
                username='teste_email',
                email=email,
                first_name='Usuário',
                last_name='Teste',
                is_superuser=True,
                is_staff=True
            )
            
            # Gera senha provisória
            alphabet = string.ascii_letters + string.digits
            senha_provisoria = ''.join(secrets.choice(alphabet) for _ in range(12))
            
            # Envia email
            sucesso = enviar_email_credenciais_usuario(
                user=user,
                senha_provisoria=senha_provisoria,
                tipo_usuario='Super Administrador'
            )
            
            if sucesso:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Email de teste enviado com sucesso para {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Falha ao enviar email para {email}')
                )
            
            # Remove usuário de teste
            user.delete()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao testar email: {e}')
            )

    def testar_email_loja(self, email):
        """Testa envio de email para loja"""
        try:
            # Cria usuário temporário para teste
            admin_user = User.objects.create_user(
                username=email,
                email=email,
                first_name='Admin',
                last_name='Loja Teste'
            )
            
            # Cria loja temporária para teste
            loja = Loja.objects.create(
                nome='Loja Teste Email',
                cnpj='12.345.678/0001-90',
                email=email,
                telefone='(11) 99999-9999',
                endereco='Endereço Teste',
                cidade='São Paulo',
                estado='SP',
                cep='01234-567',
                admin_user=admin_user
            )
            
            # Envia email
            sucesso = enviar_email_credenciais_loja(
                loja=loja,
                senha_provisoria=loja.senha_provisoria
            )
            
            if sucesso:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Email de loja enviado com sucesso para {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Falha ao enviar email de loja para {email}')
                )
            
            # Remove dados de teste
            loja.delete()
            admin_user.delete()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao testar email de loja: {e}')
            )
