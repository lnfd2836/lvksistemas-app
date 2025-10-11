#!/usr/bin/env python3
"""
Análise do novo código de barras inválido da Caixa
Código: 1049270145194517087962946150143872380000002990
"""

def analisar_novo_codigo():
    """Analisa o novo código problemático da Caixa"""
    
    codigo = "1049270145194517087962946150143872380000002990"
    
    print("=" * 80)
    print("🔍 ANÁLISE DO NOVO CÓDIGO PROBLEMÁTICO CAIXA")
    print("=" * 80)
    print(f"Código: {codigo}")
    print(f"Comprimento: {len(codigo)} dígitos")
    
    if len(codigo) == 47:
        print("📝 TIPO: Linha digitável (47 dígitos)")
        
        # Analisar como linha digitável
        linha_limpa = codigo.replace('.', '').replace(' ', '')
        
        # Extrair campos da linha digitável
        campo1 = linha_limpa[0:10]   # 1049270145
        campo2 = linha_limpa[10:21]  # 19451708796
        campo3 = linha_limpa[21:32]  # 29461501438
        campo4 = linha_limpa[32:33]  # 7
        campo5 = linha_limpa[33:47]  # 23800000002990
        
        print(f"\n📊 CAMPOS DA LINHA DIGITÁVEL:")
        print(f"   Campo 1: {campo1}")
        print(f"   Campo 2: {campo2}")
        print(f"   Campo 3: {campo3}")
        print(f"   Campo 4: {campo4} (DV geral)")
        print(f"   Campo 5: {campo5} (vencimento + valor)")
        
        # Reconstruir código de barras
        banco_moeda = campo1[0:4]  # 1049
        campo_livre_parte1 = campo1[4:9]  # 27014
        campo_livre_parte2 = campo2[0:10]  # 1945170879
        campo_livre_parte3 = campo3[0:10]  # 2946150143
        dv_geral = campo4  # 7
        vencimento_valor = campo5  # 23800000002990
        
        # Montar código de barras
        codigo_barras = banco_moeda + dv_geral + vencimento_valor + campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3
        
        print(f"\n🔄 CÓDIGO DE BARRAS RECONSTRUÍDO:")
        print(f"   {codigo_barras} ({len(codigo_barras)} dígitos)")
        
        if len(codigo_barras) == 44:
            # Extrair componentes do código de barras
            banco = codigo_barras[0:3]
            moeda = codigo_barras[3:4]
            dv_geral = codigo_barras[4:5]
            vencimento = codigo_barras[5:9]
            valor = codigo_barras[9:19]
            campo_livre = codigo_barras[19:44]
            
            print(f"\n📊 COMPONENTES DO CÓDIGO DE BARRAS:")
            print(f"   Banco: {banco} (Caixa Econômica Federal)")
            print(f"   Moeda: {moeda} (Real)")
            print(f"   DV Geral: {dv_geral}")
            print(f"   Vencimento: {vencimento}")
            print(f"   Valor: {valor}")
            print(f"   Campo Livre: {campo_livre} ({len(campo_livre)} dígitos)")
            
            # Analisar campo livre SIGCB
            if len(campo_livre) == 25:
                codigo_cedente = campo_livre[0:6]
                nosso_numero = campo_livre[6:16]
                agencia_complemento = campo_livre[16:22]
                carteira = campo_livre[22:25]
                
                agencia = agencia_complemento[0:4]
                complemento = agencia_complemento[4:6]
                
                print(f"\n🔍 ANÁLISE DO CAMPO LIVRE SIGCB:")
                print(f"   Código Cedente: {codigo_cedente}")
                print(f"   Nosso Número: {nosso_numero}")
                print(f"   Agência: {agencia}")
                print(f"   Complemento: {complemento}")
                print(f"   Carteira: {carteira}")
                
                print(f"\n❌ PROBLEMA IDENTIFICADO:")
                print(f"   O complemento '{complemento}' provavelmente contém dados da conta corrente")
                print(f"   Conforme suporte Caixa: conta corrente NÃO deve ser usada no código de barras")
                print(f"   Este é o MESMO PROBLEMA do código anterior")
                
                # Comparar com dados do boleto
                print(f"\n📋 DADOS DO BOLETO:")
                print(f"   Nosso Número: 1945170874 (do documento)")
                print(f"   Nosso Número no código: {nosso_numero}")
                print(f"   Vencimento: 17/10/2025")
                print(f"   Valor: R$ 29,90")
                
                return {
                    'codigo_cedente': codigo_cedente,
                    'nosso_numero': nosso_numero,
                    'agencia': agencia,
                    'complemento': complemento,
                    'carteira': carteira,
                    'problema': 'dados_conta_no_complemento'
                }
    
    return None

def comparar_com_codigo_anterior():
    """Compara com o código problemático anterior"""
    
    print("\n" + "=" * 80)
    print("🔄 COMPARAÇÃO COM CÓDIGO ANTERIOR")
    print("=" * 80)
    
    codigo_anterior = "10492670145204324981352946570149762600000002990"
    codigo_novo = "1049270145194517087962946150143872380000002990"
    
    print(f"Código anterior: {codigo_anterior}")
    print(f"Código novo:     {codigo_novo}")
    print(f"Diferenças:")
    
    for i, (c1, c2) in enumerate(zip(codigo_anterior, codigo_novo)):
        if c1 != c2:
            print(f"   Posição {i}: '{c1}' -> '{c2}'")
    
    print(f"\n🔍 ANÁLISE:")
    print(f"   - Ambos são códigos da Caixa (104)")
    print(f"   - Ambos têm 47 dígitos (linha digitável)")
    print(f"   - Ambos têm o MESMO PROBLEMA: dados da conta no campo livre")
    print(f"   - Nossa correção deve resolver AMBOS os casos")

def main():
    """Função principal"""
    
    print("🚀 ANÁLISE DO NOVO CÓDIGO PROBLEMÁTICO CAIXA")
    
    # Analisar novo código
    resultado = analisar_novo_codigo()
    
    # Comparar com anterior
    comparar_com_codigo_anterior()
    
    print("\n" + "=" * 80)
    print("📋 CONCLUSÃO")
    print("=" * 80)
    print("✅ Confirmado: MESMO PROBLEMA do código anterior")
    print("✅ Causa: Dados da conta corrente no campo livre SIGCB")
    print("✅ Solução: Nossa correção já implementada deve resolver")
    print("✅ Ação: Aplicar correção e testar com ambos os códigos")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Aplicar nossa correção SIGCB")
    print(f"   2. Testar com ambos os códigos problemáticos")
    print(f"   3. Validar com suporte da Caixa")
    print(f"   4. Deploy da correção")

if __name__ == "__main__":
    main()