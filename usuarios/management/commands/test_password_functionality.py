from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.core.management.color import no_style
from django.utils import timezone


class Command(BaseCommand):
    help = 'Test password management functionality after migration'
    
    def add_arguments(self, parser):
        parser.add_argument('--create-test-user', action='store_true', help='Create a test user')
        parser.add_argument('--cleanup', action='store_true', help='Remove test users')
    
    def handle(self, *args, **options):
        self.style = no_style()
        create_test = options.get('create_test_user', False)
        cleanup = options.get('cleanup', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("PASSWORD FUNCTIONALITY TEST")
        self.stdout.write("=" * 60)
        
        if cleanup:
            self.cleanup_test_users()
            return
        
        # Test 1: Database field access
        self.test_database_fields()
        
        # Test 2: Model operations
        self.test_model_operations()
        
        # Test 3: Middleware compatibility
        self.test_middleware_compatibility()
        
        # Test 4: Create test user if requested
        if create_test:
            self.create_test_user()
        
        self.stdout.write("=" * 60)
        self.stdout.write("FUNCTIONALITY TEST COMPLETE")
        self.stdout.write("=" * 60)
    
    def test_database_fields(self):
        """Test direct database field access"""
        self.stdout.write("\n1. TESTING DATABASE FIELD ACCESS:")
        
        try:
            from usuarios.models import PerfilUsuario
            
            # Test each password management field
            fields_to_test = [
                ('requires_password_change', True),
                ('requires_password_change', False),
                ('password_change_reminders_sent', 0),
                ('password_change_reminders_sent', 1),
            ]
            
            for field_name, test_value in fields_to_test:
                try:
                    count = PerfilUsuario.objects.filter(**{field_name: test_value}).count()
                    self.stdout.write(self.style.SUCCESS(f'✅ {field_name}={test_value}: {count} records'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ {field_name}={test_value}: {e}'))
            
            # Test datetime fields
            datetime_fields = ['provisional_password_created', 'password_changed_at']
            for field_name in datetime_fields:
                try:
                    count = PerfilUsuario.objects.filter(**{f'{field_name}__isnull': True}).count()
                    self.stdout.write(self.style.SUCCESS(f'✅ {field_name}__isnull=True: {count} records'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ {field_name}__isnull=True: {e}'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database field test failed: {e}'))
    
    def test_model_operations(self):
        """Test model create/update operations"""
        self.stdout.write("\n2. TESTING MODEL OPERATIONS:")
        
        try:
            from usuarios.models import PerfilUsuario
            
            # Count existing profiles
            initial_count = PerfilUsuario.objects.count()
            self.stdout.write(f'Initial profile count: {initial_count}')
            
            # Test creating a user with password fields (if we have users)
            users_without_profile = User.objects.filter(perfil__isnull=True)
            if users_without_profile.exists():
                test_user = users_without_profile.first()
                
                # Create profile with password management fields
                profile = PerfilUsuario.objects.create(
                    user=test_user,
                    requires_password_change=True,
                    provisional_password_created=timezone.now(),
                    password_change_reminders_sent=0
                )
                
                self.stdout.write(self.style.SUCCESS(f'✅ Created profile for user {test_user.username}'))
                
                # Test updating password fields
                profile.requires_password_change = False
                profile.password_changed_at = timezone.now()
                profile.password_change_reminders_sent = 1
                profile.save()
                
                self.stdout.write(self.style.SUCCESS('✅ Updated password management fields'))
                
                # Clean up
                profile.delete()
                self.stdout.write('🧹 Cleaned up test profile')
            else:
                self.stdout.write('ℹ️  No users without profiles found for testing')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Model operations test failed: {e}'))
    
    def test_middleware_compatibility(self):
        """Test middleware compatibility"""
        self.stdout.write("\n3. TESTING MIDDLEWARE COMPATIBILITY:")
        
        try:
            from usuarios.models import PerfilUsuario
            
            # Test the logic that middleware would use
            profiles_needing_change = PerfilUsuario.objects.filter(requires_password_change=True)
            count = profiles_needing_change.count()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Found {count} profiles requiring password change'))
            
            # Test the specific query that was failing
            for profile in profiles_needing_change[:5]:  # Limit to 5 for testing
                try:
                    user = profile.user
                    needs_change = profile.requires_password_change
                    self.stdout.write(f'  User {user.username}: needs_change={needs_change}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error accessing profile data: {e}'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Middleware compatibility test failed: {e}'))
    
    def create_test_user(self):
        """Create a test user for password change testing"""
        self.stdout.write("\n4. CREATING TEST USER:")
        
        try:
            with transaction.atomic():
                # Create test user
                username = f'test_password_user_{timezone.now().strftime("%Y%m%d_%H%M%S")}'
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@test.com',
                    password='temp123456'
                )
                
                # Create profile with password change requirement
                from usuarios.models import PerfilUsuario
                profile = PerfilUsuario.objects.create(
                    user=user,
                    requires_password_change=True,
                    provisional_password_created=timezone.now(),
                    password_change_reminders_sent=0
                )
                
                self.stdout.write(self.style.SUCCESS(f'✅ Created test user: {username}'))
                self.stdout.write(f'   Email: {user.email}')
                self.stdout.write(f'   Requires password change: {profile.requires_password_change}')
                self.stdout.write('   Use --cleanup to remove test users')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to create test user: {e}'))
    
    def cleanup_test_users(self):
        """Remove test users created by this command"""
        self.stdout.write("CLEANING UP TEST USERS:")
        
        try:
            test_users = User.objects.filter(username__startswith='test_password_user_')
            count = test_users.count()
            
            if count > 0:
                test_users.delete()
                self.stdout.write(self.style.SUCCESS(f'✅ Removed {count} test users'))
            else:
                self.stdout.write('ℹ️  No test users found to remove')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to cleanup test users: {e}'))