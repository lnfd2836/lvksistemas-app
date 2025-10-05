#!/usr/bin/env python
"""
Script para diagnosticar problemas de URL
"""
import os
import sys
import django
from django.conf import settings

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lojad.settings'
    django.setup()
    
    from django.urls import reverse
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    from lojas.models import Loja
    import uuid
    
    print("🔍 Diagnosticando URLs...")
    print("=" * 50)
    
    # Criar objetos de teste
    try:
        loja = Loja.objects.first()
        if not loja:
            loja = Loja.objects.create(
                id=uuid.uuid4(),
                nome='Loja Teste',
                cnpj='12.345.678/0001-90',
                email='teste@teste.com',
                telefone='(11) 99999-9999',
                endereco='Rua Teste, 123',
                cidade='São Paulo',
                estado='SP',
                cep='01234-567',
                status='ativa'
            )
        
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser(
                username='admin',
                email='admin@teste.com',
                password='admin123'
            )
    except Exception as e:
        print(f"❌ Erro ao criar objetos de teste: {e}")
        sys.exit(1)
    
    # URLs para testar
    urls_to_test = [
        ('dashboard:principal', []),
        ('dashboard:loja_especifica', [loja.id]),
        ('lojas:listar_lojas', []),
        ('lojas:criar_loja', []),
        ('lojas:editar_loja', [loja.id]),
        ('dashboard:admin_usuarios_lista', []),
        ('dashboard:admin_usuarios_editar', [user.id]),
    ]
    
    print("Testando URLs:")
    for url_name, args in urls_to_test:
        try:
            url = reverse(url_name, args=args)
            print(f"✅ {url_name}: {url}")
        except Exception as e:
            print(f"❌ {url_name}: ERRO - {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Verificando templates...")
    
    # Testar renderização de templates
    from django.template.loader import get_template
    from django.template import Context
    
    templates_to_test = [
        'lojas/listar.html',
        'dashboard/usuarios_super_admin.html',
        'base.html'
    ]
    
    for template_name in templates_to_test:
        try:
            template = get_template(template_name)
            print(f"✅ Template {template_name}: OK")
        except Exception as e:
            print(f"❌ Template {template_name}: ERRO - {e}")
    
    print("\n🚀 Diagnóstico concluído!")