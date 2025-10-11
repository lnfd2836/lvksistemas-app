#!/usr/bin/env python3
"""
Análise do novo código de barras problemático
"""

def analisar_codigo_problematico():
    """Analisa o código problemático fornecido pelo usuário"""
    
    codigo = "10492670145204324981352946570149762600000002990"
    
    print("🔍 ANÁLISE DO CÓDIGO PROBLEMÁTICO")
    print("=" * 50)
    print(f"Código: {codigo}")
    print(f"Tamanho: {len(codigo)} dígitos")
    
    if len(codigo) == 47:
        print("📋 Formato: Linha Digitável")
        
        # Decompor linha digitável
        campo1 = codigo[0:10]
        campo2 = codigo[10:21]
        campo3 = codigo[21:32]
        campo4 = codigo[32:33]
        campo5 = codigo[33:47]
        
        print(f"\n📋 Campos:")
        print(f"   Campo 1: {campo1}")
        print(f"   Campo 2: {campo2}")
        print(f"   Campo 3: {campo3}")
        print(f"   Campo 4: {campo4}")
        print(f"   Campo 5: {campo5}")
        
        # Extrair componentes
        banco = campo1[0:3]
        moeda = campo1[3:4]
        dv_geral = campo4
        vencimento = campo5[0:4]
        valor = campo5[4:14]
        
        print(f"\n📋 Componentes:")
        print(f"   Banco: {banco}")
        print(f"   Moeda: {moeda}")
        print(f"   DV Geral: {dv_geral}")
        print(f"   Fator Vencimento: {vencimento}")
        print(f"   Valor: {valor} (R$ {int(valor)/100:.2f})")
        
        # Reconstruir campo livre
        parte1 = campo1[4:9]  # 5 dígitos (sem DV)
        parte2 = campo2[0:10]  # 10 dígitos (sem DV)
        parte3 = campo3[0:10]  # 10 dígitos (sem DV)
        
        campo_livre = f"{parte1}{parte2}{parte3}"
        
        print(f"\n🔍 Campo Livre Reconstruído:")
        print(f"   Parte 1: {parte1}")
        print(f"   Parte 2: {parte2}")
        print(f"   Parte 3: {parte3}")
        print(f"   Campo Livre: {campo_livre}")
        print(f"   Tamanho: {len(campo_livre)} dígitos")
        
        if len(campo_livre) == 25:
            # Analisar campo livre SIGCB
            codigo_cedente = campo_livre[0:6]
            nosso_numero = campo_livre[6:16]
            agencia_conta = campo_livre[16:22]
            carteira = campo_livre[22:25]
            
            agencia = agencia_conta[0:4]
            conta_parte = agencia_conta[4:6]
            
            print(f"\n🔍 Análise do Campo Livre SIGCB:")
            print(f"   Código Cedente: {codigo_cedente}")
            print(f"   Nosso Número: {nosso_numero}")
            print(f"   Agência: {agencia}")
            print(f"   Conta (parte): {conta_parte}")
            print(f"   Carteira: {carteira}")
            
            # Identificar problemas
            print(f"\n❌ PROBLEMAS IDENTIFICADOS:")
            
            if codigo_cedente == "000000":
                print("   - Código do cedente é zero")
            
            if nosso_numero == "0000000000":
                print("   - Nosso número é zero")
            else:
                print(f"   - Nosso número: {nosso_numero}")
            
            if agencia == "0000":
                print("   - Agência é zero")
            else:
                print(f"   - Agência: {agencia}")
            
            if carteira not in ["001", "002", "014", "024"]:
                print(f"   - Carteira {carteira} pode não ser padrão da Caixa")
            
            # Verificar se o nosso número corresponde ao boleto
            if nosso_numero == "2043249817":
                print("   ✅ Nosso número corresponde ao boleto (2043249817)")
            else:
                print(f"   ❌ Nosso número não corresponde ao boleto (esperado: 2043249817, encontrado: {nosso_numero})")
            
            # Verificar fator de vencimento
            if vencimento == "2600":
                print("   ✅ Fator de vencimento correto (2600 = 08/11/2025)")
            else:
                print(f"   ❌ Fator de vencimento incorreto (esperado: 2600, encontrado: {vencimento})")
            
            # Verificar valor
            if valor == "0000002990":
                print("   ✅ Valor correto (R$ 29,90)")
            else:
                print(f"   ❌ Valor incorreto (esperado: 0000002990, encontrado: {valor})")
        
        # Reconstruir código de barras
        codigo_barras = f"{banco}{moeda}{dv_geral}{vencimento}{valor}{campo_livre}"
        print(f"\n🔧 Código de Barras Reconstruído:")
        print(f"   {codigo_barras}")
        print(f"   Tamanho: {len(codigo_barras)} dígitos")
        
    else:
        print("❌ Formato não reconhecido")

