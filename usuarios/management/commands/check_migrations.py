from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.core.management.color import no_style


class Command(BaseCommand):
    help = 'Check migration status and identify pending migrations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed migration information'
        )
    
    def handle(self, *args, **options):
        self.style = no_style()
        verbose = options.get('verbose', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("MIGRATION STATUS CHECK")
        self.stdout.write("=" * 60)
        
        # Check pending migrations
        self.check_pending_migrations(verbose)
        
        # Check specific password management fields
        self.check_password_fields()
        
        # Check database connection
        self.check_database_connection()
        
        self.stdout.write("=" * 60)
        self.stdout.write("CHECK COMPLETE")
        self.stdout.write("=" * 60)
    
    def check_pending_migrations(self, verbose=False):
        """Check for pending migrations"""
        self.stdout.write("\n1. CHECKING PENDING MIGRATIONS...")
        
        try:
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                self.stdout.write(self.style.ERROR('❌ PENDING MIGRATIONS FOUND:'))
                for migration, backwards in plan:
                    direction = "REVERSE" if backwards else "APPLY"
                    self.stdout.write(f'   - {migration} ({direction})')
                    
                    if verbose:
                        # Show migration details
                        try:
                            migration_obj = executor.loader.get_migration(migration.app_label, migration.name)
                            self.stdout.write(f'     Operations: {len(migration_obj.operations)}')
                            for i, op in enumerate(migration_obj.operations):
                                self.stdout.write(f'       {i+1}. {op.__class__.__name__}')
                        except Exception as e:
                            self.stdout.write(f'     Error getting details: {e}')
                
                self.stdout.write(f'\n   Total pending migrations: {len(plan)}')
                self.stdout.write('   Run: python manage.py migrate')
                
            else:
                self.stdout.write(self.style.SUCCESS('✅ All migrations are up to date'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error checking migrations: {e}'))
    
    def check_password_fields(self):
        """Check if password management fields exist in database"""
        self.stdout.write("\n2. CHECKING PASSWORD MANAGEMENT FIELDS...")
        
        required_columns = [
            'requires_password_change',
            'provisional_password_created', 
            'password_changed_at',
            'password_change_reminders_sent'
        ]
        
        try:
            # Try to import the model and check fields directly
            from usuarios.models import PerfilUsuario
            
            # Check if we can query the fields (this will fail if columns don't exist)
            missing_columns = []
            existing_columns = []
            
            for column in required_columns:
                try:
                    # Try to access the field - this will fail if column doesn't exist
                    field = PerfilUsuario._meta.get_field(column.replace('_', '_'))
                    
                    # Try a simple query to verify the column exists in database
                    with connection.cursor() as cursor:
                        if connection.vendor == 'postgresql':
                            cursor.execute(f"""
                                SELECT column_name, data_type, is_nullable, column_default
                                FROM information_schema.columns 
                                WHERE table_name = 'usuarios_perfilusuario' 
                                AND column_name = '{column}'
                            """)
                            result = cursor.fetchone()
                            if result:
                                existing_columns.append(column)
                                self.stdout.write(
                                    self.style.SUCCESS(f'✅ {column}: {result[1]} '
                                                     f'(nullable: {result[2]}, default: {result[3]})')
                                )
                            else:
                                missing_columns.append(column)
                                self.stdout.write(self.style.ERROR(f'❌ {column}: MISSING FROM DATABASE'))
                        else:
                            # For SQLite, try a simple query
                            cursor.execute(f"PRAGMA table_info(usuarios_perfilusuario)")
                            columns_info = cursor.fetchall()
                            column_names = [col[1] for col in columns_info]
                            
                            if column in column_names:
                                existing_columns.append(column)
                                # Find column info
                                col_info = next((col for col in columns_info if col[1] == column), None)
                                if col_info:
                                    self.stdout.write(
                                        self.style.SUCCESS(f'✅ {column}: {col_info[2]} '
                                                         f'(not null: {col_info[3]}, default: {col_info[4]})')
                                    )
                                else:
                                    self.stdout.write(self.style.SUCCESS(f'✅ {column}: EXISTS'))
                            else:
                                missing_columns.append(column)
                                self.stdout.write(self.style.ERROR(f'❌ {column}: MISSING FROM DATABASE'))
                                
                except Exception as field_error:
                    missing_columns.append(column)
                    self.stdout.write(self.style.ERROR(f'❌ {column}: ERROR - {field_error}'))
            
            if missing_columns:
                self.stdout.write(f'\n   Missing columns: {len(missing_columns)}')
                self.stdout.write('   These columns are required for password management functionality')
                self.stdout.write('   Run migration: python manage.py migrate usuarios 0005')
            else:
                self.stdout.write(self.style.SUCCESS(f'\n✅ All {len(existing_columns)} password management columns exist'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error checking password fields: {e}'))
    
    def check_database_connection(self):
        """Check database connection and basic info"""
        self.stdout.write("\n3. CHECKING DATABASE CONNECTION...")
        
        try:
            with connection.cursor() as cursor:
                # Test basic connection
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                self.stdout.write(self.style.SUCCESS('✅ Database connection successful'))
                self.stdout.write(f'   Database vendor: {connection.vendor}')
                
                # Get database-specific info
                if connection.vendor == 'postgresql':
                    # PostgreSQL specific queries
                    cursor.execute("SELECT version()")
                    db_version = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    table_count = cursor.fetchone()[0]
                    
                    self.stdout.write(f'   Database: {db_version}')
                    self.stdout.write(f'   Tables: {table_count}')
                    
                elif connection.vendor == 'sqlite':
                    # SQLite specific queries
                    cursor.execute("SELECT sqlite_version()")
                    db_version = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM sqlite_master 
                        WHERE type = 'table'
                    """)
                    table_count = cursor.fetchone()[0]
                    
                    self.stdout.write(f'   SQLite version: {db_version}')
                    self.stdout.write(f'   Tables: {table_count}')
                
                # Check usuarios_perfilusuario record count
                try:
                    cursor.execute("SELECT COUNT(*) FROM usuarios_perfilusuario")
                    profile_count = cursor.fetchone()[0]
                    self.stdout.write(f'   User profiles: {profile_count}')
                except Exception as table_error:
                    self.stdout.write(f'   User profiles: ERROR - {table_error}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database connection error: {e}'))