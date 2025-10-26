#!/usr/bin/env python
"""
Script para fazer deploy das correções de loop de login no Heroku
"""
import os
import sys
import subprocess
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.test import Client
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Deploy das correções no Heroku"""
    
    print("🚀 DEPLOY DAS CORREÇÕES DE LOOP NO HEROKU")
    print("=" * 50)
    
    # 1. Verificar se as correções estão funcionando localmente
    print("\n1️⃣ VERIFICANDO CORREÇÕES LOCALMENTE")
    if not verificar_correcoes_locais():
        print("❌ Correções não estão funcionando localmente. Abortando deploy.")
        return False
    
    # 2. Verificar status do Git
    print("\n2️⃣ VERIFICANDO STATUS DO GIT")
    if not verificar_git():
        print("❌ Problemas com Git. Abortando deploy.")
        return False
    
    # 3. Fazer commit das alterações
    print("\n3️⃣ FAZENDO COMMIT DAS ALTERAÇÕES")
    if not fazer_commit():
        print("❌ Erro ao fazer commit. Abortando deploy.")
        return False
    
    # 4. Deploy no Heroku
    print("\n4️⃣ FAZENDO DEPLOY NO HEROKU")
    if not deploy_heroku():
        print("❌ Erro no deploy do Heroku.")
        return False
    
    # 5. Verificar se o deploy funcionou
    print("\n5️⃣ VERIFICANDO DEPLOY NO HEROKU")
    verificar_deploy_heroku()
    
    print("\n✅ DEPLOY CONCLUÍDO COM SUCESSO!")
    print("🎉 O sistema de login deve estar funcionando corretamente no Heroku agora.")
    
    return True

def verificar_correcoes_locais():
    """Verifica se as correções estão funcionando localmente"""
    
    try:
        client = Client()
        
        # Teste 1: Página inicial não deve ter loop
        print("   🧪 Testando página inicial...")
        response = client.get('/')
        if response.status_code != 200:
            print(f"   ❌ Página inicial retornou status {response.status_code}")
            return False
        print("   ✅ Página inicial funcionando")
        
        # Teste 2: Login personalizado deve funcionar
        print("   🧪 Testando login personalizado...")
        loja = Loja.objects.filter(status='ativa').first()
        if loja:
            try:
                login_config = loja.login_personalizado
                login_url = login_config.get_login_url()
                response = client.get(login_url)
                if response.status_code != 200:
                    print(f"   ❌ Login personalizado retornou status {response.status_code}")
                    return False
                print("   ✅ Login personalizado funcionando")
            except Exception as e:
                print(f"   ❌ Erro no login personalizado: {str(e)}")
                return False
        
        # Teste 3: Admin deve funcionar
        print("   🧪 Testando admin...")
        response = client.get('/admin/')
        if response.status_code not in [200, 302]:
            print(f"   ❌ Admin retornou status {response.status_code}")
            return False
        print("   ✅ Admin funcionando")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nos testes locais: {str(e)}")
        return False

def verificar_git():
    """Verifica o status do Git"""
    
    try:
        # Verificar se há mudanças para commit
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("   📝 Mudanças detectadas:")
            for line in result.stdout.strip().split('\n'):
                print(f"      {line}")
        else:
            print("   ℹ️  Nenhuma mudança detectada")
        
        # Verificar branch atual
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        branch = result.stdout.strip()
        print(f"   🌿 Branch atual: {branch}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro no Git: {str(e)}")
        return False

def fazer_commit():
    """Faz commit das alterações"""
    
    try:
        # Adicionar arquivos modificados
        print("   📝 Adicionando arquivos...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Fazer commit
        commit_message = "Corrigir loops de redirecionamento no sistema de login"
        print(f"   💾 Fazendo commit: {commit_message}")
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        print("   ✅ Commit realizado com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e):
            print("   ℹ️  Nada para fazer commit")
            return True
        print(f"   ❌ Erro no commit: {str(e)}")
        return False

def deploy_heroku():
    """Faz deploy no Heroku"""
    
    try:
        # Verificar se Heroku CLI está instalado
        print("   🔧 Verificando Heroku CLI...")
        subprocess.run(['heroku', '--version'], 
                      capture_output=True, check=True)
        print("   ✅ Heroku CLI encontrado")
        
        # Fazer push para Heroku
        print("   🚀 Fazendo push para Heroku...")
        result = subprocess.run(['git', 'push', 'heroku', 'main'], 
                              capture_output=True, text=True, check=True)
        
        print("   ✅ Deploy realizado com sucesso")
        
        # Mostrar últimas linhas do output
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            print("   📋 Últimas linhas do deploy:")
            for line in lines[-5:]:
                print(f"      {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro no deploy: {str(e)}")
        if e.stdout:
            print("   📋 Output:")
            print(e.stdout)
        if e.stderr:
            print("   📋 Erro:")
            print(e.stderr)
        return False

def verificar_deploy_heroku():
    """Verifica se o deploy no Heroku funcionou"""
    
    try:
        # Obter URL do app
        print("   🌐 Obtendo URL do app...")
        result = subprocess.run(['heroku', 'apps:info', '--json'], 
                              capture_output=True, text=True, check=True)
        
        import json
        app_info = json.loads(result.stdout)
        app_url = app_info.get('web_url', 'https://loja-conveniencia-pdv-7fed430df60a.herokuapp.com/')
        
        print(f"   🔗 URL do app: {app_url}")
        
        # Verificar logs recentes
        print("   📋 Verificando logs recentes...")
        result = subprocess.run(['heroku', 'logs', '--tail', '--num=10'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("   📋 Logs recentes:")
            for line in result.stdout.strip().split('\n')[-5:]:
                print(f"      {line}")
        
        print(f"\n   🎯 TESTE MANUAL:")
        print(f"   1. Acesse: {app_url}")
        print(f"   2. Verifique se a página de seleção de lojas aparece")
        print(f"   3. Teste o login de uma loja específica")
        print(f"   4. Verifique se não há loops de redirecionamento")
        
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar deploy: {str(e)}")
        print("   ℹ️  Verifique manualmente se o deploy funcionou")

if __name__ == '__main__':
    main()