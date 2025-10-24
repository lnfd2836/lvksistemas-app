#!/usr/bin/env python
"""
Script para resolver problemas de exclusão de usuários
limpando suas referências antes da exclusão.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from dashboard.models import Notificacao


def clean_user_references(user_id):
    """
    Limpa todas as referências de um usuário antes de excluí-lo
    """
    print(f"🧹 Limpando referências do usuário ID {user_id}...")
    
    try:
        with transaction.atomic():
            # 1. Limpar notificações
            notificacoes_count = Notificacao.objects.filter(usuario_id=user_id).count()
            if notificacoes_count > 0:
                Notificacao.objects.filter(usuario_id=user_id).update(usuario=None)
                print(f"✅ {notificacoes_count} notificações atualizadas")
            else:
                print("✅ Nenhuma notificação encontrada")
            
            # 2. Verificar outras referências (adicione conforme necessário)
            # Exemplo: LogAcesso, SessaoAtiva, etc.
            
            try:
                from usuarios.models import LogAcesso, SessaoAtiva
                
                # Logs de acesso - geralmente mantemos o histórico
                logs_count = LogAcesso.objects.filter(user_id=user_id).count()
                if logs_count > 0:
                    print(f"📋 {logs_count} logs de acesso mantidos (histórico)")
                
                # Sessões ativas - desativar
                sessoes_count = SessaoAtiva.objects.filter(user_id=user_id, ativa=True).count()
                if sessoes_count > 0:
                    SessaoAtiva.objects.filter(user_id=user_id, ativa=True).update(ativa=False)
                    print(f"✅ {sessoes_count} sessões ativas desativadas")
                
            except ImportError:
                print("📋 Modelos de usuários não encontrados - pulando")
            
            # 3. Verificar se o usuário é admin de alguma loja
            try:
                from lojas.models import Loja
                lojas_admin = Loja.objects.filter(admin_user_id=user_id).count()
                if lojas_admin > 0:
                    print(f"⚠️  ATENÇÃO: Usuário é admin de {lojas_admin} loja(s)")
                    print("   Considere transferir a administração antes de excluir")
                    return False
            except:
                pass
            
            # 4. Verificar se é funcionário de alguma loja
            try:
                from lojas.models import Funcionario
                funcionario = Funcionario.objects.filter(user_id=user_id).first()
                if funcionario:
                    print(f"📋 Usuário é funcionário da loja: {funcionario.loja.nome}")
                    funcionario.ativo = False
                    funcionario.save()
                    print("✅ Funcionário desativado")
            except:
                pass
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao limpar referências: {e}")
        return False


def safe_delete_user(user_id):
    """
    Exclui um usuário de forma segura
    """
    print(f"\n🗑️  Iniciando exclusão segura do usuário ID {user_id}...")
    
    try:
        # Verificar se o usuário existe
        try:
            user = User.objects.get(id=user_id)
            print(f"👤 Usuário encontrado: {user.username} ({user.email})")
        except User.DoesNotExist:
            print(f"❌ Usuário com ID {user_id} não encontrado")
            return False
        
        # Limpar referências primeiro
        if not clean_user_references(user_id):
            print("❌ Falha ao limpar referências. Verifique as dependências.")
            return False
        
        # Confirmar exclusão
        print(f"\n⚠️  Tem certeza que deseja excluir o usuário '{user.username}'?")
        print("   Esta ação não pode ser desfeita!")
        
        if len(sys.argv) > 2 and sys.argv[2] == "--force":
            confirm = "sim"
        else:
            confirm = input("Digite 'sim' para confirmar: ").lower().strip()
        
        if confirm == "sim":
            # Tentar excluir o usuário
            with transaction.atomic():
                username = user.username
                user.delete()
                print(f"✅ Usuário '{username}' excluído com sucesso!")
                return True
        else:
            print("❌ Exclusão cancelada pelo usuário")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao excluir usuário: {e}")
        return False


def list_problematic_users():
    """
    Lista usuários que podem ter problemas de referência
    """
    print("🔍 Verificando usuários com possíveis problemas de referência...")
    
    try:
        # Usuários com notificações
        users_with_notifications = User.objects.filter(notificacoes__isnull=False).distinct()
        print(f"\n📋 Usuários com notificações: {users_with_notifications.count()}")
        for user in users_with_notifications[:10]:  # Mostrar apenas os primeiros 10
            notif_count = user.notificacoes.count()
            print(f"   - {user.username} (ID: {user.id}) - {notif_count} notificações")
        
        # Verificar usuários órfãos em notificações
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT usuario_id 
                FROM dashboard_notificacao 
                WHERE usuario_id IS NOT NULL 
                AND usuario_id NOT IN (SELECT id FROM auth_user)
            """)
            orphan_refs = cursor.fetchall()
            
            if orphan_refs:
                print(f"\n⚠️  Referências órfãs encontradas: {len(orphan_refs)}")
                for ref in orphan_refs:
                    print(f"   - Usuário ID {ref[0]} (não existe mais)")
            else:
                print("\n✅ Nenhuma referência órfã encontrada")
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")


if __name__ == "__main__":
    print("🚀 Script de Correção - Exclusão Segura de Usuários")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            # Listar usuários problemáticos
            list_problematic_users()
        elif sys.argv[1] == "delete" and len(sys.argv) > 2:
            # Excluir usuário específico
            user_id = int(sys.argv[2])
            safe_delete_user(user_id)
        elif sys.argv[1] == "clean" and len(sys.argv) > 2:
            # Apenas limpar referências sem excluir
            user_id = int(sys.argv[2])
            clean_user_references(user_id)
        else:
            print("Uso:")
            print("  python fix_user_deletion.py list                    # Listar usuários problemáticos")
            print("  python fix_user_deletion.py delete <id>             # Excluir usuário com ID")
            print("  python fix_user_deletion.py delete <id> --force     # Excluir sem confirmação")
            print("  python fix_user_deletion.py clean <id>              # Apenas limpar referências")
    else:
        # Listar por padrão
        list_problematic_users()
    
    print("\n🏁 Script finalizado!")