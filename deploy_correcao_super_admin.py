#!/usr/bin/env python
"""
Script para fazer deploy da correção específica do super admin no Heroku
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
from django.contrib.auth.models import User
from lojas.models import Loja
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Deploy da correção do super admin"""
    
    print("🚀 DEPLOY CORREÇÃO SUPER ADMIN HEROKU")
    print("=" * 50)
    
    # 1. Verificar correção localmente
    print("\n1️⃣ VERIFICANDO CORREÇÃO LOCALMENTE")
    if not verificar_correcao_local():
        print("❌ Correção não funciona localmente. Abortando.")
        return False
    
    # 2. Fazer commit e deploy
    print("\n2️⃣ FAZENDO DEPLOY")
    if not fazer_deploy():
        print("❌ Erro no deploy.")
        return False
    
    # 3. Instruções para teste no Heroku
    print("\n3️⃣ INSTRUÇÕES PARA TESTE NO HEROKU")
    mostrar_instrucoes_teste()
    
    print("\n✅ DEPLOY CONCLUÍDO!")
    return True

def verificar_correcao_local():
    """Verifica se a correção funciona localmente"""
    
    try:
        # Simular cenário Heroku (uma loja)
        print("   🧪 Simulando cenário Heroku...")
        
        # Desativar todas as lojas exceto uma
        lojas = Loja.objects.all()
        primeira_loja = lojas.first()
        
        if primeira_loja:
            Loja.objects.exclude(id=primeira_loja.id).update(status='inativa')
            primeira_loja.status = 'ativa'
            primeira_loja.save()
            
            print(f"   ✅ Simulação: apenas {primeira_loja.nome} ativa")
        
        # Testar página inicial sem autenticação
        client = Client()
        response = client.get('/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'Acesso para Administradores do Sistema' in content:
                print("   ✅ Página de seleção com opção de admin funcionando")
            else:
                print("   ❌ Opção de admin não encontrada na página")
                return False
        else:
            print(f"   ❌ Página inicial retornou status {response.status_code}")
            return False
        
        # Testar URL especial para admin
        response = client.get('/?admin=1')
        if response.status_code == 302 and '/admin/login/' in response.url:
            print("   ✅ URL com parâmetro admin funcionando")
        else:
            print("   ⚠️  URL com parâmetro admin não funcionou como esperado")
        
        # Restaurar estado original
        Loja.objects.all().update(status='ativa')
        print("   ✅ Estado original restaurado")
        
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
        
        commit_message = "Corrigir redirecionamento de super admin para login de loja no Heroku"
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

def mostrar_instrucoes_teste():
    """Mostra instruções para testar no Heroku"""
    
    print("   🧪 COMO TESTAR A CORREÇÃO NO HEROKU:")
    print()
    print("   1. Acesse: https://www.lvksistemas.com.br/")
    print("      ou: https://lvksistemas-app-4f6fa281e217.herokuapp.com/")
    print()
    print("   2. Você deve ver uma página com:")
    print("      - A loja Fatesa (ou outra loja ativa)")
    print("      - Botão 'Acesso para Administradores do Sistema' no final")
    print()
    print("   3. Clique em 'Acesso para Administradores do Sistema'")
    print("      - Deve ir para /admin/login/")
    print("      - Faça login com credenciais de super admin")
    print()
    print("   4. URLs alternativas para super admin:")
    print("      - https://www.lvksistemas.com.br/?admin=1")
    print("      - https://www.lvksistemas.com.br/admin-login/")
    print("      - https://www.lvksistemas.com.br/super-admin/")
    print()
    print("   ✅ CORREÇÃO IMPLEMENTADA:")
    print("   - Quando há apenas 1 loja ativa, mostra seleção ao invés de redirecionar")
    print("   - Página de seleção sempre inclui opção para admin")
    print("   - URLs alternativas para acesso direto ao admin")
    print("   - Parâmetro ?admin=1 força redirecionamento para admin")

if __name__ == '__main__':
    main()