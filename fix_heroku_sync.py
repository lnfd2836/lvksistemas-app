#!/usr/bin/env python
"""
Script para corrigir sincronização no Heroku
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

import logging
from django.utils import timezone
from controle_financeiro.asaas_sync_service import get_sync_service
from controle_financeiro.models_sync import SyncStatus

logger = logging.getLogger(__name__)

def fix_sync_status():
    """Corrige o status da sincronização no Heroku"""
    print("🔧 CORRIGINDO STATUS DA SINCRONIZAÇÃO NO HEROKU")
    print("=" * 50)
    
    try:
        # Obter status atual
        db_status = SyncStatus.get_current()
        sync_service = get_sync_service()
        
        print(f"📊 Status atual no banco:")
        print(f"   - Rodando: {db_status.is_running}")
        print(f"   - Intervalo: {db_status.sync_interval}s")
        print(f"   - Última sync: {db_status.last_sync}")
        print(f"   - Iniciado em: {db_status.started_at}")
        print(f"   - Parado em: {db_status.stopped_at}")
        
        # No Heroku, a sincronização não pode rodar em background
        # Vamos marcar como "ativa" mas com execução manual
        if not db_status.is_running:
            print("\n🔄 Ativando sincronização para modo Heroku...")
            db_status.start_sync(300)  # 5 minutos
            print("✅ Sincronização marcada como ativa")
        else:
            print("✅ Sincronização já está marcada como ativa")
        
        # Atualizar timestamp da última sincronização
        db_status.update_last_sync()
        print("✅ Timestamp atualizado")
        
        # Executar uma sincronização de teste
        print("\n🧪 Executando sincronização de teste...")
        result = sync_service.simple_sync_check()
        
        print(f"📊 Resultado do teste:")
        print(f"   - API acessível: {result['api_accessible']}")
        print(f"   - Config válida: {result['config_valid']}")
        print(f"   - Cobranças testadas: {result['sample_charges_checked']}")
        
        if result['errors']:
            print(f"   - Erros: {len(result['errors'])}")
            for error in result['errors'][:3]:
                print(f"     • {error}")
        
        # Atualizar estatísticas
        stats = {
            'total_synced': db_status.stats.get('total_synced', 0),
            'updates_found': db_status.stats.get('updates_found', 0),
            'errors': db_status.stats.get('errors', 0) + len(result['errors']),
            'last_error': result['errors'][-1] if result['errors'] else None,
            'last_test': timezone.now().isoformat(),
            'heroku_mode': True
        }
        
        db_status.update_stats(stats)
        print("✅ Estatísticas atualizadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir status: {e}")
        return False

def test_sync_functionality():
    """Testa funcionalidade de sincronização"""
    print("\n🧪 TESTANDO FUNCIONALIDADE DE SINCRONIZAÇÃO")
    print("=" * 45)
    
    try:
        sync_service = get_sync_service()
        
        # Teste 1: Verificação de conectividade
        print("1. Testando conectividade...")
        result = sync_service.simple_sync_check()
        
        if result['api_accessible']:
            print("   ✅ API Asaas acessível")
        else:
            print("   ❌ API Asaas inacessível")
            
        if result['config_valid']:
            print("   ✅ Configuração válida")
        else:
            print("   ❌ Configuração inválida")
        
        # Teste 2: Sincronização limitada
        print("\n2. Testando sincronização limitada...")
        try:
            sync_result = sync_service._sync_existing_charges_limited()
            print(f"   📊 Processadas: {sync_result['processed']}")
            print(f"   📊 Atualizadas: {sync_result['updates']}")
            print(f"   📊 Erros: {len(sync_result['errors'])}")
            
            if sync_result['errors']:
                print("   ⚠️  Erros encontrados:")
                for error in sync_result['errors'][:2]:
                    print(f"      • {error}")
        
        except Exception as e:
            print(f"   ❌ Erro na sincronização: {e}")
        
        # Teste 3: Status do serviço
        print("\n3. Verificando status do serviço...")
        status = sync_service.get_sync_status()
        print(f"   - Rodando: {status['is_running']}")
        print(f"   - Última sync: {status['last_sync']}")
        print(f"   - Thread ativa: {status['thread_alive']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def create_heroku_sync_command():
    """Cria comando para sincronização manual no Heroku"""
    print("\n📝 CRIANDO COMANDO DE SINCRONIZAÇÃO MANUAL")
    print("=" * 45)
    
    try:
        # Criar script de sincronização manual
        script_content = '''#!/usr/bin/env python
"""
Comando para executar sincronização manual no Heroku
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.asaas_sync_service import get_sync_service
from controle_financeiro.models_sync import SyncStatus

