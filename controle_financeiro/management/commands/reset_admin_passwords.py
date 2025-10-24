"""
Comando Django para resetar senhas de administradores
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class Command(BaseCommand):
    help = 'Reseta senhas dos usuários administradores'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Criar usuários que não existem'
        )
        
        parser.add_argument(
            '--test-auth',
            action='store_true',
            help='Testar autenticação após reset'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("=== RESET DE SENHAS DE ADMINISTRADORES ==="))
        
        # Lista de usuários para resetar/criar
        usuarios_admin = [
            ('admin', 'admin123', 'admin@lvksistemas.com.br'),
            ('superadmin', 'super123', 'admin@lvksistemas.com.br'),
            ('teste', '123', 'teste@lvk.com'),
            ('lvkadmin', 'lvk2024', 'admin@lvksistemas.com.br'),
        ]
        
        for username, password, email in usuarios_admin:
            self.stdout.write(f"\n--- Processando usuário: {username} ---")
            
            try:
                # Tentar encontrar usuário existente
                user = User.objects.get(username=username)
                self.stdout.write(f"✅ Usuário {username} encontrado")
                
                # Resetar senha
                user.set_password(password)
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.email = email
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Senha do {username} resetada para: {password}")
                )
                
            except User.DoesNotExist:
                if options['create_missing']:
                    # Criar usuário
                    user = User.objects.create_superuser(
                        username=username,
                        email=email,
                        password=password
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Usuário {username} criado com senha: {password}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ Usuário {username} não existe (use --create-missing para criar)")
                    )
                    continue
            
            # Testar autenticação se solicitado
            if options['test_auth']:
                test_user = authenticate(username=username, password=password)
                if test_user:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Autenticação do {username} funcionando")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Problema na autenticação do {username}")
                    )
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.HTTP_INFO("CREDENCIAIS ATUALIZADAS:"))
        self.stdout.write("admin / admin123")
        self.stdout.write("superadmin / super123") 
        self.stdout.write("teste / 123")
        self.stdout.write("lvkadmin / lvk2024")
        self.stdout.write("=" * 60)
        
        # Mostrar estatísticas
        total_users = User.objects.count()
        super_users = User.objects.filter(is_superuser=True).count()
        
        self.stdout.write(f"\n📊 ESTATÍSTICAS:")
        self.stdout.write(f"Total de usuários: {total_users}")
        self.stdout.write(f"Super admins: {super_users}")
        
        # Listar todos os super admins
        self.stdout.write(f"\n👥 SUPER ADMINS NO SISTEMA:")
        for user in User.objects.filter(is_superuser=True):
            status = "✅ Ativo" if user.is_active else "❌ Inativo"
            self.stdout.write(f"- {user.username} ({user.email}) - {status}")
        
        self.stdout.write(
            self.style.SUCCESS("\n🎉 Reset de senhas concluído!")
        )