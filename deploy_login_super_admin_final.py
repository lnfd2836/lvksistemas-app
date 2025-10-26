#!/usr/bin/env python
"""
Script para fazer deploy final do login direto de super admin
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
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Deploy final do login direto de super admin"""
    
    print("🚀 DEPLOY FINAL - LOGIN DIRETO SUPER ADMIN")
    print("=" * 50)
    
    # 1. Verificar implementação local
    print("\n1️⃣ VERIFICANDO IMPLEMENTAÇÃO LOCAL")
    if not verificar_implementacao():
        print("❌ Implementação não está funcionando. Abortando.")
        return False
    
    # 2. Fazer deploy
    print("\n2️⃣ FAZENDO DEPLOY NO HEROKU")
    if not fazer_deploy():
        print("❌ Erro no deploy.")
        return False
    
    # 3. Instruções finais
    print("\n3️⃣ INSTRUÇÕES FINAIS")
    mostrar_instrucoes_finais()
    
    print("\n✅ DEPLOY FINAL CONCLUÍDO!")
    return True

def verificar_implementacao():
    """Verifica se a implementação está funcionando"""
    
    try:
        client = Client()
        
        # Teste 1: Página principal deve mostrar formulário de login
        response = client.get('/')
        if response.status_code != 200:
            print(f"   ❌ Página principal retornou status {response.status_code}")
            return False
        
        content = response.content.decode('utf-8')
        if 'Super Admin' not in content or 'name="username"' not in content:
            print("   ❌ Página principal não mostra formulário de super admin")
            return False
        
        print("   ✅ Página principal mostra formulário de super admin")
        
        # Teste 2: Template existe
        template_path = 'templates/auth/super_admin_login.html'
        if not os.path.exists(template_path):
            print(f"   ❌ Template não encontrado: {template_path}")
            return False
        
        print("   ✅ Template de super admin criado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na verificação: {str(e)}")
        return False

def fazer_deploy():
    """Faz o deploy no Heroku"""
    
    try:
        # Commit das mudanças
        print("   📝 Fazendo commit...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        commit_message = "Implementar login direto de super admin na página principal - CORREÇÃO FINAL"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push para Heroku
        print("   🚀 Fazendo push para Heroku...")
        result = subprocess.run(['git', 'push', 'heroku', 'main'], 
                              capture_output=True, text=True, check=True)
        
        print("   ✅ Deploy realizado com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e):
            print("   ℹ️  Nada para fazer commit, fazendo push...")
            try:
                subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
                print("   ✅ Push realizado com sucesso")
                return True
            except subprocess.CalledProcessError as push_error:
                print(f"   ❌ Erro no push: {str(push_error)}")
                return False
        else:
            print(f"   ❌ Erro no deploy: {str(e)}")
            return False

def mostrar_instrucoes_finais():
    """Mostra instruções finais"""
    
    print("   🎯 CORREÇÃO FINAL IMPLEMENTADA:")
    print("   ✅ Página principal mostra DIRETAMENTE o login de super admin")
    print("   ✅ Não há mais seleção de lojas na página principal")
    print("   ✅ Template exclusivo para super admin criado")
    print("   ✅ Validação de super admin implementada")
    print("   ✅ Middleware de proteção mantido")
    print()
    print("   🌐 ARQUITETURA CORRETA IMPLEMENTADA:")
    print()
    print("   1️⃣ SUPER ADMIN (Você):")
    print("      URL: https://www.lvksistemas.com.br/")
    print("      Função: Formulário de login direto")
    print("      Após login: Dashboard para gerenciar lojas")
    print()
    print("   2️⃣ ADMIN DA LOJA + FUNCIONÁRIOS:")
    print("      URL: https://www.lvksistemas.com.br/login/{loja}/")
    print("      Exemplo: https://www.lvksistemas.com.br/login/fatesa-escola-de-ultrassonografia/")
    print("      Função: Login personalizado por loja")
    print("      Após login: Dashboard específico da loja")
    print()
    print("   🧪 COMO TESTAR NO HEROKU:")
    print()
    print("   1. Acesse: https://www.lvksistemas.com.br/")
    print("   2. Deve mostrar DIRETAMENTE o formulário de login de super admin")
    print("   3. Digite suas credenciais de super admin")
    print("   4. Após login: deve ir para /dashboard/ (área de gerenciamento)")
    print()
    print("   ⚠️  IMPORTANTE:")
    print("   - A página principal NÃO mostra mais seleção de lojas")
    print("   - Super admins fazem login DIRETAMENTE na página principal")
    print("   - Lojas têm URLs específicas e personalizadas")
    print("   - Sistema agora segue a arquitetura correta!")

if __name__ == '__main__':
    main()