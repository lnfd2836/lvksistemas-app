from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from django.core.management.color import no_style


class Command(BaseCommand):
    help = 'Verify database schema matches model definitions'
    
    def add_arguments(self, parser):
        parser.add_argument('--app', type=str, help='Specific app to verify (default: usuarios)')
        parser.add_argument('--model', type=str, help='Specific model to verify')
        parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    
    def handle(self, *args, **options):
        self.style = no_style()
        app_name = options.get('app', 'usuarios')
        model_name = options.get('model')
        verbose = options.get('verbose', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("DATABASE SCHEMA VERIFICATION")
        self.stdout.write("=" * 60)
        
        if model_name:
            self.verify_specific_model(app_name, model_name, verbose)
        else:
            self.verify_app_models(app_name, verbose)
        
        self.stdout.write("=" * 60)
        self.stdout.write("SCHEMA VERIFICATION COMPLETE")
        self.stdout.write("=" * 60)
    
    def verify_app_models(self, app_name, verbose=False):
        """Verify all models in an app"""
        self.stdout.write(f"Verifying models in app: {app_name}")
        
        try:
            app_config = apps.get_app_config(app_name)
            models = app_config.get_models()
            
            if not models:
                self.stdout.write(self.style.WARNING(f'No models found in app {app_name}'))
                return
            
            for model in models:
                self.stdout.write(f"\n--- {model.__name__} ---")
                self.verify_model_schema(model, verbose)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error verifying app {app_name}: {e}'))
    
    def verify_specific_model(self, app_name, model_name, verbose=False):
        """Verify a specific model"""
        self.stdout.write(f"Verifying model: {app_name}.{model_name}")
        
        try:
            model = apps.get_model(app_name, model_name)
            self.verify_model_schema(model, verbose)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error verifying model {model_name}: {e}'))
    
    def verify_model_schema(self, model, verbose=False):
        """Verify schema for a specific model"""
        table_name = model._meta.db_table
        
        try:
            # Get database columns
            db_columns = self.get_database_columns(table_name)
            
            # Get model fields
            model_fields = self.get_model_fields(model)
            
            # Compare schemas
            self.compare_schemas(model.__name__, model_fields, db_columns, verbose)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error verifying {model.__name__}: {e}'))
    
    def get_database_columns(self, table_name):
        """Get columns from database"""
        columns = {}
        
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY column_name
                """, [table_name])
                
                for row in cursor.fetchall():
                    columns[row[0]] = {
                        'type': row[1],
                        'nullable': row[2] == 'YES',
                        'default': row[3]
                    }
            else:
                # SQLite
                cursor.execute(f"PRAGMA table_info({table_name})")
                for row in cursor.fetchall():
                    columns[row[1]] = {
                        'type': row[2],
                        'nullable': not bool(row[3]),
                        'default': row[4]
                    }
        
        return columns
    
    def get_model_fields(self, model):
        """Get fields from Django model"""
        fields = {}
        
        for field in model._meta.fields:
            # Handle default value properly
            default_value = None
            if hasattr(field, 'default') and field.default is not None:
                try:
                    from django.db.models.fields import NOT_PROVIDED
                    if field.default != NOT_PROVIDED:
                        default_value = field.default
                except:
                    default_value = field.default
            
            fields[field.column] = {
                'type': field.get_internal_type(),
                'nullable': field.null,
                'default': default_value
            }
        
        return fields
    
    def compare_schemas(self, model_name, model_fields, db_columns, verbose=False):
        """Compare model fields with database columns"""
        missing_in_db = set(model_fields.keys()) - set(db_columns.keys())
        extra_in_db = set(db_columns.keys()) - set(model_fields.keys())
        common_fields = set(model_fields.keys()) & set(db_columns.keys())
        
        # Check missing fields
        if missing_in_db:
            self.stdout.write(self.style.ERROR(f'Missing in database: {missing_in_db}'))
        
        # Check extra fields
        if extra_in_db:
            self.stdout.write(self.style.WARNING(f'Extra in database: {extra_in_db}'))
        
        # Check common fields
        if verbose and common_fields:
            self.stdout.write(f'Common fields: {len(common_fields)}')
            for field_name in sorted(common_fields):
                model_field = model_fields[field_name]
                db_field = db_columns[field_name]
                self.stdout.write(f'  {field_name}: Model({model_field["type"]}) DB({db_field["type"]})')
        
        # Summary
        if not missing_in_db and not extra_in_db:
            self.stdout.write(self.style.SUCCESS(f'✅ {model_name} schema matches perfectly'))
        elif missing_in_db:
            self.stdout.write(self.style.ERROR(f'❌ {model_name} has missing columns in database'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  {model_name} has extra columns in database'))