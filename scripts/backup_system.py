#!/usr/bin/env python
"""
Backup System for System Optimization
Creates backups of templates, configurations, and critical files before modifications
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import zipfile


class BackupSystem:
    def __init__(self):
        self.backup_dir = Path('backups/optimization')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_info = {
            'timestamp': self.timestamp,
            'created_at': datetime.now().isoformat(),
            'backed_up_files': [],
            'backup_size_mb': 0
        }
        
    def backup_templates(self):
        """Backup all template files"""
        print("📁 Backing up templates...")
        
        templates_dir = Path('templates')
        if not templates_dir.exists():
            print("⚠️ Templates directory not found")
            return
            
        backup_templates_dir = self.backup_dir / f'templates_{self.timestamp}'
        shutil.copytree(templates_dir, backup_templates_dir)
        
        # Count files and size
        template_files = list(backup_templates_dir.rglob('*.html'))
        total_size = sum(f.stat().st_size for f in template_files)
        
        self.backup_info['templates'] = {
            'files_count': len(template_files),
            'size_mb': round(total_size / (1024 * 1024), 2),
            'backup_path': str(backup_templates_dir)
        }
        
        print(f"✅ Backed up {len(template_files)} template files")
        
    def backup_settings(self):
        """Backup Django settings and configuration files"""
        print("⚙️ Backing up configuration files...")
        
        config_files = [
            'lojad/settings.py',
            'lojad/urls.py',
            'requirements.txt',
            '.env'
        ]
        
        backup_config_dir = self.backup_dir / f'config_{self.timestamp}'
        backup_config_dir.mkdir(exist_ok=True)
        
        backed_up = []
        for config_file in config_files:
            source = Path(config_file)
            if source.exists():
                dest = backup_config_dir / source.name
                shutil.copy2(source, dest)
                backed_up.append(config_file)
                
        self.backup_info['config'] = {
            'files': backed_up,
            'backup_path': str(backup_config_dir)
        }
        
        print(f"✅ Backed up {len(backed_up)} configuration files")
        
    def backup_middleware_files(self):
        """Backup middleware files that might be modified"""
        print("🔧 Backing up middleware files...")
        
        middleware_patterns = [
            'usuarios/*middleware*.py',
            'dashboard/middleware/*.py',
            'lojas/middleware.py',
            'controle_financeiro/middleware.py'
        ]
        
        backup_middleware_dir = self.backup_dir / f'middleware_{self.timestamp}'
        backup_middleware_dir.mkdir(exist_ok=True)
        
        backed_up = []
        for pattern in middleware_patterns:
            for middleware_file in Path('.').glob(pattern):
                if middleware_file.is_file():
                    # Create subdirectory structure
                    relative_path = middleware_file.relative_to('.')
                    dest_dir = backup_middleware_dir / relative_path.parent
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest = dest_dir / relative_path.name
                    shutil.copy2(middleware_file, dest)
                    backed_up.append(str(middleware_file))
                    
        self.backup_info['middleware'] = {
            'files': backed_up,
            'backup_path': str(backup_middleware_dir)
        }
        
        print(f"✅ Backed up {len(backed_up)} middleware files")
        
    def backup_static_files(self):
        """Backup static files configuration"""
        print("📦 Backing up static files...")
        
        static_dirs = ['static', 'staticfiles']
        backed_up_dirs = []
        
        for static_dir in static_dirs:
            source_dir = Path(static_dir)
            if source_dir.exists() and any(source_dir.iterdir()):
                backup_static_dir = self.backup_dir / f'{static_dir}_{self.timestamp}'
                shutil.copytree(source_dir, backup_static_dir)
                backed_up_dirs.append(static_dir)
                
        self.backup_info['static'] = {
            'directories': backed_up_dirs,
            'backup_path': str(self.backup_dir)
        }
        
        print(f"✅ Backed up {len(backed_up_dirs)} static directories")
        
    def create_rollback_script(self):
        """Create rollback script to restore from backup"""
        print("🔄 Creating rollback script...")
        
        rollback_script = f"""#!/bin/bash
