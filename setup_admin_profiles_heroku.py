#!/usr/bin/env python
"""
Script para configurar perfis de admin no Heroku
Este script deve ser executado no Heroku para criar os perfis FATESA necessários
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from avaliacao_qualidade.models import PerfilUsuario

def setup_admin_profiles():
    """Configurar perfis de admin no Heroku"""
    
    print("=== CONFIGURANDO PERFIS ADMIN NO HEROKU ===")
    
    # Lista de usuários admin que devem ter perfil de diretoria
    admin_users = ['admin', 'superadmin', 'teste', 'lvkadmin']
    
    created_count = 0
    updated_count = 0
    
    for username in admin_users:
        try:
            user = User.objects.get(username=username)
            print(f"\n✓ Usuário encontrado: {username} ({user.email})")
            
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
                nome_completo=f'Administrador {username.title()}',
                telefone='(00) 00000-0000',
                ativo=True
            )
            
            print(f"  - Perfil FATESA criado: {perfil.get_tipo_perfil_display()}")
            print(f"  - Pode gerenciar usuários: {perfil.pode_gerenciar_usuarios()}")
            created_count += 1
            
        except User.DoesNotExist:
            print(f"⚠️  Usuário {username} não encontrado")
        except Exception as e:
            print(f"❌ Erro ao processar {username}: {e}")
    
    print(f"\n=== RESUMO ===")
    print(f"Perfis criados: {created_count}")
    print(f"Perfis atualizados: {updated_count}")
    
    # Listar todos os perfis de diretoria
    print(f"\n=== PERFIS DE DIRETORIA ===")
    perfis_diretoria = PerfilUsuario.objects.filter(tipo_perfil='diretoria')
    
    for perfil in perfis_diretoria:
        print(f"• {perfil.user.username}: {perfil.nome_completo}")
        print(f"  - Email: {perfil.user.email}")
        print(f"  - Ativo: {perfil.ativo}")
        print(f"  - Pode gerenciar usuários: {perfil.pode_gerenciar_usuarios()}")
    
    return created_count + updated_count > 0

if __name__ == '__main__':
    print("Configurando perfis de admin no Heroku...")
    
    try:
        if setup_admin_profiles():
            print("\n✅ Configuração concluída com sucesso!")
            print("\nOs seguintes usuários agora podem acessar o gerenciamento de usuários:")
            print("- admin")
            print("- superadmin") 
            print("- teste")
            print("- lvkadmin")
        else:
            print("\n⚠️  Nenhuma alteração necessária")
            
    except Exception as e:
        print(f"\n❌ Erro durante a configuração: {e}")
        sys.exit(1)