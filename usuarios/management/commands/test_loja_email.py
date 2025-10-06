"""
Comando para testar envio de email de credenciais de loja
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from lojas.models import Loja
from usuarios.email_utils import enviar_email_credenciais_loja
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Testa o envio de email de credenciais para uma loja específica'

    def add_arguments(self, parser):
        parser.add_argument('--loja-id', type=str, help='ID da loja para testar')
        parser.add_argument('--email', type=str, help='Email para teste')

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testando envio de email de credenciais de loja...')
        
        # Verifica configurações de email
        self.stdout.write(f'📧 Configurações de email:')
        self.stdout.write(f'   EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Não configurado")}')
        self.stdout.write(f'   EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "Não configurado")}')
        self.stdout.write(f'   DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "Não configurado")}')
        
        if options['loja_id']:
            try:
                loja = Loja.objects.get(id=options['loja_id'])
                self.stdout.write(f'🏪 Loja encontrada: {loja.nome}')
                self.stdout.write(f'📧 Email da loja: {loja.email}')
                self.stdout.write(f'🔑 Senha provisória: {loja.senha_provisoria}')
                
                # Testa envio de email
                sucesso = enviar_email_credenciais_loja(loja, loja.senha_provisoria)
                
                if sucesso:
                    self.stdout.write(self.style.SUCCESS('✅ Email enviado com sucesso!'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Falha ao enviar email'))
                    
            except Loja.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Loja com ID {options["loja_id"]} não encontrada'))
        
        elif options['email']:
            # Cria loja de teste
            loja_teste = type('LojaTest', (), {
                'nome': 'Loja de Teste',
                'email': options['email'],
                'senha_provisoria': 'teste123456'
            })()
            
            self.stdout.write(f'🧪 Testando com email: {options["email"]}')
            
            # Testa envio de email
            sucesso = enviar_email_credenciais_loja(loja_teste, 'teste123456')
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS('✅ Email de teste enviado com sucesso!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Falha ao enviar email de teste'))
        
        else:
            # Lista lojas recentes
            lojas_recentes = Loja.objects.order_by('-data_criacao')[:5]
            
            self.stdout.write('🏪 Lojas recentes:')
            for loja in lojas_recentes:
                self.stdout.write(f'   ID: {loja.id} | Nome: {loja.nome} | Email: {loja.email}')
            
            self.stdout.write('\n💡 Use --loja-id <ID> para testar uma loja específica')
            self.stdout.write('💡 Use --email <email> para testar com um email específico')