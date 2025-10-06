from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management.color import no_style
from django.utils import timezone
import secrets
import string


class Command(BaseCommand):
    help = 'Test password reset functionality for admin users'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to reset password')
        parser.add_argument('--list-admins', action='store_true', help='List all admin users')
        parser.add_argument('--test-generation', action='store_true', help='Test password generation')
    
    def handle(self, *args, **options):
        self.style = no_style()
        username = options.get('username')
        list_admins = options.get('list_admins', False)
        test_generation = options.get('test_generation', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("PASSWORD RESET TEST")
        self.stdout.write("=" * 60)
        
        if list_admins:
            self.list_admin_users()
            return
        
        if test_generation:
            self.test_password_generation()
            return
        
        if username:
            self.test_password_reset(username)
            return
        
        self.stdout.write("Use --help para ver as opções disponíveis")
    
    def list_admin_users(self):
        """List all admin users"""
        self.stdout.write("\nUSUÁRIOS SUPER ADMINISTRADORES:")
        
        admins = User.objects.filter(is_superuser=True).order_by('username')
        
        if not admins.exists():
            self.stdout.write("   Nenhum usuário super administrador encontrado")
            return
        
        for admin in admins:
            status = "ATIVO" if admin.is_active else "INATIVO"
            last_login = admin.last_login.strftime('%d/%m/%Y %H:%M') if admin.last_login else "Nunca"
            
            self.stdout.write(f"   Username: {admin.username}")
            self.stdout.write(f"   Email: {admin.email}")
            self.stdout.write(f"   Nome: {admin.first_name} {admin.last_name}")
            self.stdout.write(f"   Status: {status}")
            self.stdout.write(f"   Último login: {last_login}")
            
            # Check profile
            try:
                profile = admin.perfil
                needs_change = "SIM" if profile.requires_password_change else "NÃO"
                self.stdout.write(f"   Precisa trocar senha: {needs_change}")
            except:
                self.stdout.write(f"   Precisa trocar senha: N/A (sem perfil)")
            
            self.stdout.write("   " + "-" * 40)
    
    def test_password_generation(self):
        """Test password generation algorithm"""
        self.stdout.write("\nTESTANDO GERAÇÃO DE SENHAS:")
        
        try:
            passwords = []
            for i in range(3):
                password_chars = string.ascii_letters + string.digits + "!@#$%&*"
                password = ''.join(secrets.choice(password_chars) for _ in range(12))
                passwords.append(password)
                
                # Validate password
                has_upper = any(c.isupper() for c in password)
                has_lower = any(c.islower() for c in password)
                has_digit = any(c.isdigit() for c in password)
                has_special = any(c in "!@#$%&*" for c in password)
                
                self.stdout.write(f"   Senha {i+1}: {password}")
                self.stdout.write(f"     Comprimento: {len(password)}")
                self.stdout.write(f"     Maiúsculas: {has_upper}")
                self.stdout.write(f"     Minúsculas: {has_lower}")
                self.stdout.write(f"     Números: {has_digit}")
                self.stdout.write(f"     Símbolos: {has_special}")
                self.stdout.write("     " + "-" * 30)
            
            unique_passwords = set(passwords)
            self.stdout.write(f"\n   Senhas geradas: {len(passwords)}")
            self.stdout.write(f"   Senhas únicas: {len(unique_passwords)}")
            
            if len(unique_passwords) == len(passwords):
                self.stdout.write(self.style.SUCCESS("   ✅ Todas as senhas são únicas"))
            else:
                self.stdout.write(self.style.ERROR("   ❌ Algumas senhas são duplicadas"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erro na geração: {e}"))
    
    def test_password_reset(self, username):
        """Test password reset for specific user"""
        self.stdout.write(f"\nTESTANDO RESET DE SENHA PARA: {username}")
        
        try:
            user = User.objects.get(username=username, is_superuser=True)
            
            self.stdout.write(f"   Usuário encontrado: {user.username}")
            self.stdout.write(f"   Email: {user.email}")
            self.stdout.write(f"   Ativo: {user.is_active}")
            
            # Generate new password
            password_chars = string.ascii_letters + string.digits + "!@#$%&*"
            new_password = ''.join(secrets.choice(password_chars) for _ in range(12))
            
            self.stdout.write(f"   Nova senha gerada: {new_password}")
            
            # Simulate password change (without actually changing)
            self.stdout.write("   ✅ Simulação de alteração de senha bem-sucedida")
            
            # Check profile
            try:
                from usuarios.models import PerfilUsuario
                profile, created = PerfilUsuario.objects.get_or_create(
                    user=user,
                    defaults={
                        'is_super_admin': True,
                        'requires_password_change': True,
                        'provisional_password_created': timezone.now(),
                        'password_change_reminders_sent': 0
                    }
                )
                
                if created:
                    self.stdout.write("   ✅ Perfil criado")
                else:
                    self.stdout.write("   ✅ Perfil já existe")
                    
                self.stdout.write(f"   Precisa trocar senha: {profile.requires_password_change}")
                
            except Exception as profile_error:
                self.stdout.write(f"   ⚠️  Erro no perfil: {profile_error}")
            
            # Test email (simulation)
            self.stdout.write("   📧 Simulação de envio de email:")
            self.stdout.write(f"     Para: {user.email}")
            self.stdout.write(f"     Assunto: Nova Senha Provisória - LVK Sistemas")
            self.stdout.write(f"     Conteúdo: Credenciais com nova senha")
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"   ❌ Usuário '{username}' não encontrado ou não é super admin"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erro no teste: {e}"))