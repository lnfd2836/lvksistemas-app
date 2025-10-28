"""
Comando para configurar email do Gmail
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import re


class Command(BaseCommand):
    help = 'Ajuda a configurar email do Gmail'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Seu email do Gmail (ex: seuemail@gmail.com)'
        )
        parser.add_argument(
            '--senha-app',
            type=str,
            help='Senha de app do Gmail (16 caracteres)'
        )
        parser.add_argument(
            '--testar',
            action='store_true',
            help='Testar configuração após configurar'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("📧 CONFIGURADOR DE EMAIL GMAIL - LVK"))
        self.stdout.write("=" * 50)
        
        # Mostrar instruções
        self.mostrar_instrucoes()
        
        # Se argumentos foram fornecidos, configurar
        if options['email'] and options['senha_app']:
            self.configurar_email(options['email'], options['senha_app'])
            
            if options['testar']:
                self.testar_configuracao(options['email'])
        else:
            # Modo interativo
            self.configurar_interativo()

    def mostrar_instrucoes(self):
        """Mostra instruções para configurar Gmail"""
        self.stdout.write(self.style.HTTP_INFO("\n📋 INSTRUÇÕES PARA CONFIGURAR GMAIL:"))
        self.stdout.write("-" * 40)
        
        self.stdout.write("\n1️⃣ ATIVAR VERIFICAÇÃO EM 2 ETAPAS:")
        self.stdout.write("   • Acesse: https://myaccount.google.com/security")
        self.stdout.write("   • Ative a 'Verificação em 2 etapas'")
        
        self.stdout.write("\n2️⃣ CRIAR SENHA DE APP:")
        self.stdout.write("   • Acesse: https://myaccount.google.com/apppasswords")
        self.stdout.write("   • Clique em 'Gerar senha de app'")
        self.stdout.write("   • Escolha 'Outro (nome personalizado)'")
        self.stdout.write("   • Digite: 'LVK Sistemas'")
        self.stdout.write("   • Copie a senha de 16 caracteres gerada")
        
        self.stdout.write("\n3️⃣ CONFIGURAR NO SISTEMA:")
        self.stdout.write("   • Use este comando ou edite o arquivo .env")
        
        self.stdout.write(self.style.WARNING("\n⚠️  IMPORTANTE:"))
        self.stdout.write("   • NÃO use sua senha normal do Gmail")
        self.stdout.write("   • Use APENAS a senha de app de 16 caracteres")
        self.stdout.write("   • A senha de app não tem espaços")

    def configurar_interativo(self):
        """Configuração interativa"""
        self.stdout.write(self.style.HTTP_INFO("\n🔧 CONFIGURAÇÃO INTERATIVA"))
        self.stdout.write("-" * 30)
        
        try:
            # Solicitar email
            email = input("\n📧 Digite seu email do Gmail: ").strip()
            if not self.validar_email(email):
                self.stdout.write(self.style.ERROR("❌ Email inválido!"))
                return
            
            # Solicitar senha de app
            senha_app = input("🔐 Digite a senha de app (16 caracteres): ").strip()
            if not self.validar_senha_app(senha_app):
                self.stdout.write(self.style.ERROR("❌ Senha de app inválida! Deve ter 16 caracteres."))
                return
            
            # Configurar
            self.configurar_email(email, senha_app)
            
            # Perguntar se quer testar
            testar = input("\n🧪 Testar configuração agora? (s/n): ").strip().lower()
            if testar in ['s', 'sim', 'y', 'yes']:
                self.testar_configuracao(email)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n\n⚠️  Configuração cancelada pelo usuário."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Erro durante configuração: {e}"))

    def configurar_email(self, email, senha_app):
        """Configura email no arquivo .env"""
        self.stdout.write(self.style.HTTP_INFO(f"\n🔧 Configurando email: {email}"))
        
        try:
            env_path = os.path.join(settings.BASE_DIR, '.env')
            
            # Ler arquivo .env atual
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    content = f.read()
            else:
                content = ""
            
            # Atualizar configurações
            updates = {
                'EMAIL_HOST_USER': email,
                'EMAIL_HOST_PASSWORD': senha_app,
                'DEFAULT_FROM_EMAIL': email,
            }
            
            for key, value in updates.items():
                pattern = rf'^{key}=.*$'
                replacement = f'{key}={value}'
                
                if re.search(pattern, content, re.MULTILINE):
                    # Atualizar linha existente
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                else:
                    # Adicionar nova linha
                    content += f'\n{replacement}'
            
            # Salvar arquivo
            with open(env_path, 'w') as f:
                f.write(content)
            
            self.stdout.write(self.style.SUCCESS("✅ Configurações salvas no arquivo .env"))
            self.stdout.write(self.style.WARNING("⚠️  REINICIE o servidor Django para aplicar as mudanças!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao salvar configurações: {e}"))

    def testar_configuracao(self, email_destino):
        """Testa a configuração de email"""
        self.stdout.write(self.style.HTTP_INFO(f"\n🧪 Testando envio para: {email_destino}"))
        
        try:
            from django.core.mail import send_mail
            
            send_mail(
                subject='✅ Teste de Email - LVK Sistemas',
                message=f'''
🎉 Parabéns! Seu email foi configurado com sucesso!

📧 Email configurado: {email_destino}
🕐 Data/Hora: {self.get_current_datetime()}
🖥️  Sistema: LVK Sistemas

Este é um email de teste para confirmar que as configurações estão funcionando corretamente.

---
LVK Sistemas
suporte@lvksistemas.com.br
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_destino],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS("✅ Email de teste enviado com sucesso!"))
            self.stdout.write(f"📧 Verifique a caixa de entrada de: {email_destino}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao enviar email de teste: {e}"))
            self.mostrar_solucoes_erro(str(e))

    def validar_email(self, email):
        """Valida formato do email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        return re.match(pattern, email) is not None

    def validar_senha_app(self, senha):
        """Valida senha de app do Gmail"""
        # Remove espaços e verifica se tem 16 caracteres
        senha_limpa = senha.replace(' ', '')
        return len(senha_limpa) == 16 and senha_limpa.isalnum()

    def get_current_datetime(self):
        """Retorna data/hora atual formatada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def mostrar_solucoes_erro(self, erro):
        """Mostra soluções para erros comuns"""
        self.stdout.write(self.style.WARNING("\n🔧 POSSÍVEIS SOLUÇÕES:"))
        
        if "authentication" in erro.lower() or "username" in erro.lower():
            self.stdout.write("   • Verifique se o email está correto")
            self.stdout.write("   • Verifique se a senha de app está correta")
            self.stdout.write("   • Certifique-se que a verificação em 2 etapas está ativa")
            
        elif "connection" in erro.lower() or "timeout" in erro.lower():
            self.stdout.write("   • Verifique sua conexão com a internet")
            self.stdout.write("   • Tente novamente em alguns minutos")
            
        elif "ssl" in erro.lower() or "tls" in erro.lower():
            self.stdout.write("   • Verifique as configurações de TLS/SSL")
            
        self.stdout.write("\n📞 Se o problema persistir:")
        self.stdout.write("   • Contate: suporte@lvksistemas.com.br")
        self.stdout.write("   • Ou execute: python manage.py test_email_system --tipo=diagnostico")