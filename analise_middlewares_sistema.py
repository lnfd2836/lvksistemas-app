#!/usr/bin/env python3
"""
Análise completa dos middlewares do sistema LVK
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.conf import settings

def analisar_middlewares():
    """Analisa todos os middlewares configurados"""
    
    print("=" * 80)
    print("🔍 ANÁLISE COMPLETA DOS MIDDLEWARES - SISTEMA LVK")
    print("=" * 80)
    print()
    
    middlewares = settings.MIDDLEWARE
    print(f"📊 TOTAL DE MIDDLEWARES CONFIGURADOS: {len(middlewares)}")
    print()
    
    # Categorizar middlewares
    categorias = {
        'Django Core': [],
        'Segurança': [],
        'Autenticação': [],
        'Lojas': [],
        'Financeiro': [],
        'Usuários': [],
        'Dashboard': [],
        'Email/Credenciais': [],
        'Avaliação Qualidade': [],
        'Terceiros': []
    }
    
    for i, middleware in enumerate(middlewares, 1):
        print(f"{i:2d}. {middleware}")
        
        # Categorizar
        if 'django.' in middleware:
            categorias['Django Core'].append(middleware)
        elif 'security' in middleware.lower() or 'csrf' in middleware.lower() or 'clickjacking' in middleware.lower():
            categorias['Segurança'].append(middleware)
        elif 'auth' in middleware.lower() or 'login' in middleware.lower():
            categorias['Autenticação'].append(middleware)
        elif 'loja' in middleware.lower():
            categorias['Lojas'].append(middleware)
        elif 'financeiro' in middleware.lower() or 'asaas' in middleware.lower() or 'webhook' in middleware.lower():
            categorias['Financeiro'].append(middleware)
        elif 'usuario' in middleware.lower() or 'password' in middleware.lower():
            categorias['Usuários'].append(middleware)
        elif 'dashboard' in middleware.lower():
            categorias['Dashboard'].append(middleware)
        elif 'email' in middleware.lower() or 'credential' in middleware.lower():
            categorias['Email/Credenciais'].append(middleware)
        elif 'avaliacao' in middleware.lower():
            categorias['Avaliação Qualidade'].append(middleware)
        else:
            categorias['Terceiros'].append(middleware)
    
    print()
    print("=" * 80)
    print("📋 MIDDLEWARES POR CATEGORIA")
    print("=" * 80)
    
    for categoria, mws in categorias.items():
        if mws:
            print(f"\n🏷️  {categoria} ({len(mws)} middlewares):")
            for mw in mws:
                print(f"   • {mw.split('.')[-1]}")

if __name__ == '__main__':
    analisar_middlewares()