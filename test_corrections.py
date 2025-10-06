#!/usr/bin/env python
"""
Script para testar as correções aplicadas
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import SessaoAtiva
from django.test import Client
from django.urls import reverse

def test_session_management():
    """Testa o gerenciamento de sessões"""
    print("🔍 Testando gerenciamento de sessões...")
    
    try:
        # Verificar se existem usuários super admin
        super_users = User.objects.filter(is_superuser=True)
        print(f"✅ Super usuários encontrados: {super_users.count()}")
        
        # Verificar sessões ativas
        active_sessions = SessaoAtiva.objects.filter(ativa=True)
        print(f"✅ Sessões ativas: {active_sessions.count()}")
        
        # Testar URL de gerenciamento de sessões
        client = Client()
        if super_users.exists():
            user = super_users.first()
            client.force_login(user)
            
            response = client.get('/dashboard/admin/sessoes/')
            if response.status_code == 200:
                print("✅ Página de gerenciamento de sessões carregou com sucesso")
            else:
                print(f"❌ Erro ao carregar página de sessões: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de sessões: {str(e)}")
        return False

def test_login_urls():
    """Testa as URLs de login"""
    print("\n🔍 Testando URLs de login...")
    
    try:
        client = Client()
        
        # Testar URL principal de login
        response = client.get('/login/')
        if response.status_code == 200:
            print("✅ URL /login/ funcionando")
        else:
            print(f"❌ Erro na URL /login/: {response.status_code}")
        
        # Testar URL de loja login
        response = client.get('/loja/login/')
        if response.status_code == 200:
            print("✅ URL /loja/login/ funcionando")
        else:
            print(f"❌ Erro na URL /loja/login/: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de URLs: {str(e)}")
        return False

def test_allowed_hosts():
    """Verifica os domínios permitidos"""
    print("\n🔍 Verificando domínios permitidos...")
    
    allowed_hosts = settings.ALLOWED_HOSTS
    required_hosts = [
        'lvksistemas.com.br',
        'www.lvksistemas.com.br', 
        'crmvendas.net.br',
        'www.crmvendas.net.br'
    ]
    
    for host in required_hosts:
        if host in allowed_hosts:
            print(f"✅ Domínio {host} configurado")
        else:
            print(f"❌ Domínio {host} NÃO configurado")
    
    return True

def main():
    """Função principal"""
    print("🚀 Iniciando testes das correções aplicadas...\n")
    
    results = []
    results.append(test_session_management())
    results.append(test_login_urls())
    results.append(test_allowed_hosts())
    
    print(f"\n📊 Resultados dos testes:")
    print(f"✅ Sucessos: {sum(results)}")
    print(f"❌ Falhas: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 Todas as correções foram aplicadas com sucesso!")
    else:
        print("\n⚠️  Algumas correções precisam de atenção.")

if __name__ == '__main__':
    main()