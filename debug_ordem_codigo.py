#!/usr/bin/env python3
"""
Debug da ordem de montagem do código de barras
"""

def analisar_ordem_montagem():
    """Analisa a ordem de montagem do código"""
    
    print("=" * 80)
    print("🔍 DEBUG DA ORDEM DE MONTAGEM DO CÓDIGO DE BARRAS")
    print("=" * 80)
    
    # Dados do código problemático
    linha = "10492670145205044404292946150143882610000002990"
    
    # Como está sendo montado atualmente (INCORRETO)
    campo1 = linha[0:10]   # 1049267014
    campo2 = linha[10:21]  # 52050444042
    campo3 = linha[21:32]  # 92946150143
    campo4 = linha[32:33]  # 8
    campo5 = linha[33:47]  # 82610000002990
    
    banco_moeda = campo1[0:4]  # 1049
    campo_livre_parte1 = campo1[4:9]  # 26701
    campo_livre_parte2 = campo2[0:10]  # 5205044404
    campo_livre_parte3 = campo3[0:10]  # 9294615014
    dv_geral = campo4  # 8
    vencimento_valor = campo5  # 82610000002990
    
    # MONTAGEM ATUAL (INCORRETA)
    codigo_atual = banco_moeda + dv_geral + vencimento_valor + campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3
    
    print(f"📋 MONTAGEM ATUAL (INCORRETA):")
    print(f"   Banco+Moeda: {banco_moeda}")
    print(f"   DV: {dv_geral}")
    print(f"   Vencimento+Valor: {vencimento_valor}")
    print(f"   Campo Livre P1: {campo_livre_parte1}")
    print(f"   Campo Livre P2: {campo_livre_parte2}")
    print(f"   Campo Livre P3: {campo_livre_parte3}")
    print(f"   Código montado: {codigo_atual}")
    
    # MONTAGEM CORRETA FEBRABAN
    # Formato: banco(3) + moeda(1) + dv(1) + vencimento(4) + valor(10) + campo_livre(25)
    
    banco = banco_moeda[0:3]  # 104
    moeda = banco_moeda[3:4]  # 9
    vencimento = vencimento_valor[0:4]  # 8261
    valor = vencimento_valor[4:14]  # 0000002990
    campo_livre = campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3  # 25 dígitos
    
    print(f"\n📋 COMPONENTES CORRETOS:")
    print(f"   Banco: {banco}")
    print(f"   Moeda: {moeda}")
    print(f"   Vencimento: {vencimento}")
    print(f"   Valor: {valor}")
    print(f"   Campo Livre: {campo_livre} ({len(campo_livre)} dígitos)")
    
    # Código sem DV para cálculo correto
    codigo_sem_dv_correto = banco + moeda + vencimento + valor + campo_livre
    
    print(f"\n📋 CÓDIGO SEM DV (CORRETO):")
    print(f"   {codigo_sem_dv_correto}")
    print(f"   Comprimento: {len(codigo_sem_dv_correto)} dígitos")
    
    # Calcular DV correto
    dv_correto = calcular_dv_febraban(codigo_sem_dv_correto)
    
    print(f"\n📊 CÁLCULO DO DV:")
    print(f"   DV atual (incorreto): {dv_geral}")
    print(f"   DV correto: {dv_correto}")
    
    # Código de barras correto
    codigo_correto = banco + moeda + str(dv_correto) + vencimento + valor + campo_livre
    
    print(f"\n✅ CÓDIGO DE BARRAS CORRETO:")
    print(f"   {codigo_correto}")
    print(f"   Comprimento: {len(codigo_correto)} dígitos")
    
    return codigo_correto

def calcular_dv_febraban(codigo):
    """Calcula DV usando algoritmo FEBRABAN"""
    
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
        dv = 11 - resto
        if dv == 10:
            return 0
        return dv

