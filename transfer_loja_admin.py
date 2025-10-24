#!/usr/bin/env python
"""
Script para transferir administração de loja antes de excluir usuário
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from lojas.models import Loja
from django.db import transaction


def listar_lojas_usuario(user_id):
    """Lista lojas administradas por um usuário"""
    try:
        user = User.objects.get(id=user_id)
        print(f"👤 Usuário: {user.username} ({user.email})")
        
        lojas = Loja.objects.filter(admin_user=user)
        
        if lojas.exists():
            print(f"\n🏪 Lojas administradas ({lojas.count()}):")
            for loja in lojas:
                print(f"   • ID: {loja.id}")
                print(f"     Nome: {loja.nome}")
                print(f"     Status: {loja.status}")
                print(f"     Tipo: {loja.tipo_loja.get_nome_display() if loja.tipo_loja else 'Não definido'}")
                print(f"     Data criação: {loja.data_criacao}")
                print()
        else:
            print("✅ Usuário não administra nenhuma loja")
            
        return lojas
        
    except User.DoesNotExist:
        print(f"❌ Usuário com ID {user_id} não encontrado")
        return None


def transferir_administracao(loja_id, novo_admin_id):
    """Transfere administração de uma loja para outro usuário"""
    try:
        with transaction.atomic():
            loja = Loja.objects.get(id=loja_id)
            novo_admin = User.objects.get(id=novo_admin_id)
            
            admin_anterior = loja.admin_user
            
            print(f"🔄 Transferindo administração da loja '{loja.nome}'")
            print(f"   De: {admin_anterior.username} (ID: {admin_anterior.id})")
            print(f"   Para: {novo_admin.username} (ID: {novo_admin.id})")
            
            loja.admin_user = novo_admin
            loja.save()
            
            print("✅ Transferência realizada com sucesso!")
            return True
            
    except Loja.DoesNotExist:
        print(f"❌ Loja com ID {loja_id} não encontrada")
        return False
    except User.DoesNotExist:
        print(f"❌ Novo administrador com ID {novo_admin_id} não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro na transferência: {e}")
        return False


def remover_administracao(loja_id):
    """Remove administração de uma loja (define como NULL)"""
    try:
        with transaction.atomic():
            loja = Loja.objects.get(id=loja_id)
            
            admin_anterior = loja.admin_user
            
            print(f"🗑️ Removendo administração da loja '{loja.nome}'")
            print(f"   Administrador atual: {admin_anterior.username} (ID: {admin_anterior.id})")
            
            loja.admin_user = None
            loja.save()
            
            print("✅ Administração removida com sucesso!")
            print("⚠️  ATENÇÃO: Loja ficará sem administrador!")
            return True
            
    except Loja.DoesNotExist:
        print(f"❌ Loja com ID {loja_id} não encontrada")
        return False
    except Exception as e:
        print(f"❌ Erro ao remover administração: {e}")
        return False


def listar_usuarios_disponiveis():
    """Lista usuários disponíveis para serem administradores"""
    print("👥 Usuários disponíveis para administração:")
    
    # Buscar superusuários
    superusers = User.objects.filter(is_superuser=True, is_active=True)
    if superusers.exists():
        print("\n🔑 Superusuários:")
        for user in superusers:
            print(f"   • ID: {user.id} - {user.username} ({user.email})")
    
    # Buscar usuários ativos sem loja
    usuarios_sem_loja = User.objects.filter(
        is_active=True,
        loja_admin__isnull=True
    ).exclude(is_superuser=True)[:10]
    
    if usuarios_sem_loja.exists():
        print("\n👤 Usuários sem loja (primeiros 10):")
        for user in usuarios_sem_loja:
            print(f"   • ID: {user.id} - {user.username} ({user.email})")


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python transfer_loja_admin.py list <user_id>                    # Listar lojas do usuário")
        print("  python transfer_loja_admin.py transfer <loja_id> <novo_admin>   # Transferir administração")
        print("  python transfer_loja_admin.py remove <loja_id>                  # Remover administração")
        print("  python transfer_loja_admin.py users                             # Listar usuários disponíveis")
        return
    
    comando = sys.argv[1]
    
    if comando == "list" and len(sys.argv) > 2:
        user_id = int(sys.argv[2])
        listar_lojas_usuario(user_id)
        
    elif comando == "transfer" and len(sys.argv) > 3:
        loja_id = sys.argv[2]
        novo_admin_id = int(sys.argv[3])
        transferir_administracao(loja_id, novo_admin_id)
        
    elif comando == "remove" and len(sys.argv) > 2:
        loja_id = sys.argv[2]
        remover_administracao(loja_id)
        
    elif comando == "users":
        listar_usuarios_disponiveis()
        
    else:
        print("❌ Comando inválido ou parâmetros insuficientes")


if __name__ == "__main__":
    main()