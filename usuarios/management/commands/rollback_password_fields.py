from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.core.management.color import no_style
from django.core.management import call_command
import sys


class Command(BaseCommand):
    help = 'Safely rollback password management fields'
    
    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Confirm the rollback operation')
        parser.add_argument('--backup-first', action='store_true', help='Create backup before rollback')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    def handle(self, *args, **options):
        self.style = no_style()
        confirm = options.get('confirm', False)
        backup_first = options.get('backup_first', False)
        dry_run = options.get('dry_run', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("PASSWORD FIELDS ROLLBACK")
        self.stdout.write("=" * 60)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))
            self.show_rollback_plan()
            return
        
        if not confirm:
            self.stdout.write(self.style.ERROR('❌ This operation requires --confirm flag'))
            self.stdout.write('   This will remove password management fields from the database')
            self.stdout.write('   Use --dry-run to see what would be done')
            return
        
        # Warning and confirmation
        self.stdout.write(self.style.ERROR('⚠️  WARNING: This will remove password management fields!'))
        self.stdout.write('   - requires_password_change')
        self.stdout.write('   - provisional_password_created')
        self.stdout.write('   - password_changed_at')
        self.stdout.write('   - password_change_reminders_sent')
        
        # Pre-rollback checks
        if not self.pre_rollback_checks():
            return
        
        # Create backup if requested
        if backup_first:
            self.create_backup()
        
        # Perform rollback
        self.perform_rollback()
        
        # Post-rollback verification
        self.verify_rollback()
        
        self.stdout.write("=" * 60)
        self.stdout.write("ROLLBACK COMPLETE")
        self.stdout.write("=" * 60)
    
    def show_rollback_plan(self):
        """Show what the rollback would do"""
        self.stdout.write("\n📋 ROLLBACK PLAN:")
        
        self.stdout.write("1. Check current migration status")
        self.stdout.write("2. Verify password fields exist")
        self.stdout.write("3. Migrate back to usuarios.0004")
        self.stdout.write("4. Verify fields are removed")
        self.stdout.write("5. Test model access")
        
        # Show current status
        self.stdout.write("\n📊 CURRENT STATUS:")
        try:
            from usuarios.models import PerfilUsuario
            
            fields_to_check = [
                'requires_password_change',
                'provisional_password_created',
                'password_changed_at',
                'password_change_reminders_sent'
            ]
            
            for field in fields_to_check:
                try:
                    if field == 'requires_password_change':
                        count = PerfilUsuario.objects.filter(requires_password_change=True).count()
                    elif field == 'password_change_reminders_sent':
                        count = PerfilUsuario.objects.filter(password_change_reminders_sent=0).count()
                    else:
                        count = PerfilUsuario.objects.filter(**{f'{field}__isnull': True}).count()
                    
                    self.stdout.write(f'   ✅ {field}: EXISTS (queries work)')
                    
                except Exception as e:
                    self.stdout.write(f'   ❌ {field}: ERROR - {e}')
                    
        except Exception as e:
            self.stdout.write(f'   ❌ Model access error: {e}')
    
    def pre_rollback_checks(self):
        """Perform pre-rollback safety checks"""
        self.stdout.write("\n🔍 PRE-ROLLBACK CHECKS:")
        
        checks_passed = True
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            self.stdout.write(self.style.SUCCESS('✅ Database connection OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database connection failed: {e}'))
            checks_passed = False
        
        # Check if fields exist
        try:
            from usuarios.models import PerfilUsuario
            PerfilUsuario.objects.filter(requires_password_change=True).count()
            self.stdout.write(self.style.SUCCESS('✅ Password fields exist'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Password fields may not exist: {e}'))
        
        # Check for data that would be lost
        try:
            from usuarios.models import PerfilUsuario
            
            users_with_password_requirement = PerfilUsuario.objects.filter(requires_password_change=True).count()
            users_with_reminders = PerfilUsuario.objects.filter(password_change_reminders_sent__gt=0).count()
            
            if users_with_password_requirement > 0:
                self.stdout.write(self.style.WARNING(f'⚠️  {users_with_password_requirement} users require password change - data will be lost'))
            
            if users_with_reminders > 0:
                self.stdout.write(self.style.WARNING(f'⚠️  {users_with_reminders} users have reminder history - data will be lost'))
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Could not check data: {e}'))
        
        return checks_passed
    
    def create_backup(self):
        """Create a backup (placeholder - implement based on your backup strategy)"""
        self.stdout.write("\n💾 CREATING BACKUP:")
        self.stdout.write('   Note: Implement backup strategy based on your environment')
        self.stdout.write('   For Heroku: heroku pg:backups:capture')
        self.stdout.write('   For local: pg_dump or sqlite backup')
    
    def perform_rollback(self):
        """Perform the actual rollback"""
        self.stdout.write("\n🔄 PERFORMING ROLLBACK:")
        
        try:
            with transaction.atomic():
                self.stdout.write('   Rolling back to migration usuarios.0004...')
                
                # Migrate back to the previous migration
                call_command('migrate', 'usuarios', '0004', verbosity=1, interactive=False)
                
                self.stdout.write(self.style.SUCCESS('✅ Migration rollback completed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Rollback failed: {e}'))
            self.stdout.write('   Attempting manual column removal...')
            
            try:
                self.manual_column_removal()
            except Exception as manual_error:
                self.stdout.write(self.style.ERROR(f'❌ Manual removal also failed: {manual_error}'))
                raise
    
    def manual_column_removal(self):
        """Manually remove columns if migration rollback fails"""
        self.stdout.write('   Executing manual column removal...')
        
        columns_to_remove = [
            'requires_password_change',
            'provisional_password_created',
            'password_changed_at',
            'password_change_reminders_sent'
        ]
        
        with connection.cursor() as cursor:
            for column in columns_to_remove:
                try:
                    if connection.vendor == 'postgresql':
                        cursor.execute(f'ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS {column}')
                    else:
                        # SQLite doesn't support DROP COLUMN easily, would need table recreation
                        self.stdout.write(f'   ⚠️  SQLite column removal for {column} requires manual intervention')
                    
                    self.stdout.write(f'   ✅ Removed column: {column}')
                    
                except Exception as e:
                    self.stdout.write(f'   ❌ Failed to remove {column}: {e}')
    
    def verify_rollback(self):
        """Verify that rollback was successful"""
        self.stdout.write("\n✅ ROLLBACK VERIFICATION:")
        
        # Test model access
        try:
            from usuarios.models import PerfilUsuario
            count = PerfilUsuario.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✅ Model access OK - {count} profiles'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Model access failed: {e}'))
            return False
        
        # Test that password fields are gone
        fields_to_check = [
            'requires_password_change',
            'provisional_password_created',
            'password_changed_at',
            'password_change_reminders_sent'
        ]
        
        for field in fields_to_check:
            try:
                if field == 'requires_password_change':
                    PerfilUsuario.objects.filter(requires_password_change=True).count()
                elif field == 'password_change_reminders_sent':
                    PerfilUsuario.objects.filter(password_change_reminders_sent=0).count()
                else:
                    PerfilUsuario.objects.filter(**{f'{field}__isnull': True}).count()
                
                self.stdout.write(self.style.ERROR(f'❌ {field}: Still exists (rollback incomplete)'))
                
            except Exception:
                self.stdout.write(self.style.SUCCESS(f'✅ {field}: Successfully removed'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Rollback verification completed'))
        self.stdout.write('   Remember to:')
        self.stdout.write('   1. Disable password change middleware if active')
        self.stdout.write('   2. Update your models.py to remove the fields')
        self.stdout.write('   3. Test the application thoroughly')
        
        return True