#!/usr/bin/env python
"""
Script para analisar e remover arquivos redundantes do sistema
"""

import os
import sys
import shutil
from pathlib import Path

def analyze_redundant_files():
    """Analisa arquivos redundantes no sistema"""
    
    print("🔍 ANÁLISE DE ARQUIVOS REDUNDANTES")
    print("=" * 50)
    
    redundant_files = []
    
    # 1. Arquivos de documentação redundantes/obsoletos
    docs_to_remove = [
        "CORRECAO_BOTAO_SEMPRE_VISIVEL.md",
        "CORRECAO_ERRO_500_DETALHES_LOJA.md", 
        "CORRECAO_ERRO_500.md",
        "CORRECAO_FINAL_TEMPLATE_DJANGO.md",
        "CORRECAO_MIGRACAO_HEROKU.md",
        "CORRECAO_URLS_LOGIN_DASHBOARD.md",
        "CORRECOES_APLICADAS_SESSOES_LOGIN.md",
        "CORRECOES_APLICADAS.md",
        "DASHBOARD_FIXES.md",
        "DEPLOY_HEROKU_SUCESSO.md",  # Mantém apenas o mais recente
        "DNS_QUICK_REFERENCE.md",
        "DOCUMENTACAO_COMPLETA_MIGRACAO.md",
        "domain_diagnosis.md",
        "FINAL_URL_FIXES.md",
        "heroku_configuration_status.md",
        "MIDDLEWARE_APRIMORADO.md",
        "MONITORAMENTO_DATABASE.md",
        "OPTIMIZATION_SUMMARY.md",
        "PROCEDIMENTOS_DEPLOYMENT.md",
        "PROCEDIMENTOS_ROLLBACK.md",
        "RECUPERACAO_CREDENCIAIS_LOJA.md",
        "REMOCAO_BOTAO_ALTERAR_SENHA.md",
        "SENHA_AUTOMATICA_SUPER_ADMIN.md",
        "SIMPLIFICACAO_SENHA_AUTOMATICA.md",
        "SISTEMA_BOLETOS_AUTOMATICOS.md",
        "SISTEMA_EMAIL_CORRIGIDO.md",
        "SISTEMA_EMAIL_FUNCIONANDO.md",
        "SISTEMA_EMAIL.md",
        "URL_FIXES_SUMMARY.md"
    ]
    
    # 2. Scripts de teste/debug temporários
    scripts_to_remove = [
        "check_users.py",
        "check_wagner_user.py", 
        "create_superuser.py",
        "create_wagner_user.py",
        "debug_login_loja.py",
        "find_loja_daniel.py",
        "gerar_credenciais_daniel.py",
        "run_url_tests.py",
        "test_auth_service.py",
        "test_corrections.py", 
        "test_login_nayara.py",
        "test_wagner_login.py",
        "clear_template_cache.py",
        "diagnose_urls.py"
    ]
    
    # 3. Arquivos de log temporários
    log_files_to_remove = [
        "django_server.log",
        "server.log"
    ]
    
    # 4. Middlewares redundantes (manter apenas os ativos)
    middleware_to_remove = [
        "usuarios/middleware.py",  # Substituído por improved_middleware.py
        "usuarios/password_views.py"  # Funcionalidade integrada
    ]
    
    # 5. Arquivos de configuração obsoletos
    config_to_remove = [
        "requirements_basic.txt",  # Manter apenas requirements.txt
        "env_example.txt"  # Informação já está na documentação
    ]
    
    # Compilar lista completa
    all_files_to_remove = (
        docs_to_remove + 
        scripts_to_remove + 
        log_files_to_remove + 
        middleware_to_remove + 
        config_to_remove
    )
    
    # Verificar quais arquivos existem
    existing_files = []
    total_size = 0
    
    for file_path in all_files_to_remove:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            existing_files.append((file_path, size))
    
    print(f"📊 RESUMO DA ANÁLISE:")
    print(f"   Arquivos redundantes encontrados: {len(existing_files)}")
    print(f"   Espaço total a ser liberado: {total_size / 1024:.1f} KB")
    print()
    
    # Categorizar por tipo
    categories = {
        "📄 Documentação obsoleta": [],
        "🧪 Scripts de teste/debug": [],
        "📝 Arquivos de log": [],
        "⚙️  Middlewares redundantes": [],
        "🔧 Configurações obsoletas": []
    }
    
    for file_path, size in existing_files:
        if file_path in docs_to_remove:
            categories["📄 Documentação obsoleta"].append((file_path, size))
        elif file_path in scripts_to_remove:
            categories["🧪 Scripts de teste/debug"].append((file_path, size))
        elif file_path in log_files_to_remove:
            categories["📝 Arquivos de log"].append((file_path, size))
        elif file_path in middleware_to_remove:
            categories["⚙️  Middlewares redundantes"].append((file_path, size))
        elif file_path in config_to_remove:
            categories["🔧 Configurações obsoletas"].append((file_path, size))
    
    # Mostrar por categoria
    for category, files in categories.items():
        if files:
            print(f"{category}:")
            for file_path, size in files:
                print(f"   - {file_path} ({size} bytes)")
            print()
    
    return existing_files

