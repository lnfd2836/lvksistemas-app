#!/usr/bin/env python3
"""
Script para resetar senha do admin
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User


def reset_admin_password():
    """Reseta senha do usuário admin"""
    
    print("🔧 RESETANDO SENHA DO ADMIN")
    print("=" * 30)
    
    # Nova senha segura
    new_password = 'Admin@LVK2024!'
    
    try:
        # Buscar usuário admin
        user = User.objects.get(username='admin')
        
        # Resetar senha
        user.set_password(new_password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        print("✅ Senha resetada com sucesso!")
        print()
        print("🔐 CREDENCIAIS ATUALIZADAS:")
        print(f"👤 Username: admin")
        print(f"🔑 Password: {new_password}")
        print(f"📧 Email: {user.email}")
        print(f"🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
        
        return True
        
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False


def reset_all_superuser_passwords():
    """Reseta senhas de todos os superusuários"""
    
    print("\n🔧 RESETANDO SENHAS DE TODOS OS SUPERUSUÁRIOS")
    print("=" * 45)
    
    # Senhas para cada usuário
    passwords = {
        'admin': 'Admin@LVK2024!',
        'superadmin': 'SuperAdmin@LVK2024!', 
        'luiz': 'Luiz@LVK2024!',
        'test_super_admin': 'TestAdmin@LVK2024!'
    }
    
    success_count = 0
    
    for username, password in passwords.items():
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_active = True
            user.is_superuser = True
            user.is_staff = True
            user.save()
            
            print(f"✅ {username}: Senha resetada")
            success_count += 1
            
        except User.DoesNotExist:
            print(f"⚠️ {username}: Usuário não encontrado")
        except Exception as e:
            print(f"❌ {username}: Erro - {str(e)}")
    
    print(f"\n🎯 {success_count} senhas resetadas com sucesso!")
    
    return success_count > 0


def show_final_credentials():
    """Mostra credenciais finais"""
    
    print("\n🔐 CREDENCIAIS FINAIS PARA ACESSO:")
    print("=" * 35)
    
    credentials = [
        ('admin', 'Admin@LVK2024!'),
        ('superadmin', 'SuperAdmin@LVK2024!'),
        ('luiz', 'Luiz@LVK2024!'),
        ('test_super_admin', 'TestAdmin@LVK2024!')
    ]
    
    print("📋 ESCOLHA UMA DAS OPÇÕES:")
    print("-" * 25)
    
    for i, (username, password) in enumerate(credentials, 1):
        try:
            user = User.objects.get(username=username)
            if user.is_active and user.is_superuser:
                print(f"{i}️⃣ Username: {username}")
                print(f"   Password: {password}")
                print(f"   Email: {user.email}")
                print()
        except User.DoesNotExist:
            pass
    
    print("🌐 URL DE ACESSO:")
    print("🔗 https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
    print()
    print("💡 RECOMENDAÇÃO:")
    print("Use o usuário 'admin' com a senha 'Admin@LVK2024!'")


def test_new_credentials():
    """Testa as novas credenciais"""
    
    print("\n🧪 TESTANDO NOVAS CREDENCIAIS:")
    print("-" * 30)
    
    from django.contrib.auth import authenticate
    
    test_creds = [
        ('admin', 'Admin@LVK2024!'),
        ('superadmin', 'SuperAdmin@LVK2024!'),
        ('luiz', 'Luiz@LVK2024!')
    ]
    
    for username, password in test_creds:
        try:
            user = authenticate(username=username, password=password)
            if user and user.is_superuser:
                print(f"✅ {username}: Login funcionando")
            elif user:
                print(f"⚠️ {username}: Usuário válido mas não é superuser")
            else:
                print(f"❌ {username}: Login falhou")
        except Exception as e:
            print(f"💥 {username}: Erro - {str(e)}")


def main():
    print("🚀 RESET DE SENHAS DE ADMIN")
    print("=" * 40)
    
    # Resetar senha do admin principal
    if reset_admin_password():
        print("✅ Admin principal configurado")
    
    # Resetar todas as senhas
    if reset_all_superuser_passwords():
        print("✅ Todos os superusuários configurados")
    
    # Mostrar credenciais finais
    show_final_credentials()
    
    # Testar credenciais
    test_new_credentials()
    
    print("\n🎯 PRONTO PARA USO!")
    print("Acesse o admin com as credenciais mostradas acima")


if __name__ == '__main__':
    main()