from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management.color import no_style
from django.utils import timezone
import logging
import json


class Command(BaseCommand):
    help = 'Monitor database health and log issues'
    
    def add_arguments(self, parser):
        parser.add_argument('--json', action='store_true', help='Output in JSON format')
        parser.add_argument('--alert-threshold', type=int, default=5, help='Alert threshold for errors')
    
    def handle(self, *args, **options):
        self.style = no_style()
        json_output = options.get('json', False)
        alert_threshold = options.get('alert_threshold', 5)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('database_health')
        
        health_data = {
            'timestamp': timezone.now().isoformat(),
            'status': 'healthy',
            'checks': {},
            'alerts': []
        }
        
        if not json_output:
            self.stdout.write("=" * 60)
            self.stdout.write("DATABASE HEALTH MONITORING")
            self.stdout.write("=" * 60)
        
        # Run health checks
        self.check_database_connection(health_data, logger)
        self.check_password_fields(health_data, logger)
        self.check_migration_status(health_data, logger)
        self.check_user_profiles(health_data, logger)
        
        # Determine overall status
        failed_checks = sum(1 for check in health_data['checks'].values() if not check['passed'])
        if failed_checks >= alert_threshold:
            health_data['status'] = 'critical'
        elif failed_checks > 0:
            health_data['status'] = 'warning'
        
        # Output results
        if json_output:
            self.stdout.write(json.dumps(health_data, indent=2))
        else:
            self.display_health_summary(health_data)
        
        # Log alerts
        for alert in health_data['alerts']:
            logger.error(f"DATABASE HEALTH ALERT: {alert}")
        
        # Exit with error code if critical
        if health_data['status'] == 'critical':
            exit(1)
    
    def check_database_connection(self, health_data, logger):
        """Check basic database connectivity"""
        check_name = 'database_connection'
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            health_data['checks'][check_name] = {
                'passed': True,
                'message': 'Database connection successful',
                'details': {
                    'vendor': connection.vendor,
                    'connection_time': 'OK'
                }
            }
            
            if not health_data.get('json', False):
                self.stdout.write(self.style.SUCCESS('✅ Database connection: OK'))
                
        except Exception as e:
            health_data['checks'][check_name] = {
                'passed': False,
                'message': f'Database connection failed: {e}',
                'details': {'error': str(e)}
            }
            health_data['alerts'].append(f'Database connection failed: {e}')
            
            if not health_data.get('json', False):
                self.stdout.write(self.style.ERROR(f'❌ Database connection: FAILED - {e}'))
    
    def check_password_fields(self, health_data, logger):
        """Check password management fields accessibility"""
        check_name = 'password_fields'
        
        try:
            from usuarios.models import PerfilUsuario
            
            # Test each critical field
            test_results = {}
            fields_to_test = [
                'requires_password_change',
                'provisional_password_created',
                'password_changed_at',
                'password_change_reminders_sent'
            ]
            
            for field in fields_to_test:
                try:
                    if field == 'requires_password_change':
                        count = PerfilUsuario.objects.filter(requires_password_change=True).count()
                    elif field == 'password_change_reminders_sent':
                        count = PerfilUsuario.objects.filter(password_change_reminders_sent=0).count()
                    else:
                        count = PerfilUsuario.objects.filter(**{f'{field}__isnull': True}).count()
                    
                    test_results[field] = {'accessible': True, 'count': count}
                    
                except Exception as e:
                    test_results[field] = {'accessible': False, 'error': str(e)}
                    health_data['alerts'].append(f'Password field {field} not accessible: {e}')
            
            # Check if all fields are accessible
            all_accessible = all(result['accessible'] for result in test_results.values())
            
            health_data['checks'][check_name] = {
                'passed': all_accessible,
                'message': 'All password fields accessible' if all_accessible else 'Some password fields not accessible',
                'details': test_results
            }
            
            if not health_data.get('json', False):
                if all_accessible:
                    self.stdout.write(self.style.SUCCESS('✅ Password fields: OK'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Password fields: FAILED'))
                    
        except Exception as e:
            health_data['checks'][check_name] = {
                'passed': False,
                'message': f'Password fields check failed: {e}',
                'details': {'error': str(e)}
            }
            health_data['alerts'].append(f'Password fields check failed: {e}')
    
    def check_migration_status(self, health_data, logger):
        """Check if all migrations are applied"""
        check_name = 'migration_status'
        
        try:
            from django.db.migrations.executor import MigrationExecutor
            
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            pending_count = len(plan)
            
            health_data['checks'][check_name] = {
                'passed': pending_count == 0,
                'message': f'{pending_count} pending migrations' if pending_count > 0 else 'All migrations applied',
                'details': {
                    'pending_migrations': pending_count,
                    'migrations': [str(migration) for migration, backwards in plan]
                }
            }
            
            if pending_count > 0:
                health_data['alerts'].append(f'{pending_count} pending migrations found')
            
            if not health_data.get('json', False):
                if pending_count == 0:
                    self.stdout.write(self.style.SUCCESS('✅ Migrations: OK'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Migrations: {pending_count} pending'))
                    
        except Exception as e:
            health_data['checks'][check_name] = {
                'passed': False,
                'message': f'Migration status check failed: {e}',
                'details': {'error': str(e)}
            }
    
    def check_user_profiles(self, health_data, logger):
        """Check user profiles health"""
        check_name = 'user_profiles'
        
        try:
            from usuarios.models import PerfilUsuario
            from django.contrib.auth.models import User
            
            total_users = User.objects.count()
            total_profiles = PerfilUsuario.objects.count()
            users_needing_password_change = PerfilUsuario.objects.filter(requires_password_change=True).count()
            
            # Check for users without profiles
            users_without_profiles = User.objects.filter(perfil__isnull=True).count()
            
            health_data['checks'][check_name] = {
                'passed': users_without_profiles == 0,
                'message': f'{users_without_profiles} users without profiles' if users_without_profiles > 0 else 'All users have profiles',
                'details': {
                    'total_users': total_users,
                    'total_profiles': total_profiles,
                    'users_without_profiles': users_without_profiles,
                    'users_needing_password_change': users_needing_password_change
                }
            }
            
            if users_without_profiles > 0:
                health_data['alerts'].append(f'{users_without_profiles} users without profiles')
            
            if not health_data.get('json', False):
                self.stdout.write(f'Users: {total_users}, Profiles: {total_profiles}')
                if users_without_profiles == 0:
                    self.stdout.write(self.style.SUCCESS('✅ User profiles: OK'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  User profiles: {users_without_profiles} missing'))
                    
        except Exception as e:
            health_data['checks'][check_name] = {
                'passed': False,
                'message': f'User profiles check failed: {e}',
                'details': {'error': str(e)}
            }
    
    def display_health_summary(self, health_data):
        """Display health summary in human-readable format"""
        self.stdout.write(f"\nOverall Status: {health_data['status'].upper()}")
        
        passed_checks = sum(1 for check in health_data['checks'].values() if check['passed'])
        total_checks = len(health_data['checks'])
        
        self.stdout.write(f"Checks Passed: {passed_checks}/{total_checks}")
        
        if health_data['alerts']:
            self.stdout.write(f"\n🚨 ALERTS ({len(health_data['alerts'])}):")
            for alert in health_data['alerts']:
                self.stdout.write(f"  - {alert}")
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("MONITORING COMPLETE")
        self.stdout.write("=" * 60)