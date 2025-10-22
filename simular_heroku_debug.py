#!/usr/bin/env python3
"""
Simular Ambiente Heroku para Debug
Testa exatamente como seria no Heroku
"""

import os
import sys
import django
from pathlib import Path

# Remove .env local para simular Heroku
if os.path.exists('.env'):
    os.rename('.env', '.env.backup')
    print("📁 Arquivo .env temporariamente renomeado")

# Simula variáveis de ambiente do Heroku
os.environ['ASAAS_API_KEY'] = '$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl'
os.environ['ASAAS_ENVIRONMENT'] = 'production'
os.environ['DYNO'] = 'web.1'  # Simula ambiente Heroku
os.environ['SECRET_KEY'] = 'django-test-key-for-heroku-simulation'
os.environ['DEBUG'] = 'False'

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

try:
    django.setup()
    
    print("🚀 SIMULANDO AMBIENTE HEROKU")
    print("=" * 50)
    print(f"🔑 ASAAS_API_KEY: {os.environ.get('ASAAS_API_KEY', 'NÃO CONFIGURADA')[:30]}...")
    print(f"🌐 ASAAS_ENVIRONMENT: {os.environ.get('ASAAS_ENVIRONMENT', 'NÃO CONFIGURADO')}")
    print(f"⚙️ DYNO: {os.environ.get('DYNO', 'NÃO CONFIGURADO')}")
    print("=" * 50)
    
    # Importa e testa o serviço
    from controle_financeiro.asaas_service import AsaasService
    from django.conf import settings
    
    print(f"\n📋 CONFIGURAÇÕES DJANGO:")
    print(f"🔑 settings.ASAAS_API_KEY: {getattr(settings, 'ASAAS_API_KEY', 'NÃO CONFIGURADA')[:30]}...")
    print(f"🌐 settings.ASAAS_ENVIRONMENT: {getattr(settings, 'ASAAS_ENVIRONMENT', 'NÃO CONFIGURADO')}")
    
    # Inicializa o serviço
    print(f"\n🔧 INICIALIZANDO ASAAS SERVICE:")
    asaas = AsaasService()
    print(f"🔑 asaas.api_key: {asaas.api_key[:30] if asaas.api_key else 'NÃO CONFIGURADA'}...")
    print(f"🌐 asaas.environment: {asaas.environment}")
    print(f"📡 asaas.base_url: {asaas.base_url}")
    
    # Testa validação
    print(f"\n🧪 TESTANDO VALIDAÇÃO:")
    try:
        config_valida = asaas.validar_configuracao()
        
        if config_valida:
            print("✅ Configuração válida!")
            
            # Testa criação de cliente
            print(f"\n👤 TESTANDO CRIAÇÃO DE CLIENTE:")
            from controle_financeiro.models import ControleFinanceiro
            
            controle = ControleFinanceiro.objects.first()
            if controle:
                print(f"📋 Usando controle: {controle.loja.nome}")
                
                cliente = asaas.criar_cliente(controle)
                if cliente:
                    print(f"✅ Cliente criado: {cliente.get('id', 'N/A')}")
                    
                    # Testa geração de cobrança
                    print(f"\n📄 TESTANDO GERAÇÃO DE COBRANÇA:")
                    resultado = asaas.gerar_cobranca_com_pix(controle, dias_vencimento=30)
                    
                    if resultado.get('success'):
                        print("✅ Cobrança gerada com sucesso!")
                        print(f"🆔 ID: {resultado['cobranca']['id']}")
                        print(f"💰 Valor: R$ {resultado['cobranca']['value']}")
                    else:
                        print(f"❌ Erro na cobrança: {resultado.get('error', 'Erro desconhecido')}")
                        print(f"📋 Detalhes: {resultado.get('details', 'N/A')}")
                else:
                    print("❌ Erro ao criar cliente")
            else:
                print("❌ Nenhum controle financeiro encontrado")
                
        else:
            print("❌ Configuração inválida!")
            
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 50)
    print("📊 RESUMO:")
    print("- Se viu '✅ Configuração válida!' = API Key funcionando")
    print("- Se viu '✅ Cobrança gerada!' = Sistema 100% funcional")
    print("- Se viu erros = Verifique os detalhes acima")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Restaura .env se foi renomeado
    if os.path.exists('.env.backup'):
        os.rename('.env.backup', '.env')
        print("📁 Arquivo .env restaurado")