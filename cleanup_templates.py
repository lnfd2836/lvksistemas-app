#!/usr/bin/env python
"""
Script para limpar templates redundantes
"""

import os

def cleanup_redundant_templates():
    """Remove templates redundantes identificados"""
    
    print("🧹 LIMPEZA DE TEMPLATES REDUNDANTES")
    print("=" * 50)
    
    # Templates redundantes identificados
    redundant_templates = [
        "templates/auth/loja_login_clean.html",  # Redundante com loja_login.html
        "templates/debug/system_info.html",     # Template de debug não usado
    ]
    
    # Verificar quais existem
    existing_templates = []
    for template in redundant_templates:
        if os.path.exists(template):
            size = os.path.getsize(template)
            existing_templates.append((template, size))
    
    if not existing_templates:
        print("✅ Nenhum template redundante encontrado!")
        return
    
    print(f"📊 Templates redundantes encontrados: {len(existing_templates)}")
    for template, size in existing_templates:
        print(f"   - {template} ({size} bytes)")
    
    # Confirmar remoção
    confirm = input("\n🤔 Deseja remover estes templates? (y/n): ").strip().lower()
    
    if confirm in ['y', 'yes', 's', 'sim']:
        removed_count = 0
        total_size = 0
        
        for template, size in existing_templates:
            try:
                os.remove(template)
                print(f"   ✅ Removido: {template}")
                removed_count += 1
                total_size += size
            except Exception as e:
                print(f"   ❌ Erro ao remover {template}: {e}")
        
        print(f"\n📊 LIMPEZA CONCLUÍDA:")
        print(f"   Templates removidos: {removed_count}")
        print(f"   Espaço liberado: {total_size / 1024:.1f} KB")
    else:
        print("❌ Operação cancelada.")

if __name__ == "__main__":
    cleanup_redundant_templates()