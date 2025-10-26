#!/usr/bin/env python
"""
Script para fazer deploy final do middleware exclusivo de lojas
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
    """Deploy final do middleware exclusivo de lojas"""
    
    print("🚀 DEPLOY FINAL - MIDDLEWARE EXCLUSIVO DE LOJAS")
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
    
    print("\n✅ DEPLOY FINAL CONCLUÍDO COM SUCESSO!")
    return True

def verificar_implementacao():
    """Verifica se a implementação está funcionando"""
    
    try:
        # Verificar middleware na configuração
        middlewares = settings.MIDDLEWARE
        middleware_loja = 'lojas.middleware_loja_especifica.LojaEspecificaMiddleware'
        
        if middleware_loja not in middlewares:
            print("   ❌ Middleware não encontrado na configuração")
            return False
        
        print("   ✅ Middleware configurado")
        
        # Verificar se todas as lojas têm configuração
        lojas_ativas = Loja.objects.filter(status='ativa')
        lojas_sem_config = 0
        
        for loja in lojas_ativas:
            try:
                login_config = loja.login_personalizado
                if not login_config.ativo:
                    print(f"   ⚠️  {loja.nome}: Login inativo")
            except LoginPersonalizado.DoesNotExist:
                lojas_sem_config += 1
        
        if lojas_sem_config > 0:
            print(f"   ⚠️  {lojas_sem_config} lojas sem configuração de login")
        else:
            print("   ✅ Todas as lojas têm configuração de login")
        
        # Testar uma loja
        loja_teste = lojas_ativas.first()
        if loja_teste:
            try:
                login_config = loja_teste.login_personalizado
                client = Client()
                response = client.get(login_config.get_login_url())
                
                if response.status_code == 200:
                    print(f"   ✅ Teste de loja funcionando: {loja_teste.nome}")
                else:
                    print(f"   ❌ Problema no teste da loja: Status {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ❌ Erro no teste da loja: {str(e)}")
                return False
        
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
        
        commit_message = "Implementar middleware exclusivo para lojas - sistema completo de login isolado"
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
    """Mostra instruções finais para teste no Heroku"""
    
    print("   🎯 SISTEMA COMPLETO IMPLEMENTADO:")
    print("   ✅ Middleware exclusivo para super admins")
    print("   ✅ Middleware exclusivo para lojas específicas")
    print("   ✅ Signals automáticos para criação de lojas")
    print("   ✅ Sistema de login isolado por loja")
    print("   ✅ Proteção contra acesso cruzado")
    print()
    print("   🌐 ARQUITETURA FINAL:")
    print()
    print("   1️⃣ SUPER ADMIN:")
    print("      URL: https://www.lvksistemas.com.br/")
    print("      Função: Login direto de super admin")
    print("      Middleware: SuperAdminMiddleware (prioridade máxima)")
    print("      Após login: Dashboard para gerenciar lojas")
    print()
    print("   2️⃣ LOJAS ESPECÍFICAS:")
    print("      URLs: https://www.lvksistemas.com.br/login/{loja}/")
    print("      Função: Login personalizado exclusivo por loja")
    print("      Middleware: LojaEspecificaMiddleware")
    print("      Criação: Automática via signals quando loja é criada")
    print("      Após login: Dashboard específico da loja")
    print()
    print("   🧪 COMO TESTAR NO HEROKU:")
    print()
    print("   1. SUPER ADMIN:")
    print("      - Acesse: https://www.lvksistemas.com.br/")
    print("      - Deve mostrar formulário de login de super admin")
    print("      - Faça login com credenciais de super admin")
    print("      - Deve ir para /dashboard/ (área de gerenciamento)")
    print()
    print("   2. LOJA FATESA (CORRIGIDA):")
    print("      - Acesse: https://www.lvksistemas.com.br/login/fatesa-escola-de-ultrassonografia/")
    print("      - Deve mostrar página de login personalizada da Fatesa")
    print("      - Título: 'Login - Fatesa Escola de Ultrassonografia'")
    print("      - Tema corporativo (azul)")
    print()
    print("   3. OUTRAS LOJAS:")
    print("      - Felix: https://www.lvksistemas.com.br/login/felix-ribeirao-pretosp-clinica-de-estetica/")
    print("      - Loja Felix: https://www.lvksistemas.com.br/login/loja-felix/")
    print()
    print("   4. PROTEÇÃO SUPER ADMIN:")
    print("      - Super admin pode VISUALIZAR páginas de login das lojas")
    print("      - Super admin NÃO pode fazer login via páginas das lojas")
    print("      - Tentativas de login via loja são bloqueadas e redirecionadas para /admin/")
    print()
    print("   ✅ FUNCIONALIDADES IMPLEMENTADAS:")
    print("   - Sistema de login completamente isolado")
    print("   - Criação automática de configuração para novas lojas")
    print("   - Middleware exclusivo para cada tipo de usuário")
    print("   - Proteção contra acesso cruzado")
    print("   - URLs personalizadas por loja")
    print("   - Temas personalizáveis por loja")
    print("   - Logs detalhados de acesso")
    print("   - Sessões isoladas por contexto")
    print()
    print("   🎉 SISTEMA COMPLETO E FUNCIONAL!")
    print("   - Super Admin: Gerencia o sistema e cria lojas")
    print("   - Lojas: Cada uma com login exclusivo e isolado")
    print("   - Middleware: Garante isolamento e segurança")
    print("   - Automação: Configuração automática para novas lojas")

if __name__ == '__main__':
    main()