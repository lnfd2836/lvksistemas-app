#!/usr/bin/env python3
"""
Teste rápido do cálculo de DV dos boletos
"""

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

def testar_boleto(linha_digitavel, valor, origem):
    """Testa um boleto específico"""
    print(f"\n🔍 Testando boleto {origem} - R$ {valor}")
    print(f"Linha: {linha_digitavel}")
    
    # Extrair código de barras
    codigo_limpo = linha_digitavel.replace('.', '').replace(' ', '')
    codigo_barras = codigo_limpo
    
    print(f"Código: {codigo_barras}")
    print(f"DV atual: {codigo_barras[4]}")
    
    # Calcular DV correto
    codigo_sem_dv = codigo_barras[:4] + codigo_barras[5:]
    dv_calculado = calcular_dv_modulo11_febraban(codigo_sem_dv)
    
    print(f"DV calculado: {dv_calculado}")
    print(f"Status: {'✅ CORRETO' if codigo_barras[4] == str(dv_calculado) else '❌ INCORRETO'}")
    
    return codigo_barras[4] == str(dv_calculado)

def main():
    print("🧪 TESTE DE CÁLCULO DE DV DOS BOLETOS")
    print("="*50)
    
    # Boleto local (funciona)
    boleto_local = "10492.67014 55183.938624 92946.150148 8 22660000001990"
    resultado_local = testar_boleto(boleto_local, "19,90", "LOCAL")
    
    # Boleto Heroku (erro)
    boleto_heroku = "10492.67014 55185.752544 12946.150146 0 22660000002990"
    resultado_heroku = testar_boleto(boleto_heroku, "29,90", "HEROKU")
    
    print(f"\n{'='*50}")
    print("RESULTADO FINAL:")
    print(f"Local: {'✅ OK' if resultado_local else '❌ ERRO'}")
    print(f"Heroku: {'✅ OK' if resultado_heroku else '❌ ERRO'}")
    
    if not resultado_heroku:
        print(f"\n🚨 PROBLEMA: DV do Heroku está incorreto!")
        print("Isso indica que há uma diferença na geração entre local e Heroku.")

if __name__ == "__main__":
    main()
