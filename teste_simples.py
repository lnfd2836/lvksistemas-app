import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import ControleFinanceiro

print('🎯 TESTE SIMPLES DA API ASAAS')
print('=' * 40)

# Testar configuração
asaas = AsaasService()
if asaas.validar_configuracao():
    print('✅ API Key válida')
else:
    print('❌ API Key inválida')
    exit(1)

# Buscar controle
controle = ControleFinanceiro.objects.first()
if controle:
    print(f'✅ Controle encontrado: {controle.loja.nome}')
    print(f'   Valor: R$ {controle.valor_mensal}')
else:
    print('❌ Nenhum controle encontrado')
    exit(1)

# Testar geração de cobrança
print('\n🔄 Testando geração de cobrança...')
try:
    resultado = asaas.gerar_cobranca_com_pix(controle, dias_vencimento=30)
    if resultado.get('success'):
        cobranca = resultado['cobranca']
        pix = resultado.get('pix', {})
        print('✅ Cobrança gerada com sucesso!')
        print(f'   ID: {cobranca["id"]}')
        print(f'   Valor: R$ {cobranca["value"]}')
        print(f'   PIX QR Code: {"Sim" if pix.get("encodedImage") else "Não"}')
        print(f'   PIX Copy/Paste: {"Sim" if pix.get("payload") else "Não"}')
    else:
        print(f'❌ Erro: {resultado.get("error")}')
except Exception as e:
    print(f'❌ Exceção: {e}')

print('\n🎉 Teste concluído!')
