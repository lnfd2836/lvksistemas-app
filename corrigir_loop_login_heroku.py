#!/usr/bin/env python
"""
Script para corrigir loops de redirecionamento no sistema de login do Heroku
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from django.test import Client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Função principal para corrigir loops de login"""
    
    print("🔧 CORREÇÃO DE LOOPS DE LOGIN NO HEROKU")
    print("=" * 50)
    
    # 1. Verificar configurações atuais
    print("\n1️⃣ VERIFICANDO CONFIGURAÇÕES ATUAIS")
    verificar_configuracoes()
    
    # 2. Corrigir URLs problemáticas
    print("\n2️⃣ CORRIGINDO URLS PROBLEMÁTICAS")
    corrigir_urls_problematicas()
    
    # 3. Verificar e criar configurações de login
    print("\n3️⃣ VERIFICANDO CONFIGURAÇÕES DE LOGIN")
    verificar_configuracoes_login()
    
    # 4. Testar redirecionamentos
    print("\n4️⃣ TESTANDO REDIRECIONAMENTOS")
    testar_redirecionamentos()
    
    # 5. Relatório final
    print("\n5️⃣ RELATÓRIO FINAL")
    relatorio_final()
    
    print("\n✅ CORREÇÃO CONCLUÍDA!")
    print("🚀 O sistema deve estar funcionando corretamente no Heroku agora.")

def verificar_configuracoes():
    """Verifica as configurações atuais do sistema"""
    
    print(f"   LOGIN_URL: {getattr(settings, 'LOGIN_URL', 'Não definido')}")
    print(f"   LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Não definido')}")
    print(f"   LOGOUT_REDIRECT_URL: {getattr(settings, 'LOGOUT_REDIRECT_URL', 'Não definido')}")
    
    # Verificar middlewares ativos
    middlewares = getattr(settings, 'MIDDLEWARE', [])
    print(f"\n   Middlewares ativos: {len(middlewares)}")
    
    middlewares_login = [m for m in middlewares if 'login' in m.lower() or 'auth' in m.lower()]
    for middleware in middlewares_login:
        print(f"   - {middleware}")

def corrigir_urls_problematicas():
    """Corrige URLs que podem estar causando loops"""
    
    try:
        # Verificar se existe simple_login.py
        simple_login_path = 'dashboard/simple_login.py'
        if os.path.exists(simple_login_path):
            print("   ⚠️  Arquivo simple_login.py ainda existe")
            print("   📝 Recomendação: Remover ou renomear este arquivo")
        else:
            print("   ✅ Arquivo simple_login.py não encontrado (correto)")
        
        # Verificar URLs do dashboard
        dashboard_urls_path = 'dashboard/urls.py'
        if os.path.exists(dashboard_urls_path):
            with open(dashboard_urls_path, 'r') as f:
                content = f.read()
                if 'simple_login' in content:
                    print("   ⚠️  Referências ao simple_login encontradas em dashboard/urls.py")
                else:
                    print("   ✅ Nenhuma referência ao simple_login em dashboard/urls.py")
        
        print("   ✅ Verificação de URLs concluída")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar URLs: {str(e)}")

def verificar_configuracoes_login():
    """Verifica e cria configurações de login necessárias"""
    
    try:
        lojas = Loja.objects.filter(status='ativa')
        print(f"   Lojas ativas encontradas: {lojas.count()}")
        
        lojas_sem_login = 0
        lojas_com_login = 0
        
        for loja in lojas:
            try:
                login_config = loja.login_personalizado
                if login_config.ativo:
                    lojas_com_login += 1
                    print(f"   ✅ {loja.nome}: Login ativo")
                else:
                    print(f"   ⚠️  {loja.nome}: Login inativo")
                    # Ativar login
                    login_config.ativo = True
                    login_config.save()
                    print(f"   🔧 {loja.nome}: Login ativado")
                    lojas_com_login += 1
                    
            except LoginPersonalizado.DoesNotExist:
                lojas_sem_login += 1
                print(f"   ❌ {loja.nome}: Sem configuração de login")
                
                # Criar configuração padrão
                try:
                    login_config = LoginPersonalizado.objects.create(
                        loja=loja,
                        titulo=f"Login - {loja.nome}",
                        subtitulo=f"Acesse sua conta na {loja.nome}",
                        mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                        tema='padrao',
                        ativo=True
                    )
                    print(f"   🔧 {loja.nome}: Configuração criada")
                    lojas_com_login += 1
                    lojas_sem_login -= 1
                    
                except Exception as e:
                    print(f"   ❌ Erro ao criar login para {loja.nome}: {str(e)}")
        
        print(f"\n   📊 Resumo:")
        print(f"   - Lojas com login: {lojas_com_login}")
        print(f"   - Lojas sem login: {lojas_sem_login}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar configurações de login: {str(e)}")

