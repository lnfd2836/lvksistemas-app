#!/usr/bin/env python
"""
Script para verificar permissões de usuários no Heroku
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from avaliacao_qualidade.models import PerfilUsuario

def check_permissions():
    """Verificar permissões de todos os usuários"""
    
    print("=== VERIFICANDO USUÁRIOS COM PERFIL FATESA ===")
    perfis = PerfilUsuario.objects.all().select_related('user')
    
    if not perfis.exists():
        print("❌ Nenhum usuário com perfil FATESA encontrado!")
        return False
    
    for perfil in perfis:
        print(f"Usuário: {perfil.user.username} ({perfil.user.email})")
        print(f"  - Tipo: {perfil.get_tipo_perfil_display()}")
        print(f"  - Ativo: {perfil.ativo}")
        print(f"  - Pode gerenciar usuários: {perfil.pode_gerenciar_usuarios()}")
        print(f"  - Superuser: {perfil.user.is_superuser}")
        print(f"  - Staff: {perfil.user.is_staff}")
        print("---")
    
    print(f"\n=== USUÁRIOS SEM PERFIL FATESA ===")
    users_without_profile = User.objects.filter(perfil_fatesa__isnull=True)
    
    for user in users_without_profile:
        print(f"• {user.username} ({user.email}) - Superuser: {user.is_superuser}")
    
    return True

def create_missing_profiles():
    """Criar perfis para usuários admin que não têm"""
    
    print(f"\n=== CRIANDO PERFIS FALTANTES ===")
    
    # Usuários que devem ter perfil de diretoria
    admin_usernames = ['admin', 'superadmin', 'teste', 'lvkadmin']
    
    created_count = 0
    
    for username in admin_usernames:
        try:
            user = User.objects.get(username=username)
            
            if hasattr(user, 'perfil_fatesa'):
                continue  # Já tem perfil
            
            # Criar perfil
            perfil = PerfilUsuario.objects.create(
                user=user,
                tipo_perfil='diretoria',
                nome_completo=f'Administrador {username.title()}',
                telefone='(00) 00000-0000',
                ativo=True
            )
            
            print(f"✓ Perfil criado para {username}")
            created_count += 1
            
        except User.DoesNotExist:
            print(f"⚠️  Usuário {username} não encontrado")
        except Exception as e:
            print(f"❌ Erro ao criar perfil para {username}: {e}")
    
    return created_count

if __name__ == '__main__':
    print("Verificando permissões de usuários...")
    
    if not check_permissions():
        print("Criando perfis necessários...")
        created = create_missing_profiles()
        
        if created > 0:
            print(f"\n✅ {created} perfis criados com sucesso!")
            check_permissions()  # Verificar novamente
        else:
            print("\n⚠️  Nenhum perfil foi criado")
    
    print("\n=== RESUMO FINAL ===")
    diretoria_count = PerfilUsuario.objects.filter(tipo_perfil='diretoria').count()
    print(f"Usuários com perfil de Diretoria: {diretoria_count}")
    
    if diretoria_count > 0:
        print("✅ Usuários podem acessar o gerenciamento de usuários")
    else:
        print("❌ Nenhum usuário pode gerenciar usuários")