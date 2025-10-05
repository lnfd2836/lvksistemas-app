#!/usr/bin/env python
"""
Script para limpar cache de templates Django
"""
import os
import sys
import django
from django.conf import settings
from django.core.cache import cache

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lojad.settings'
    django.setup()
    
    print("🧹 Limpando cache de templates...")
    
    # Limpar cache do Django
    cache.clear()
    print("✅ Cache do Django limpo")
    
    # Limpar cache de templates compilados
    try:
        from django.template.loader import get_template
        from django.template.engine import Engine
        
        # Recarregar engines de template
        for engine in Engine.get_default().all():
            if hasattr(engine, 'env'):
                engine.env.cache.clear()
        
        print("✅ Cache de templates limpo")
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível limpar cache de templates: {e}")
    
    print("🚀 Cache limpo! Tente acessar a aplicação novamente.")