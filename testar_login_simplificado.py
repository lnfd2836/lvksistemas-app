#!/usr/bin/env python3
"""
Script para testar o sistema de login simplificado
"""

import os
import sys

# Configurar Django antes de importar qualquer coisa
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def testar_redirecionamento_inteligente():
    """Testa o redirecionamento inteligente da página inicial"""
    
    print("\n" + "="*60)
    print("TESTANDO REDIRECIONAMENTO INTELIGENTE")
    print("="*60)
    
    client = Client()
    
    try:
        # Teste 1: Acesso à página inicial sem autenticação
        print("\n1. Testando acesso à página inicial (/)...")
        response = client.get('/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   Redirecionado para: {response.url}")
        elif response.status_code == 200:
            print("   Página de seleção de loja exibida")
        
        # Teste 2: Verificar URLs antigas
        print("\n2. Testando URLs antigas...")
        
        old_urls = ['/login/', '/loja/login/']
        for url in old_urls:
            response = client.get(url)
            print(f"   {url} -> Status: {response.status_code}")
            if response.status_code == 302:
                print(f"   Redirecionado para: {response.url}")
        
        return True
        
    except Exception as e:
        print(f"   ERRO: {str(e)}")
        return False


def testar_selecao_loja():
    """Testa a página de seleção de loja"""
    
    print("\n" + "="*60)
    print("TESTANDO SELEÇÃO DE LOJA")
    print("="*60)
    
    try:
        # Verificar lojas ativas
        lojas_ativas = Loja.objects.filter(status='ativa')
        print(f"\nLojas ativas encontradas: {lojas_ativas.count()}")
        
        for loja in lojas_ativas:
            print(f"   - {loja.nome} (ID: {loja.id})")
            
            # Verificar se tem login personalizado
            try:
                login_config = loja.login_personalizado
                print(f"     Login personalizado: {'Ativo' if login_config.ativo else 'Inativo'}")
                print(f"     URL: {login_config.get_login_url()}")
            except LoginPersonalizado.DoesNotExist:
                print("     Login personalizado: Não configurado")
        
        return True
        
    except Exception as e:
        print(f"   ERRO: {str(e)}")
        return False


def testar_login_personalizado():
    """Testa o login personalizado das lojas"""
    
    print("\n" + "="*60)
    print("TESTANDO LOGIN PERSONALIZADO")
    print("="*60)
    
    client = Client()
    
    try:
        # Buscar lojas com login personalizado
        lojas_com_login = LoginPersonalizado.objects.filter(ativo=True)
        
        print(f"\nLojas com login personalizado: {lojas_com_login.count()}")
        
        for login_config in lojas_com_login:
            loja = login_config.loja
            print(f"\n   Testando loja: {loja.nome}")
            
            # Testar acesso à página de login
            login_url = login_config.get_login_url()
            print(f"   URL de login: {login_url}")
            
            response = client.get(login_url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✓ Página de login carregada com sucesso")
            else:
                print(f"   ✗ Erro ao carregar página de login")
        
        return True
        
    except Exception as e:
        print(f"   ERRO: {str(e)}")
        return False


def testar_acesso_admin():
    """Testa o acesso de administradores"""
    
    print("\n" + "="*60)
    print("TESTANDO ACESSO DE ADMINISTRADORES")
    print("="*60)
    
    client = Client()
    
    try:
        # Teste 1: Acesso ao admin sem autenticação
        print("\n1. Testando acesso ao admin sem autenticação...")
        response = client.get('/admin-login/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   Redirecionado para: {response.url}")
        
        # Teste 2: Verificar se super usuários existem
        print("\n2. Verificando super usuários...")
        super_users = User.objects.filter(is_superuser=True, is_active=True)
        print(f"   Super usuários ativos: {super_users.count()}")
        
        for user in super_users:
            print(f"   - {user.username} ({user.email})")
        
        return True
        
    except Exception as e:
        print(f"   ERRO: {str(e)}")
        return False


def criar_configuracoes_padrao():
    """Cria configurações padrão para lojas sem login personalizado"""
    
    print("\n" + "="*60)
    print("CRIANDO CONFIGURAÇÕES PADRÃO")
    print("="*60)
    
    try:
        lojas_sem_login = Loja.objects.filter(
            status='ativa'
        ).exclude(
            id__in=LoginPersonalizado.objects.values_list('loja_id', flat=True)
        )
        
        print(f"\nLojas sem login personalizado: {lojas_sem_login.count()}")
        
        for loja in lojas_sem_login:
            print(f"\n   Criando configuração para: {loja.nome}")
            
            try:
                login_config = LoginPersonalizado.objects.create(
                    loja=loja,
                    titulo=f"Login - {loja.nome}",
                    subtitulo=f"Acesse sua conta na {loja.nome}",
                    mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                    tema='padrao',
                    ativo=True
                )
                
                print(f"   ✓ Configuração criada com sucesso")
                print(f"   URL: {login_config.get_login_url()}")
                
            except Exception as e:
                print(f"   ✗ Erro ao criar configuração: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"   ERRO: {str(e)}")
        return False


def gerar_relatorio_sistema():
    """Gera um relatório completo do sistema"""
    
    print("\n" + "="*60)
    print("RELATÓRIO DO SISTEMA DE LOGIN")
    print("="*60)
    
    try:
        # Estatísticas gerais
        total_lojas = Loja.objects.count()
        lojas_ativas = Loja.objects.filter(status='ativa').count()
        lojas_com_login = LoginPersonalizado.objects.filter(ativo=True).count()
        total_usuarios = User.objects.filter(is_active=True).count()
        super_usuarios = User.objects.filter(is_superuser=True, is_active=True).count()
        
        print(f"\nEstatísticas Gerais:")
        print(f"   Total de lojas: {total_lojas}")
        print(f"   Lojas ativas: {lojas_ativas}")
        print(f"   Lojas com login personalizado: {lojas_com_login}")
        print(f"   Total de usuários ativos: {total_usuarios}")
        print(f"   Super usuários: {super_usuarios}")
        
        # URLs disponíveis
        print(f"\nURLs do Sistema:")
        print(f"   Página inicial: /")
        print(f"   Admin do sistema: /admin-login/")
        print(f"   Login Django Admin: /admin/login/")
        
        # Lojas e seus logins
        print(f"\nLojas e URLs de Login:")
        for loja in Loja.objects.filter(status='ativa'):
            try:
                login_config = loja.login_personalizado
                if login_config.ativo:
                    print(f"   {loja.nome}: {login_config.get_login_url()}")
                else:
                    print(f"   {loja.nome}: Login desativado")
            except LoginPersonalizado.DoesNotExist:
                print(f"   {loja.nome}: Sem configuração de login")
        
        return True
        
    except Exception as e:
        print(f"   ERRO: {str(e)}")
        return False


def main():
    """Função principal"""
    
    print("TESTE DO SISTEMA DE LOGIN SIMPLIFICADO")
    print("=" * 80)
    
    testes = [
        ("Redirecionamento Inteligente", testar_redirecionamento_inteligente),
        ("Seleção de Loja", testar_selecao_loja),
        ("Login Personalizado", testar_login_personalizado),
        ("Acesso de Administradores", testar_acesso_admin),
        ("Configurações Padrão", criar_configuracoes_padrao),
        ("Relatório do Sistema", gerar_relatorio_sistema),
    ]
    
    resultados = []
    
    for nome, funcao in testes:
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"\nERRO no teste '{nome}': {str(e)}")
            resultados.append((nome, False))
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✓ PASSOU" if resultado else "✗ FALHOU"
        print(f"   {nome}: {status}")
        if resultado:
            sucessos += 1
    
    print(f"\nResultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("\n🎉 Todos os testes passaram! Sistema pronto para uso.")
    else:
        print(f"\n⚠️  {len(resultados) - sucessos} teste(s) falharam. Verifique os erros acima.")
    
    return sucessos == len(resultados)


if __name__ == '__main__':
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO FATAL: {str(e)}")
        sys.exit(1)