# Design Document

## Overview

The database migration fix will ensure that all pending migrations, specifically the password management fields migration (0005_add_password_management_fields.py), are properly applied to the production Heroku database. The solution involves verifying migration status, applying pending migrations, and implementing safeguards to prevent future migration deployment issues.

## Architecture

The fix will use Django's built-in migration system with Heroku-specific deployment considerations:
- **Migration Status Check** to identify pending migrations
- **Safe Migration Application** using Django management commands
- **Database Schema Verification** to confirm successful migration
- **Deployment Process Enhancement** to prevent future issues

## Components and Interfaces

### 1. Migration Status Verification

**Management Command for Migration Check:**
```python
# usuarios/management/commands/check_migrations.py
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

class Command(BaseCommand):
    help = 'Check migration status and identify pending migrations'
    
    def handle(self, *args, **options):
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            self.stdout.write(self.style.WARNING('Pending migrations found:'))
            for migration, backwards in plan:
                self.stdout.write(f'  - {migration}')
        else:
            self.stdout.write(self.style.SUCCESS('All migrations are up to date'))
            
        # Check specific table columns
        self.check_password_fields()
    
    def check_password_fields(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'usuarios_perfilusuario' 
                AND column_name IN ('requires_password_change', 'provisional_password_created', 'password_changed_at', 'password_change_reminders_sent')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            required_columns = [
                'requires_password_change',
                'provisional_password_created', 
                'password_changed_at',
                'password_change_reminders_sent'
            ]
            
            missing_columns = set(required_columns) - set(existing_columns)
            
            if missing_columns:
                self.stdout.write(self.style.ERROR(f'Missing columns: {missing_columns}'))
            else:
                self.stdout.write(self.style.SUCCESS('All password management columns exist'))
```

### 2. Safe Migration Application

**Migration Application Strategy:**
```python
# usuarios/management/commands/apply_password_migrations.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction, connection

class Command(BaseCommand):
    help = 'Safely apply password management migrations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without applying changes'
        )
    
    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write('DRY RUN - No changes will be applied')
            call_command('showmigrations', '--plan')
            return
            
        try:
            with transaction.atomic():
                self.stdout.write('Applying migrations...')
                call_command('migrate', 'usuarios', verbosity=2)
                self.stdout.write(self.style.SUCCESS('Migrations applied successfully'))
                
                # Verify the migration worked
                self.verify_migration()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration failed: {e}'))
            raise
    
    def verify_migration(self):
        from usuarios.models import PerfilUsuario
        
        # Try to access the new fields
        try:
            # This will fail if the columns don't exist
            PerfilUsuario.objects.filter(requires_password_change=True).count()
            self.stdout.write(self.style.SUCCESS('Migration verification successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration verification failed: {e}'))
            raise
```

### 3. Heroku Deployment Integration

**Release Phase Configuration:**
```yaml
# Procfile
release: python manage.py migrate --noinput
web: gunicorn lojad.wsgi:application --log-file -
```

**Pre-deployment Migration Check:**
```bash
#!/bin/bash
# scripts/check_heroku_migrations.sh

echo "Checking migration status on Heroku..."
heroku run python manage.py showmigrations --app your-app-name

echo "Checking for pending migrations..."
PENDING=$(heroku run python manage.py showmigrations --plan --app your-app-name | grep -c "[ ]")

if [ "$PENDING" -gt 0 ]; then
    echo "WARNING: $PENDING pending migrations found"
    echo "Run: heroku run python manage.py migrate --app your-app-name"
    exit 1
else
    echo "All migrations are up to date"
fi
```

### 4. Database Schema Verification

