from controle_financeiro.models import ConfiguracaoBoleto

print('🔍 CONFIGURAÇÕES ATIVAS:')
configs = ConfiguracaoBoleto.objects.filter(ativo=True)
for config in configs:
    print(f'   ID: {config.id}, Banco: {config.codigo_banco} ({config.nome_banco})')
