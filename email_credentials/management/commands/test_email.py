"""
Comando para testar o sistema de email
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from avaliacao_qualidade.models import PerfilUsuario
from lojas.models import Loja


class Command(BaseCommand):
    help = 'Testa o sistema de envio de emails'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email para enviar teste'
        )
        parser.add_argument(
            '--test-user-creation',
            action='store_true',
            help='Testar criação de usuário com envio de email'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📧 Testando Sistema de Email')
        )
        
        # Mostrar configurações atuais
        self.stdout.write(f'\n⚙️ Configurações:')
        self.stdout.write(f'  Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  Host: {getattr(settings, "EMAIL_HOST", "N/A")}')
        self.stdout.write(f'  Port: {getattr(settings, "EMAIL_PORT", "N/A")}')
        self.stdout.write(f'  User: {getattr(settings, "EMAIL_HOST_USER", "N/A") or "(vazio)"}')
        self.stdout.write(f'  From: {settings.DEFAULT_FROM_EMAIL}')
        
        # Teste básico de email
        email_destino = options.get('email', 'teste@exemplo.com')
        
        self.stdout.write(f'\n🧪 Teste 1: Email básico para {email_destino}')
        
        try:
            send_mail(
                'Teste Sistema FATESA - Email Funcionando',
                f'''Este é um teste do sistema de email da FATESA.

Data/Hora: {self.get_timestamp()}
Backend: {settings.EMAIL_BACKEND}

Se você recebeu este email, o sistema está funcionando corretamente!

Atenciosamente,
Sistema FATESA''',
                settings.DEFAULT_FROM_EMAIL,
                [email_destino],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS('  ✅ Email básico enviado com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Erro ao enviar email básico: {str(e)}')
            )
        
        # Teste de criação de usuário
        if options['test_user_creation']:
            self.stdout.write(f'\n🧪 Teste 2: Criação de usuário com email')
            
            try:
                # Obter loja FATESA
                loja_fatesa = Loja.objects.filter(nome__icontains='fatesa').first()
                
                if not loja_fatesa:
                    self.stdout.write(
                        self.style.ERROR('  ❌ Loja FATESA não encontrada')
                    )
                    return
                
                # Criar usuário de teste
                from avaliacao_qualidade.forms import CadastroUsuarioForm
                
                form_data = {
                    'username': f'teste_email_{self.get_timestamp_short()}',
                    'email': email_destino,
                    'nome_completo': 'Usuário Teste Email',
                    'tipo_perfil': 'professor',
                    'telefone': '(11) 99999-9999',
                    'especialidade': 'Teste de Email',
                }
                
                form = CadastroUsuarioForm(data=form_data)
                
                if form.is_valid():
                    user = form.save(loja_associada=loja_fatesa)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Usuário criado: {user.username}')
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Email enviado para: {user.email}')
                    )
                    
                    # Limpar usuário de teste
                    user.delete()
                    self.stdout.write('  🗑️ Usuário de teste removido')
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Formulário inválido: {form.errors}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Erro no teste de usuário: {str(e)}')
                )
        
        # Instruções
        self.stdout.write(f'\n📋 Instruções:')
        
        if 'console' in settings.EMAIL_BACKEND:
            self.stdout.write('  📺 Modo Console: Emails aparecem no terminal')
            self.stdout.write('  ⚙️ Para produção: Configure EMAIL_HOST_USER e EMAIL_HOST_PASSWORD')
        else:
            self.stdout.write('  📧 Modo SMTP: Emails são enviados via servidor')
            self.stdout.write('  📬 Verifique a caixa de entrada do destinatário')
        
        self.stdout.write(f'\n🎉 Teste concluído!')
    
    def get_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime('%d/%m/%Y %H:%M:%S')
    
    def get_timestamp_short(self):
        from django.utils import timezone
        return timezone.now().strftime('%H%M%S')