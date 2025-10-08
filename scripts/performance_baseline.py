#!/usr/bin/env python
"""
Performance Baseline Measurement Script
Captures current system metrics before optimization
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path


class PerformanceBaseline:
    def __init__(self):
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'file_sizes': {},
            'template_count': {},
            'static_resources': {},
            'page_load_times': {},
            'database_queries': {},
            'middleware_count': 0,
            'total_files': 0
        }
        
    def measure_file_sizes(self):
        """Measure current file sizes and counts"""
        print("📊 Measuring file sizes and counts...")
        
        # Templates
        templates_dir = Path('templates')
        if templates_dir.exists():
            template_files = list(templates_dir.rglob('*.html'))
            self.metrics['template_count']['total'] = len(template_files)
            self.metrics['template_count']['by_app'] = {}
            
            total_size = 0
            for template in template_files:
                size = template.stat().st_size
                total_size += size
                app_name = str(template.parent.name)
                if app_name not in self.metrics['template_count']['by_app']:
                    self.metrics['template_count']['by_app'][app_name] = {'count': 0, 'size': 0}
                self.metrics['template_count']['by_app'][app_name]['count'] += 1
                self.metrics['template_count']['by_app'][app_name]['size'] += size
                
            self.metrics['file_sizes']['templates_total_kb'] = total_size / 1024
            
        # Static files
        static_dir = Path('static')
        staticfiles_dir = Path('staticfiles')
        
        for dir_path, key in [(static_dir, 'static'), (staticfiles_dir, 'staticfiles')]:
            if dir_path.exists():
                static_files = list(dir_path.rglob('*'))
                static_files = [f for f in static_files if f.is_file()]
                total_size = sum(f.stat().st_size for f in static_files)
                self.metrics['file_sizes'][f'{key}_files'] = len(static_files)
                self.metrics['file_sizes'][f'{key}_size_kb'] = total_size / 1024
                
        # Python files
        python_files = list(Path('.').rglob('*.py'))
        python_files = [f for f in python_files if 'venv' not in str(f) and '.git' not in str(f)]
        total_size = sum(f.stat().st_size for f in python_files)
        self.metrics['file_sizes']['python_files'] = len(python_files)
        self.metrics['file_sizes']['python_size_kb'] = total_size / 1024
        self.metrics['total_files'] = len(python_files)
        
    def analyze_templates(self):
        """Analyze template redundancy"""
        print("🔍 Analyzing template redundancy...")
        
        auth_templates = Path('templates/auth')
        if auth_templates.exists():
            login_templates = list(auth_templates.glob('*login*.html'))
            self.metrics['template_analysis'] = {
                'login_templates_count': len(login_templates),
                'login_templates': [str(t.name) for t in login_templates]
            }
            
            # Analyze template sizes
            for template in login_templates:
                size = template.stat().st_size
                self.metrics['template_analysis'][f'{template.name}_size'] = size
                
    def measure_middleware_count(self):
        """Count configured middlewares from settings file"""
        print("⚙️ Analyzing middleware configuration...")
        
        settings_file = Path('lojad/settings.py')
        if settings_file.exists():
            content = settings_file.read_text()
            
            # Extract MIDDLEWARE list
            middleware_section = False
            middlewares = []
            
            for line in content.splitlines():
                line = line.strip()
                if 'MIDDLEWARE = [' in line:
                    middleware_section = True
                    continue
                elif middleware_section and line == ']':
                    break
                elif middleware_section and line.startswith("'") and line.endswith("',"):
                    middleware = line.strip("',")
                    middlewares.append(middleware)
                    
            self.metrics['middleware_count'] = len(middlewares)
            self.metrics['middlewares'] = middlewares
            
            # Count custom middlewares
            custom_middlewares = [m for m in middlewares if not m.startswith('django.')]
            self.metrics['custom_middleware_count'] = len(custom_middlewares)
            self.metrics['custom_middlewares'] = custom_middlewares
        
    def measure_page_load_simulation(self):
        """Simulate page loads to measure response times (file-based analysis)"""
        print("⏱️ Analyzing page templates...")
        
        # Analyze template files instead of making HTTP requests
        template_files = [
            'templates/auth/login.html',
            'templates/auth/loja_login.html', 
            'templates/auth/loja_login_clean.html',
            'templates/base.html'
        ]
        
        self.metrics['page_load_times'] = {}
        
        for template_file in template_files:
            template_path = Path(template_file)
            if template_path.exists():
                size = template_path.stat().st_size
                content = template_path.read_text()
                
                # Count external resources
                external_resources = 0
                if 'cdn.jsdelivr.net' in content:
                    external_resources += content.count('cdn.jsdelivr.net')
                if 'cdnjs.cloudflare.com' in content:
                    external_resources += content.count('cdnjs.cloudflare.com')
                    
                self.metrics['page_load_times'][template_path.name] = {
                    'file_size': size,
                    'external_resources': external_resources,
                    'lines': len(content.splitlines())
                }
                
    def analyze_database_config(self):
        """Analyze database configuration"""
        print("🗄️ Analyzing database configuration...")
        
        settings_file = Path('lojad/settings.py')
        if settings_file.exists():
            content = settings_file.read_text()
            
            # Look for database configuration
            db_config = {}
            if 'sqlite' in content.lower():
                db_config['type'] = 'SQLite'
            elif 'postgresql' in content.lower() or 'psycopg' in content.lower():
                db_config['type'] = 'PostgreSQL'
            elif 'mysql' in content.lower():
                db_config['type'] = 'MySQL'
            else:
                db_config['type'] = 'Unknown'
                
            # Check for connection pooling
            db_config['has_connection_pooling'] = 'CONN_MAX_AGE' in content
            
            self.metrics['database_config'] = db_config
        
    def analyze_static_resources(self):
        """Analyze static resource usage in templates"""
        print("📦 Analyzing static resource usage...")
        
        base_template = Path('templates/base.html')
        if base_template.exists():
            content = base_template.read_text()
            
            # Count CDN resources
            cdn_resources = []
            if 'bootstrap' in content.lower():
                cdn_resources.append('Bootstrap')
            if 'chart.js' in content.lower():
                cdn_resources.append('Chart.js')
            if 'font-awesome' in content.lower():
                cdn_resources.append('Font Awesome')
                
            self.metrics['static_resources'] = {
                'cdn_resources': cdn_resources,
                'cdn_count': len(cdn_resources),
                'base_template_size': base_template.stat().st_size
            }
            
    def generate_report(self):
        """Generate and save baseline report"""
        print("📋 Generating baseline report...")
        
        # Create reports directory
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        # Save detailed metrics
        report_file = reports_dir / f'performance_baseline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
        # Generate summary
        summary = {
            'Total Templates': self.metrics['template_count']['total'],
            'Login Templates': self.metrics.get('template_analysis', {}).get('login_templates_count', 0),
            'Total Middlewares': self.metrics['middleware_count'],
            'Custom Middlewares': self.metrics['custom_middleware_count'],
            'Python Files': self.metrics['file_sizes']['python_files'],
            'Total Size (KB)': round(
                self.metrics['file_sizes'].get('templates_total_kb', 0) +
                self.metrics['file_sizes'].get('python_size_kb', 0), 2
            )
        }
        
        print("\n" + "="*50)
        print("📊 PERFORMANCE BASELINE SUMMARY")
        print("="*50)
        for key, value in summary.items():
            print(f"{key:.<30} {value}")
        print("="*50)
        print(f"📄 Detailed report saved: {report_file}")
        
        return report_file
        
    def run_baseline(self):
        """Run complete baseline measurement"""
        print("🚀 Starting Performance Baseline Measurement")
        print("="*50)
        
        self.measure_file_sizes()
        self.analyze_templates()
        self.measure_middleware_count()
        self.analyze_static_resources()
        self.measure_page_load_simulation()
        self.analyze_database_config()
        
        report_file = self.generate_report()
        
        print(f"\n✅ Baseline measurement completed!")
        print(f"📊 Report saved to: {report_file}")
        
        return self.metrics


if __name__ == '__main__':
    baseline = PerformanceBaseline()
    baseline.run_baseline()