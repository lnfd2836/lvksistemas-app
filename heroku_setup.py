#!/usr/bin/env python
"""
Script de configuração específica para Heroku
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    sys.exit(1)

from django.core.management import call_command
from django.contrib.auth.models import User
from lojas.models import Loja
from lojas.services.isolamento_service import IsolamentoService

def setup_database():
    """Configura banco de dados inicial"""
    print("🗄️  Configurando banco de dados...")
    
    try:
        # Executar migrações
        call_command('migrate', verbosity=1)
        print("✅ Migrações executadas")
        
        # Coletar arquivos estáticos
        call_command('collectstatic', '--noinput', verbosity=1)
        print("✅ Arquivos estáticos coletados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração do banco: {e}")
        return False

def setup_isolation():
    """Configura isolamento de lojas"""
    print("🔒 Configurando isolamento de lojas...")
    
    try:
        # Verificar se há lojas ativas
        lojas_ativas = Loja.objects.filter(status='ativa')
        
        if not lojas_ativas.exists():
            print("ℹ️  Nenhuma loja ativa encontrada - isolamento será configurado quando lojas forem criadas")
            return True
        
        # Configurar isolamento para lojas existentes
        for loja in lojas_ativas:
            try:
                if IsolamentoService.create_loja_database(loja):
                    print(f"✅ Isolamento configurado para loja: {loja.nome}")
                else:
                    print(f"⚠️  Erro ao configurar isolamento para loja: {loja.nome}")
            except Exception as e:
                print(f"⚠️  Erro na loja {loja.nome}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração de isolamento: {e}")
        return False

def check_environment():
    """Verifica variáveis de ambiente"""
    print("🔍 Verificando variáveis de ambiente...")
    
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'ASAAS_API_KEY',
        'ASAAS_ENVIRONMENT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Variáveis faltando: {', '.join(missing_vars)}")
        return False
    
    print("✅ Variáveis de ambiente OK")
    return True

def create_default_superuser():
    """Cria superusuário padrão se não existir"""
    print("👤 Verificando superusuário...")
    
    try:
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superusuário já existe")
            return True
        
        # Verificar se há variáveis para criar superuser
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if admin_email and admin_password:
            User.objects.create_superuser(
                username='admin',
                email=admin_email,
                password=admin_password
            )
            print("✅ Superusuário criado automaticamente")
            return True
        else:
            print("ℹ️  Configure ADMIN_EMAIL e ADMIN_PASSWORD para criar superuser automaticamente")
            return True
            
    except Exception as e:
        print(f"⚠️  Erro ao criar superusuário: {e}")
        return True  # Não é crítico

def validate_deployment():
    """Valida se o deployment está funcionando"""
    print("🔍 Validando deployment...")
    
    try:
        # Testar conexão com banco
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexão com banco OK")
        
        # Verificar se apps estão carregados
        from django.apps import apps
        app_configs = apps.get_app_configs()
        print(f"✅ {len(app_configs)} apps carregados")
        
        # Verificar isolamento
        status = IsolamentoService.get_isolation_status()
        print(f"✅ Status do isolamento: {status.get('isolation_active', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def main():
    """Função principal"""
    print("⚙️  CONFIGURAÇÃO HEROKU - LVK SISTEMAS")
    print("=" * 40)
    
    success = True
    
    # Verificar ambiente
    if not check_environment():
        print("⚠️  Algumas variáveis de ambiente estão faltando")
    
    # Configurar banco
    if not setup_database():
        success = False
    
    # Configurar isolamento
    if not setup_isolation():
        print("⚠️  Isolamento não configurado completamente")
    
    # Criar superusuário
    create_default_superuser()
    
    # Validar deployment
    if not validate_deployment():
        success = False
    
    if success:
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🌐 Sistema pronto para uso")
    else:
        print("\n⚠️  CONFIGURAÇÃO CONCLUÍDA COM AVISOS")
        print("🔍 Verifique os logs para mais detalhes")
    
    return success

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        sys.exit(1)