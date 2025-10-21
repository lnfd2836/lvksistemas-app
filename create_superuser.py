#!/usr/bin/env python
"""
Script administrativo para criar um novo superusuário
Útil para criar contas de backup ou novos administradores
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Create a new superuser"""
    
    try:
        username = "superadmin"
        email = "admin@lvksistemas.com.br"
        password = "SuperAdmin123!"
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User {username} already exists")
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"✅ Updated existing user {username} with superuser privileges")
        else:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Created new superuser: {username}")
        
        print(f"🔑 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"📧 Email: {email}")
        print(f"🌐 Login at: https://www.lvksistemas.com.br/login/")
        print(f"📄 Then access: https://www.lvksistemas.com.br/financeiro/boletos/configurar/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating superuser: {str(e)}")
        return False

if __name__ == "__main__":
    print("👑 Creating superuser...")
    success = create_superuser()
    sys.exit(0 if success else 1)