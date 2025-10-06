#!/usr/bin/env python
"""
Script para encontrar a Loja Daniel
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from lojas.models import Loja

def find_loja_daniel():
    """Encontra a Loja Daniel"""
    print("🔍 Procurando Loja Daniel...")
    print("=" * 40)
    
    # Buscar por nome
    lojas_daniel = Loja.objects.filter(nome__icontains="daniel")
    
    if lojas_daniel.exists():
        for loja in lojas_daniel:
            print(f"✅ Loja encontrada:")
            print(f"   - Nome: {loja.nome}")
            print(f"   - ID: {loja.id}")
            print(f"   - CNPJ: {loja.cnpj}")
            print(f"   - Email: {loja.email}")
            print(f"   - Status: {loja.status}")
            print(f"   - Admin User: {loja.admin_user.username}")
            print(f"   - Senha Provisória: {loja.senha_provisoria}")
            print()
    else:
        print("❌ Nenhuma loja com 'Daniel' no nome encontrada")
        
        # Listar todas as lojas
        print("\n📋 Todas as lojas cadastradas:")
        all_lojas = Loja.objects.all()
        for i, loja in enumerate(all_lojas, 1):
            print(f"{i}. {loja.nome} - {loja.email} - {loja.cnpj}")

if __name__ == '__main__':
    find_loja_daniel()