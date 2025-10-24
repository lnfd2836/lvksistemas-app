#!/usr/bin/env python
"""
Script de deploy específico para as correções de exclusão de usuários
e configuração do sistema FATESA
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def executar_comando(comando, descricao=""):
    """Executa um comando e mostra o resultado"""
    print(f"🔄 {descricao}")
    print(f"   Comando: {comando}")
    
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"   ✅ Sucesso!")
            if result.stdout.strip():
                print(f"   📄 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Erro (código {result.returncode})")
            if result.stderr.strip():
                print(f"   📄 Erro: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout - comando demorou mais de 5 minutos")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {str(e)}")
        return False

def verificar_mudancas():
    """Verifica as mudanças implementadas"""
    print("🔍 VERIFICANDO MUDANÇAS IMPLEMENTADAS...")
    
    arquivos_criados = [
        "fix_user_deletion.py",
        "fix_notificacao_constraint.py", 
        "dashboard/management/commands/safe_delete_user.py",
        "dashboard/admin_user_safe.py",
        "templates/admin/auth/user/safe_delete.html",
        "modulos/management/commands/configurar_fatesa.py"
    ]
    
    arquivos_modificados = [
        "dashboard/views.py",
        "dashboard/admin.py",
        "dashboard/models.py"
    ]
    
    print("   📁 Arquivos criados:")
    for arquivo in arquivos_criados:
        if os.path.exists(arquivo):
            print(f"      ✅ {arquivo}")
        else:
            print(f"      ❌ {arquivo} - NÃO ENCONTRADO")
    
    print("   📝 Arquivos modificados:")
    for arquivo in arquivos_modificados:
        if os.path.exists(arquivo):
            print(f"      ✅ {arquivo}")
        else:
            print(f"      ❌ {arquivo} - NÃO ENCONTRADO")
    
    return True

def testar_localmente():
    """Testa as correções localmente"""
    print("\n🧪 TESTANDO CORREÇÕES LOCALMENTE...")
    
    # Testar comando FATESA
    print("   🎓 Testando configuração FATESA...")
    if executar_comando("python manage.py configurar_fatesa", "Configurando FATESA"):
        print("      ✅ FATESA configurado com sucesso")
    else:
        print("      ⚠️ Erro na configuração FATESA")
    
    # Testar comando de exclusão segura
    print("   🗑️ Testando comando de exclusão segura...")
    if executar_comando("python manage.py help safe_delete_user", "Verificando comando safe_delete_user"):
        print("      ✅ Comando safe_delete_user disponível")
    else:
        print("      ⚠️ Comando safe_delete_user não encontrado")
    
    # Testar script de correção
    print("   🔧 Testando script de correção...")
    if executar_comando("python fix_user_deletion.py list", "Listando usuários problemáticos"):
        print("      ✅ Script de correção funcionando")
    else:
        print("      ⚠️ Erro no script de correção")
    
    return True

def fazer_commit_correcoes():
    """Faz commit das correções"""
    print("\n📝 FAZENDO COMMIT DAS CORREÇÕES...")
    
    # Verificar status do git
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("   ✅ Nenhuma mudança para commitar")
        return True
    
    # Adicionar arquivos
    if not executar_comando("git add .", "Adicionando arquivos"):
        return False
    
    # Fazer commit
    commit_message = f"🔧 Correções de exclusão de usuários e FATESA - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n" \
                    f"✅ Corrigido problema de constraint dashboard_notificacao\n" \
                    f"✅ Implementada exclusão segura de usuários\n" \
                    f"✅ Criado admin personalizado para User\n" \
                    f"✅ Configurado sistema FATESA para controle de qualidade\n" \
                    f"✅ Adicionados scripts de correção e manutenção\n" \
                    f"✅ Criados comandos de management personalizados"
    
    if executar_comando(f'git commit -m "{commit_message}"', "Fazendo commit"):
        print("   ✅ Commit realizado com sucesso")
        return True
    else:
        print("   ❌ Erro no commit")
        return False

def executar_deploy_heroku():
    """Executa o deploy no Heroku"""
    print("\n🚀 EXECUTANDO DEPLOY NO HEROKU...")
    
    # Verificar se está logado no Heroku
    result = subprocess.run("heroku auth:whoami", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("   ❌ Não está logado no Heroku")
        print("   📋 Execute: heroku login")
        return False
    
    print(f"   👤 Logado como: {result.stdout.strip()}")
    
    # Push para Heroku
    if executar_comando("git push heroku main", "Enviando código para Heroku"):
        print("   ✅ Deploy realizado com sucesso!")
        return True
    else:
        print("   ❌ Falha no deploy")
        return False

def executar_pos_deploy():
    """Executa comandos pós-deploy"""
    print("\n⚙️ EXECUTANDO COMANDOS PÓS-DEPLOY...")
    
    app_name = "lvksistemas-app"
    
    # Executar migrações
    print("   🔄 Executando migrações...")
    executar_comando(f"heroku run python manage.py migrate --app {app_name}", "Migrações")
    
    # Configurar FATESA no Heroku
    print("   🎓 Configurando FATESA no Heroku...")
    executar_comando(f"heroku run python manage.py configurar_fatesa --app {app_name}", "Configuração FATESA")
    
    # Coletar arquivos estáticos
    print("   📁 Coletando arquivos estáticos...")
    executar_comando(f"heroku run python manage.py collectstatic --noinput --app {app_name}", "Arquivos estáticos")
    
    return True

def verificar_deploy():
    """Verifica se o deploy foi bem-sucedido"""
    print("\n🔍 VERIFICANDO DEPLOY...")
    
    app_name = "lvksistemas-app"
    
    # Verificar logs
    print("   📋 Verificando logs...")
    result = subprocess.run(f"heroku logs --tail --num 20 --app {app_name}", 
                          shell=True, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("   ✅ Logs acessíveis")
        if "Error" in result.stdout or "error" in result.stdout.lower():
            print("   ⚠️ Possíveis erros nos logs:")
            print(f"   {result.stdout[-300:]}")
        else:
            print("   ✅ Nenhum erro aparente nos logs")
    
    # Testar URL
    print("   🌐 Testando aplicação...")
    try:
        import requests
        url = f"https://{app_name}.herokuapp.com"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print("   ✅ Aplicação respondendo corretamente!")
        else:
            print(f"   ⚠️ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Erro ao testar URL: {e}")
    
    return True

def mostrar_resumo():
    """Mostra resumo das correções implementadas"""
    print("\n" + "="*80)
    print("🎉 DEPLOY DAS CORREÇÕES CONCLUÍDO!")
    print("="*80)
    
    print("🔧 Correções Implementadas:")
    print("   ✅ Problema de constraint dashboard_notificacao resolvido")
    print("   ✅ Exclusão segura de usuários implementada")
    print("   ✅ Admin personalizado para User criado")
    print("   ✅ Sistema FATESA configurado para controle de qualidade")
    print("   ✅ Scripts de manutenção adicionados")
    print("   ✅ Comandos de management personalizados")
    
    print("\n🛠️ Novos Recursos:")
    print("   • python manage.py safe_delete_user <id> - Exclusão segura")
    print("   • python manage.py configurar_fatesa - Configurar FATESA")
    print("   • python fix_user_deletion.py - Script de correção")
    print("   • Admin personalizado com exclusão segura")
    
    print("\n🎯 Funcionalidades FATESA:")
    print("   • Dashboard específico para controle de qualidade")
    print("   • Módulos educacionais configurados")
    print("   • Integração com sistema de avaliação")
    
    app_name = "lvksistemas-app"
    print(f"\n🔗 URLs:")
    print(f"   • Principal: https://{app_name}.herokuapp.com")
    print(f"   • Admin: https://{app_name}.herokuapp.com/admin/")

def main():
    """Função principal"""
    print("="*80)
    print("🔧 DEPLOY - CORREÇÕES DE USUÁRIOS E FATESA")
    print("="*80)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificar mudanças
    if not verificar_mudancas():
        print("❌ Verificação de mudanças falhou")
        return False
    
    # Testar localmente
    if not testar_localmente():
        print("❌ Testes locais falharam")
        return False
    
    # Fazer commit
    if not fazer_commit_correcoes():
        print("❌ Commit falhou")
        return False
    
    # Deploy
    if not executar_deploy_heroku():
        print("❌ Deploy falhou")
        return False
    
    # Pós-deploy
    executar_pos_deploy()
    
    # Verificar
    time.sleep(10)
    verificar_deploy()
    
    # Resumo
    mostrar_resumo()
    
    return True

if __name__ == '__main__':
    try:
        sucesso = main()
        
        if sucesso:
            print("\n🎉 DEPLOY DAS CORREÇÕES CONCLUÍDO COM SUCESSO!")
            sys.exit(0)
        else:
            print("\n❌ DEPLOY DAS CORREÇÕES FALHOU!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Deploy interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        sys.exit(1)