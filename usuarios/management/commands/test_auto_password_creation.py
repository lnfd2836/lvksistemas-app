from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management.color import no_style
from django.utils import timezone
import secrets
import string


class Command(BaseCommand):
    help = 'Test automatic password generation for admin users'
    
    def add_arguments(self, parser):
        parser.add_argument('--create-test', action='store_true', help='Create a test admin user')
        parser.add_argument('--cleanup', action='store_true', help='Remove test users')
    
    def handle(self, *args, **options):
        self.style = no_style()
        create_test = options.get('create_test', False)
        cleanup = options.get('cleanup', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("AUTO PASSWORD CREATION TEST")
        self.stdout.write("=" * 60)
        
        if cleanup:
            self.cleanup_test_users()
            return
        
        if create_test:
            self.create_test_admin()
            return
        
        # Test password generation
        self.test_password_generation()
        
        self.stdout.write("=" * 60)
        self.stdout.write("TEST COMPLETE")
        self.stdout.write("=" * 60)
    
    def test_password_generation(self):
        """Test password generation algorithm"""
        self.stdout.write("\n1. TESTING PASSWORD GENERATION:")
        
        try:
            # Generate multiple passwords to test
            passwords = []
            for i in range(5):
                password_chars = string.ascii_letters + string.digits + "!@#$%&*"
                password = ''.join(secrets.choice(password_chars) for _ in range(12))
                passwords.append(password)
                
                # Validate password strength
                has_upper = any(c.isupper() for c in password)
                has_lower = any(c.islower() for c in password)
                has_digit = any(c.isdigit() for c in password)
                has_special = any(c in "!@#$%&*" for c in password)
                
                self.stdout.write(f"   Password {i+1}: {password}")
                self.stdout.write(f"     Length: {len(password)}")
                self.stdout.write(f"     Has uppercase: {has_upper}")
                self.stdout.write(f"     Has lowercase: {has_lower}")
                self.stdout.write(f"     Has digits: {has_digit}")
                self.stdout.write(f"     Has special chars: {has_special}")
                self.stdout.write("     " + "-" * 30)
            
            # Check uniqueness
            unique_passwords = set(passwords)
            self.stdout.write(f"\n   Generated {len(passwords)} passwords")
            self.stdout.write(f"   Unique passwords: {len(unique_passwords)}")
            
            if len(unique_passwords) == len(passwords):
                self.stdout.write(self.style.SUCCESS("   ✅ All passwords are unique"))
            else:
                self.stdout.write(self.style.ERROR("   ❌ Some passwords are duplicated"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Password generation failed: {e}"))
    
    def create_test_admin(self):
        """Create a test admin user with auto-generated password"""
        self.stdout.write("\n2. CREATING TEST ADMIN USER:")
        
        try:
            from django.db import transaction
            
            # Generate unique username
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            username = f"test_admin_{timestamp}"
            email = f"{username}@test.com"
            
            with transaction.atomic():
                # Generate password
                password_chars = string.ascii_letters + string.digits + "!@#$%&*"
                provisional_password = ''.join(secrets.choice(password_chars) for _ in range(12))
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=provisional_password,
                    first_name="Test",
                    last_name="Admin",
                    is_superuser=True,
                    is_staff=True,
                    is_active=True
                )
                
                # Create profile
                from usuarios.models import PerfilUsuario
                profile = PerfilUsuario.objects.create(
                    user=user,
                    is_super_admin=True,
                    requires_password_change=True,
                    provisional_password_created=timezone.now(),
                    password_change_reminders_sent=0
                )
                
                self.stdout.write(self.style.SUCCESS("✅ Test admin user created successfully!"))
                self.stdout.write(f"   Username: {username}")
                self.stdout.write(f"   Email: {email}")
                self.stdout.write(f"   Password: {provisional_password}")
                self.stdout.write(f"   Requires password change: {profile.requires_password_change}")
                self.stdout.write("   Use --cleanup to remove test users")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to create test admin: {e}"))
    
    def cleanup_test_users(self):
        """Remove test admin users"""
        self.stdout.write("CLEANING UP TEST USERS:")
        
        try:
            # Remove test users
            test_users = User.objects.filter(username__startswith='test_admin_')
            count = test_users.count()
            
            if count > 0:
                test_users.delete()
                self.stdout.write(self.style.SUCCESS(f"✅ Removed {count} test admin users"))
            else:
                self.stdout.write("ℹ️  No test admin users found")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Cleanup failed: {e}"))
    
    def test_email_functionality(self):
        """Test email sending functionality"""
        self.stdout.write("\n3. TESTING EMAIL FUNCTIONALITY:")
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # Test email configuration
            self.stdout.write(f"   Email backend: {settings.EMAIL_BACKEND}")
            self.stdout.write(f"   Email host: {getattr(settings, 'EMAIL_HOST', 'Not configured')}")
            self.stdout.write(f"   Default from email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured')}")
            
            # Try to send a test email (to a safe address)
            test_email = "test@example.com"  # Safe test email
            
            try:
                send_mail(
                    'Test Email - LVK Sistemas',
                    'This is a test email to verify email functionality.',
                    settings.DEFAULT_FROM_EMAIL,
                    [test_email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS("   ✅ Email sending test passed"))
            except Exception as email_error:
                self.stdout.write(self.style.WARNING(f"   ⚠️  Email sending failed: {email_error}"))
                self.stdout.write("   This is normal if email is not configured")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Email test failed: {e}"))