#!/usr/bin/env python
"""
Script para garantir que todos os usuários admin tenham perfis FATESA
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from avaliacao_qualidade.models import PerfilUsuario

def create_all_admin_profiles():
    """Criar perfis FATESA para todos os usuários admin"""
    
    print("=== CRIANDO PERFIS PARA TODOS OS USUÁRIOS ADMIN ===")
    
    # Buscar todos os usuários superuser
    admin_users = User.objects.filter(is_superuser=True)
    
    created_count = 0
    updated_count = 0
    
    for user in admin_users:
        try:
            print(f"\nProcessando usuário: {user.username} ({user.email})")
            
            # Verificar se já tem perfil
            if hasattr(user, 'perfil_fatesa'):
                perfil = user.perfil_fatesa
                print(f"  - Já possui perfil: {perfil.get_tipo_perfil_display()}")
                
                # Garantir que seja diretoria
                if perfil.tipo_perfil != 'diretoria':
                    perfil.tipo_perfil = 'diretoria'
                    perfil.save()
                    print(f"  - Atualizado para Diretoria")
                    updated_count += 1
                
                continue
            
            # Criar perfil de diretoria
            perfil = PerfilUsuario.objects.create(
                user=user,
                tipo_perfil='diretoria',
                nome_completo=f'Administrador {user.username.title()}',
                telefone='(00) 00000-0000',
                ativo=True
            )
            
            print(f"  - Perfil FATESA criado: {perfil.get_tipo_perfil_display()}")
            print(f"  - Pode gerenciar usuários: {perfil.pode_gerenciar_usuarios()}")
            created_count += 1
            
        except Exception as e:
            print(f"  - ❌ Erro ao processar {user.username}: {e}")
    
    print(f"\n=== RESUMO FINAL ===")
    print(f"Perfis criados: {created_count}")
    print(f"Perfis atualizados: {updated_count}")
    
    # Listar todos os perfis de diretoria
    print(f"\n=== USUÁRIOS COM ACESSO AO GERENCIAMENTO ===")
    perfis_diretoria = PerfilUsuario.objects.filter(tipo_perfil='diretoria').select_related('user')
    
    for perfil in perfis_diretoria:
        print(f"✓ {perfil.user.username}: {perfil.nome_completo}")
        print(f"  - Email: {perfil.user.email}")
        print(f"  - Pode gerenciar usuários: {perfil.pode_gerenciar_usuarios()}")
    
    return created_count + updated_count

if __name__ == '__main__':
    print("Garantindo que todos os admins tenham perfis FATESA...")
    
    try:
        changes = create_all_admin_profiles()
        
        if changes > 0:
            print(f"\n✅ {changes} alterações realizadas com sucesso!")
        else:
            print(f"\n✅ Todos os usuários admin já possuem perfis adequados!")
            
        print("\nAgora todos os usuários admin podem acessar:")
        print("- https://lvksistemas-app-4f6fa281e217.herokuapp.com/avaliacao-qualidade/usuarios/")
        print("- Todas as funcionalidades de gerenciamento de usuários")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        sys.exit(1)