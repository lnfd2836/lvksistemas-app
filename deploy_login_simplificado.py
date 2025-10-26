#!/usr/bin/env python3
"""
Script para fazer deploy do sistema de login simplificado no Heroku
"""

import os
import sys
import subprocess
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

import django
django.setup()

from django.contrib.auth.models import User
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def executar_comando(comando, descricao=""):
    """Executa um comando e retorna o resultado"""
    print(f"\n{'='*60}")
    print(f"EXECUTANDO: {descricao or comando}")
    print(f"{'='*60}")
    
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos
        )
        
        if resultado.stdout:
            print("STDOUT:")
            print(resultado.stdout)
        
        if resultado.stderr:
            print("STDERR:")
            print(resultado.stderr)
        
        if resultado.returncode == 0:
            print(f"✓ {descricao or comando} - SUCESSO")
            return True
        else:
            print(f"✗ {descricao or comando} - FALHOU (código: {resultado.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {descricao or comando} - TIMEOUT")
        return False
    except Exception as e:
        print(f"✗ {descricao or comando} - ERRO: {str(e)}")
        return False


def verificar_heroku_cli():
    """Verifica se o Heroku CLI está instalado"""
    print("\n" + "="*60)
    print("VERIFICANDO HEROKU CLI")
    print("="*60)
    
    try:
        resultado = subprocess.run(['heroku', '--version'], capture_output=True, text=True)
        if resultado.returncode == 0:
            print(f"✓ Heroku CLI instalado: {resultado.stdout.strip()}")
            return True
        else:
            print("✗ Heroku CLI não encontrado")
            return False
    except FileNotFoundError:
        print("✗ Heroku CLI não instalado")
        return False


def verificar_git_status():
    """Verifica o status do Git"""
    print("\n" + "="*60)
    print("VERIFICANDO STATUS DO GIT")
    print("="*60)
    
    # Verificar se há mudanças não commitadas
    resultado = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    
    if resultado.stdout.strip():
        print("Mudanças não commitadas encontradas:")
        print(resultado.stdout)
        
        resposta = input("\nDeseja fazer commit das mudanças? (s/n): ").lower()
        if resposta == 's':
            return fazer_commit_mudancas()
        else:
            print("Deploy cancelado - faça commit das mudanças primeiro")
            return False
    else:
        print("✓ Repositório Git limpo")
        return True


def fazer_commit_mudancas():
    """Faz commit das mudanças pendentes"""
    print("\nFazendo commit das mudanças...")
    
    comandos = [
        "git add .",
        "git commit -m 'Implementação do sistema de login simplificado'",
    ]
    
    for comando in comandos:
        if not executar_comando(comando):
            return False
    
    return True


def criar_configuracoes_login_heroku():
    """Cria configurações de login para todas as lojas no Heroku"""
    print("\n" + "="*60)
    print("CRIANDO CONFIGURAÇÕES DE LOGIN NO HEROKU")
    print("="*60)
    
    try:
        # Verificar lojas sem configuração de login
        lojas_sem_login = Loja.objects.filter(
            status='ativa'
        ).exclude(
            id__in=LoginPersonalizado.objects.values_list('loja_id', flat=True)
        )
        
        print(f"Lojas sem configuração de login: {lojas_sem_login.count()}")
        
        for loja in lojas_sem_login:
            print(f"\nCriando configuração para: {loja.nome}")
            
            try:
                login_config = LoginPersonalizado.objects.create(
                    loja=loja,
                    titulo=f"Login - {loja.nome}",
                    subtitulo=f"Acesse sua conta na {loja.nome}",
                    mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                    tema='padrao',
                    ativo=True
                )
                
                print(f"   ✓ Configuração criada: {login_config.get_login_url()}")
                
            except Exception as e:
                print(f"   ✗ Erro ao criar configuração: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao criar configurações: {str(e)}")
        return False


def testar_sistema_local():
    """Testa o sistema localmente antes do deploy"""
    print("\n" + "="*60)
    print("TESTANDO SISTEMA LOCALMENTE")
    print("="*60)
    
    return executar_comando(
        "python testar_login_simplificado.py",
        "Teste do sistema de login simplificado"
    )


def fazer_deploy_heroku():
    """Faz o deploy para o Heroku"""
    print("\n" + "="*60)
    print("FAZENDO DEPLOY PARA O HEROKU")
    print("="*60)
    
    comandos = [
        ("git push heroku main", "Push para Heroku"),
        ("heroku run python manage.py migrate", "Executar migrações"),
        ("heroku run python manage.py collectstatic --noinput", "Coletar arquivos estáticos"),
    ]
    
    for comando, descricao in comandos:
        if not executar_comando(comando, descricao):
            return False
    
    return True