def gerar_codigo_correto():
    """Gera o código correto baseado nos dados do boleto"""
    
    print(f"\n" + "=" * 50)
    print("🔧 GERANDO CÓDIGO CORRETO")
    print("=" * 50)
    
    # Dados do boleto da imagem
    banco = "104"
    moeda = "9"
    fator_vencimento = "2600"  # 08/11/2025
    valor_centavos = "0000002990"  # R$ 29,90
    nosso_numero = "2043249817"
    agencia = "2946"
    conta_parte = "12"  # Primeiros 2 dígitos da conta
    carteira = "014"  # Carteira 14 formatada como 014
    
    # Código do cedente (últimos 6 dígitos do código do cedente)
    # Baseado no padrão: 267015 (últimos 6 dígitos de 1267015)
    codigo_cedente = "267015"
    
    # Montar campo livre
    campo_livre = f"{codigo_cedente}{nosso_numero}{agencia}{conta_parte}{carteira}"
    
    print(f"📋 Componentes Corretos:")
    print(f"   Código Cedente: {codigo_cedente}")
    print(f"   Nosso Número: {nosso_numero}")
    print(f"   Agência: {agencia}")
    print(f"   Conta (parte): {conta_parte}")
    print(f"   Carteira: {carteira}")
    print(f"   Campo Livre: {campo_livre}")
    
    # Calcular DV geral
    codigo_sem_dv = f"{banco}{moeda}{fator_vencimento}{valor_centavos}{campo_livre}"
    dv_geral = calcular_dv_modulo11_febraban(codigo_sem_dv)
    
    # Montar código de barras
    codigo_barras_correto = f"{banco}{moeda}{dv_geral}{fator_vencimento}{valor_centavos}{campo_livre}"
    
    print(f"\n✅ Código de Barras Correto:")
    print(f"   {codigo_barras_correto}")
    
    # Gerar linha digitável
    linha_digitavel_correta = gerar_linha_digitavel_correta(codigo_barras_correto)
    
    if linha_digitavel_correta:
        print(f"\n✅ Linha Digitável Correta:")
        print(f"   {linha_digitavel_correta}")
    else:
        print(f"\n❌ Erro ao gerar linha digitável")
        linha_digitavel_correta = ""
    
    return codigo_barras_correto, linha_digitavel_correta

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

def calcular_dv_modulo10_febraban(codigo):
    """Calcula dígito verificador módulo 10 FEBRABAN"""
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

def gerar_linha_digitavel_correta(codigo_barras):
    """Gera linha digitável correta a partir do código de barras"""
    
    if len(codigo_barras) != 44:
        return None
    
    # Extrair componentes
    banco = codigo_barras[0:3]
    moeda = codigo_barras[3:4]
    dv_geral = codigo_barras[4:5]
    vencimento = codigo_barras[5:9]
    valor = codigo_barras[9:19]
    campo_livre = codigo_barras[19:44]
    
    # Campo 1: Banco + Moeda + primeiros 5 do campo livre + DV
    campo1_base = f"{banco}{moeda}{campo_livre[0:5]}"
    dv1 = calcular_dv_modulo10_febraban(campo1_base)
    campo1 = f"{campo1_base}{dv1}"
    
    # Campo 2: Próximos 10 dígitos do campo livre + DV
    campo2_base = campo_livre[5:15]
    dv2 = calcular_dv_modulo10_febraban(campo2_base)
    campo2 = f"{campo2_base}{dv2}"
    
    # Campo 3: Últimos 10 dígitos do campo livre + DV
    campo3_base = campo_livre[15:25]
    dv3 = calcular_dv_modulo10_febraban(campo3_base)
    campo3 = f"{campo3_base}{dv3}"
    
    # Campo 4: DV geral
    campo4 = dv_geral
    
    # Campo 5: Fator vencimento + valor
    campo5 = f"{vencimento}{valor}"
    
    linha_digitavel = f"{campo1}{campo2}{campo3}{campo4}{campo5}"
    
    return linha_digitavel

def main():
    """Função principal"""
    
    analisar_codigo_problematico()
    codigo_correto, linha_correta = gerar_codigo_correto()
    
    print(f"\n" + "=" * 50)
    print("📊 COMPARAÇÃO FINAL")
    print("=" * 50)
    
    codigo_original = "10492670145204324981352946570149762600000002990"
    
    print(f"Código Original:  {codigo_original}")
    print(f"Código Corrigido: {linha_correta}")
    print(f"Diferenças:       {' '.join(['^' if a != b else ' ' for a, b in zip(codigo_original, linha_correta)])}")

if __name__ == "__main__":
    main()
