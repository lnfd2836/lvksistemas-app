"""
Comando para resetar credenciais de admin no Heroku
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class Command(BaseCommand):
    help = 'Reseta credenciais de admin no Heroku'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username do admin (padrão: admin)'
        )
        
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@LVK2024!',
            help='Nova senha (padrão: Admin@LVK2024!)'
        )
        
        parser.add_argument(
            '--create-all',
            action='store_true',
            help='Criar/resetar todos os usuários admin'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        create_all = options['create_all']
        
        self.stdout.write(
            self.style.SUCCESS('🔧 Resetando credenciais de admin no Heroku')
        )
        
        if create_all:
            self.create_all_admins()
        else:
            self.reset_single_admin(username, password)
    
    def reset_single_admin(self, username, password):
        """Reseta um único admin"""
        try:
            # Tentar encontrar usuário
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f'✅ Usuário "{username}" encontrado')
            except User.DoesNotExist:
                # Criar usuário
                user = User.objects.create_superuser(
                    username=username,
                    email='admin@lvksistemas.com.br',
                    password=password
                )
                self.stdout.write(f'✅ Usuário "{username}" criado')
            
            # Resetar senha e permissões
            user.set_password(password)
            user.is_active = True
            user.is_superuser = True
            user.is_staff = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'🔑 Senha resetada para "{username}"')
            )
            
            # Testar login
            test_user = authenticate(username=username, password=password)
            if test_user:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Login testado com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Teste de login falhou')
                )
            
            # Mostrar credenciais
            self.stdout.write('\n🔐 CREDENCIAIS:')
            self.stdout.write(f'👤 Username: {username}')
            self.stdout.write(f'🔑 Password: {password}')
            self.stdout.write(f'📧 Email: {user.email}')
            self.stdout.write(f'🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro: {str(e)}')
            )
    
    def create_all_admins(self):
        """Cria/reseta todos os admins"""
        admins = [
            {
                'username': 'admin',
                'password': 'Admin@LVK2024!',
                'email': 'admin@lvksistemas.com.br'
            },
            {
                'username': 'superadmin',
                'password': 'SuperAdmin@LVK2024!', 
                'email': 'admin@lvksistemas.com.br'
            },
            {
                'username': 'luiz',
                'password': 'Luiz@LVK2024!',
                'email': 'pjluiz25@hotmail.com'
            }
        ]
        
        success_count = 0
        
        for admin_data in admins:
            try:
                username = admin_data['username']
                password = admin_data['password']
                email = admin_data['email']
                
                # Criar ou atualizar usuário
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'is_superuser': True,
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                # Resetar senha
                user.set_password(password)
                user.is_active = True
                user.is_superuser = True
                user.is_staff = True
                user.email = email
                user.save()
                
                action = 'criado' if created else 'atualizado'
                self.stdout.write(f'✅ {username}: {action}')
                success_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro com {username}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 {success_count} admins configurados!')
        )
        
        # Mostrar todas as credenciais
        self.stdout.write('\n🔐 CREDENCIAIS DISPONÍVEIS:')
        self.stdout.write('-' * 30)
        
        for admin_data in admins:
            username = admin_data['username']
            password = admin_data['password']
            
            try:
                user = User.objects.get(username=username)
                if user.is_active and user.is_superuser:
                    self.stdout.write(f'👤 {username} | 🔑 {password}')
            except User.DoesNotExist:
                pass
        
        self.stdout.write(f'\n🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/')
        self.stdout.write(f'💡 RECOMENDAÇÃO: Use admin / Admin@LVK2024!')