#!/usr/bin/env python3
"""
Correção do problema do DV - testar com dados reais
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.boleto_caixa_service import BoletoCaixaService
from controle_financeiro.models import ConfiguracaoBoleto, ControleFinanceiro

def testar_geracao_com_dv_correto():
    """Testa geração com DV correto"""
    
    print("=" * 80)
    print("🔧 TESTE DE GERAÇÃO COM DV CORRETO")
    print("=" * 80)
    
    try:
        # Buscar configuração real
        config = ConfiguracaoBoleto.objects.filter(codigo_banco="104").first()
        controle = ControleFinanceiro.objects.first()
        
        if not config or not controle:
            print("❌ Configuração ou controle não encontrado")
            return
        
        print(f"📋 CONFIGURAÇÃO:")
        print(f"   Agência: {config.agencia}")
        print(f"   Conta: {config.conta}")
        print(f"   Código Cedente: {config.codigo_cedente}")
        print(f"   Carteira: {config.carteira}")
        
        # Gerar boleto
        servico = BoletoCaixaService()
        resultado = servico.gerar_boleto_caixa(controle, config, dias_vencimento=30)
        
        print(f"\n✅ BOLETO GERADO:")
        print(f"   Código de barras: {resultado['codigo_barras']}")
        print(f"   Linha digitável: {resultado['linha_digitavel']}")
        print(f"   Válido: {resultado['is_valid']}")
        
        if not resultado['is_valid']:
            print(f"   ❌ Erros: {resultado.get('validation_result', {}).get('errors', [])}")
        
        # Analisar o código gerado
        codigo_barras = resultado['codigo_barras']
        
        if len(codigo_barras) == 44:
            banco = codigo_barras[0:3]
            moeda = codigo_barras[3:4]
            dv = codigo_barras[4:5]
            vencimento = codigo_barras[5:9]
            valor = codigo_barras[9:19]
            campo_livre = codigo_barras[19:44]
            
            print(f"\n🔍 ANÁLISE DO CÓDIGO GERADO:")
            print(f"   Banco: {banco}")
            print(f"   Moeda: {moeda}")
            print(f"   DV: {dv}")
            print(f"   Vencimento: {vencimento}")
            print(f"   Valor: {valor}")
            print(f"   Campo Livre: {campo_livre}")
            
            # Verificar DV
            codigo_sem_dv = f"{banco}{moeda}{vencimento}{valor}{campo_livre}"
            dv_calculado = servico._calcular_dv_codigo_barras(codigo_sem_dv)
            
            print(f"\n📊 VERIFICAÇÃO DO DV:")
            print(f"   Código sem DV: {codigo_sem_dv}")
            print(f"   DV no código: {dv}")
            print(f"   DV calculado: {dv_calculado}")
            
            if str(dv) == str(dv_calculado):
                print(f"   ✅ DV CORRETO!")
            else:
                print(f"   ❌ DV INCORRETO!")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def comparar_com_codigo_heroku():
    """Compara com o código gerado no Heroku"""
    
    print(f"\n{'='*80}")
    print("🔄 COMPARAÇÃO COM CÓDIGO HEROKU")
    print(f"{'='*80}")
    
    codigo_heroku = "10492670145205044404292946150143882610000002990"
    
    print(f"📋 CÓDIGO HEROKU (PROBLEMÁTICO):")
    print(f"   Linha: {codigo_heroku}")
    
    # Reconstruir código de barras do Heroku
    campo1 = codigo_heroku[0:10]   # 1049267014
    campo2 = codigo_heroku[10:21]  # 52050444042
    campo3 = codigo_heroku[21:32]  # 92946150143
    campo4 = codigo_heroku[32:33]  # 8
    campo5 = codigo_heroku[33:47]  # 82610000002990
    
    banco_moeda = campo1[0:4]  # 1049
    campo_livre_parte1 = campo1[4:9]  # 26701
    campo_livre_parte2 = campo2[0:10]  # 5205044404
    campo_livre_parte3 = campo3[0:10]  # 9294615014
    dv_geral = campo4  # 8
    vencimento_valor = campo5  # 82610000002990
    
    # Separar vencimento e valor corretamente
    vencimento = vencimento_valor[0:4]  # 8261
    valor = vencimento_valor[4:14]  # 0000002990
    campo_livre = campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3
    
    # Montar código correto
    banco = banco_moeda[0:3]
    moeda = banco_moeda[3:4]
    codigo_sem_dv = f"{banco}{moeda}{vencimento}{valor}{campo_livre}"
    
    # Calcular DV correto
    servico = BoletoCaixaService()
    dv_correto = servico._calcular_dv_codigo_barras(codigo_sem_dv)
    
    print(f"\n📊 ANÁLISE DO CÓDIGO HEROKU:")
    print(f"   DV no código: {dv_geral}")
    print(f"   DV correto: {dv_correto}")
    print(f"   Diferença: {int(dv_geral) - dv_correto}")
    
    if str(dv_geral) == str(dv_correto):
        print(f"   ✅ DV está correto!")
    else:
        print(f"   ❌ DV está incorreto!")
        
        # Código corrigido
        codigo_correto = f"{banco}{moeda}{dv_correto}{vencimento}{valor}{campo_livre}"
        print(f"   ✅ Código correto seria: {codigo_correto}")

def main():
    """Função principal"""
    
    print("🚀 CORREÇÃO DO PROBLEMA DO DV")
    
    # Testar geração local
    resultado_local = testar_geracao_com_dv_correto()
    
    # Comparar com Heroku
    comparar_com_codigo_heroku()
    
    print(f"\n{'='*80}")
    print("📋 CONCLUSÃO")
    print(f"{'='*80}")
    
    if resultado_local and resultado_local.get('is_valid'):
        print("✅ GERAÇÃO LOCAL FUNCIONANDO")
        print("✅ DV sendo calculado corretamente")
        print("❌ Problema pode estar no Heroku ou cache")
        
        print(f"\n🎯 AÇÕES:")
        print("   1. 🔄 Limpar cache do Heroku")
        print("   2. 🚀 Fazer novo deploy")
        print("   3. 🧪 Testar novamente")
    else:
        print("❌ PROBLEMA PERSISTE LOCALMENTE")
        print("❌ Precisa investigar mais")

if __name__ == "__main__":
    main()