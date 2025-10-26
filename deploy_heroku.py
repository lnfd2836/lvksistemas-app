#!/usr/bin/env python
"""
Script para deploy no Heroku com verificações de segurança
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, check=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_heroku_cli():
    """Verifica se Heroku CLI está instalado"""
    print("🔍 Verificando Heroku CLI...")
    stdout, stderr, code = run_command("heroku --version", check=False)
    
    if code != 0:
        print("❌ Heroku CLI não encontrado!")
        print("📥 Instale com: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    print(f"✅ Heroku CLI encontrado: {stdout}")
    return True

def check_git_status():
    """Verifica status do Git"""
    print("\n🔍 Verificando status do Git...")
    
    # Verificar se é um repositório Git
    stdout, stderr, code = run_command("git status", check=False)
    if code != 0:
        print("❌ Não é um repositório Git!")
        print("🔧 Inicializando repositório...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit"')
        return True
    
    # Verificar se há mudanças não commitadas
    if "nothing to commit" not in stdout:
        print("⚠️  Há mudanças não commitadas:")
        print(stdout)
        
        response = input("💾 Fazer commit das mudanças? (y/n): ")
        if response.lower() == 'y':
            run_command("git add .")
            commit_msg = input("📝 Mensagem do commit (ou Enter para padrão): ")
            if not commit_msg:
                commit_msg = "Deploy updates"
            run_command(f'git commit -m "{commit_msg}"')
        else:
            print("⚠️  Deploy pode falhar com mudanças não commitadas")
    
    print("✅ Git status OK")
    return True

def check_heroku_app():
    """Verifica se app Heroku existe"""
    print("\n🔍 Verificando app Heroku...")
    
    # Listar apps
    stdout, stderr, code = run_command("heroku apps", check=False)
    if code != 0:
        print("❌ Erro ao acessar Heroku. Faça login:")
        run_command("heroku login")
        return None
    
    print("📱 Apps Heroku disponíveis:")
    apps = []
    for line in stdout.split('\n'):
        if line.strip() and not line.startswith('==='):
            app_name = line.split()[0]
            apps.append(app_name)
            print(f"   - {app_name}")
    
    if not apps:
        print("❌ Nenhum app encontrado!")
        app_name = input("🆕 Nome do novo app (ou Enter para auto-gerar): ")
        if app_name:
            run_command(f"heroku create {app_name}")
        else:
            run_command("heroku create")
        return app_name
    
    # Verificar se já tem remote configurado
    stdout, stderr, code = run_command("git remote -v", check=False)
    if "heroku" in stdout:
        # Extrair nome do app do remote
        for line in stdout.split('\n'):
            if 'heroku' in line and 'git.heroku.com' in line:
                app_name = line.split('/')[-1].replace('.git', '').strip()
                print(f"✅ App configurado: {app_name}")
                return app_name
    
    # Selecionar app
    print("\n🎯 Selecione o app para deploy:")
    for i, app in enumerate(apps, 1):
        print(f"   {i}. {app}")
    
    try:
        choice = int(input("Número do app: ")) - 1
        selected_app = apps[choice]
        
        # Configurar remote
        run_command(f"heroku git:remote -a {selected_app}")
        print(f"✅ Remote configurado para: {selected_app}")
        return selected_app
        
    except (ValueError, IndexError):
        print("❌ Seleção inválida!")
        return None

def check_environment_variables(app_name):
    """Verifica e configura variáveis de ambiente"""
    print(f"\n🔍 Verificando variáveis de ambiente para {app_name}...")
    
    # Variáveis obrigatórias
    required_vars = {
        'SECRET_KEY': 'Chave secreta do Django',
        'DEBUG': 'False para produção',
        'ASAAS_API_KEY': 'Chave da API Asaas',
        'ASAAS_ENVIRONMENT': 'production ou sandbox',
        'EMAIL_HOST_USER': 'Email para envio',
        'EMAIL_HOST_PASSWORD': 'Senha do email',
    }
    
    # Obter variáveis atuais
    stdout, stderr, code = run_command(f"heroku config -a {app_name}", check=False)
    current_vars = {}
    
    if code == 0:
        for line in stdout.split('\n'):
            if ':' in line and not line.startswith('==='):
                key, value = line.split(':', 1)
                current_vars[key.strip()] = value.strip()
    
    # Verificar variáveis obrigatórias
    missing_vars = []
    for var, description in required_vars.items():
        if var not in current_vars:
            missing_vars.append((var, description))
    
    if missing_vars:
        print("⚠️  Variáveis de ambiente faltando:")
        for var, desc in missing_vars:
            print(f"   - {var}: {desc}")
        
        print("\n🔧 Configure as variáveis:")
        for var, desc in missing_vars:
            value = input(f"💡 {var} ({desc}): ")
            if value:
                run_command(f'heroku config:set {var}="{value}" -a {app_name}')
    
    # Configurar variáveis específicas do Heroku
    heroku_vars = {
        'SITE_URL': f'https://{app_name}.herokuapp.com',
        'ALLOWED_HOSTS': f'{app_name}.herokuapp.com',
    }
    
    for var, value in heroku_vars.items():
        if var not in current_vars:
            run_command(f'heroku config:set {var}="{value}" -a {app_name}')
            print(f"✅ Configurado {var}={value}")
    
    print("✅ Variáveis de ambiente verificadas")

def check_database(app_name):
    """Verifica e configura banco de dados"""
    print(f"\n🔍 Verificando banco de dados para {app_name}...")
    
    # Verificar se PostgreSQL está configurado
    stdout, stderr, code = run_command(f"heroku addons -a {app_name}", check=False)
    
    if "heroku-postgresql" not in stdout:
        print("🗄️  Configurando PostgreSQL...")
        run_command(f"heroku addons:create heroku-postgresql:mini -a {app_name}")
        print("✅ PostgreSQL configurado")
    else:
        print("✅ PostgreSQL já configurado")

def run_migrations(app_name):
    """Executa migrações no Heroku"""
    print(f"\n🔄 Executando migrações em {app_name}...")
    
    # Executar migrações
    stdout, stderr, code = run_command(f"heroku run python manage.py migrate -a {app_name}", check=False)
    
    if code == 0:
        print("✅ Migrações executadas com sucesso")
    else:
        print(f"⚠️  Erro nas migrações: {stderr}")
        return False
    
    # Coletar arquivos estáticos
    print("📦 Coletando arquivos estáticos...")
    run_command(f"heroku run python manage.py collectstatic --noinput -a {app_name}", check=False)
    
    return True

def create_superuser(app_name):
    """Cria superusuário se necessário"""
    print(f"\n👤 Verificando superusuário em {app_name}...")
    
    response = input("🆕 Criar superusuário? (y/n): ")
    if response.lower() == 'y':
        print("🔧 Execute manualmente após o deploy:")
        print(f"   heroku run python manage.py createsuperuser -a {app_name}")

def deploy_to_heroku(app_name):
    """Faz o deploy para o Heroku"""
    print(f"\n🚀 Fazendo deploy para {app_name}...")
    
    # Push para Heroku
    stdout, stderr, code = run_command("git push heroku main", check=False)
    
    if code != 0:
        # Tentar com master
        stdout, stderr, code = run_command("git push heroku master", check=False)
    
    if code == 0:
        print("✅ Deploy realizado com sucesso!")
        print(f"🌐 App disponível em: https://{app_name}.herokuapp.com")
        return True
    else:
        print(f"❌ Erro no deploy: {stderr}")
        return False

def post_deploy_setup(app_name):
    """Configurações pós-deploy"""
    print(f"\n⚙️  Configurações pós-deploy para {app_name}...")
    
    # Setup do isolamento
    print("🔒 Configurando isolamento de lojas...")
    run_command(f"heroku run python manage.py setup_isolamento --setup -a {app_name}", check=False)
    
    # Verificar logs
    print("📋 Verificando logs...")
    stdout, stderr, code = run_command(f"heroku logs --tail -n 50 -a {app_name}", check=False)
    
    if "error" in stdout.lower() or "error" in stderr.lower():
        print("⚠️  Possíveis erros encontrados nos logs")
        print("🔍 Execute: heroku logs --tail -a {app_name}")
    
    print("✅ Configurações pós-deploy concluídas")

def main():
    """Função principal"""
    print("🚀 DEPLOY PARA HEROKU - LVK SISTEMAS")
    print("=" * 50)
    
    # Verificações pré-deploy
    if not check_heroku_cli():
        return False
    
    if not check_git_status():
        return False
    
    app_name = check_heroku_app()
    if not app_name:
        return False
    
    # Configurações
    check_environment_variables(app_name)
    check_database(app_name)
    
    # Confirmar deploy
    print(f"\n🎯 Pronto para deploy em: {app_name}")
    response = input("🚀 Continuar com o deploy? (y/n): ")
    
    if response.lower() != 'y':
        print("❌ Deploy cancelado")
        return False
    
    # Deploy
    if not deploy_to_heroku(app_name):
        return False
    
    # Migrações
    if not run_migrations(app_name):
        print("⚠️  Deploy realizado mas migrações falharam")
    
    # Configurações finais
    post_deploy_setup(app_name)
    create_superuser(app_name)
    
    print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
    print(f"🌐 Acesse: https://{app_name}.herokuapp.com")
    print(f"📊 Admin: https://{app_name}.herokuapp.com/admin/")
    print(f"📋 Logs: heroku logs --tail -a {app_name}")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Deploy cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        sys.exit(1)