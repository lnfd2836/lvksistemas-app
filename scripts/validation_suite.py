#!/usr/bin/env python
"""
Validation Suite for System Optimization
Quick validation script that doesn't require Django setup
"""

import json
from datetime import datetime
from pathlib import Path


class ValidationSuite:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'validations': {},
            'status': 'PASS'
        }
        
    def validate_backup_exists(self):
        """Validate that backup was created successfully"""
        print("🔍 Validating backup system...")
        
        backup_dir = Path('backups/optimization')
        if not backup_dir.exists():
            self.results['validations']['backup'] = 'FAIL - Backup directory not found'
            self.results['status'] = 'FAIL'
            return False
            
        # Check for recent backup files
        backup_files = list(backup_dir.glob('*20251006*'))
        if len(backup_files) < 3:  # Should have at least backup info, rollback script, and archive
            self.results['validations']['backup'] = 'FAIL - Insufficient backup files'
            self.results['status'] = 'FAIL'
            return False
            
        self.results['validations']['backup'] = f'PASS - {len(backup_files)} backup files created'
        print(f"  ✅ Backup validation passed - {len(backup_files)} files")
        return True
        
    def validate_baseline_report(self):
        """Validate that baseline report was generated"""
        print("🔍 Validating baseline report...")
        
        reports_dir = Path('reports')
        if not reports_dir.exists():
            self.results['validations']['baseline'] = 'FAIL - Reports directory not found'
            self.results['status'] = 'FAIL'
            return False
            
        # Check for recent baseline report
        baseline_files = list(reports_dir.glob('performance_baseline_*20251006*.json'))
        if not baseline_files:
            self.results['validations']['baseline'] = 'FAIL - Baseline report not found'
            self.results['status'] = 'FAIL'
            return False
            
        # Validate report content
        latest_report = baseline_files[-1]
        try:
            with open(latest_report) as f:
                data = json.load(f)
                
            required_keys = ['template_count', 'middleware_count', 'file_sizes', 'template_analysis']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                self.results['validations']['baseline'] = f'FAIL - Missing keys: {missing_keys}'
                self.results['status'] = 'FAIL'
                return False
                
            self.results['validations']['baseline'] = f'PASS - Report contains all required metrics'
            print(f"  ✅ Baseline report validation passed")
            return True
            
        except Exception as e:
            self.results['validations']['baseline'] = f'FAIL - Report parsing error: {str(e)}'
            self.results['status'] = 'FAIL'
            return False
            
    def validate_critical_files_exist(self):
        """Validate that critical files still exist"""
        print("🔍 Validating critical files...")
        
        critical_files = [
            'lojad/settings.py',
            'templates/base.html',
            'templates/auth/login.html',
            'manage.py'
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.results['validations']['critical_files'] = f'FAIL - Missing files: {missing_files}'
            self.results['status'] = 'FAIL'
            return False
            
        self.results['validations']['critical_files'] = f'PASS - All {len(critical_files)} critical files exist'
        print(f"  ✅ Critical files validation passed")
        return True
        
    def validate_redundancy_identified(self):
        """Validate that redundancies were properly identified"""
        print("🔍 Validating redundancy identification...")
        
        reports_dir = Path('reports')
        baseline_files = list(reports_dir.glob('performance_baseline_*20251006*.json'))
        
        if not baseline_files:
            self.results['validations']['redundancy'] = 'FAIL - No baseline report to analyze'
            self.results['status'] = 'FAIL'
            return False
            
        try:
            with open(baseline_files[-1]) as f:
                data = json.load(f)
                
            # Check if login template redundancy was identified
            login_templates = data.get('template_analysis', {}).get('login_templates_count', 0)
            if login_templates < 2:
                self.results['validations']['redundancy'] = 'FAIL - Login template redundancy not identified'
                self.results['status'] = 'FAIL'
                return False
                
            # Check if custom middlewares were identified
            custom_middlewares = data.get('custom_middleware_count', 0)
            if custom_middlewares < 2:
                self.results['validations']['redundancy'] = 'FAIL - Custom middleware analysis incomplete'
                self.results['status'] = 'FAIL'
                return False
                
            self.results['validations']['redundancy'] = f'PASS - Identified {login_templates} login templates, {custom_middlewares} custom middlewares'
            print(f"  ✅ Redundancy identification passed")
            return True
            
        except Exception as e:
            self.results['validations']['redundancy'] = f'FAIL - Analysis error: {str(e)}'
            self.results['status'] = 'FAIL'
            return False
            
    def generate_validation_report(self):
        """Generate validation report"""
        print("📋 Generating validation report...")
        
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f'validation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        # Print summary
        print("\n" + "="*50)
        print("🔍 VALIDATION RESULTS")
        print("="*50)
        print(f"Overall Status: {self.results['status']}")
        print("\nValidation Details:")
        for validation, result in self.results['validations'].items():
            status_icon = "✅" if result.startswith('PASS') else "❌"
            print(f"  {status_icon} {validation}: {result}")
        print("="*50)
        print(f"📄 Report saved: {report_file}")
        
        return self.results['status'] == 'PASS'
        
    def run_validation(self):
        """Run complete validation suite"""
        print("🚀 Starting Validation Suite")
        print("="*50)
        
        validations = [
            self.validate_backup_exists,
            self.validate_baseline_report,
            self.validate_critical_files_exist,
            self.validate_redundancy_identified
        ]
        
        all_passed = True
        for validation in validations:
            if not validation():
                all_passed = False
                
        success = self.generate_validation_report()
        
        if success:
            print(f"\n✅ All validations passed! System ready for optimization.")
        else:
            print(f"\n❌ Some validations failed. Please review before proceeding.")
            
        return success


if __name__ == '__main__':
    validator = ValidationSuite()
    validator.run_validation()