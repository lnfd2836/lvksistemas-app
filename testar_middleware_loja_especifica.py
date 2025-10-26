#!/usr/bin/env python
"""
Script para testar o middleware exclusivo de lojas específicas
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from lojas.middleware_loja_especifica import criar_middleware_para_loja
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Testa o middleware exclusivo de lojas específicas"""
    
    print("🔧 TESTE MIDDLEWARE EXCLUSIVO DE LOJAS")
    print("=" * 50)
    
    # 1. Verificar configuração do middleware
    print("\n1️⃣ VERIFICANDO CONFIGURAÇÃO DO MIDDLEWARE")
    verificar_configuracao_middleware()
    
    # 2. Testar criação automática de configuração
    print("\n2️⃣ TESTANDO CRIAÇÃO AUTOMÁTICA DE CONFIGURAÇÃO")
    testar_criacao_automatica()
    
    # 3. Testar login de lojas específicas
    print("\n3️⃣ TESTANDO LOGIN DE LOJAS ESPECÍFICAS")
    testar_login_lojas()
    
    # 4. Testar proteção contra super admin
    print("\n4️⃣ TESTANDO PROTEÇÃO CONTRA SUPER ADMIN")
    testar_protecao_super_admin()
    
    # 5. Testar isolamento entre lojas
    print("\n5️⃣ TESTANDO ISOLAMENTO ENTRE LOJAS")
    testar_isolamento_lojas()
    
    print("\n✅ TESTES CONCLUÍDOS")

def verificar_configuracao_middleware():
    """Verifica se o middleware está configurado corretamente"""
    
    try:
        middlewares = settings.MIDDLEWARE
        middleware_loja = 'lojas.middleware_loja_especifica.LojaEspecificaMiddleware'
        
        if middleware_loja in middlewares:
            posicao = middlewares.index(middleware_loja)
            print(f"   ✅ Middleware encontrado na posição {posicao}")
            
            # Verificar se está na posição correta (após super admin middleware)
            super_admin_middleware = 'dashboard.middleware.super_admin_middleware.SuperAdminMiddleware'
            if super_admin_middleware in middlewares:
                pos_super_admin = middlewares.index(super_admin_middleware)
                if posicao > pos_super_admin:
                    print("   ✅ Posição correta: após SuperAdminMiddleware")
                else:
                    print("   ⚠️  Posição pode estar incorreta")
        else:
            print("   ❌ Middleware não encontrado na configuração")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na verificação: {str(e)}")
        return False

def testar_criacao_automatica():
    """Testa a criação automática de configuração para lojas"""
    
    try:
        lojas = Loja.objects.filter(status='ativa')
        print(f"   📊 Testando {lojas.count()} lojas ativas")
        
        for loja in lojas:
            print(f"\n   🏪 {loja.nome}")
            
            # Verificar se tem configuração
            try:
                login_config = loja.login_personalizado
                print(f"      ✅ Configuração existente: {login_config.get_login_url()}")
                
                # Verificar se está ativa
                if login_config.ativo:
                    print("      ✅ Configuração ativa")
                else:
                    print("      ⚠️  Configuração inativa")
                    
            except LoginPersonalizado.DoesNotExist:
                print("      ❌ Sem configuração - criando automaticamente...")
                
                # Testar criação automática
                sucesso = criar_middleware_para_loja(loja)
                if sucesso:
                    login_config = loja.login_personalizado
                    print(f"      ✅ Configuração criada: {login_config.get_login_url()}")
                else:
                    print("      ❌ Falha na criação automática")
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {str(e)}")

