#!/usr/bin/env python
"""
Script de configuração e inicialização da sincronização em tempo real com Asaas
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings
from controle_financeiro.asaas_sync_service import get_sync_service
from controle_financeiro.asaas_service import AsaasService
import logging

logger = logging.getLogger(__name__)


def check_requirements():
    """Verifica se todos os requisitos estão atendidos"""
    print("🔍 Verificando requisitos...")
    
    issues = []
    
    # Verificar configuração do Asaas
    try:
        asaas_service = AsaasService()
        if not asaas_service.validar_configuracao():
            issues.append("❌ Configuração da API do Asaas inválida")
        else:
            print("✅ API do Asaas configurada corretamente")
    except Exception as e:
        issues.append(f"❌ Erro na configuração do Asaas: {str(e)}")
    
    # Verificar Celery (opcional)
    try:
        from celery import Celery
        print("✅ Celery disponível para tasks automáticas")
    except ImportError:
        issues.append("⚠️ Celery não instalado - tasks automáticas não funcionarão")
    
    # Verificar banco de dados
    try:
        from controle_financeiro.models import CobrancaAsaas
        count = CobrancaAsaas.objects.count()
        print(f"✅ Banco de dados OK ({count} cobranças cadastradas)")
    except Exception as e:
        issues.append(f"❌ Erro no banco de dados: {str(e)}")
    
    return issues


def setup_database():
    """Executa migrações necessárias"""
    print("\n📊 Configurando banco de dados...")
    
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'controle_financeiro'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações executadas com sucesso")
    except Exception as e:
        print(f"❌ Erro nas migrações: {str(e)}")
        return False
    
    return True


def test_sync_service():
    """Testa o serviço de sincronização"""
    print("\n🔄 Testando serviço de sincronização...")
    
    try:
        sync_service = get_sync_service()
        
        # Testar sincronização única
        result = sync_service.sync_all_charges()
        
        print(f"✅ Teste de sincronização concluído:")
        print(f"   - Processadas: {result['total_processed']}")
        print(f"   - Atualizadas: {result['updates_made']}")
        print(f"   - Novas: {result['new_charges']}")
        print(f"   - Erros: {len(result['errors'])}")
        
        if result['errors']:
            print("⚠️ Erros encontrados:")
            for error in result['errors'][:3]:  # Mostrar apenas os 3 primeiros
                print(f"   - {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de sincronização: {str(e)}")
        return False


def start_sync_service(interval=300):
    """Inicia o serviço de sincronização"""
    print(f"\n🚀 Iniciando sincronização em tempo real (intervalo: {interval}s)...")
    
    try:
        sync_service = get_sync_service()
        
        if sync_service.start_real_time_sync(interval):
            print("✅ Sincronização iniciada com sucesso!")
            print("💡 Use o comando 'python manage.py start_asaas_sync --status' para verificar o status")
            print("💡 Acesse /financeiro/sync/ no admin para o dashboard de controle")
            return True
        else:
            print("⚠️ Sincronização já estava em execução")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao iniciar sincronização: {str(e)}")
        return False


def show_status():
    """Mostra o status atual"""
    print("\n📊 Status atual da sincronização:")
    
    try:
        sync_service = get_sync_service()
        status = sync_service.get_sync_status()
        
        if status['is_running']:
            print("✅ Sincronização ATIVA")
            print(f"   - Intervalo: {status['sync_interval']}s")
            print(f"   - Última execução: {status['last_sync'] or 'Nunca'}")
        else:
            print("❌ Sincronização PARADA")
        
        stats = status['stats']
        print(f"\n📈 Estatísticas:")
        print(f"   - Total sincronizado: {stats['total_synced']}")
        print(f"   - Atualizações: {stats['updates_found']}")
        print(f"   - Erros: {stats['errors']}")
        
        if stats['last_error']:
            print(f"   - Último erro: {stats['last_error']}")
        
    except Exception as e:
        print(f"❌ Erro ao obter status: {str(e)}")


def setup_celery_tasks():
    """Configura tasks do Celery"""
    print("\n⚙️ Configurando tasks automáticas do Celery...")
    
    try:
        from controle_financeiro.celery_config import get_celery_config
        config = get_celery_config()
        
        print("✅ Configuração do Celery preparada")
        print("💡 Para ativar as tasks automáticas, execute:")
        print("   celery -A lojad worker --loglevel=info")
        print("   celery -A lojad beat --loglevel=info")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração do Celery: {str(e)}")
        return False


def main():
    """Função principal"""
    print("🔧 CONFIGURAÇÃO DA SINCRONIZAÇÃO EM TEMPO REAL COM ASAAS")
    print("=" * 60)
    
    # Verificar requisitos
    issues = check_requirements()
    
    if issues:
        print("\n⚠️ Problemas encontrados:")
        for issue in issues:
            print(f"   {issue}")
        
        if any("❌" in issue for issue in issues):
            print("\n❌ Corrija os problemas críticos antes de continuar")
            return False
    
    # Configurar banco de dados
    if not setup_database():
        return False
    
    # Testar sincronização
    if not test_sync_service():
        print("⚠️ Teste de sincronização falhou, mas você pode continuar")
    
    # Configurar Celery
    setup_celery_tasks()
    
    # Mostrar opções
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Para iniciar sincronização em tempo real:")
    print("   python setup_asaas_sync.py --start")
    print()
    print("2. Para verificar status:")
    print("   python setup_asaas_sync.py --status")
    print()
    print("3. Para usar comando Django:")
    print("   python manage.py start_asaas_sync")
    print()
    print("4. Para acessar dashboard web:")
    print("   http://seu-site.com/financeiro/sync/")
    print()
    print("5. Para tasks automáticas (Celery):")
    print("   celery -A lojad worker --loglevel=info")
    print("   celery -A lojad beat --loglevel=info")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Configurar sincronização Asaas')
    parser.add_argument('--start', action='store_true', help='Iniciar sincronização')
    parser.add_argument('--status', action='store_true', help='Mostrar status')
    parser.add_argument('--interval', type=int, default=300, help='Intervalo em segundos')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.start:
        if start_sync_service(args.interval):
            print("\n✅ Sincronização iniciada! Pressione Ctrl+C para parar")
            try:
                import time
                while True:
                    time.sleep(30)
                    show_status()
            except KeyboardInterrupt:
                print("\n\n🛑 Parando sincronização...")
                sync_service = get_sync_service()
                sync_service.stop_real_time_sync()
                print("✅ Sincronização parada")
    else:
        main()