# Rollback script for optimization backup {self.timestamp}
# Created: {datetime.now().isoformat()}

echo "🔄 Rolling back system optimization changes..."
echo "Backup timestamp: {self.timestamp}"

# Restore templates
if [ -d "backups/optimization/templates_{self.timestamp}" ]; then
    echo "📁 Restoring templates..."
    rm -rf templates/
    cp -r backups/optimization/templates_{self.timestamp} templates/
    echo "✅ Templates restored"
fi

# Restore configuration
if [ -d "backups/optimization/config_{self.timestamp}" ]; then
    echo "⚙️ Restoring configuration files..."
    cp backups/optimization/config_{self.timestamp}/settings.py lojad/settings.py
    cp backups/optimization/config_{self.timestamp}/urls.py lojad/urls.py
    if [ -f "backups/optimization/config_{self.timestamp}/.env" ]; then
        cp backups/optimization/config_{self.timestamp}/.env .env
    fi
    echo "✅ Configuration restored"
fi

# Restore middleware
if [ -d "backups/optimization/middleware_{self.timestamp}" ]; then
    echo "🔧 Restoring middleware files..."
    cp -r backups/optimization/middleware_{self.timestamp}/* .
    echo "✅ Middleware restored"
fi

echo "✅ Rollback completed!"
echo "⚠️ Please restart the Django server"
"""
        
        rollback_file = self.backup_dir / f'rollback_{self.timestamp}.sh'
        rollback_file.write_text(rollback_script)
        rollback_file.chmod(0o755)  # Make executable
        
        self.backup_info['rollback_script'] = str(rollback_file)
        print(f"✅ Rollback script created: {rollback_file}")
        
    def create_backup_archive(self):
        """Create compressed archive of all backups"""
        print("📦 Creating backup archive...")
        
        archive_name = self.backup_dir / f'optimization_backup_{self.timestamp}.zip'
        
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.backup_dir):
                for file in files:
                    if not file.endswith('.zip'):  # Don't include other zip files
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.backup_dir)
                        zipf.write(file_path, arcname)
                        
        archive_size = archive_name.stat().st_size / (1024 * 1024)
        self.backup_info['archive'] = {
            'path': str(archive_name),
            'size_mb': round(archive_size, 2)
        }
        
        print(f"✅ Backup archive created: {archive_name} ({archive_size:.2f} MB)")
        
    def save_backup_info(self):
        """Save backup information"""
        info_file = self.backup_dir / f'backup_info_{self.timestamp}.json'
        
        # Calculate total backup size
        total_size = 0
        for key in ['templates', 'config', 'middleware', 'static']:
            if key in self.backup_info and 'size_mb' in self.backup_info[key]:
                total_size += self.backup_info[key]['size_mb']
                
        self.backup_info['total_size_mb'] = round(total_size, 2)
        
        with open(info_file, 'w') as f:
            json.dump(self.backup_info, f, indent=2)
            
        print(f"📋 Backup info saved: {info_file}")
        
    def run_backup(self):
        """Run complete backup process"""
        print("🚀 Starting System Backup for Optimization")
        print("="*50)
        
        self.backup_templates()
        self.backup_settings()
        self.backup_middleware_files()
        self.backup_static_files()
        self.create_rollback_script()
        self.save_backup_info()
        self.create_backup_archive()
        
        print("\n" + "="*50)
        print("📊 BACKUP SUMMARY")
        print("="*50)
        print(f"Timestamp: {self.timestamp}")
        print(f"Backup Directory: {self.backup_dir}")
        print(f"Total Size: {self.backup_info.get('total_size_mb', 0):.2f} MB")
        print(f"Rollback Script: {self.backup_info.get('rollback_script', 'N/A')}")
        print("="*50)
        
        print(f"\n✅ Backup completed successfully!")
        print(f"📁 Backup location: {self.backup_dir}")
        print(f"🔄 To rollback: bash {self.backup_info.get('rollback_script', '')}")
        
        return self.backup_info


if __name__ == '__main__':
    backup = BackupSystem()
    backup.run_backup()