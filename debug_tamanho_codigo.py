#!/usr/bin/env python3
"""
Debug do tamanho do código de barras
"""

def debug_tamanho_codigo():
    """Debug do tamanho do código de barras"""
    
    # Dados do boleto
    banco = "104"
    moeda = "9"
    fator_vencimento = "2600"  # 08/11/2025
    valor_centavos = "0000002990"  # R$ 29,90
    nosso_numero = "2043249817"
    agencia = "2946"
    conta_parte = "12"  # Primeiros 2 dígitos da conta
    carteira = "014"  # Carteira 14 formatada como 014
    codigo_cedente = "267015"  # Últimos 6 dígitos do código do cedente
    
    # Montar campo livre
    campo_livre = f"{codigo_cedente}{nosso_numero}{agencia}{conta_parte}{carteira}"
    
    print(f"🔍 DEBUG DO TAMANHO DO CÓDIGO DE BARRAS")
    print(f"=" * 50)
    print(f"Banco: {banco} ({len(banco)} dígitos)")
    print(f"Moeda: {moeda} ({len(moeda)} dígitos)")
    print(f"Fator Vencimento: {fator_vencimento} ({len(fator_vencimento)} dígitos)")
    print(f"Valor Centavos: {valor_centavos} ({len(valor_centavos)} dígitos)")
    print(f"Campo Livre: {campo_livre} ({len(campo_livre)} dígitos)")
    
    # Calcular DV geral
    codigo_sem_dv = f"{banco}{moeda}{fator_vencimento}{valor_centavos}{campo_livre}"
    print(f"\nCódigo sem DV: {codigo_sem_dv} ({len(codigo_sem_dv)} dígitos)")
    
    # Calcular DV
    dv_geral = calcular_dv_modulo11_febraban(codigo_sem_dv)
    print(f"DV Geral: {dv_geral}")
    
    # Montar código de barras
    codigo_barras = f"{banco}{moeda}{dv_geral}{fator_vencimento}{valor_centavos}{campo_livre}"
    print(f"\nCódigo de Barras: {codigo_barras} ({len(codigo_barras)} dígitos)")
    
    # Verificar tamanho esperado
    tamanho_esperado = 3 + 1 + 1 + 4 + 10 + 25  # banco + moeda + dv + vencimento + valor + campo_livre
    print(f"Tamanho Esperado: {tamanho_esperado} dígitos")
    
    if len(codigo_barras) == 44:
        print("✅ Tamanho correto!")
    else:
        print(f"❌ Tamanho incorreto! Esperado: 44, Atual: {len(codigo_barras)}")
        
        # Verificar cada componente
        print(f"\n🔍 ANÁLISE DETALHADA:")
        print(f"   Banco: {banco} = {len(banco)} dígitos")
        print(f"   Moeda: {moeda} = {len(moeda)} dígitos")
        print(f"   DV: {dv_geral} = {len(str(dv_geral))} dígitos")
        print(f"   Vencimento: {fator_vencimento} = {len(fator_vencimento)} dígitos")
        print(f"   Valor: {valor_centavos} = {len(valor_centavos)} dígitos")
        print(f"   Campo Livre: {campo_livre} = {len(campo_livre)} dígitos")
        print(f"   Total: {len(banco) + len(moeda) + len(str(dv_geral)) + len(fator_vencimento) + len(valor_centavos) + len(campo_livre)} dígitos")

def calcular_dv_modulo11_febraban(codigo):
    """Calcula dígito verificador módulo 11 FEBRABAN"""
    sequencia = "4329876543298765432987654329876543298765432"
    soma = 0
    
    for i, digito in enumerate(reversed(codigo)):
        if digito.isdigit():
            multiplicador = int(sequencia[i % len(sequencia)])
            produto = int(digito) * multiplicador
            soma += produto
    
    resto = soma % 11
    
    if resto in [0, 10, 11]:
        return 1
    else:
        return 11 - resto

if __name__ == "__main__":
    debug_tamanho_codigo()
