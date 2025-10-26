#!/usr/bin/env python
"""
Script para debugar problemas específicos do Heroku
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
from dashboard.services.authentication import AuthenticationService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Debug específico para problemas do Heroku"""
    
    print("🔍 DEBUG ESPECÍFICO HEROKU")
    print("=" * 50)
    
    # 1. Verificar dados no banco
    print("\n1️⃣ VERIFICANDO DADOS NO BANCO")
    verificar_dados_banco()
    
    # 2. Verificar configurações
    print("\n2️⃣ VERIFICANDO CONFIGURAÇÕES")
    verificar_configuracoes()
    
    # 3. Verificar middlewares
    print("\n3️⃣ VERIFICANDO MIDDLEWARES")
    verificar_middlewares()
    
    # 4. Gerar script de correção para Heroku
    print("\n4️⃣ GERANDO SCRIPT DE CORREÇÃO")
    gerar_script_correcao()
    
    print("\n✅ DEBUG CONCLUÍDO")

def verificar_dados_banco():
    """Verifica os dados no banco que podem estar causando o problema"""
    
    try:
        # Verificar usuários
        total_users = User.objects.count()
        super_users = User.objects.filter(is_superuser=True)
        print(f"   👥 Total de usuários: {total_users}")
        print(f"   👑 Super usuários: {super_users.count()}")
        
        for user in super_users:
            print(f"      - {user.username} (ativo: {user.is_active})")
        
        # Verificar lojas
        total_lojas = Loja.objects.count()
        lojas_ativas = Loja.objects.filter(status='ativa')
        print(f"   🏪 Total de lojas: {total_lojas}")
        print(f"   🏪 Lojas ativas: {lojas_ativas.count()}")
        
        for loja in lojas_ativas:
            print(f"      - {loja.nome} (status: {loja.status})")
            try:
                login_config = loja.login_personalizado
                print(f"        Login: {login_config.ativo} - {login_config.get_login_url()}")
            except LoginPersonalizado.DoesNotExist:
                print(f"        Login: Não configurado")
        
        # Verificar se há apenas uma loja ativa (cenário Heroku)
        if lojas_ativas.count() == 1:
            print("   ⚠️  CENÁRIO HEROKU DETECTADO: Apenas uma loja ativa!")
            loja_unica = lojas_ativas.first()
            print(f"      Loja única: {loja_unica.nome}")
            
            # Verificar se essa loja tem URL personalizada que pode estar causando confusão
            try:
                login_config = loja_unica.login_personalizado
                url = login_config.get_login_url()
                print(f"      URL de login: {url}")
                
                # Verificar se a URL contém "fatesa" (mencionado no problema)
                if 'fatesa' in url.lower():
                    print("   🎯 POSSÍVEL CAUSA: URL da Fatesa detectada!")
                    
            except LoginPersonalizado.DoesNotExist:
                print("      Sem configuração de login")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar dados: {str(e)}")

def verificar_configuracoes():
    """Verifica configurações que podem estar diferentes no Heroku"""
    
    try:
        print(f"   🔧 DEBUG: {settings.DEBUG}")
        print(f"   🌐 ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   🔑 LOGIN_URL: {getattr(settings, 'LOGIN_URL', 'Não definido')}")
        print(f"   🔑 LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Não definido')}")
        print(f"   🔑 LOGOUT_REDIRECT_URL: {getattr(settings, 'LOGOUT_REDIRECT_URL', 'Não definido')}")
        
        # Verificar se há variáveis de ambiente específicas do Heroku
        heroku_vars = [
            'DATABASE_URL',
            'HEROKU_APP_NAME',
            'DYNO',
            'PORT'
        ]
        
        print("   🌍 Variáveis de ambiente Heroku:")
        for var in heroku_vars:
            value = os.environ.get(var, 'Não definido')
            if value != 'Não definido':
                print(f"      {var}: {value[:50]}...")
            else:
                print(f"      {var}: {value}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar configurações: {str(e)}")

def verificar_middlewares():
    """Verifica middlewares que podem estar causando problemas"""
    
    try:
        middlewares = settings.MIDDLEWARE
        print(f"   📋 Total de middlewares: {len(middlewares)}")
        
        # Middlewares que podem causar problemas de redirecionamento
        problematicos = [
            'lojas.middleware.LojaMiddleware',
            'usuarios.improved_middleware.ImprovedAuthenticationMiddleware',
            'lojas.middleware_login_isolado.LoginIsoladoMiddleware',
        ]
        
        for middleware in middlewares:
            status = "⚠️ " if middleware in problematicos else "✅"
            print(f"      {status} {middleware}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar middlewares: {str(e)}")

def gerar_script_correcao():
    """Gera um script específico para corrigir o problema no Heroku"""
    
    script_content = '''#!/usr/bin/env python
"""
Script de correção específica para o problema do super admin no Heroku
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado

def main():
    print("🔧 CORREÇÃO ESPECÍFICA HEROKU - SUPER ADMIN")
    print("=" * 50)
    
    # 1. Verificar se há apenas uma loja ativa
    lojas_ativas = Loja.objects.filter(status='ativa')
    print(f"Lojas ativas: {lojas_ativas.count()}")
    
    if lojas_ativas.count() == 1:
        loja = lojas_ativas.first()
        print(f"Loja única: {loja.nome}")
        
        # Verificar se é a Fatesa
        if 'fatesa' in loja.nome.lower():
            print("✅ Loja Fatesa detectada - isso explica o redirecionamento")
            
            # Verificar configuração de login
            try:
                login_config = loja.login_personalizado
                print(f"URL de login: {login_config.get_login_url()}")
                
                # A correção pode ser criar mais lojas ou ajustar a lógica
                print("💡 SOLUÇÕES POSSÍVEIS:")
                print("1. Criar mais lojas ativas para forçar seleção")
                print("2. Ajustar lógica do smart_redirect")
                print("3. Verificar se super admin está sendo detectado corretamente")
                
            except LoginPersonalizado.DoesNotExist:
                print("❌ Loja sem configuração de login")
    
    # 2. Verificar super admins
    super_admins = User.objects.filter(is_superuser=True, is_active=True)
    print(f"\\nSuper admins ativos: {super_admins.count()}")
    
    for admin in super_admins:
        print(f"- {admin.username}")
        
        # Testar AuthenticationService
        from dashboard.services.authentication import AuthenticationService
        try:
            dashboard_url = AuthenticationService.determine_user_dashboard(admin)
            print(f"  Dashboard URL: {dashboard_url}")
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")

if __name__ == '__main__':
    main()
'''
    
    try:
        with open('correcao_heroku_super_admin.py', 'w') as f:
            f.write(script_content)
        print("   ✅ Script de correção gerado: correcao_heroku_super_admin.py")
        print("   📝 Execute este script no Heroku para diagnosticar o problema específico")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar script: {str(e)}")

if __name__ == '__main__':
    main()