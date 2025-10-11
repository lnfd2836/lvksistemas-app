#!/usr/bin/env python3
"""
Debug profundo do algoritmo de DV
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.boleto_caixa_service import BoletoCaixaService

def debug_dv_passo_a_passo():
    """Debug do DV passo a passo"""
    
    print("=" * 80)
    print("🔍 DEBUG PROFUNDO DO ALGORITMO DE DV")
    print("=" * 80)
    
    # Código sem DV do Heroku
    codigo_sem_dv = "1049526100000029902670152113272360294615014"
    
    print(f"Código sem DV: {codigo_sem_dv}")
    print(f"Comprimento: {len(codigo_sem_dv)} dígitos")
    
    # Testar com nosso algoritmo
    servico = BoletoCaixaService()
    dv_nosso = servico._calcular_dv_codigo_barras(codigo_sem_dv)
    
    print(f"\n📊 RESULTADO NOSSO ALGORITMO:")
    print(f"   DV calculado: {dv_nosso}")
    
    # Debug passo a passo
    print(f"\n🔍 DEBUG PASSO A PASSO:")
    
    sequencia = "4329876543298765432987654329876543298765432"
    soma = 0
    
    print(f"Sequência multiplicação: {sequencia}")
    print(f"Código (reverso):        {''.join(reversed(codigo_sem_dv))}")
    
    print(f"\n📋 CÁLCULOS DETALHADOS:")
    for i, digito in enumerate(reversed(codigo_sem_dv)):
        if digito.isdigit():
            multiplicador = int(sequencia[i % len(sequencia)])
            produto = int(digito) * multiplicador
            soma += produto
            
            if i < 10:  # Mostrar apenas os primeiros 10 para não poluir
                print(f"   Pos {i:2d}: {digito} × {multiplicador} = {produto:2d} (soma: {soma})")
    
    resto = soma % 11
    
    print(f"\n📊 CÁLCULO FINAL:")
    print(f"   Soma total: {soma}")
    print(f"   Resto (soma % 11): {resto}")
    
    if resto in [0, 10, 11]:
        dv_final = 1
        print(f"   Resto {resto} → DV = 1")
    else:
        dv_temp = 11 - resto
        if dv_temp == 10:
            dv_final = 0
            print(f"   11 - {resto} = {dv_temp} → DV = 0 (regra especial)")
        else:
            dv_final = dv_temp
            print(f"   11 - {resto} = {dv_final}")
    
    print(f"   DV final: {dv_final}")
    
    return dv_final

def testar_algoritmos_alternativos():
    """Testa algoritmos alternativos de DV"""
    
    print(f"\n{'='*80}")
    print("🧪 TESTE DE ALGORITMOS ALTERNATIVOS")
    print(f"{'='*80}")
    
    codigo_sem_dv = "1049526100000029902670152113272360294615014"
    
    # Algoritmo 1: FEBRABAN padrão (nosso atual)
    dv1 = debug_dv_passo_a_passo()
    
    # Algoritmo 2: Módulo 11 sem regras especiais
    print(f"\n📊 ALGORITMO 2 - Módulo 11 simples:")
    sequencia = "4329876543298765432987654329876543298765432"
    soma = 0
    
    for i, digito in enumerate(reversed(codigo_sem_dv)):
        if digito.isdigit():
            multiplicador = int(sequencia[i % len(sequencia)])
            produto = int(digito) * multiplicador
            soma += produto
    
    resto = soma % 11
    dv2 = 11 - resto if resto != 0 else 0
    
    print(f"   Soma: {soma}, Resto: {resto}, DV: {dv2}")
    
    # Algoritmo 3: Módulo 11 com regra diferente
    print(f"\n📊 ALGORITMO 3 - Módulo 11 Caixa específico:")
    if resto in [0, 1]:
        dv3 = 0
    elif resto == 10:
        dv3 = 1
    else:
        dv3 = 11 - resto
    
    print(f"   Resto: {resto}, DV: {dv3}")
    
    # Algoritmo 4: Sequência diferente
    print(f"\n📊 ALGORITMO 4 - Sequência diferente:")
    sequencia_alt = "2345678923456789234567892345678923456789234"
    soma_alt = 0
    
    for i, digito in enumerate(reversed(codigo_sem_dv)):
        if digito.isdigit():
            multiplicador = int(sequencia_alt[i % len(sequencia_alt)])
            produto = int(digito) * multiplicador
            soma_alt += produto
    
    resto_alt = soma_alt % 11
    dv4 = 11 - resto_alt if resto_alt not in [0, 1] else 0
    
    print(f"   Soma: {soma_alt}, Resto: {resto_alt}, DV: {dv4}")
    
    print(f"\n📋 RESUMO DOS ALGORITMOS:")
    print(f"   Algoritmo 1 (FEBRABAN atual): {dv1}")
    print(f"   Algoritmo 2 (Módulo 11 simples): {dv2}")
    print(f"   Algoritmo 3 (Caixa específico): {dv3}")
    print(f"   Algoritmo 4 (Sequência diferente): {dv4}")
    print(f"   DV no código Heroku: 6")
    
    # Verificar qual bate
    dvs = [dv1, dv2, dv3, dv4]
    if 6 in dvs:
        indice = dvs.index(6) + 1
        print(f"   ✅ Algoritmo {indice} produz DV = 6!")
    else:
        print(f"   ❌ Nenhum algoritmo produz DV = 6")
    
    return dvs

def verificar_ordem_campos():
    """Verifica se a ordem dos campos está correta"""
    
    print(f"\n{'='*80}")
    print("🔍 VERIFICAÇÃO DA ORDEM DOS CAMPOS")
    print(f"{'='*80}")
    
    # Dados do código Heroku
    linha = "10492670145211327236402946150144652610000002990"
    
    # Extrair campos
    campo1 = linha[0:10]   # 1049267014
    campo2 = linha[10:21]  # 52113272364
    campo3 = linha[21:32]  # 02946150144
    campo4 = linha[32:33]  # 6
    campo5 = linha[33:47]  # 52610000002990
    
    print(f"📋 CAMPOS DA LINHA DIGITÁVEL:")
    print(f"   Campo 1: {campo1}")
    print(f"   Campo 2: {campo2}")
    print(f"   Campo 3: {campo3}")
    print(f"   Campo 4: {campo4}")
    print(f"   Campo 5: {campo5}")
    
    # Ordem atual (que estamos usando)
    banco_moeda = campo1[0:4]  # 1049
    campo_livre_p1 = campo1[4:9]  # 26701
    campo_livre_p2 = campo2[0:10]  # 5211327236
    campo_livre_p3 = campo3[0:10]  # 0294615014
    vencimento_valor = campo5  # 52610000002990
    
    vencimento = vencimento_valor[0:4]  # 5261
    valor = vencimento_valor[4:14]  # 0000002990
    campo_livre = campo_livre_p1 + campo_livre_p2 + campo_livre_p3
    
    banco = banco_moeda[0:3]
    moeda = banco_moeda[3:4]
    
    codigo_atual = banco + moeda + vencimento + valor + campo_livre
    
    print(f"\n📊 ORDEM ATUAL:")
    print(f"   Banco: {banco}")
    print(f"   Moeda: {moeda}")
    print(f"   Vencimento: {vencimento}")
    print(f"   Valor: {valor}")
    print(f"   Campo Livre: {campo_livre}")
    print(f"   Código sem DV: {codigo_atual}")
    
    # Testar DV com esta ordem
    servico = BoletoCaixaService()
    dv_atual = servico._calcular_dv_codigo_barras(codigo_atual)
    
    print(f"   DV calculado: {dv_atual}")
    print(f"   DV no código: 6")
    print(f"   Match: {'✅' if str(dv_atual) == '6' else '❌'}")

def main():
    """Função principal"""
    
    print("🚀 DEBUG PROFUNDO DO ALGORITMO DE DV")
    
    # Debug passo a passo
    dv_principal = debug_dv_passo_a_passo()
    
    # Testar algoritmos alternativos
    dvs_alternativos = testar_algoritmos_alternativos()
    
    # Verificar ordem dos campos
    verificar_ordem_campos()
    
    print(f"\n{'='*80}")
    print("📋 CONCLUSÃO DO DEBUG")
    print(f"{'='*80}")
    
    print(f"🔍 RESULTADOS:")
    print(f"   DV no código Heroku: 6")
    print(f"   DV nosso algoritmo: {dv_principal}")
    print(f"   Diferença: {6 - dv_principal}")
    
    if 6 in dvs_alternativos:
        print(f"   ✅ Um dos algoritmos alternativos produz DV = 6")
        print(f"   🔧 Pode ser necessário ajustar algoritmo")
    else:
        print(f"   ❌ Nenhum algoritmo testado produz DV = 6")
        print(f"   🔍 Problema pode estar na ordem dos campos ou especificação")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("   1. 🔍 Investigar especificação oficial SIGCB da Caixa")
    print("   2. 📞 Contatar suporte técnico da Caixa")
    print("   3. 🧪 Testar com ferramenta oficial de validação")
    print("   4. 📋 Comparar com outros geradores de boleto Caixa")

if __name__ == "__main__":
    main()