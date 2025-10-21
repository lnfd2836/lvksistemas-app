#!/usr/bin/env python
"""
Script administrativo para resetar senha do usuário admin
Execute no servidor de produção se não conseguir acessar a conta admin
IMPORTANTE: Altere a senha padrão após o primeiro acesso
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User

def reset_admin_password():
    """Reset the admin user password"""
    
    try:
        # Get the admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            print("❌ No superuser found in database")
            return False
        
        # Set a new password
        new_password = "admin123"  # Change this to a secure password
        admin_user.set_password(new_password)
        admin_user.save()
        
        print(f"✅ Password reset successfully for user: {admin_user.username}")
        print(f"🔑 New password: {new_password}")
        print(f"🌐 Login at: https://www.lvksistemas.com.br/login/")
        print(f"📄 Then access: https://www.lvksistemas.com.br/financeiro/boletos/configurar/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔐 Resetting admin password...")
    success = reset_admin_password()
    sys.exit(0 if success else 1)