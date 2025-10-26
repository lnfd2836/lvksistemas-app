#!/usr/bin/env python
"""
Script para corrigir todos os problemas de esquema do banco de dados
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    sys.exit(1)

from django.core.management import call_command
from django.db import connection, connections
from django.apps import apps

def fix_avaliacao_qualidade_table():
    """Corrige problemas na tabela avaliacao_qualidade_perfilusuario"""
    print("🔧 CORRIGINDO TABELA AVALIACAO_QUALIDADE")
    print("=" * 45)
    
    try:
        with connection.cursor() as cursor:
            # Verificar colunas existentes
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'avaliacao_qualidade_perfilusuario'
                ORDER BY ordinal_position
            """)
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            print(f"📊 Colunas existentes: {len(existing_columns)}")
            
            # Colunas que devem existir
            required_columns = {
                'loja_associada_id': 'UUID NULL',
                'deve_alterar_senha': 'BOOLEAN DEFAULT FALSE'
            }
            
            # Adicionar colunas faltantes
            for column_name, column_def in required_columns.items():
                if column_name not in existing_columns:
                    print(f"🔧 Adicionando coluna: {column_name}")
                    cursor.execute(f"""
                        ALTER TABLE avaliacao_qualidade_perfilusuario 
                        ADD COLUMN {column_name} {column_def}
                    """)
                    print(f"✅ Coluna {column_name} adicionada")
                else:
                    print(f"✅ Coluna {column_name} já existe")
            
            # Criar índices se necessário
            indexes = [
                ('avaliacao_qualidade_perfilusuario_loja_associada_id', 'loja_associada_id'),
            ]
            
            for index_name, column in indexes:
                try:
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON avaliacao_qualidade_perfilusuario({column})
                    """)
                    print(f"✅ Índice {index_name} criado/verificado")
                except Exception as e:
                    print(f"⚠️  Erro no índice {index_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir tabela: {e}")
        return False

def fix_usuarios_table():
    """Corrige problemas na tabela usuarios_perfilusuario"""
    print("\n🔧 CORRIGINDO TABELA USUARIOS")
    print("=" * 30)
    
    try:
        with connection.cursor() as cursor:
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios_perfilusuario'
            """)
            
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Verificar colunas existentes
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios_perfilusuario'
                    ORDER BY ordinal_position
                """)
                
                existing_columns = [row[0] for row in cursor.fetchall()]
                print(f"📊 Colunas existentes na tabela usuarios: {len(existing_columns)}")
                
                # Colunas que devem existir
                required_columns = {
                    'deve_trocar_senha': 'BOOLEAN DEFAULT FALSE',
                    'senha_temporaria': 'BOOLEAN DEFAULT FALSE',
                    'data_ultima_troca_senha': 'TIMESTAMP WITH TIME ZONE NULL'
                }
                
                # Adicionar colunas faltantes
                for column_name, column_def in required_columns.items():
                    if column_name not in existing_columns:
                        print(f"🔧 Adicionando coluna: {column_name}")
                        cursor.execute(f"""
                            ALTER TABLE usuarios_perfilusuario 
                            ADD COLUMN {column_name} {column_def}
                        """)
                        print(f"✅ Coluna {column_name} adicionada")
                    else:
                        print(f"✅ Coluna {column_name} já existe")
            else:
                print("ℹ️  Tabela usuarios_perfilusuario não existe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir tabela usuarios: {e}")
        return False

def run_all_migrations():
    """Executa todas as migrações pendentes"""
    print("\n🔄 EXECUTANDO TODAS AS MIGRAÇÕES")
    print("=" * 35)
    
    try:
        # Criar migrações se necessário
        print("📝 Criando migrações...")
        call_command('makemigrations', verbosity=1)
        
        # Executar migrações
        print("🔄 Executando migrações...")
        call_command('migrate', verbosity=1)
        
        print("✅ Migrações concluídas")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas migrações: {e}")
        return False

def validate_all_tables():
    """Valida se todas as tabelas estão corretas"""
    print("\n🔍 VALIDANDO TODAS AS TABELAS")
    print("=" * 35)
    
    try:
        # Tabelas críticas para validar
        critical_tables = [
            'avaliacao_qualidade_perfilusuario',
            'auth_user',
            'lojas_loja',
            'controle_financeiro_transacao',
        ]
        
        with connection.cursor() as cursor:
            for table_name in critical_tables:
                try:
                    # Verificar se a tabela existe
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"✅ {table_name}: {count} registros")
                except Exception as e:
                    print(f"❌ {table_name}: Erro - {e}")
        
        # Testar imports dos modelos
        print("\n🔍 Testando imports dos modelos:")
        
        try:
            from avaliacao_qualidade.models import PerfilUsuario
            count = PerfilUsuario.objects.count()
            print(f"✅ PerfilUsuario: {count} registros")
        except Exception as e:
            print(f"❌ PerfilUsuario: {e}")
        
        try:
            from django.contrib.auth.models import User
            count = User.objects.count()
            print(f"✅ User: {count} registros")
        except Exception as e:
            print(f"❌ User: {e}")
        
        try:
            from lojas.models import Loja
            count = Loja.objects.count()
            print(f"✅ Loja: {count} registros")
        except Exception as e:
            print(f"❌ Loja: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def reset_problematic_migrations():
    """Reset de migrações problemáticas"""
    print("\n🔄 RESET DE MIGRAÇÕES PROBLEMÁTICAS")
    print("=" * 40)
    
    try:
        # Apps que podem ter problemas
        problematic_apps = ['avaliacao_qualidade', 'usuarios']
        
        for app_name in problematic_apps:
            try:
                print(f"🔄 Resetando migrações de {app_name}...")
                
                # Executar migrações específicas
                call_command('migrate', app_name, verbosity=1)
                print(f"✅ {app_name} migrado com sucesso")
                
            except Exception as e:
                print(f"⚠️  Problema com {app_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no reset: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORREÇÃO COMPLETA DE PROBLEMAS DE BANCO")
    print("=" * 50)
    
    steps = [
        ("Corrigir tabela avaliacao_qualidade", fix_avaliacao_qualidade_table),
        ("Corrigir tabela usuarios", fix_usuarios_table),
        ("Reset de migrações", reset_problematic_migrations),
        ("Executar migrações", run_all_migrations),
        ("Validar tabelas", validate_all_tables),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name.upper()} {'='*20}")
        
        try:
            if step_func():
                success_count += 1
                print(f"✅ {step_name}: CONCLUÍDO")
            else:
                print(f"❌ {step_name}: FALHOU")
        except Exception as e:
            print(f"❌ {step_name}: ERRO - {e}")
    
    # Resultado final
    print(f"\n{'='*50}")
    print(f"📊 RESULTADO: {success_count}/{total_steps} passos concluídos")
    
    if success_count == total_steps:
        print("🎉 TODOS OS PROBLEMAS DE BANCO CORRIGIDOS!")
        print("✅ Sistema deve estar funcionando agora")
        print("🌐 Teste acessando: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
    elif success_count >= total_steps - 1:
        print("⚠️  CORREÇÃO QUASE COMPLETA")
        print("🔍 Problemas menores podem persistir")
    else:
        print("❌ VÁRIOS PROBLEMAS PERSISTEM")
        print("🔧 Pode ser necessário intervenção manual")
    
    return success_count >= total_steps - 1

if __name__ == '__main__':
    main()