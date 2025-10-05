#!/usr/bin/env python
"""
Script para executar testes de URL routing
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lojad.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Executar testes específicos de URL
    test_modules = [
        'tests.test_url_patterns',
        'tests.test_template_rendering', 
        'tests.test_url_regression'
    ]
    
    print("🔍 Executando testes de URL routing...")
    print("=" * 50)
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n❌ {failures} teste(s) falharam!")
        sys.exit(1)
    else:
        print("\n✅ Todos os testes de URL passaram!")
        print("🚀 As correções de URL routing foram aplicadas com sucesso!")
        sys.exit(0)