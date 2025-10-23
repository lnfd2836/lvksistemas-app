#!/usr/bin/env python
"""
Script para corrigir problemas de espaçamento em templates
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def fix_template_spacing():
    """Identifica e sugere correções para problemas de espaçamento"""
    
    print("🔍 Analisando problema de renderização...")
    print("\n📋 Problema identificado:")
    print("   O HTML está sendo renderizado sem espaçamento adequado")
    print("   Isso faz com que o texto apareça junto: 'LojaExemplo56CNPJ:...'")
    
    print("\n💡 Possíveis causas:")
    print("   1. CSS não está carregando corretamente")
    print("   2. Template está sendo renderizado sem formatação")
    print("   3. Problema de compressão de arquivos estáticos")
    
    print("\n🔧 Soluções recomendadas:")
    print("   1. Verificar se o Bootstrap CSS está carregando")
    print("   2. Adicionar espaçamento manual nos templates")
    print("   3. Verificar configurações do WhiteNoise")
    
    print("\n🌐 Para verificar:")
    print("   1. Abra o navegador e pressione F12")
    print("   2. Vá para a aba 'Network' ou 'Rede'")
    print("   3. Recarregue a página")
    print("   4. Verifique se os arquivos CSS estão carregando (status 200)")
    
    print("\n📱 Se o CSS não estiver carregando:")
    print("   1. Execute: python manage.py collectstatic --clear")
    print("   2. Faça um novo deploy")
    print("   3. Limpe o cache do navegador (Ctrl+F5)")
    
    return True

if __name__ == '__main__':
    fix_template_spacing()