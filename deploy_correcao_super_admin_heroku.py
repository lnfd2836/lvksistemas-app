#!/usr/bin/env python
"""
Script para fazer deploy da correção do middleware super admin no Heroku
"""

import subprocess
import sys
import os

def executar_comando(comando, descricao):
    """Executa um comando e mostra o resultado"""
    print(f"🔄 {descricao}...")
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {descricao} - Sucesso")
            if result.stdout:
                print(f"📝 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {descricao} - Erro")
            if result.stderr:
                print(f"🚨 Erro: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {descricao} - Exceção: {e}")
        return False

def main():
    """
    Deploy das correções para o Heroku
    """
    print("🚀 DEPLOY DA CORREÇÃO DO MIDDLEWARE SUPER ADMIN")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ Erro: Execute este script no diretório raiz do projeto Django")
        sys.exit(1)
    
    # Lista de comandos para deploy
    comandos = [
        ("git add .", "Adicionando arquivos ao git"),
        ("git commit -m 'Fix: Corrigir middleware que bloqueava super admin de acessar lojas'", "Fazendo commit das correções"),
        ("git push heroku main", "Fazendo push para o Heroku"),
        ("heroku run python manage.py migrate --app lvksistemas-app", "Executando migrações no Heroku"),
        ("heroku run python manage.py collectstatic --noinput --app lvksistemas-app", "Coletando arquivos estáticos"),
    ]
    
    success_count = 0
    
    for comando, descricao in comandos:
        if executar_comando(comando, descricao):
            success_count += 1
        else:
            print(f"⚠️ Falha em: {descricao}")
            resposta = input("Continuar mesmo assim? (s/n): ")
            if resposta.lower() != 's':
                print("❌ Deploy cancelado pelo usuário")
                sys.exit(1)
    
    print("=" * 60)
    print(f"📊 RESULTADO: {success_count}/{len(comandos)} comandos executados com sucesso")
    
    if success_count == len(comandos):
        print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("✅ As correções foram aplicadas no Heroku")
        print("🌐 Teste o acesso em: https://lvksistemas-app-4f6fa281e217.herokuapp.com/lojas/")
    else:
        print("⚠️ DEPLOY PARCIALMENTE CONCLUÍDO")
        print("🔍 Verifique os erros acima")
    
    print("=" * 60)
    
    # Comandos adicionais para verificação
    print("\n📋 COMANDOS ÚTEIS PARA VERIFICAÇÃO:")
    print("heroku logs --tail")
    print("heroku run python manage.py shell")
    print("heroku run python manage.py createsuperuser")

if __name__ == '__main__':
    main()