#!/usr/bin/env python3
"""
Comando para criar usuário admin no Heroku
Execute: heroku run "python criar_admin_heroku.py" --app lvksistemas-app
"""

import os
import sys
import django
from pathlib import Path

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    from django.db import transaction
    
    print("🚀 CRIANDO USUÁRIO ADMIN NO HEROKU")
    print("=" * 50)
    
    with transaction.atomic():
        # Verifica se já existe
        try:
            user = User.objects.get(username='admin')
            print(f"👤 Usuário 'admin' já existe (ID: {user.id})")
            
            # Atualiza a senha
            user.set_password('admin123')
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            print("✅ Senha atualizada para 'admin123'")
            print("✅ Permissões de admin configuradas")
            
        except User.DoesNotExist:
            # Cria novo usuário
            user = User.objects.create_user(
                username='admin',
                email='admin@lvksistemas.com.br',
                password='admin123',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            
            print("✅ Usuário 'admin' criado com sucesso!")
            print(f"📧 Email: {user.email}")
            print("🔑 Senha: admin123")
            print("👑 Permissões: Superusuário")
    
    # Lista todos os usuários
    print("\n👥 Usuários no sistema:")
    print("-" * 30)
    
    for user in User.objects.all():
        status = "✅ Ativo" if user.is_active else "❌ Inativo"
        tipo = []
        
        if user.is_superuser:
            tipo.append("Super")
        if user.is_staff:
            tipo.append("Staff")
        
        tipo_str = ", ".join(tipo) if tipo else "User"
        
        print(f"👤 {user.username} ({tipo_str}) - {status}")
    
    print("\n" + "=" * 50)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("\n📋 Credenciais para login:")
    print("👤 Usuário: admin")
    print("🔑 Senha: admin123")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)