#!/usr/bin/env python3
"""
Validação específica do código gerado no Heroku
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.boleto_caixa_service import BoletoCaixaService

def validar_codigo_especifico():
    """Valida o código específico gerado no Heroku"""
    
    codigo_linha = "10492670145205044404292946150143882610000002990"
    
    print("=" * 80)
    print("🔍 VALIDAÇÃO ESPECÍFICA DO CÓDIGO HEROKU")
    print("=" * 80)
    print(f"Linha digitável: {codigo_linha}")
    
    # Reconstruir código de barras
    campo1 = codigo_linha[0:10]   # 1049267014
    campo2 = codigo_linha[10:21]  # 52050444042
    campo3 = codigo_linha[21:32]  # 92946150143
    campo4 = codigo_linha[32:33]  # 8
    campo5 = codigo_linha[33:47]  # 82610000002990
    
    # Montar código de barras
    banco_moeda = campo1[0:4]  # 1049
    campo_livre_parte1 = campo1[4:9]  # 26701
    campo_livre_parte2 = campo2[0:10]  # 5205044404
    campo_livre_parte3 = campo3[0:10]  # 9294615014
    dv_geral = campo4  # 8
    vencimento_valor = campo5  # 82610000002990
    
    codigo_barras = banco_moeda + dv_geral + vencimento_valor + campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3
    
    print(f"Código de barras: {codigo_barras}")
    print(f"Comprimento: {len(codigo_barras)} dígitos")
    
    # Validar usando nosso serviço
    print(f"\n🔧 VALIDANDO COM NOSSO SERVIÇO...")
    
    try:
        servico = BoletoCaixaService()
        
        # Testar validação do código de barras
        resultado_barras = servico.validar_boleto_existente(codigo_barras)
        
        print(f"✅ Validação código de barras:")
        print(f"   Válido: {resultado_barras.is_valid}")
        if not resultado_barras.is_valid:
            print(f"   Erros: {resultado_barras.errors}")
        if resultado_barras.warnings:
            print(f"   Avisos: {resultado_barras.warnings}")
        
        # Testar validação da linha digitável
        resultado_linha = servico.validar_boleto_existente(codigo_barras, codigo_linha)
        
        print(f"\n✅ Validação linha digitável:")
        print(f"   Válido: {resultado_linha.is_valid}")
        if not resultado_linha.is_valid:
            print(f"   Erros: {resultado_linha.errors}")
        if resultado_linha.warnings:
            print(f"   Avisos: {resultado_linha.warnings}")
        
        return resultado_barras.is_valid and resultado_linha.is_valid
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def testar_dv_manualmente():
    """Testa o cálculo do DV manualmente"""
    
    print(f"\n{'='*80}")
    print("🔧 TESTE MANUAL DO DÍGITO VERIFICADOR")
    print(f"{'='*80}")
    
    # Código sem DV
    codigo_sem_dv = "104982610000002990267015205044404929461501"
    
    print(f"Código sem DV: {codigo_sem_dv}")
    print(f"Comprimento: {len(codigo_sem_dv)} dígitos")
    
    # Calcular DV usando nosso algoritmo
    try:
        servico = BoletoCaixaService()
        dv_calculado = servico._calcular_dv_codigo_barras(codigo_sem_dv)
        
        print(f"\n📊 CÁLCULO DO DV:")
        print(f"   DV calculado: {dv_calculado}")
        print(f"   DV no código: 8")
        
        if str(dv_calculado) == "8":
            print(f"   ✅ DV CORRETO!")
        else:
            print(f"   ❌ DV INCORRETO! Esperado: {dv_calculado}, Atual: 8")
            
        return str(dv_calculado) == "8"
        
    except Exception as e:
        print(f"❌ Erro no cálculo do DV: {e}")
        return False

def verificar_campo_livre():
    """Verifica se o campo livre está correto"""
    
    print(f"\n{'='*80}")
    print("🔍 VERIFICAÇÃO DO CAMPO LIVRE")
    print(f"{'='*80}")
    
    campo_livre = "2670152050444049294615014"
    
    print(f"Campo livre: {campo_livre}")
    print(f"Comprimento: {len(campo_livre)} dígitos")
    
    # Analisar componentes
    codigo_cedente = campo_livre[0:6]    # 267015
    nosso_numero = campo_livre[6:16]     # 2050444049
    agencia_compl = campo_livre[16:22]   # 294615
    carteira = campo_livre[22:25]        # 014
    
    agencia = agencia_compl[0:4]         # 2946
    complemento = agencia_compl[4:6]     # 15
    
    print(f"\n📊 COMPONENTES:")
    print(f"   Código Cedente: {codigo_cedente}")
    print(f"   Nosso Número: {nosso_numero}")
    print(f"   Agência: {agencia}")
    print(f"   Complemento: {complemento}")
    print(f"   Carteira: {carteira}")
    
    # Verificar nossa correção
    ultimos_2_cedente = codigo_cedente[-2:]
    
    print(f"\n✅ VERIFICAÇÃO DA CORREÇÃO:")
    print(f"   Últimos 2 dígitos do cedente: {ultimos_2_cedente}")
    print(f"   Complemento usado: {complemento}")
    
    if complemento == ultimos_2_cedente:
        print(f"   ✅ CORREÇÃO APLICADA CORRETAMENTE!")
        return True
    else:
        print(f"   ❌ CORREÇÃO NÃO APLICADA!")
        return False

def main():
    """Função principal"""
    
    print("🚀 VALIDAÇÃO ESPECÍFICA DO CÓDIGO HEROKU")
    
    # Validar código completo
    codigo_valido = validar_codigo_especifico()
    
    # Testar DV manualmente
    dv_correto = testar_dv_manualmente()
    
    # Verificar campo livre
    campo_livre_ok = verificar_campo_livre()
    
    print(f"\n{'='*80}")
    print("📋 RESULTADO FINAL")
    print(f"{'='*80}")
    
    print(f"✅ Campo livre correto: {campo_livre_ok}")
    print(f"✅ DV correto: {dv_correto}")
    print(f"✅ Código válido: {codigo_valido}")
    
    if campo_livre_ok and dv_correto and codigo_valido:
        print(f"\n🎉 CÓDIGO DEVERIA ESTAR VÁLIDO!")
        print(f"   - Nossa correção está funcionando")
        print(f"   - DV está correto")
        print(f"   - Problema pode ser na validação da Caixa")
    elif campo_livre_ok and not dv_correto:
        print(f"\n❌ PROBLEMA NO DÍGITO VERIFICADOR!")
        print(f"   - Campo livre correto")
        print(f"   - DV incorreto - precisa corrigir algoritmo")
    elif not campo_livre_ok:
        print(f"\n❌ PROBLEMA NO CAMPO LIVRE!")
        print(f"   - Correção não aplicada corretamente")
    else:
        print(f"\n❌ PROBLEMA DESCONHECIDO!")
        print(f"   - Precisa investigar mais")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    if codigo_valido:
        print("   1. 📞 Entrar em contato com suporte Caixa")
        print("   2. 🔍 Verificar se há mudanças na especificação")
        print("   3. 🧪 Testar com outros bancos")
    else:
        print("   1. 🔧 Corrigir algoritmo de DV se necessário")
        print("   2. 🔍 Verificar outros componentes do código")
        print("   3. 🧪 Testar com configuração diferente")

if __name__ == "__main__":
    main()