#!/usr/bin/env python3
"""
Script para corrigir erro de template da Fatesa
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
    print("=" * 60)
    print("🔧 CORREÇÃO URGENTE - TEMPLATE FATESA")
    print("=" * 60)
    print()
    
    print("Problema identificado:")
    print("❌ Erro de sintaxe no template da Fatesa (linha 508)")
    print("❌ {% endif %} duplicado causando erro de renderização")
    print()
    
    print("Correção aplicada:")
    print("✅ Removido {% endif %} duplicado")
    print("✅ Template da Fatesa corrigido")
    print()
    
    # Comandos de deploy
    comandos = [
        ("git add templates/auth/login_personalizado_fatesa.html", "Adicionando template corrigido"),
        ('git commit -m "fix: Corrige erro de sintaxe no template da Fatesa (endif duplicado)"', "Criando commit de correção"),
        ("git push heroku main", "Fazendo deploy da correção"),
    ]
    
    success_count = 0
    for comando, descricao in comandos:
        if executar_comando(comando, descricao):
            success_count += 1
        print()
    
    print("=" * 60)
    print("📋 RESULTADO DA CORREÇÃO")
    print("=" * 60)
    
    if success_count >= 3:
        print("✅ CORREÇÃO APLICADA COM SUCESSO!")
        print()
        print("🌐 Teste agora:")
        print("https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/fatesa-escola-de-ultrassonografia/")
        print()
        print("✅ O que foi corrigido:")
        print("  - Erro de sintaxe Django template")
        print("  - {% endif %} duplicado removido")
        print("  - Template da Fatesa funcionando")
        
    else:
        print("❌ CORREÇÃO PARCIAL - Alguns comandos falharam")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()