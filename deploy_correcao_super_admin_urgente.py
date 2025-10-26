#!/usr/bin/env python3
"""
Deploy urgente da correção do super admin
"""

import subprocess
import sys

def executar_comando(comando, descricao):
    """Executa um comando e mostra o resultado"""
    print(f"🔧 {descricao}...")
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {descricao} - Sucesso!")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {descricao} - Erro!")
            if result.stderr.strip():
                print(f"   Erro: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {descricao} - Exceção: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 80)
    print("🚨 DEPLOY URGENTE - CORREÇÃO SUPER ADMIN")
    print("=" * 80)
    print()
    
    print("Problema crítico:")
    print("❌ Super admin não consegue acessar dashboard")
    print("❌ Middleware estava bloqueando acesso incorretamente")
    print()
    
    print("Correção aplicada:")
    print("✅ Middleware problemático desabilitado")
    print("✅ Middleware corrigido para acesso total")
    print("✅ Super admin agora tem acesso completo")
    print()
    
    # Comandos de deploy
    comandos = [
        ("git add .", "Adicionando correções ao Git"),
        ('git commit -m "fix: URGENTE - Corrige bloqueio de super admin no dashboard"', "Criando commit urgente"),
        ("git push heroku main", "Fazendo deploy urgente para Heroku"),
    ]
    
    success_count = 0
    for comando, descricao in comandos:
        if executar_comando(comando, descricao):
            success_count += 1
        print()
    
    print("=" * 80)
    print("📋 RESULTADO DO DEPLOY URGENTE")
    print("=" * 80)
    
    if success_count >= 3:
        print("✅ DEPLOY URGENTE CONCLUÍDO COM SUCESSO!")
        print()
        print("🎯 Correção aplicada:")
        print("  - Middleware problemático desabilitado")
        print("  - Super admin tem acesso total ao sistema")
        print("  - Pode acessar qualquer dashboard")
        print()
        print("🧪 TESTE IMEDIATO:")
        print("  1. Faça login como super admin")
        print("  2. Acesse https://lvksistemas-app-4f6fa281e217.herokuapp.com/dashboard/")
        print("  3. Deve funcionar normalmente agora")
        
    else:
        print("❌ DEPLOY PARCIAL - Alguns comandos falharam")
        print("   Tente fazer o deploy manualmente se necessário")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()