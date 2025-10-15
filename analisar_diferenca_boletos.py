#!/usr/bin/env python3
"""
Análise da diferença entre boleto local e Heroku
"""

def extrair_codigo_barras(linha_digitavel):
    """Extrai o código de barras de 44 dígitos da linha digitável"""
    # Remove pontos e espaços
    codigo_limpo = linha_digitavel.replace('.', '').replace(' ', '')
    
    # Extrai os campos
    campo1 = codigo_limpo[:10]  # 1049267014
    campo2 = codigo_limpo[10:21]  # 55183938624
    campo3 = codigo_limpo[21:32]  # 92946150148
    dv_geral = codigo_limpo[32]  # 8 ou 0
    campo4 = codigo_limpo[33:]  # 22660000001990 ou 22660000002990
    
    # Reconstrói o código de barras
    codigo_barras = campo1 + campo2 + campo3 + dv_geral + campo4
    
    return codigo_barras, dv_geral

def calcular_dv_modulo11_febraban(codigo):
    """Calcula DV usando módulo 11 FEBRABAN"""
    soma = 0
    peso = 2
    
    # Multiplica cada dígito pela sequência de pesos (da direita para esquerda)
    for digito in reversed(codigo):
        if digito.isdigit():
            soma += int(digito) * peso
            peso += 1
            if peso > 9:
                peso = 2
    
    resto = soma % 11
    if resto in [0, 10, 11]:
        return 1
    else:
        dv = 11 - resto
        if dv == 10:
            return 0
        return dv

def analisar_boleto(linha_digitavel, valor, origem):
    """Analisa um boleto específico"""
    print(f"\n{'='*60}")
    print(f"ANÁLISE DO BOLETO {origem.upper()} - R$ {valor}")
    print(f"{'='*60}")
    
    # Extrair código de barras
    codigo_barras, dv_atual = extrair_codigo_barras(linha_digitavel)
    
    print(f"Linha digitável: {linha_digitavel}")
    print(f"Código de barras: {codigo_barras}")
    print(f"DV atual: {dv_atual}")
    
    # Calcular DV correto
    codigo_sem_dv = codigo_barras[:4] + codigo_barras[5:]  # Remove DV da posição 5
    dv_calculado = calcular_dv_modulo11_febraban(codigo_sem_dv)
    
    print(f"DV calculado: {dv_calculado}")
    print(f"DV está correto: {'✅ SIM' if str(dv_atual) == str(dv_calculado) else '❌ NÃO'}")
    
    # Analisar campos
    print(f"\nAnálise dos campos:")
    print(f"Campo 1: {codigo_barras[:10]} (Banco: {codigo_barras[:3]}, Moeda: {codigo_barras[3]}, DV: {codigo_barras[4]})")
    print(f"Campo 2: {codigo_barras[5:15]} (Vencimento: {codigo_barras[5:9]}, Valor: {codigo_barras[9:19]})")
    print(f"Campo 3: {codigo_barras[15:25]} (Campo livre: {codigo_barras[15:25]})")
    print(f"Campo 4: {codigo_barras[25:35]} (Campo livre: {codigo_barras[25:35]})")
    print(f"Campo 5: {codigo_barras[35:44]} (Campo livre: {codigo_barras[35:44]})")
    
    return {
        'codigo_barras': codigo_barras,
        'dv_atual': dv_atual,
        'dv_calculado': dv_calculado,
        'correto': str(dv_atual) == str(dv_calculado)
    }

def main():
    # Boleto local (funciona)
    boleto_local = "10492.67014 55183.938624 92946.150148 8 22660000001990"
    
    # Boleto Heroku (erro)
    boleto_heroku = "10492.67014 55185.752544 12946.150146 0 22660000002990"
    
    print("🔍 ANÁLISE COMPARATIVA DE BOLETOS")
    print("="*60)
    
    # Analisar boleto local
    resultado_local = analisar_boleto(boleto_local, "19,90", "LOCAL")
    
    # Analisar boleto Heroku
    resultado_heroku = analisar_boleto(boleto_heroku, "29,90", "HEROKU")
    
    # Comparação
    print(f"\n{'='*60}")
    print("COMPARAÇÃO")
    print(f"{'='*60}")
    
    print(f"Boleto Local - DV correto: {'✅ SIM' if resultado_local['correto'] else '❌ NÃO'}")
    print(f"Boleto Heroku - DV correto: {'✅ SIM' if resultado_heroku['correto'] else '❌ NÃO'}")
    
    if not resultado_heroku['correto']:
        print(f"\n🚨 PROBLEMA IDENTIFICADO:")
        print(f"DV do Heroku está incorreto!")
        print(f"DV atual: {resultado_heroku['dv_atual']}")
        print(f"DV correto: {resultado_heroku['dv_calculado']}")
        
        # Mostrar código corrigido
        codigo_corrigido = resultado_heroku['codigo_barras'][:4] + str(resultado_heroku['dv_calculado']) + resultado_heroku['codigo_barras'][5:]
        print(f"\nCódigo de barras corrigido: {codigo_corrigido}")
        
        # Reconstruir linha digitável corrigida
        codigo_limpo = codigo_corrigido
        linha_corrigida = f"{codigo_limpo[:5]}.{codigo_limpo[5:10]} {codigo_limpo[10:15]}.{codigo_limpo[15:20]}.{codigo_limpo[20:25]} {codigo_limpo[25:30]}.{codigo_limpo[30:35]}.{codigo_limpo[35:40]} {codigo_limpo[40]} {codigo_limpo[41:]}"
        print(f"Linha digitável corrigida: {linha_corrigida}")

if __name__ == "__main__":
    main()