def testar_heroku_pos_deploy():
    """Testa o sistema no Heroku após o deploy"""
    print("\n" + "="*60)
    print("TESTANDO SISTEMA NO HEROKU")
    print("="*60)
    
    # Obter URL do app
    resultado = subprocess.run(['heroku', 'info', '--json'], capture_output=True, text=True)
    
    if resultado.returncode == 0:
        import json
        info = json.loads(resultado.stdout)
        app_url = info.get('web_url', 'https://seu-app.herokuapp.com/')
        
        print(f"URL do app: {app_url}")
        
        # Testar endpoints principais
        import requests
        
        endpoints = [
            ('/', 'Página inicial'),
            ('/admin/login/', 'Login do admin'),
        ]
        
        for endpoint, descricao in endpoints:
            try:
                url = app_url.rstrip('/') + endpoint
                response = requests.get(url, timeout=30)
                
                if response.status_code in [200, 302]:
                    print(f"✓ {descricao} ({endpoint}): Status {response.status_code}")
                else:
                    print(f"✗ {descricao} ({endpoint}): Status {response.status_code}")
                    
            except Exception as e:
                print(f"✗ {descricao} ({endpoint}): Erro - {str(e)}")
        
        return True
    else:
        print("✗ Não foi possível obter informações do app")
        return False


def gerar_relatorio_final():
    """Gera relatório final do deploy"""
    print("\n" + "="*80)
    print("RELATÓRIO FINAL DO DEPLOY")
    print("="*80)
    
    try:
        # Estatísticas
        total_lojas = Loja.objects.count()
        lojas_ativas = Loja.objects.filter(status='ativa').count()
        lojas_com_login = LoginPersonalizado.objects.filter(ativo=True).count()
        
        print(f"\nEstatísticas:")
        print(f"   Total de lojas: {total_lojas}")
        print(f"   Lojas ativas: {lojas_ativas}")
        print(f"   Lojas com login personalizado: {lojas_com_login}")
        
        # URLs das lojas
        print(f"\nURLs de Login das Lojas:")
        for loja in Loja.objects.filter(status='ativa'):
            try:
                login_config = loja.login_personalizado
                if login_config.ativo:
                    print(f"   {loja.nome}: {login_config.get_login_url()}")
            except LoginPersonalizado.DoesNotExist:
                print(f"   {loja.nome}: Sem configuração de login")
        
        # Instruções para usuários
        print(f"\nInstruções para Usuários:")
        print(f"   1. Acesse a página inicial do sistema")
        print(f"   2. Selecione sua loja na lista")
        print(f"   3. Faça login com suas credenciais")
        print(f"   4. Super administradores: use /admin/login/")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao gerar relatório: {str(e)}")
        return False


def main():
    """Função principal"""
    print("DEPLOY DO SISTEMA DE LOGIN SIMPLIFICADO")
    print("=" * 80)
    
    # Lista de etapas
    etapas = [
        ("Verificar Heroku CLI", verificar_heroku_cli),
        ("Verificar Git Status", verificar_git_status),
        ("Criar Configurações de Login", criar_configuracoes_login_heroku),
        ("Testar Sistema Localmente", testar_sistema_local),
        ("Deploy para Heroku", fazer_deploy_heroku),
        ("Testar Heroku Pós-Deploy", testar_heroku_pos_deploy),
        ("Gerar Relatório Final", gerar_relatorio_final),
    ]
    
    resultados = []
    
    for nome, funcao in etapas:
        print(f"\n{'='*20} {nome} {'='*20}")
        
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
            
            if not resultado:
                print(f"\n❌ FALHA na etapa: {nome}")
                
                resposta = input("Deseja continuar mesmo assim? (s/n): ").lower()
                if resposta != 's':
                    print("Deploy cancelado pelo usuário.")
                    return False
                    
        except Exception as e:
            print(f"\n❌ ERRO na etapa '{nome}': {str(e)}")
            resultados.append((nome, False))
            
            resposta = input("Deseja continuar mesmo assim? (s/n): ").lower()
            if resposta != 's':
                print("Deploy cancelado devido a erro.")
                return False
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DO DEPLOY")
    print("="*80)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅ SUCESSO" if resultado else "❌ FALHA"
        print(f"   {nome}: {status}")
        if resultado:
            sucessos += 1
    
    print(f"\nResultado: {sucessos}/{len(resultados)} etapas concluídas com sucesso")
    
    if sucessos == len(resultados):
        print("\n🎉 Deploy concluído com sucesso!")
        print("   O sistema de login simplificado está ativo no Heroku.")
    else:
        print(f"\n⚠️  Deploy parcialmente concluído.")
        print("   Verifique os erros acima e corrija se necessário.")
    
    return sucessos == len(resultados)


if __name__ == '__main__':
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\nDeploy interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO FATAL: {str(e)}")
        sys.exit(1)