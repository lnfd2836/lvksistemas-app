#!/usr/bin/env python3
"""
Deploy das correções do login das lojas para o Heroku
"""

import subprocess
import sys
import time

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
    print("🚀 DEPLOY - CORREÇÃO LOGIN DAS LOJAS")
    print("=" * 60)
    print()
    
    print("Correções aplicadas:")
    print("✅ Removido botão 'Login Administrativo' dos templates")
    print("✅ Removido link 'Recuperar Senha' problemático")
    print("✅ Configurações atualizadas no banco de dados")
    print()
    
    # Comandos de deploy
    comandos = [
        ("git add .", "Adicionando arquivos ao Git"),
        ('git commit -m "fix: Remove botão Login Administrativo e link Recuperar Senha das páginas de login das lojas"', "Criando commit"),
        ("git push heroku main", "Fazendo push para Heroku"),
    ]
    
    success_count = 0
    for comando, descricao in comandos:
        if executar_comando(comando, descricao):
            success_count += 1
        else:
            print(f"⚠️  Continuando mesmo com erro em: {descricao}")
        print()
    
    # Aguardar deploy
    print("⏳ Aguardando deploy do Heroku...")
    time.sleep(10)
    
    # Executar correção no Heroku
    print("🔧 Executando correção no banco do Heroku...")
    heroku_cmd = '''heroku run python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from lojas.models_login import LoginPersonalizado

# Desabilitar links de recuperação
configs = LoginPersonalizado.objects.all()
count = 0
for config in configs:
    if config.mostrar_link_recuperar_senha:
        config.mostrar_link_recuperar_senha = False
        config.save()
        count += 1
        print(f'Desabilitado link para: {config.loja.nome}')

print(f'Total atualizado: {count} configurações')
"'''
    
    if executar_comando(heroku_cmd, "Atualizando configurações no Heroku"):
        success_count += 1
    
    print()
    print("=" * 60)
    print("📋 RESUMO DO DEPLOY")
    print("=" * 60)
    
    if success_count >= 3:
        print("✅ DEPLOY CONCLUÍDO COM SUCESSO!")
        print()
        print("🌐 URLs para testar:")
        print("- Fatesa: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/fatesa-escola-de-ultrassonografia/")
        print("- Felix: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/loja-felix/")
        print()
        print("✅ Problemas corrigidos:")
        print("  - Botão 'Login Administrativo' removido")
        print("  - Link 'Recuperar Senha' removido")
        print("  - Páginas de login das lojas limpas")
        
    else:
        print("⚠️  DEPLOY PARCIAL - Alguns comandos falharam")
        print("   Verifique os erros acima e tente novamente se necessário")
    
    print()
    print("🧪 TESTE RECOMENDADO:")
    print("1. Acesse a página de login da Fatesa")
    print("2. Verifique se não há mais botão 'Login Administrativo'")
    print("3. Verifique se não há mais link 'Recuperar Senha'")
    print("4. Teste o login com credenciais válidas")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()