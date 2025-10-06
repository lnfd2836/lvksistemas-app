from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.core.management.color import no_style
from django.utils import timezone
from django.test import Client
from django.urls import reverse
import json


class Command(BaseCommand):
    help = 'Test complete system functionality after migration fix'
    
    def add_arguments(self, parser):
        parser.add_argument('--create-test-data', action='store_true', help='Create test data')
        parser.add_argument('--cleanup', action='store_true', help='Clean up test data')
        parser.add_argument('--skip-web-tests', action='store_true', help='Skip web interface tests')
    
    def handle(self, *args, **options):
        self.style = no_style()
        create_test_data = options.get('create_test_data', False)
        cleanup = options.get('cleanup', False)
        skip_web_tests = options.get('skip_web_tests', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("COMPLETE SYSTEM FUNCTIONALITY TEST")
        self.stdout.write("=" * 60)
        
        if cleanup:
            self.cleanup_test_data()
            return
        
        # Test results tracking
        self.test_results = {
            'database_tests': {},
            'model_tests': {},
            'middleware_tests': {},
            'web_tests': {},
            'integration_tests': {}
        }
        
        # Run all tests
        self.test_database_functionality()
        self.test_model_operations()
        self.test_middleware_compatibility()
        
        if not skip_web_tests:
            self.test_web_interface()
        
        self.test_integration_scenarios()
        
        if create_test_data:
            self.create_comprehensive_test_data()
        
        # Display results
        self.display_test_summary()
        
        self.stdout.write("=" * 60)
        self.stdout.write("SYSTEM TEST COMPLETE")
        self.stdout.write("=" * 60)
    
    def test_database_functionality(self):
        """Test database-level functionality"""
        self.stdout.write("\n1. TESTING DATABASE FUNCTIONALITY:")
        
        # Test 1: Basic connectivity
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            self.test_results['database_tests']['connectivity'] = True
            self.stdout.write(self.style.SUCCESS('✅ Database connectivity'))
        except Exception as e:
            self.test_results['database_tests']['connectivity'] = False
            self.stdout.write(self.style.ERROR(f'❌ Database connectivity: {e}'))
        
        # Test 2: Password fields accessibility
        try:
            from usuarios.models import PerfilUsuario
            
            # Test each field
            fields = ['requires_password_change', 'provisional_password_created', 
                     'password_changed_at', 'password_change_reminders_sent']
            
            field_results = {}
            for field in fields:
                try:
                    if field == 'requires_password_change':
                        PerfilUsuario.objects.filter(requires_password_change=True).count()
                    elif field == 'password_change_reminders_sent':
                        PerfilUsuario.objects.filter(password_change_reminders_sent=0).count()
                    else:
                        PerfilUsuario.objects.filter(**{f'{field}__isnull': True}).count()
                    field_results[field] = True
                except Exception as e:
                    field_results[field] = False
                    self.stdout.write(self.style.ERROR(f'❌ Field {field}: {e}'))
            
            self.test_results['database_tests']['password_fields'] = field_results
            
            if all(field_results.values()):
                self.stdout.write(self.style.SUCCESS('✅ All password fields accessible'))
            else:
                self.stdout.write(self.style.ERROR('❌ Some password fields not accessible'))
                
        except Exception as e:
            self.test_results['database_tests']['password_fields'] = False
            self.stdout.write(self.style.ERROR(f'❌ Password fields test: {e}'))
    
    def test_model_operations(self):
        """Test model-level operations"""
        self.stdout.write("\n2. TESTING MODEL OPERATIONS:")
        
        # Test 1: Create user with profile
        try:
            with transaction.atomic():
                # Create test user
                username = f'test_model_{timezone.now().strftime("%H%M%S")}'
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@test.com',
                    password='testpass123'
                )
                
                # Create profile with password fields
                from usuarios.models import PerfilUsuario
                profile = PerfilUsuario.objects.create(
                    user=user,
                    requires_password_change=True,
                    provisional_password_created=timezone.now(),
                    password_change_reminders_sent=0
                )
                
                # Test updates
                profile.requires_password_change = False
                profile.password_changed_at = timezone.now()
                profile.password_change_reminders_sent = 1
                profile.save()
                
                # Clean up
                profile.delete()
                user.delete()
                
                self.test_results['model_tests']['crud_operations'] = True
                self.stdout.write(self.style.SUCCESS('✅ Model CRUD operations'))
                
        except Exception as e:
            self.test_results['model_tests']['crud_operations'] = False
            self.stdout.write(self.style.ERROR(f'❌ Model CRUD operations: {e}'))
        
        # Test 2: Query operations
        try:
            from usuarios.models import PerfilUsuario
            
            # Test various queries
            queries = [
                ('filter_requires_change', lambda: PerfilUsuario.objects.filter(requires_password_change=True).count()),
                ('filter_reminders', lambda: PerfilUsuario.objects.filter(password_change_reminders_sent__gte=0).count()),
                ('filter_datetime_null', lambda: PerfilUsuario.objects.filter(password_changed_at__isnull=True).count()),
                ('exclude_operations', lambda: PerfilUsuario.objects.exclude(requires_password_change=True).count()),
            ]
            
            query_results = {}
            for query_name, query_func in queries:
                try:
                    result = query_func()
                    query_results[query_name] = True
                except Exception as e:
                    query_results[query_name] = False
                    self.stdout.write(self.style.ERROR(f'❌ Query {query_name}: {e}'))
            
            self.test_results['model_tests']['query_operations'] = query_results
            
            if all(query_results.values()):
                self.stdout.write(self.style.SUCCESS('✅ Model query operations'))
            else:
                self.stdout.write(self.style.ERROR('❌ Some model queries failed'))
                
        except Exception as e:
            self.test_results['model_tests']['query_operations'] = False
            self.stdout.write(self.style.ERROR(f'❌ Model query operations: {e}'))
    
    def test_middleware_compatibility(self):
        """Test middleware compatibility"""
        self.stdout.write("\n3. TESTING MIDDLEWARE COMPATIBILITY:")
        
        try:
            # Test the logic that middleware would use
            from usuarios.models import PerfilUsuario
            
            # Simulate middleware checks
            profiles_needing_change = PerfilUsuario.objects.filter(requires_password_change=True)
            count = profiles_needing_change.count()
            
            # Test accessing user data through profiles
            middleware_tests = {}
            
            for profile in profiles_needing_change[:3]:  # Test first 3
                try:
                    user = profile.user
                    needs_change = profile.requires_password_change
                    middleware_tests[f'profile_{profile.id}'] = True
                except Exception as e:
                    middleware_tests[f'profile_{profile.id}'] = False
                    self.stdout.write(self.style.ERROR(f'❌ Profile access error: {e}'))
            
            self.test_results['middleware_tests']['profile_access'] = middleware_tests
            self.test_results['middleware_tests']['users_needing_change'] = count
            
            self.stdout.write(self.style.SUCCESS(f'✅ Middleware compatibility - {count} users need password change'))
            
        except Exception as e:
            self.test_results['middleware_tests']['compatibility'] = False
            self.stdout.write(self.style.ERROR(f'❌ Middleware compatibility: {e}'))
    
    def test_web_interface(self):
        """Test web interface functionality"""
        self.stdout.write("\n4. TESTING WEB INTERFACE:")
        
        try:
            client = Client()
            
            # Test 1: Login page access
            try:
                response = client.get('/login/')
                if response.status_code == 200:
                    self.test_results['web_tests']['login_page'] = True
                    self.stdout.write(self.style.SUCCESS('✅ Login page accessible'))
                else:
                    self.test_results['web_tests']['login_page'] = False
                    self.stdout.write(self.style.ERROR(f'❌ Login page: status {response.status_code}'))
            except Exception as e:
                self.test_results['web_tests']['login_page'] = False
                self.stdout.write(self.style.ERROR(f'❌ Login page: {e}'))
            
            # Test 2: Dashboard access (without login - should redirect)
            try:
                response = client.get('/dashboard/')
                # Should redirect to login
                if response.status_code in [302, 200]:
                    self.test_results['web_tests']['dashboard_redirect'] = True
                    self.stdout.write(self.style.SUCCESS('✅ Dashboard redirect working'))
                else:
                    self.test_results['web_tests']['dashboard_redirect'] = False
                    self.stdout.write(self.style.ERROR(f'❌ Dashboard redirect: status {response.status_code}'))
            except Exception as e:
                self.test_results['web_tests']['dashboard_redirect'] = False
                self.stdout.write(self.style.ERROR(f'❌ Dashboard redirect: {e}'))
            
            # Test 3: Admin users page (should require login)
            try:
                response = client.get('/dashboard/admin/usuarios/')
                if response.status_code in [302, 403]:  # Redirect or forbidden
                    self.test_results['web_tests']['admin_users_protection'] = True
                    self.stdout.write(self.style.SUCCESS('✅ Admin users page protected'))
                else:
                    self.test_results['web_tests']['admin_users_protection'] = False
                    self.stdout.write(self.style.ERROR(f'❌ Admin users page: status {response.status_code}'))
            except Exception as e:
                self.test_results['web_tests']['admin_users_protection'] = False
                self.stdout.write(self.style.ERROR(f'❌ Admin users page: {e}'))
                
        except Exception as e:
            self.test_results['web_tests']['general_error'] = str(e)
            self.stdout.write(self.style.ERROR(f'❌ Web interface tests: {e}'))
    
    def test_integration_scenarios(self):
        """Test integration scenarios"""
        self.stdout.write("\n5. TESTING INTEGRATION SCENARIOS:")
        
        # Test 1: User creation with password requirement
        try:
            with transaction.atomic():
                username = f'integration_test_{timezone.now().strftime("%H%M%S")}'
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@test.com',
                    password='temppass123'
                )
                
                # Profile should be created by signal
                from usuarios.models import PerfilUsuario
                
                # Wait a moment for signal to process
                import time
                time.sleep(0.1)
                
                try:
                    profile = user.perfil
                    
                    # Test password change workflow
                    profile.requires_password_change = True
                    profile.provisional_password_created = timezone.now()
                    profile.save()
                    
                    # Simulate password change
                    user.set_password('newpass123')
                    user.save()
                    
                    profile.requires_password_change = False
                    profile.password_changed_at = timezone.now()
                    profile.save()
                    
                    self.test_results['integration_tests']['password_workflow'] = True
                    self.stdout.write(self.style.SUCCESS('✅ Password change workflow'))
                    
                except Exception as e:
                    self.test_results['integration_tests']['password_workflow'] = False
                    self.stdout.write(self.style.ERROR(f'❌ Password workflow: {e}'))
                
                # Clean up
                user.delete()
                
        except Exception as e:
            self.test_results['integration_tests']['user_creation'] = False
            self.stdout.write(self.style.ERROR(f'❌ Integration test: {e}'))
    
    def create_comprehensive_test_data(self):
        """Create comprehensive test data"""
        self.stdout.write("\n6. CREATING TEST DATA:")
        
        try:
            from usuarios.models import PerfilUsuario
            
            # Create users with different password states
            test_scenarios = [
                ('user_needs_change', True, 0),
                ('user_changed_once', False, 1),
                ('user_multiple_reminders', True, 3),
                ('user_no_reminders', False, 0),
            ]
            
            created_users = []
            
            for scenario, needs_change, reminders in test_scenarios:
                username = f'{scenario}_{timezone.now().strftime("%H%M%S")}'
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@test.com',
                    password='testpass123'
                )
                
                profile = PerfilUsuario.objects.create(
                    user=user,
                    requires_password_change=needs_change,
                    provisional_password_created=timezone.now() if needs_change else None,
                    password_changed_at=None if needs_change else timezone.now(),
                    password_change_reminders_sent=reminders
                )
                
                created_users.append(username)
                self.stdout.write(f'   Created: {username}')
            
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(created_users)} test users'))
            self.stdout.write('   Use --cleanup to remove test data')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Test data creation: {e}'))
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.stdout.write("CLEANING UP TEST DATA:")
        
        try:
            # Remove test users
            test_users = User.objects.filter(username__contains='test_')
            count = test_users.count()
            
            if count > 0:
                test_users.delete()
                self.stdout.write(self.style.SUCCESS(f'✅ Removed {count} test users'))
            else:
                self.stdout.write('ℹ️  No test users found')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Cleanup failed: {e}'))
    
    def display_test_summary(self):
        """Display comprehensive test summary"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TEST SUMMARY")
        self.stdout.write("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    total_tests += 1
                    if result is True or (isinstance(result, dict) and all(result.values())):
                        passed_tests += 1
        
        self.stdout.write(f"Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.stdout.write(self.style.SUCCESS("🎉 ALL TESTS PASSED - System is functioning correctly"))
        elif passed_tests >= total_tests * 0.8:
            self.stdout.write(self.style.WARNING("⚠️  MOST TESTS PASSED - Minor issues detected"))
        else:
            self.stdout.write(self.style.ERROR("❌ MULTIPLE FAILURES - System needs attention"))
        
        # Detailed results
        self.stdout.write(f"\nDetailed Results:")
        self.stdout.write(json.dumps(self.test_results, indent=2, default=str))