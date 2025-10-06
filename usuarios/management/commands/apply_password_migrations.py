from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction, connection
from django.core.management.color import no_style
from io import StringIO


class Command(BaseCommand):
    help = 'Safely apply password management migrations'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated')
        parser.add_argument('--force', action='store_true', help='Force migration')
    
    def handle(self, *args, **options):
        self.style = no_style()
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("SAFE MIGRATION APPLICATION")
        self.stdout.write("=" * 60)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be applied'))
            self.show_migration_plan()
            return
        
        if not force and not self.pre_migration_checks():
            self.stdout.write(self.style.ERROR('Pre-migration checks failed. Use --force to override.'))
            return
        
        self.apply_migrations()
        self.verify_migration()
        
        self.stdout.write("=" * 60)
        self.stdout.write("MIGRATION APPLICATION COMPLETE")
        self.stdout.write("=" * 60)
    
    def show_migration_plan(self):
        self.stdout.write("MIGRATION PLAN:")
        try:
            output = StringIO()
            call_command('showmigrations', '--plan', stdout=output)
            plan_output = output.getvalue()
            if plan_output.strip():
                self.stdout.write(plan_output)
            else:
                self.stdout.write("No migrations to apply")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error showing migration plan: {e}'))
    
    def pre_migration_checks(self):
        self.stdout.write("PRE-MIGRATION CHECKS:")
        checks_passed = True
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            self.stdout.write(self.style.SUCCESS('Database connection OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database connection failed: {e}'))
            checks_passed = False
        
        return checks_passed
    
    def apply_migrations(self):
        self.stdout.write("APPLYING MIGRATIONS:")
        try:
            with transaction.atomic():
                self.stdout.write('Starting migration process...')
                call_command('migrate', 'usuarios', verbosity=2, interactive=False)
                self.stdout.write(self.style.SUCCESS('Migrations applied successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration failed: {e}'))
            raise
    
    def verify_migration(self):
        self.stdout.write("POST-MIGRATION VERIFICATION:")
        try:
            from usuarios.models import PerfilUsuario
            count = PerfilUsuario.objects.count()
            self.stdout.write(self.style.SUCCESS(f'Model access OK - {count} profiles'))
            
            # Test password fields
            PerfilUsuario.objects.filter(requires_password_change=True).count()
            self.stdout.write(self.style.SUCCESS('requires_password_change field accessible'))
            
            self.stdout.write(self.style.SUCCESS('Migration verification PASSED'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Verification error: {e}'))
            return False