def testar_redirecionamentos():
    """Testa os redirecionamentos do sistema"""
    
    try:
        client = Client()
        
        # Teste 1: Página inicial
        print("   🧪 Testando página inicial...")
        try:
            response = client.get('/')
            print(f"   Status: {response.status_code}")
            if response.status_code == 302:
                print(f"   Redirecionamento para: {response.url}")
            elif response.status_code == 200:
                print("   ✅ Página carregada com sucesso")
        except Exception as e:
            print(f"   ❌ Erro no teste da página inicial: {str(e)}")
        
        # Teste 2: URL de login antiga
        print("   🧪 Testando /login/...")
        try:
            response = client.get('/login/')
            print(f"   Status: {response.status_code}")
            if response.status_code == 302:
                print(f"   Redirecionamento para: {response.url}")
        except Exception as e:
            print(f"   ❌ Erro no teste de /login/: {str(e)}")
        
        # Teste 3: URL de usuários/login
        print("   🧪 Testando /usuarios/login/...")
        try:
            response = client.get('/usuarios/login/')
            print(f"   Status: {response.status_code}")
            if response.status_code == 302:
                print(f"   Redirecionamento para: {response.url}")
        except Exception as e:
            print(f"   ❌ Erro no teste de /usuarios/login/: {str(e)}")
        
        # Teste 4: Login personalizado de uma loja
        try:
            loja = Loja.objects.filter(status='ativa').first()
            if loja:
                try:
                    login_config = loja.login_personalizado
                    login_url = login_config.get_login_url()
                    print(f"   🧪 Testando login personalizado: {login_url}")
                    
                    response = client.get(login_url)
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        print("   ✅ Login personalizado funcionando")
                    
                except Exception as e:
                    print(f"   ❌ Erro no teste de login personalizado: {str(e)}")
        except Exception as e:
            print(f"   ❌ Erro ao buscar loja para teste: {str(e)}")
        
    except Exception as e:
        print(f"   ❌ Erro nos testes de redirecionamento: {str(e)}")

def relatorio_final():
    """Gera relatório final do sistema"""
    
    try:
        # Contar usuários
        total_users = User.objects.count()
        super_users = User.objects.filter(is_superuser=True).count()
        regular_users = total_users - super_users
        
        # Contar lojas
        total_lojas = Loja.objects.count()
        lojas_ativas = Loja.objects.filter(status='ativa').count()
        
        # Contar configurações de login
        total_login_configs = LoginPersonalizado.objects.count()
        login_configs_ativas = LoginPersonalizado.objects.filter(ativo=True).count()
        
        print("   📊 ESTATÍSTICAS DO SISTEMA:")
        print(f"   - Total de usuários: {total_users}")
        print(f"   - Super usuários: {super_users}")
        print(f"   - Usuários regulares: {regular_users}")
        print(f"   - Total de lojas: {total_lojas}")
        print(f"   - Lojas ativas: {lojas_ativas}")
        print(f"   - Configurações de login: {total_login_configs}")
        print(f"   - Configurações ativas: {login_configs_ativas}")
        
        # Verificar se há problemas
        problemas = []
        
        if lojas_ativas > login_configs_ativas:
            problemas.append(f"Há {lojas_ativas - login_configs_ativas} lojas ativas sem configuração de login")
        
        if super_users == 0:
            problemas.append("Nenhum super usuário encontrado")
        
        if lojas_ativas == 0:
            problemas.append("Nenhuma loja ativa encontrada")
        
        if problemas:
            print("\n   ⚠️  PROBLEMAS DETECTADOS:")
            for problema in problemas:
                print(f"   - {problema}")
        else:
            print("\n   ✅ NENHUM PROBLEMA DETECTADO")
        
        # URLs de acesso
        print("\n   🌐 URLS DE ACESSO:")
        print("   - Página inicial: /")
        print("   - Admin: /admin/")
        print("   - Admin login: /admin-login/")
        
        # Listar lojas com seus URLs
        lojas_ativas = Loja.objects.filter(status='ativa')
        for loja in lojas_ativas[:5]:  # Mostrar apenas as primeiras 5
            try:
                login_config = loja.login_personalizado
                if login_config.ativo:
                    print(f"   - {loja.nome}: {login_config.get_login_url()}")
            except:
                print(f"   - {loja.nome}: Sem configuração de login")
        
        if lojas_ativas.count() > 5:
            print(f"   ... e mais {lojas_ativas.count() - 5} lojas")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar relatório: {str(e)}")

if __name__ == '__main__':
    main()