def remove_redundant_files(files_to_remove, dry_run=True):
    """Remove arquivos redundantes"""
    
    if dry_run:
        print("🔍 SIMULAÇÃO (DRY RUN) - Nenhum arquivo será removido")
    else:
        print("🗑️  REMOVENDO ARQUIVOS REDUNDANTES")
    
    print("=" * 50)
    
    removed_count = 0
    total_size_freed = 0
    
    for file_path, size in files_to_remove:
        try:
            if dry_run:
                print(f"   [SIMULAÇÃO] Removeria: {file_path}")
            else:
                os.remove(file_path)
                print(f"   ✅ Removido: {file_path}")
                removed_count += 1
                total_size_freed += size
        except Exception as e:
            print(f"   ❌ Erro ao remover {file_path}: {e}")
    
    print()
    if dry_run:
        print(f"📊 SIMULAÇÃO CONCLUÍDA:")
        print(f"   Arquivos que seriam removidos: {len(files_to_remove)}")
        print(f"   Espaço que seria liberado: {sum(size for _, size in files_to_remove) / 1024:.1f} KB")
    else:
        print(f"📊 LIMPEZA CONCLUÍDA:")
        print(f"   Arquivos removidos: {removed_count}")
        print(f"   Espaço liberado: {total_size_freed / 1024:.1f} KB")

def fix_middleware_duplicates():
    """Corrige duplicações no MIDDLEWARE do settings.py"""
    
    print("🔧 CORRIGINDO DUPLICAÇÕES NO MIDDLEWARE")
    print("=" * 50)
    
    settings_file = "lojad/settings.py"
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup do arquivo original
        backup_file = f"{settings_file}.backup"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Backup criado: {backup_file}")
        
        # Corrigir duplicações no MIDDLEWARE
        lines = content.split('\n')
        new_lines = []
        in_middleware = False
        seen_middleware = set()
        
        for line in lines:
            if 'MIDDLEWARE = [' in line:
                in_middleware = True
                new_lines.append(line)
                continue
            elif in_middleware and line.strip() == ']':
                in_middleware = False
                new_lines.append(line)
                continue
            elif in_middleware:
                # Remove duplicatas
                stripped = line.strip()
                if stripped and stripped not in seen_middleware:
                    seen_middleware.add(stripped)
                    new_lines.append(line)
                elif stripped in seen_middleware:
                    print(f"   🗑️  Removendo duplicata: {stripped}")
            else:
                new_lines.append(line)
        
        # Salvar arquivo corrigido
        new_content = '\n'.join(new_lines)
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Duplicações corrigidas em {settings_file}")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware: {e}")

def main():
    """Função principal"""
    
    print("🧹 SISTEMA DE LIMPEZA DE ARQUIVOS REDUNDANTES")
    print("=" * 60)
    print()
    
    # Análise
    files_to_remove = analyze_redundant_files()
    
    if not files_to_remove:
        print("✅ Nenhum arquivo redundante encontrado!")
        return
    
    # Perguntar se quer fazer dry run ou remoção real
    print("🤔 O que deseja fazer?")
    print("1. Simulação (dry run) - apenas mostrar o que seria removido")
    print("2. Remover arquivos redundantes")
    print("3. Apenas corrigir duplicações no middleware")
    print("4. Fazer tudo (corrigir middleware + remover arquivos)")
    print("5. Cancelar")
    
    choice = input("\nEscolha uma opção (1-5): ").strip()
    
    if choice == "1":
        remove_redundant_files(files_to_remove, dry_run=True)
    elif choice == "2":
        remove_redundant_files(files_to_remove, dry_run=False)
    elif choice == "3":
        fix_middleware_duplicates()
    elif choice == "4":
        fix_middleware_duplicates()
        print()
        remove_redundant_files(files_to_remove, dry_run=False)
    elif choice == "5":
        print("❌ Operação cancelada.")
    else:
        print("❌ Opção inválida.")

if __name__ == "__main__":
    main()