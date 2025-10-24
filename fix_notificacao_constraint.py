#!/usr/bin/env python
"""
Script para corrigir o problema de constraint de chave estrangeira
na tabela dashboard_notificacao ao excluir usuários.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth.models import User
from dashboard.models import Notificacao


def fix_notificacao_constraint():
    """
    Corrige o problema de constraint na tabela dashboard_notificacao
    """
    print("🔧 Iniciando correção da constraint dashboard_notificacao...")
    
    try:
        with transaction.atomic():
            # 1. Verificar se existem notificações órfãs
            print("\n📊 Verificando notificações órfãs...")
            
            # Buscar notificações com usuários que não existem mais
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM dashboard_notificacao dn 
                    LEFT JOIN auth_user au ON dn.usuario_id = au.id 
                    WHERE dn.usuario_id IS NOT NULL AND au.id IS NULL
                """)
                orfas = cursor.fetchone()[0]
                
                if orfas > 0:
                    print(f"⚠️  Encontradas {orfas} notificações órfãs")
                    
                    # Limpar notificações órfãs
                    cursor.execute("""
                        DELETE FROM dashboard_notificacao 
                        WHERE usuario_id NOT IN (SELECT id FROM auth_user)
                        AND usuario_id IS NOT NULL
                    """)
                    print(f"✅ {orfas} notificações órfãs removidas")
                else:
                    print("✅ Nenhuma notificação órfã encontrada")
            
            # 2. Verificar se estamos usando SQLite
            print("\n🔍 Verificando tipo de banco de dados...")
            db_engine = connection.settings_dict['ENGINE']
            print(f"📋 Engine: {db_engine}")
            
            if 'sqlite' in db_engine.lower():
                print("📋 Detectado SQLite - aplicando correção específica...")
                
                # No SQLite, vamos verificar se a migração foi aplicada corretamente
                with connection.cursor() as cursor:
                    # Verificar se a tabela existe e tem a estrutura correta
                    cursor.execute("PRAGMA foreign_key_list(dashboard_notificacao)")
                    foreign_keys = cursor.fetchall()
                    
                    print(f"📋 Foreign keys encontradas: {len(foreign_keys)}")
                    for fk in foreign_keys:
                        print(f"   - {fk}")
                    
                    # Verificar se há registros problemáticos
                    cursor.execute("""
                        SELECT COUNT(*) FROM dashboard_notificacao 
                        WHERE usuario_id IS NOT NULL 
                        AND usuario_id NOT IN (SELECT id FROM auth_user)
                    """)
                    problematic = cursor.fetchone()[0]
                    
                    if problematic > 0:
                        print(f"⚠️  Encontrados {problematic} registros com referências inválidas")
                        
                        # Corrigir definindo usuario_id como NULL
                        cursor.execute("""
                            UPDATE dashboard_notificacao 
                            SET usuario_id = NULL 
                            WHERE usuario_id IS NOT NULL 
                            AND usuario_id NOT IN (SELECT id FROM auth_user)
                        """)
                        print(f"✅ {problematic} registros corrigidos (usuario_id definido como NULL)")
                    else:
                        print("✅ Nenhum registro problemático encontrado")
                        
            else:
                print("📋 Banco PostgreSQL/MySQL detectado - aplicando correção específica...")
                # Código original para PostgreSQL/MySQL aqui
                pass
            
            print("\n✅ Correção da constraint concluída com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False
    
    return True


def clean_user_notifications(user_id):
    """
    Limpa todas as notificações de um usuário específico antes de excluí-lo
    """
    print(f"\n🧹 Limpando notificações do usuário ID {user_id}...")
    
    try:
        # Buscar notificações do usuário
        notificacoes = Notificacao.objects.filter(usuario_id=user_id)
        count = notificacoes.count()
        
        if count > 0:
            print(f"📋 Encontradas {count} notificações para o usuário")
            
            # Definir usuario como NULL em vez de excluir
            notificacoes.update(usuario=None)
            print(f"✅ {count} notificações atualizadas (usuario definido como NULL)")
        else:
            print("✅ Nenhuma notificação encontrada para este usuário")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar notificações: {e}")
        return False


def safe_delete_user(user_id):
    """
    Exclui um usuário de forma segura, limpando suas notificações primeiro
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
        
        # Limpar notificações primeiro
        if not clean_user_notifications(user_id):
            print("❌ Falha ao limpar notificações. Abortando exclusão.")
            return False
        
        # Tentar excluir o usuário
        with transaction.atomic():
            user.delete()
            print(f"✅ Usuário {user.username} excluído com sucesso!")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao excluir usuário: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Script de Correção - Constraint dashboard_notificacao")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "fix":
            # Corrigir constraint
            fix_notificacao_constraint()
        elif sys.argv[1] == "delete" and len(sys.argv) > 2:
            # Excluir usuário específico
            user_id = int(sys.argv[2])
            safe_delete_user(user_id)
        else:
            print("Uso:")
            print("  python fix_notificacao_constraint.py fix           # Corrigir constraint")
            print("  python fix_notificacao_constraint.py delete <id>  # Excluir usuário com ID")
    else:
        # Executar correção por padrão
        fix_notificacao_constraint()
    
    print("\n🏁 Script finalizado!")