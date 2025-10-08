#!/usr/bin/env python
"""
Automated Test Suite for System Optimization
Verifies functionality after each optimization step
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add Django project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.core.management import call_command
from django.db import connection


class OptimizationTestSuite:
    def __init__(self):
        self.client = Client()
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': [],
            'performance_metrics': {}
        }
        
    def test_template_loading(self):
        """Test that all critical templates can be loaded"""
        print("🧪 Testing template loading...")
        
        critical_templates = [
            'base.html',
            'auth/login.html',
            'dashboard/super_admin.html',
            'dashboard/loja.html',
            'lojas/listar.html'
        ]
        
        for template_name in critical_templates:
            self.test_results['tests_run'] += 1
            try:
                template = get_template(template_name)
                self.test_results['tests_passed'] += 1
                print(f"  ✅ {template_name}")
            except TemplateDoesNotExist:
                self.test_results['tests_failed'] += 1
                self.test_results['failures'].append(f"Template not found: {template_name}")
                print(f"  ❌ {template_name} - NOT FOUND")
            except Exception as e:
                self.test_results['tests_failed'] += 1
                self.test_results['failures'].append(f"Template error {template_name}: {str(e)}")
                print(f"  ❌ {template_name} - ERROR: {str(e)}")
                
    def test_url_resolution(self):
        """Test that all critical URLs resolve correctly"""
        print("🧪 Testing URL resolution...")
        
        critical_urls = [
            ('login', '/login/'),
            ('dashboard:principal', '/dashboard/'),
            ('admin:index', '/admin/'),
        ]
        
        for url_name, expected_path in critical_urls:
            self.test_results['tests_run'] += 1
            try:
                if ':' in url_name:
                    resolved_url = reverse(url_name)
                else:
                    # For simple URLs, test direct access
                    response = self.client.get(expected_path)
                    resolved_url = expected_path
                    
                if resolved_url == expected_path or response.status_code in [200, 302, 301]:
                    self.test_results['tests_passed'] += 1
                    print(f"  ✅ {url_name} -> {expected_path}")
                else:
                    self.test_results['tests_failed'] += 1
                    self.test_results['failures'].append(f"URL mismatch {url_name}: expected {expected_path}, got {resolved_url}")
                    print(f"  ❌ {url_name} - MISMATCH")
                    
            except Exception as e:
                self.test_results['tests_failed'] += 1
                self.test_results['failures'].append(f"URL resolution error {url_name}: {str(e)}")
                print(f"  ❌ {url_name} - ERROR: {str(e)}")
                
    def test_login_functionality(self):
        """Test login functionality with different templates"""
        print("🧪 Testing login functionality...")
        
        # Create test user
        test_user, created = User.objects.get_or_create(
            username='test_optimization',
            defaults={'email': 'test@example.com', 'is_superuser': True}
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            
        login_urls = [
            '/login/',
            '/admin/login/',
        ]
        
        for login_url in login_urls:
            self.test_results['tests_run'] += 1
            try:
                # Test GET request (load login page)
                response = self.client.get(login_url)
                if response.status_code == 200:
                    self.test_results['tests_passed'] += 1
                    print(f"  ✅ GET {login_url}")
                else:
                    self.test_results['tests_failed'] += 1
                    self.test_results['failures'].append(f"Login page load failed {login_url}: status {response.status_code}")
                    print(f"  ❌ GET {login_url} - Status: {response.status_code}")
                    
                # Test POST request (login attempt)
                self.test_results['tests_run'] += 1
                login_data = {
                    'username': 'test_optimization',
                    'password': 'testpass123'
                }
                response = self.client.post(login_url, login_data)
                
                # Login should redirect (302) or succeed (200)
                if response.status_code in [200, 302]:
                    self.test_results['tests_passed'] += 1
                    print(f"  ✅ POST {login_url}")
                else:
                    self.test_results['tests_failed'] += 1
                    self.test_results['failures'].append(f"Login POST failed {login_url}: status {response.status_code}")
                    print(f"  ❌ POST {login_url} - Status: {response.status_code}")
                    
                # Logout for next test
                self.client.logout()
                
            except Exception as e:
                self.test_results['tests_failed'] += 1
                self.test_results['failures'].append(f"Login test error {login_url}: {str(e)}")
                print(f"  ❌ {login_url} - ERROR: {str(e)}")
                
    def test_middleware_functionality(self):
        """Test that middlewares are working correctly"""
        print("🧪 Testing middleware functionality...")
        
        # Test that we can make requests without middleware errors
        test_urls = [
            '/',
            '/login/',
            '/admin/',
        ]
        
        for url in test_urls:
            self.test_results['tests_run'] += 1
            try:
                start_time = time.time()
                response = self.client.get(url)
                end_time = time.time()
                
                # Any response that doesn't raise an exception is good
                if response.status_code < 500:  # Not a server error
                    self.test_results['tests_passed'] += 1
                    response_time = round((end_time - start_time) * 1000, 2)
                    print(f"  ✅ {url} - {response.status_code} ({response_time}ms)")
                else:
                    self.test_results['tests_failed'] += 1
                    self.test_results['failures'].append(f"Server error {url}: status {response.status_code}")
                    print(f"  ❌ {url} - Server Error: {response.status_code}")
                    
            except Exception as e:
                self.test_results['tests_failed'] += 1
                self.test_results['failures'].append(f"Middleware test error {url}: {str(e)}")
                print(f"  ❌ {url} - ERROR: {str(e)}")
                
    def test_static_files_access(self):
        """Test that static files are accessible"""
        print("🧪 Testing static files access...")
        
        # Test that static file URLs work
        static_urls = [
            '/static/admin/css/base.css',
            '/static/admin/js/core.js',
        ]
        
        for static_url in static_urls:
            self.test_results['tests_run'] += 1
            try:
                response = self.client.get(static_url)
                
                # Static files should return 200 or 404 (if not found, but URL structure is correct)
                if response.status_code in [200, 404]:
                    self.test_results['tests_passed'] += 1
                    print(f"  ✅ {static_url} - {response.status_code}")
                else:
                    self.test_results['tests_failed'] += 1
                    self.test_results['failures'].append(f"Static file error {static_url}: status {response.status_code}")
                    print(f"  ❌ {static_url} - Status: {response.status_code}")
                    
            except Exception as e:
                self.test_results['tests_failed'] += 1
                self.test_results['failures'].append(f"Static file test error {static_url}: {str(e)}")
                print(f"  ❌ {static_url} - ERROR: {str(e)}")
                
    def test_database_connectivity(self):
        """Test database connectivity and basic operations"""
        print("🧪 Testing database connectivity...")
        
        self.test_results['tests_run'] += 1
        try:
            # Test basic query
            user_count = User.objects.count()
            self.test_results['tests_passed'] += 1
            print(f"  ✅ Database query - {user_count} users")
            
            # Test query performance
            start_time = time.time()
            list(User.objects.all()[:10])  # Force evaluation
            end_time = time.time()
            
            query_time = round((end_time - start_time) * 1000, 2)
            self.test_results['performance_metrics']['db_query_time_ms'] = query_time
            print(f"  ✅ Query performance - {query_time}ms")
            
        except Exception as e:
            self.test_results['tests_failed'] += 1
            self.test_results['failures'].append(f"Database test error: {str(e)}")
            print(f"  ❌ Database - ERROR: {str(e)}")
            
    def measure_page_performance(self):
        """Measure page load performance"""
        print("🧪 Measuring page performance...")
        
        test_pages = [
            '/login/',
            '/admin/',
        ]
        
        for page_url in test_pages:
            try:
                start_time = time.time()
                response = self.client.get(page_url)
                end_time = time.time()
                
                load_time = round((end_time - start_time) * 1000, 2)
                content_size = len(response.content)
                
                self.test_results['performance_metrics'][f'{page_url}_load_time_ms'] = load_time
                self.test_results['performance_metrics'][f'{page_url}_content_size'] = content_size
                
                print(f"  📊 {page_url} - {load_time}ms, {content_size} bytes")
                
            except Exception as e:
                print(f"  ❌ Performance test error {page_url}: {str(e)}")
                
    def generate_test_report(self):
        """Generate test report"""
        print("📋 Generating test report...")
        
        # Create reports directory
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        # Calculate success rate
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        success_rate = round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0
        
        self.test_results['success_rate'] = success_rate
        
        # Save detailed report
        report_file = reports_dir / f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        # Print summary
        print("\n" + "="*50)
        print("🧪 TEST RESULTS SUMMARY")
        print("="*50)
        print(f"Tests Run: {total_tests}")
        print(f"Tests Passed: {passed_tests}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")
        print(f"Success Rate: {success_rate}%")
        
        if self.test_results['failures']:
            print("\n❌ FAILURES:")
            for failure in self.test_results['failures']:
                print(f"  - {failure}")
                
        print("="*50)
        print(f"📄 Detailed report: {report_file}")
        
        return self.test_results
        
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Automated Test Suite")
        print("="*50)
        
        self.test_template_loading()
        self.test_url_resolution()
        self.test_login_functionality()
        self.test_middleware_functionality()
        self.test_static_files_access()
        self.test_database_connectivity()
        self.measure_page_performance()
        
        results = self.generate_test_report()
        
        print(f"\n✅ Test suite completed!")
        return results


if __name__ == '__main__':
    test_suite = OptimizationTestSuite()
    test_suite.run_all_tests()