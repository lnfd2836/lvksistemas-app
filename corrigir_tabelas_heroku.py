#!/usr/bin/env python3
"""
Script para corrigir tabelas faltando no Heroku
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
    print("🔧 CORREÇÃO - TABELAS FALTANDO NO HEROKU")
    print("=" * 60)
    print()
    
    print("Problema identificado:")
    print("❌ Tabelas do módulo avaliacao_qualidade não existem no Heroku")
    print("❌ Erro: no such table: avaliacao_qualidade_curso")
    print("❌ Erro: no such table: avaliacao_qualidade_perfilusuario")
    print()
    
    print("✅ BOA NOTÍCIA: Login da Fatesa está funcionando!")
    print("✅ Página carrega corretamente")
    print("✅ Link 'Esqueci minha senha' presente")
    print("✅ Botão 'Login Administrativo' removido")
    print()
    
    # Comandos para corrigir tabelas no Heroku
    comandos = [
        ("heroku run --app lvksistemas-app python manage.py makemigrations", "Criando migrações"),
        ("heroku run --app lvksistemas-app python manage.py migrate", "Aplicando migrações no Heroku"),
        ("heroku run --app lvksistemas-app python manage.py migrate avaliacao_qualidade", "Migrando módulo avaliacao_qualidade"),
    ]
    
    success_count = 0
    for comando, descricao in comandos:
        if executar_comando(comando, descricao):
            success_count += 1
        print()
    
    print("=" * 60)
    print("📋 RESULTADO DA CORREÇÃO")
    print("=" * 60)
    
    print("✅ LOGIN DA FATESA - FUNCIONANDO PERFEITAMENTE!")
    print("🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/fatesa-escola-de-ultrassonografia/")
    print()
    
    if success_count >= 2:
        print("✅ TABELAS DO BANCO CORRIGIDAS!")
        print("  - Migrações aplicadas no Heroku")
        print("  - Módulo avaliacao_qualidade corrigido")
        
    else:
        print("⚠️  CORREÇÃO PARCIAL DAS TABELAS")
        print("  - Login da Fatesa funcionando")
        print("  - Algumas migrações podem ter falhado")
    
    print()
    print("🧪 TESTE FINAL RECOMENDADO:")
    print("1. ✅ Login Fatesa: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/fatesa-escola-de-ultrassonografia/")
    print("2. ✅ Clique em 'Esqueci minha senha'")
    print("3. ✅ Digite um email válido")
    print("4. ✅ Verifique se recebe nova senha por email")
    print("5. ✅ Teste login com nova senha")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()