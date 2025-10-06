from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management.color import no_style


class Command(BaseCommand):
    help = 'Check admin users and their login credentials'
    
    def add_arguments(self, parser):
        parser.add_argument('--reset-password', type=str, help='Reset password for specific username')
        parser.add_argument('--create-admin', action='store_true', help='Create new admin user')
    
    def handle(self, *args, **options):
        self.style = no_style()
        reset_user = options.get('reset_password')
        create_admin = options.get('create_admin')
        
        self.stdout.write("=" * 60)
        self.stdout.write("ADMIN USERS CHECK")
        self.stdout.write("=" * 60)
        
        if create_admin:
            self.create_admin_user()
            return
        
        if reset_user:
            self.reset_user_password(reset_user)
            return
        
        # Check existing admin users
        self.check_admin_users()
        
        self.stdout.write("=" * 60)
        self.stdout.write("ADMIN CHECK COMPLETE")
        self.stdout.write("=" * 60)
    
    def check_admin_users(self):
        """Check all admin users in the system"""
        self.stdout.write("\n1. CHECKING SUPERUSERS:")
        
        superusers = User.objects.filter(is_superuser=True)
        
        if superusers.exists():
            for user in superusers:
                self.stdout.write(f"   Username: {user.username}")
                self.stdout.write(f"   Email: {user.email}")
                self.stdout.write(f"   Active: {user.is_active}")
                self.stdout.write(f"   Staff: {user.is_staff}")
                self.stdout.write(f"   Last login: {user.last_login}")
                
                # Check if user has profile
                try:
                    profile = user.perfil
                    self.stdout.write(f"   Has profile: Yes")
                    self.stdout.write(f"   Super admin: {profile.is_super_admin}")
                    self.stdout.write(f"   Needs password change: {profile.requires_password_change}")
                except:
                    self.stdout.write(f"   Has profile: No")
                
                self.stdout.write("   " + "-" * 40)
        else:
            self.stdout.write(self.style.ERROR("   ❌ No superusers found!"))
        
        self.stdout.write("\n2. CHECKING STAFF USERS:")
        
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        
        if staff_users.exists():
            for user in staff_users:
                self.stdout.write(f"   Username: {user.username}")
                self.stdout.write(f"   Email: {user.email}")
                self.stdout.write(f"   Active: {user.is_active}")
                self.stdout.write("   " + "-" * 40)
        else:
            self.stdout.write("   No staff users found")
        
        self.stdout.write("\n3. CHECKING USERS WITH ADMIN PROFILES:")
        
        try:
            from usuarios.models import PerfilUsuario
            admin_profiles = PerfilUsuario.objects.filter(is_super_admin=True)
            
            if admin_profiles.exists():
                for profile in admin_profiles:
                    user = profile.user
                    self.stdout.write(f"   Username: {user.username}")
                    self.stdout.write(f"   Email: {user.email}")
                    self.stdout.write(f"   Active: {user.is_active}")
                    self.stdout.write(f"   Superuser: {user.is_superuser}")
                    self.stdout.write(f"   Needs password change: {profile.requires_password_change}")
                    self.stdout.write("   " + "-" * 40)
            else:
                self.stdout.write("   No admin profiles found")
        except Exception as e:
            self.stdout.write(f"   Error checking profiles: {e}")
        
        # Show common usernames to try
        self.stdout.write("\n4. COMMON ADMIN USERNAMES TO TRY:")
        common_usernames = ['admin', 'administrator', 'root', 'luiz', 'lvk', 'sistema']
        
        for username in common_usernames:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(self.style.SUCCESS(f"   ✅ {username} - EXISTS"))
            except User.DoesNotExist:
                self.stdout.write(f"   ❌ {username} - not found")
    
    def reset_user_password(self, username):
        """Reset password for a specific user"""
        self.stdout.write(f"\nRESETTING PASSWORD FOR: {username}")
        
        try:
            user = User.objects.get(username=username)
            
            # Generate new password
            import secrets
            import string
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Update profile if exists
            try:
                profile = user.perfil
                profile.requires_password_change = True
                profile.provisional_password_created = timezone.now()
                profile.save()
                self.stdout.write("   Profile updated to require password change")
            except:
                self.stdout.write("   No profile found for user")
            
            self.stdout.write(self.style.SUCCESS(f"✅ Password reset successfully!"))
            self.stdout.write(f"   Username: {username}")
            self.stdout.write(f"   New password: {new_password}")
            self.stdout.write("   ⚠️  Save this password securely!")
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User '{username}' not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error resetting password: {e}"))
    
    def create_admin_user(self):
        """Create a new admin user"""
        self.stdout.write("\nCREATING NEW ADMIN USER:")
        
        try:
            # Check if admin already exists
            if User.objects.filter(username='admin').exists():
                self.stdout.write(self.style.WARNING("User 'admin' already exists"))
                return
            
            # Generate password
            import secrets
            import string
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            # Create user
            user = User.objects.create_superuser(
                username='admin',
                email='admin@lvksistemas.com.br',
                password=password
            )
            
            # Create profile
            from usuarios.models import PerfilUsuario
            from django.utils import timezone
            
            profile = PerfilUsuario.objects.create(
                user=user,
                is_super_admin=True,
                requires_password_change=True,
                provisional_password_created=timezone.now()
            )
            
            self.stdout.write(self.style.SUCCESS("✅ Admin user created successfully!"))
            self.stdout.write(f"   Username: admin")
            self.stdout.write(f"   Email: admin@lvksistemas.com.br")
            self.stdout.write(f"   Password: {password}")
            self.stdout.write("   ⚠️  Save this password securely!")
            self.stdout.write("   User will be required to change password on first login")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating admin user: {e}"))