from controle_financeiro.models import ConfiguracaoBoleto, BoletoGerado, CobrancaAsaas

print('🔍 DIAGNÓSTICO DAS CONFIGURAÇÕES DE BOLETO')
print('=' * 50)

# 1. Verificar configurações existentes
print('\n1️⃣ CONFIGURAÇÕES EXISTENTES:')
configs = ConfiguracaoBoleto.objects.all()
for config in configs:
    print(f'   ID: {config.id}, Banco: {config.codigo_banco} ({config.nome_banco}), Ativo: {config.ativo}')

# 2. Verificar se existe configuração do Asaas
print('\n2️⃣ CONFIGURAÇÃO DO ASAAS:')
config_asaas = ConfiguracaoBoleto.objects.filter(codigo_banco="461").first()
if config_asaas:
    print(f'   ✅ Configuração Asaas encontrada: ID {config_asaas.id}')
    print(f'   Ativo: {config_asaas.ativo}')
    print(f'   Nome: {config_asaas.nome_banco}')
else:
    print('   ❌ Configuração Asaas NÃO encontrada!')

# 3. Verificar configurações ativas
print('\n3️⃣ CONFIGURAÇÕES ATIVAS:')
configs_ativas = ConfiguracaoBoleto.objects.filter(ativo=True)
for config in configs_ativas:
    print(f'   ID: {config.id}, Banco: {config.codigo_banco} ({config.nome_banco})')

# 4. Verificar último boleto gerado
print('\n4️⃣ ÚLTIMO BOLETO GERADO:')
ultimo_boleto = BoletoGerado.objects.all().order_by('-id').first()
if ultimo_boleto:
    print(f'   ID: {ultimo_boleto.id}')
    print(f'   Número: {ultimo_boleto.numero_boleto}')
    print(f'   Banco: {ultimo_boleto.configuracao.codigo_banco} ({ultimo_boleto.configuracao.nome_banco})')
    print(f'   Configuração ID: {ultimo_boleto.configuracao.id}')
    
    # Verificar se tem dados do Asaas
    cobranca = CobrancaAsaas.objects.filter(controle_financeiro=ultimo_boleto.controle_financeiro).first()
    if cobranca:
        print(f'   ✅ Tem dados do Asaas: {cobranca.asaas_id}')
    else:
        print(f'   ❌ NÃO tem dados do Asaas')

# 5. CORREÇÃO AUTOMÁTICA
print('\n5️⃣ APLICANDO CORREÇÕES:')

# Desativar todas as configurações antigas
configs_antigas = ConfiguracaoBoleto.objects.exclude(codigo_banco="461")
for config in configs_antigas:
    config.ativo = False
    config.save()
    print(f'   ✅ Desativada configuração {config.id} ({config.nome_banco})')

# Ativar configuração do Asaas
if config_asaas:
    config_asaas.ativo = True
    config_asaas.save()
    print(f'   ✅ Ativada configuração Asaas {config_asaas.id}')
else:
    print('   ❌ Não foi possível ativar Asaas - configuração não existe')

print('\n🎉 CORREÇÃO CONCLUÍDA!')