**Schema Comparison Tool:**
```python
# usuarios/management/commands/verify_schema.py
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

class Command(BaseCommand):
    help = 'Verify database schema matches model definitions'
    
    def handle(self, *args, **options):
        self.verify_perfil_usuario_schema()
    
    def verify_perfil_usuario_schema(self):
        model = apps.get_model('usuarios', 'PerfilUsuario')
        table_name = model._meta.db_table
        
        # Get actual database columns
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY column_name
            """)
            db_columns = {row[0]: {
                'type': row[1],
                'nullable': row[2] == 'YES',
                'default': row[3]
            } for row in cursor.fetchall()}
        
        # Get model field definitions
        model_fields = {}
        for field in model._meta.fields:
            model_fields[field.column] = {
                'type': field.get_internal_type(),
                'nullable': field.null,
                'default': field.default
            }
        
        # Compare schemas
        missing_in_db = set(model_fields.keys()) - set(db_columns.keys())
        extra_in_db = set(db_columns.keys()) - set(model_fields.keys())
        
        if missing_in_db:
            self.stdout.write(self.style.ERROR(f'Missing in database: {missing_in_db}'))
        
        if extra_in_db:
            self.stdout.write(self.style.WARNING(f'Extra in database: {extra_in_db}'))
        
        if not missing_in_db and not extra_in_db:
            self.stdout.write(self.style.SUCCESS('Schema verification passed'))
```

## Data Models

The existing `PerfilUsuario` model already has the required fields defined:

```python
# Fields that should exist after migration
requires_password_change = models.BooleanField(default=False)
provisional_password_created = models.DateTimeField(null=True, blank=True)
password_changed_at = models.DateTimeField(null=True, blank=True)
password_change_reminders_sent = models.IntegerField(default=0)
```

## Error Handling

### 1. Migration Failure Recovery
- **Backup Strategy**: Create database backup before migration
- **Rollback Plan**: Ability to revert to previous migration state
- **Partial Failure**: Handle cases where some columns are added but others fail

### 2. Production Safety
- **Zero Downtime**: Use database transactions for atomic migrations
- **Validation**: Verify migration success before marking deployment complete
- **Monitoring**: Track migration performance and any errors

### 3. Edge Cases
- **Concurrent Migrations**: Handle multiple deployment attempts
- **Large Tables**: Optimize migration for tables with many rows
- **Connection Issues**: Retry logic for database connectivity problems

## Testing Strategy

### 1. Local Testing
- Test migration on local database copy
- Verify all fields are accessible after migration
- Test rollback scenarios

### 2. Staging Environment
- Apply migration to staging environment first
- Run full application test suite
- Verify no regression in existing functionality

### 3. Production Verification
- Monitor application logs during and after migration
- Test critical user flows (login, password change)
- Verify database performance is not impacted

## Implementation Plan

### Phase 1: Preparation and Verification
1. Create migration status check command
2. Verify current production database state
3. Create database backup strategy

### Phase 2: Safe Migration Application
1. Create safe migration application command
2. Test migration process in staging
3. Prepare rollback procedures

### Phase 3: Production Deployment
1. Apply migration to production database
2. Verify migration success
3. Monitor application functionality

### Phase 4: Process Improvement
1. Update deployment process to include migration checks
2. Create monitoring for future migration issues
3. Document migration procedures

## Security Considerations

- **Database Access**: Ensure migration commands have appropriate permissions
- **Backup Security**: Protect database backups with encryption
- **Audit Trail**: Log all migration activities for compliance
- **Access Control**: Limit who can run migration commands in production

## Performance Impact

- **Migration Time**: Password management fields are simple additions with minimal impact
- **Downtime**: Use release phase to minimize user-facing downtime
- **Database Load**: Monitor database performance during migration
- **Application Performance**: Verify no performance regression after migration

## Monitoring and Alerting

### Migration Success Metrics
- Migration completion time
- Number of rows affected
- Any error messages or warnings
- Post-migration application health checks

### Ongoing Monitoring
- Database query performance for new columns
- Application error rates after migration
- User login success rates
- Password change functionality usage

## Rollback Strategy

### Immediate Rollback
```sql
-- Emergency rollback if needed
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS requires_password_change;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS provisional_password_created;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_changed_at;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_change_reminders_sent;
```

### Application Rollback
- Revert to previous application version
- Disable password change middleware temporarily
- Restore from database backup if necessary