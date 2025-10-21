#!/usr/bin/env python
"""
Script administrativo para verificar usuários e permissões
Útil para diagnóstico de problemas de acesso
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User

def debug_user_access():
    """Debug user access and permissions"""
    
    print("🔍 Debugging User Access and Permissions")
    print("=" * 50)
    
    # Check all users
    users = User.objects.all()
    print(f"📊 Total users in database: {users.count()}")
    
    superusers = User.objects.filter(is_superuser=True)
    print(f"👑 Superusers: {superusers.count()}")
    
    for user in superusers:
        print(f"   - {user.username} (active: {user.is_active}, staff: {user.is_staff})")
    
    # Check regular users
    regular_users = User.objects.filter(is_superuser=False)
    print(f"👤 Regular users: {regular_users.count()}")
    
    for user in regular_users[:5]:  # Show first 5
        print(f"   - {user.username} (active: {user.is_active}, staff: {user.is_staff})")
    
    print("\n🔐 Authentication Requirements for configurar_boletos:")
    print("   1. User must be logged in (@login_required)")
    print("   2. User must be superuser (@user_passes_test(is_superuser))")
    
    print("\n💡 To access the page, the user needs to:")
    print("   1. Go to /login/")
    print("   2. Login with superuser credentials")
    print("   3. Then access /financeiro/boletos/configurar/")
    
    # Check if there's a default superuser password
    superuser = superusers.first()
    if superuser:
        print(f"\n🔑 Try logging in with username: {superuser.username}")
        print("   Common passwords to try: admin, admin123, password, 123456")

if __name__ == "__main__":
    debug_user_access()