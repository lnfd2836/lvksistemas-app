from controle_financeiro.models import BoletoGerado, CobrancaAsaas

print('🔍 VERIFICANDO BOLETO 138')
print('=' * 40)

boleto = BoletoGerado.objects.filter(id=138).first()
if boleto:
    print(f'✅ Boleto 138 encontrado!')
    print(f'   Número: {boleto.numero_boleto}')
    print(f'   Banco: {boleto.configuracao.codigo_banco}')
    print(f'   Valor: R$ {boleto.valor}')
    print(f'   Data vencimento: {boleto.data_vencimento}')
    
    # Verificar se tem dados do Asaas
    cobranca = CobrancaAsaas.objects.filter(controle_financeiro=boleto.controle_financeiro).first()
    if cobranca:
        print(f'✅ Cobrança Asaas encontrada!')
        print(f'   ID Asaas: {cobranca.asaas_id}')
        print(f'   PIX QR Code: {"Sim" if cobranca.pix_qr_code else "Não"}')
        print(f'   PIX Copy/Paste: {"Sim" if cobranca.pix_copy_paste else "Não"}')
        print(f'   Status: {cobranca.status}')
    else:
        print('⚠️ Cobrança Asaas não encontrada')
else:
    print('❌ Boleto 138 não encontrado')

# Verificar todos os boletos recentes
print('\n📋 ÚLTIMOS 5 BOLETOS:')
boletos = BoletoGerado.objects.all().order_by('-id')[:5]
for b in boletos:
    print(f'   ID: {b.id}, Número: {b.numero_boleto}, Banco: {b.configuracao.codigo_banco}')
