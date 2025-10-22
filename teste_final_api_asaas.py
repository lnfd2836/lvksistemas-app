#!/usr/bin/env python3
"""
Teste Final - API Asaas com Configurações Corretas
"""

import os
import sys
import django
from pathlib import Path

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

def testar_configuracao_atual():
    """Testa a configuração atual do sistema"""
    print("🚀 TESTE FINAL - API ASAAS")
    print("=" * 50)
    
    try:
        django.setup()
        
        from django.conf import settings
        from controle_financeiro.asaas_service import AsaasService
        
        print("📋 CONFIGURAÇÕES ATUAIS:")
        api_key = getattr(settings, 'ASAAS_API_KEY', '')
        environment = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
        
        print(f"🔑 API Key: {'Configurada' if api_key else 'NÃO CONFIGURADA'}")
        print(f"🌐 Environment: {environment}")
        
        if api_key:
            print(f"📏 Tamanho: {len(api_key)} caracteres")
            print(f"🔤 Formato: {'Válido' if api_key.startswith('$aact_') else 'Inválido'}")
            print(f"🎯 Tipo: {'Produção' if 'prod' in api_key else 'Sandbox'}")
        
        # Testa o serviço
        print(f"\n🔧 TESTANDO ASAAS SERVICE:")
        asaas = AsaasService()
        
        print(f"🔑 Service API Key: {'Configurada' if asaas.api_key else 'NÃO CONFIGURADA'}")
        print(f"🌐 Service Environment: {asaas.environment}")
        print(f"📡 Service URL: {asaas.base_url}")
        
        if asaas.api_key:
            print(f"\n🧪 TESTANDO VALIDAÇÃO:")
            try:
                config_valida = asaas.validar_configuracao()
                
                if config_valida:
                    print("✅ CONFIGURAÇÃO VÁLIDA!")
                    print("✅ API funcionando perfeitamente!")
                    return True
                else:
                    print("❌ Configuração inválida")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro na validação: {e}")
                return False
        else:
            print("❌ API Key não configurada no serviço")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

def gerar_comandos_heroku():
    """Gera comandos para configurar no Heroku"""
    print(f"\n🔧 COMANDOS PARA HEROKU:")
    print("=" * 50)
    
    api_key = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl"
    
    print("# 1. Configurar API Key")
    print(f"heroku config:set ASAAS_API_KEY='{api_key}' --app lvksistemas-app")
    
    print("\n# 2. Configurar ambiente")
    print("heroku config:set ASAAS_ENVIRONMENT='production' --app lvksistemas-app")
    
    print("\n# 3. Verificar configuração")
    print("heroku config --app lvksistemas-app")
    
    print("\n# 4. Fazer deploy das correções")
    print("git add .")
    print('git commit -m "Fix: Corrige configuração API Asaas"')
    print("git push heroku main")
    
    print("\n# 5. Testar no Heroku")
    print('heroku run "python -c \\"')
    print('from controle_financeiro.asaas_service import AsaasService')
    print('asaas = AsaasService()')
    print('print(\\"API Key:\\", \\"Configurada\\" if asaas.api_key else \\"NÃO CONFIGURADA\\")')
    print('print(\\"Validação:\\", \\"OK\\" if asaas.validar_configuracao() else \\"ERRO\\")')
    print('\\"" --app lvksistemas-app')

def main():
    """Função principal"""
    funcionando = testar_configuracao_atual()
    
    gerar_comandos_heroku()
    
    print(f"\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    print("=" * 50)
    
    if funcionando:
        print("✅ SISTEMA FUNCIONANDO LOCALMENTE!")
        print("\n📋 Para funcionar no Heroku:")
        print("1. Execute os comandos acima")
        print("2. Teste a geração de boleto")
        print("3. Confirme que não há mais erro 400")
        
        print(f"\n🌐 URL para teste:")
        print("https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/67/")
        
    else:
        print("❌ SISTEMA COM PROBLEMAS!")
        print("\n🔧 Verifique:")
        print("1. Se a API Key está configurada")
        print("2. Se as settings estão corretas")
        print("3. Se há conectividade com a internet")
    
    return funcionando

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)