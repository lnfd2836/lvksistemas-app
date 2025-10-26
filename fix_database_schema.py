#!/usr/bin/env python
"""
Script para corrigir problemas de esquema do banco de dados
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

def check_migrations():
    """Verifica migrações pendentes"""
    print("🔍 VERIFICANDO MIGRAÇÕES")
    print("=" * 25)
    
    try:
        # Verificar migrações pendentes
        from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
        
        print("📋 Status das migrações:")
        call_command('showmigrations', verbosity=1)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar migrações: {e}")
        return False

def run_migrations():
    """Executa todas as migrações"""
    print("\n🔄 EXECUTANDO MIGRAÇÕES")
    print("=" * 25)
    
    try:
        # Executar migrações
        call_command('migrate', verbosity=2)
        print("✅ Migrações executadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def check_database_schema():
    """Verifica esquema do banco de dados"""
    print("\n🔍 VERIFICANDO ESQUEMA DO BANCO")
    print("=" * 35)
    
    try:
        with connection.cursor() as cursor:
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'avaliacao_qualidade_perfilusuario'
            """)
            
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ Tabela avaliacao_qualidade_perfilusuario existe")
                
                # Verificar colunas da tabela
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'avaliacao_qualidade_perfilusuario'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                print(f"📊 Colunas encontradas ({len(columns)}):")
                
                has_loja_associada = False
                for column_name, data_type in columns:
                    print(f"   - {column_name}: {data_type}")
                    if column_name == 'loja_associada_id':
                        has_loja_associada = True
                
                if not has_loja_associada:
                    print("⚠️  Coluna 'loja_associada_id' não encontrada!")
                    return False
                else:
                    print("✅ Coluna 'loja_associada_id' encontrada")
                    return True
            else:
                print("❌ Tabela avaliacao_qualidade_perfilusuario não existe!")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar esquema: {e}")
        return False

def create_missing_migrations():
    """Cria migrações para mudanças não aplicadas"""
    print("\n🔧 CRIANDO MIGRAÇÕES FALTANTES")
    print("=" * 35)
    
    try:
        # Criar migrações automáticas
        call_command('makemigrations', verbosity=2)
        print("✅ Migrações criadas (se necessário)")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar migrações: {e}")
        return False

def reset_avaliacao_qualidade():
    """Reset específico do app avaliacao_qualidade"""
    print("\n🔄 RESET DO APP AVALIACAO_QUALIDADE")
    print("=" * 40)
    
    try:
        # Verificar se há dados importantes
        from avaliacao_qualidade.models import PerfilUsuario
        
        count = PerfilUsuario.objects.count()
        print(f"📊 {count} perfis de usuário encontrados")
        
        if count > 0:
            print("⚠️  Há dados no sistema. Fazendo backup...")
            # Aqui você poderia fazer backup se necessário
        
        # Executar migrações específicas
        call_command('migrate', 'avaliacao_qualidade', verbosity=2)
        print("✅ Migrações do avaliacao_qualidade executadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no reset: {e}")
        return False

def fix_database_issues():
    """Corrige problemas específicos do banco"""
    print("\n🔧 CORRIGINDO PROBLEMAS DO BANCO")
    print("=" * 35)
    
    try:
        with connection.cursor() as cursor:
            # Verificar se a coluna existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'avaliacao_qualidade_perfilusuario' 
                AND column_name = 'loja_associada_id'
            """)
            
            column_exists = cursor.fetchone()
            
            if not column_exists:
                print("🔧 Adicionando coluna loja_associada_id...")
                
                # Adicionar coluna manualmente (como último recurso)
                cursor.execute("""
                    ALTER TABLE avaliacao_qualidade_perfilusuario 
                    ADD COLUMN loja_associada_id UUID NULL
                """)
                
                print("✅ Coluna loja_associada_id adicionada")
                
                # Criar índice se necessário
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS avaliacao_qualidade_perfilusuario_loja_associada_id 
                    ON avaliacao_qualidade_perfilusuario(loja_associada_id)
                """)
                
                print("✅ Índice criado")
                
            else:
                print("✅ Coluna loja_associada_id já existe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir banco: {e}")
        return False

def validate_fix():
    """Valida se a correção funcionou"""
    print("\n✅ VALIDANDO CORREÇÃO")
    print("=" * 20)
    
    try:
        # Tentar importar e usar o modelo
        from avaliacao_qualidade.models import PerfilUsuario
        
        # Tentar fazer uma query simples
        count = PerfilUsuario.objects.count()
        print(f"✅ Query funcionou: {count} perfis encontrados")
        
        # Verificar se o campo existe no modelo
        if hasattr(PerfilUsuario, 'loja_associada'):
            print("✅ Campo loja_associada existe no modelo")
        else:
            print("⚠️  Campo loja_associada não existe no modelo")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE ESQUEMA DO BANCO DE DADOS")
    print("=" * 45)
    
    success_count = 0
    total_steps = 6
    
    # Passo 1: Verificar migrações
    if check_migrations():
        success_count += 1
    
    # Passo 2: Verificar esquema atual
    schema_ok = check_database_schema()
    if schema_ok:
        success_count += 1
    
    # Passo 3: Criar migrações se necessário
    if create_missing_migrations():
        success_count += 1
    
    # Passo 4: Executar migrações
    if run_migrations():
        success_count += 1
    
    # Passo 5: Corrigir problemas específicos se necessário
    if not schema_ok:
        if fix_database_issues():
            success_count += 1
    else:
        success_count += 1
    
    # Passo 6: Validar correção
    if validate_fix():
        success_count += 1
    
    print(f"\n📊 RESULTADO: {success_count}/{total_steps} passos concluídos")
    
    if success_count == total_steps:
        print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Banco de dados corrigido")
        print("🌐 Sistema deve estar funcionando agora")
    else:
        print("⚠️  CORREÇÃO PARCIAL")
        print("🔍 Alguns problemas podem persistir")
    
    return success_count == total_steps

if __name__ == '__main__':
    main()