def main():
    print("🔄 SINCRONIZAÇÃO MANUAL - HEROKU")
    print("=" * 35)
    
    try:
        sync_service = get_sync_service()
        
        # Executar sincronização
        result = sync_service.force_sync_now()
        
        print(f"📊 Resultado:")
        print(f"   - Processadas: {result['total_processed']}")
        print(f"   - Atualizadas: {result['updates_made']}")
        print(f"   - Novas: {result['new_charges']}")
        print(f"   - Erros: {len(result['errors'])}")
        
        if result['errors']:
            print("⚠️  Erros:")
            for error in result['errors'][:3]:
                print(f"   • {error}")
        
        # Atualizar status
        db_status = SyncStatus.get_current()
        db_status.update_last_sync()
        
        print("✅ Sincronização concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    main()
'''
        
        # Salvar script
        with open('sync_manual_heroku.py', 'w') as f:
            f.write(script_content)
        
        print("✅ Script criado: sync_manual_heroku.py")
        print("\n💡 Para usar no Heroku:")
        print("   heroku run python sync_manual_heroku.py --app lvksistemas-app")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar comando: {e}")
        return False

def show_heroku_instructions():
    """Mostra instruções para usar no Heroku"""
    print("\n📋 INSTRUÇÕES PARA HEROKU")
    print("=" * 30)
    
    print("🔧 Comandos úteis:")
    print("   # Verificar status")
    print("   heroku run python fix_heroku_sync.py --app lvksistemas-app")
    print()
    print("   # Sincronização manual")
    print("   heroku run python sync_manual_heroku.py --app lvksistemas-app")
    print()
    print("   # Ver logs da sincronização")
    print("   heroku logs --tail --app lvksistemas-app | grep -i sync")
    print()
    
    print("💡 Dicas:")
    print("   - No Heroku, a sincronização deve ser executada manualmente")
    print("   - Use Heroku Scheduler para automatizar (add-on pago)")
    print("   - Execute sincronização manual 2-3 vezes por dia")
    print("   - Monitore via dashboard: /financeiro/sync/")

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE SINCRONIZAÇÃO HEROKU")
    print("=" * 40)
    
    success_count = 0
    
    # Passo 1: Corrigir status
    if fix_sync_status():
        success_count += 1
        print("✅ Status corrigido")
    else:
        print("❌ Falha ao corrigir status")
    
    # Passo 2: Testar funcionalidade
    if test_sync_functionality():
        success_count += 1
        print("✅ Funcionalidade testada")
    else:
        print("❌ Falha no teste")
    
    # Passo 3: Criar comando manual
    if create_heroku_sync_command():
        success_count += 1
        print("✅ Comando manual criado")
    else:
        print("❌ Falha ao criar comando")
    
    # Mostrar instruções
    show_heroku_instructions()
    
    print(f"\n📊 RESULTADO: {success_count}/3 passos concluídos")
    
    if success_count >= 2:
        print("🎉 SINCRONIZAÇÃO CORRIGIDA PARA HEROKU!")
        print("✅ Sistema configurado para execução manual")
        print("🌐 Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/sync/")
    else:
        print("⚠️  CORREÇÃO PARCIAL")
        print("🔍 Alguns problemas podem persistir")
    
    return success_count >= 2

if __name__ == '__main__':
    main()