def testar_login_lojas():
    """Testa o login específico de cada loja"""
    
    try:
        client = Client()
        lojas = Loja.objects.filter(status='ativa')
        
        for loja in lojas:
            print(f"\n   🧪 Testando {loja.nome}")
            
            try:
                login_config = loja.login_personalizado
                url_login = login_config.get_login_url()
                
                print(f"      URL: {url_login}")
                
                # Teste GET - deve mostrar página de login
                response = client.get(url_login)
                print(f"      GET Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    
                    # Verificar elementos essenciais
                    checks = [
                        ('Formulário', 'form' in content),
                        ('Campo username', 'name="username"' in content),
                        ('Campo password', 'name="password"' in content),
                        ('CSRF token', 'csrf' in content),
                        ('Título da loja', login_config.titulo in content if login_config.titulo else True)
                    ]
                    
                    for check_name, check_result in checks:
                        status = "✅" if check_result else "❌"
                        print(f"      {status} {check_name}")
                        
                else:
                    print(f"      ❌ Status inesperado: {response.status_code}")
                    if response.status_code == 302:
                        print(f"      Redirecionamento para: {response.url}")
                
            except LoginPersonalizado.DoesNotExist:
                print("      ❌ Sem configuração de login")
            except Exception as e:
                print(f"      ❌ Erro: {str(e)}")
        
    except Exception as e:
        print(f"   ❌ Erro geral: {str(e)}")

def testar_protecao_super_admin():
    """Testa se super admins são protegidos adequadamente"""
    
    try:
        # Buscar super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if not super_admin:
            print("   ⚠️  Nenhum super admin encontrado para teste")
            return
        
        client = Client()
        client.force_login(super_admin)
        
        print(f"   👤 Testando com super admin: {super_admin.username}")
        
        # Buscar uma loja para testar
        loja = Loja.objects.filter(status='ativa').first()
        if not loja:
            print("   ⚠️  Nenhuma loja ativa encontrada")
            return
        
        try:
            login_config = loja.login_personalizado
            url_login = login_config.get_login_url()
            
            print(f"   🧪 Testando acesso a: {url_login}")
            
            # Teste GET - super admin deve poder visualizar (para administração)
            response = client.get(url_login)
            print(f"      GET Status: {response.status_code}")
            
            if response.status_code == 200:
                print("      ✅ Super admin pode visualizar página de login da loja")
            elif response.status_code == 302:
                print(f"      🔄 Redirecionado para: {response.url}")
                if '/admin/' in response.url:
                    print("      ✅ Redirecionamento correto para admin")
                else:
                    print("      ❌ Redirecionamento incorreto")
            
            # Teste POST - super admin NÃO deve conseguir fazer login
            print("   🧪 Testando tentativa de login via POST...")
            response = client.post(url_login, {
                'username': 'test',
                'password': 'test'
            })
            
            print(f"      POST Status: {response.status_code}")
            
            if response.status_code == 302 and '/admin/' in response.url:
                print("      ✅ Super admin bloqueado corretamente no POST")
            elif response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'Super administradores devem usar' in content:
                    print("      ✅ Mensagem de bloqueio exibida")
                else:
                    print("      ❌ Super admin não foi bloqueado adequadamente")
            
        except LoginPersonalizado.DoesNotExist:
            print("   ⚠️  Loja sem configuração de login")
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {str(e)}")

def testar_isolamento_lojas():
    """Testa se o isolamento entre lojas está funcionando"""
    
    try:
        lojas = list(Loja.objects.filter(status='ativa')[:2])  # Pegar 2 lojas
        
        if len(lojas) < 2:
            print("   ⚠️  Menos de 2 lojas ativas - teste de isolamento limitado")
            return
        
        print(f"   🧪 Testando isolamento entre {lojas[0].nome} e {lojas[1].nome}")
        
        # Buscar usuário comum (não super admin)
        usuario_comum = User.objects.filter(is_superuser=False).first()
        if not usuario_comum:
            print("   ⚠️  Nenhum usuário comum encontrado")
            return
        
        client = Client()
        
        # Testar acesso às duas lojas
        for i, loja in enumerate(lojas):
            try:
                login_config = loja.login_personalizado
                url_login = login_config.get_login_url()
                
                print(f"\n   🏪 Loja {i+1}: {loja.nome}")
                print(f"      URL: {url_login}")
                
                # Teste sem autenticação
                response = client.get(url_login)
                print(f"      Status sem auth: {response.status_code}")
                
                if response.status_code == 200:
                    print("      ✅ Página acessível sem autenticação")
                else:
                    print(f"      ❌ Problema no acesso: {response.status_code}")
                
            except LoginPersonalizado.DoesNotExist:
                print(f"      ❌ Loja {loja.nome} sem configuração")
        
    except Exception as e:
        print(f"   ❌ Erro no teste de isolamento: {str(e)}")

if __name__ == '__main__':
    main()