def gerar_linha_digitavel_correta(codigo_barras):
    """Gera linha digitável correta"""
    
    print(f"\n{'='*80}")
    print("🔧 GERANDO LINHA DIGITÁVEL CORRETA")
    print(f"{'='*80}")
    
    if len(codigo_barras) != 44:
        print(f"❌ Código deve ter 44 dígitos, tem {len(codigo_barras)}")
        return None
    
    # Extrair campos
    banco = codigo_barras[0:3]      # 104
    moeda = codigo_barras[3:4]      # 9
    dv_geral = codigo_barras[4:5]   # DV
    vencimento = codigo_barras[5:9] # Fator vencimento
    valor = codigo_barras[9:19]     # Valor
    campo_livre = codigo_barras[19:44]  # Campo livre (25)
    
    print(f"📋 COMPONENTES DO CÓDIGO:")
    print(f"   Banco: {banco}")
    print(f"   Moeda: {moeda}")
    print(f"   DV: {dv_geral}")
    print(f"   Vencimento: {vencimento}")
    print(f"   Valor: {valor}")
    print(f"   Campo Livre: {campo_livre}")
    
    # Campo 1: Banco + Moeda + primeiros 5 do campo livre + DV
    campo1_base = f"{banco}{moeda}{campo_livre[0:5]}"
    dv1 = calcular_dv_modulo10(campo1_base)
    campo1 = f"{campo1_base[0:5]}.{campo1_base[5:10]}{dv1}"
    
    # Campo 2: Próximos 10 dígitos do campo livre + DV
    campo2_base = campo_livre[5:15]
    dv2 = calcular_dv_modulo10(campo2_base)
    campo2 = f"{campo2_base[0:5]}.{campo2_base[5:10]}{dv2}"
    
    # Campo 3: Últimos 10 dígitos do campo livre + DV
    campo3_base = campo_livre[15:25]
    dv3 = calcular_dv_modulo10(campo3_base)
    campo3 = f"{campo3_base[0:5]}.{campo3_base[5:10]}{dv3}"
    
    # Campo 4: DV geral
    campo4 = dv_geral
    
    # Campo 5: Fator vencimento + valor
    campo5 = f"{vencimento}{valor}"
    
    linha_correta = f"{campo1} {campo2} {campo3} {campo4} {campo5}"
    
    print(f"\n✅ LINHA DIGITÁVEL CORRETA:")
    print(f"   {linha_correta}")
    
    return linha_correta

def calcular_dv_modulo10(codigo):
    """Calcula DV módulo 10"""
    
    soma = 0
    multiplicador = 2
    
    for digito in reversed(codigo):
        if digito.isdigit():
            produto = int(digito) * multiplicador
            if produto > 9:
                produto = sum(int(d) for d in str(produto))
            soma += produto
            multiplicador = 3 - multiplicador
    
    resto = soma % 10
    return 0 if resto == 0 else 10 - resto

def main():
    """Função principal"""
    
    print("🚀 DEBUG DA ORDEM DE MONTAGEM DO CÓDIGO DE BARRAS")
    
    # Analisar ordem atual
    codigo_correto = analisar_ordem_montagem()
    
    # Gerar linha digitável correta
    if codigo_correto:
        linha_correta = gerar_linha_digitavel_correta(codigo_correto)
    
    print(f"\n{'='*80}")
    print("📋 CONCLUSÃO")
    print(f"{'='*80}")
    
    print("❌ PROBLEMA IDENTIFICADO:")
    print("   - Ordem de montagem do código de barras está incorreta")
    print("   - DV sendo calculado com ordem errada")
    print("   - Precisa corrigir a montagem no serviço")
    
    print(f"\n🔧 CORREÇÃO NECESSÁRIA:")
    print("   1. Corrigir ordem: banco + moeda + dv + vencimento + valor + campo_livre")
    print("   2. Recalcular DV com ordem correta")
    print("   3. Testar novamente")

if __name__ == "__main__":
    main()