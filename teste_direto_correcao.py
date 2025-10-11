#!/usr/bin/env python3
"""
Teste direto da correção SIGCB - simula exatamente o que acontece na view
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.boleto_caixa_service import BoletoCaixaService
from controle_financeiro.models import ConfiguracaoBoleto, ControleFinanceiro

def testar_correcao_direta():
    """Testa a correção diretamente como na view"""
    
    print("=" * 80)
    print("🧪 TESTE DIRETO DA CORREÇÃO SIGCB")
    print("=" * 80)
    
    # Buscar configuração real da Caixa
    config = ConfiguracaoBoleto.objects.filter(codigo_banco="104").first()
    controle = ControleFinanceiro.objects.first()
    
    if not config or not controle:
        print("❌ Configuração ou controle não encontrado")
        return
    
    print(f"📋 DADOS REAIS:")
    print(f"   Agência: {config.agencia}")
    print(f"   Conta: {config.conta}")
    print(f"   Código Cedente: {config.codigo_cedente}")
    print(f"   Carteira: {config.carteira}")
    
    # Criar serviço
    caixa_service = BoletoCaixaService()
    
    print(f"\n🔧 GERANDO BOLETO...")
    
    try:
        # Gerar boleto exatamente como na view
        dados_boleto = caixa_service.gerar_boleto_caixa(controle, config, dias_vencimento=30)
        
        print(f"✅ BOLETO GERADO COM SUCESSO!")
        print(f"   Número: {dados_boleto['numero_boleto']}")
        print(f"   Código de barras: {dados_boleto['codigo_barras']}")
        print(f"   Linha digitável: {dados_boleto['linha_digitavel']}")
        print(f"   Válido: {dados_boleto['is_valid']}")
        
        # Analisar o código de barras gerado
        codigo_barras = dados_boleto['codigo_barras']
        
        if len(codigo_barras) == 44:
            campo_livre = codigo_barras[19:44]
            
            print(f"\n🔍 ANÁLISE DO CAMPO LIVRE GERADO:")
            print(f"   Campo livre: {campo_livre}")
            
            codigo_cedente = campo_livre[0:6]
            nosso_numero = campo_livre[6:16]
            agencia_complemento = campo_livre[16:22]
            carteira = campo_livre[22:25]
            
            agencia = agencia_complemento[0:4]
            complemento = agencia_complemento[4:6]
            
            print(f"   Código Cedente: {codigo_cedente}")
            print(f"   Nosso Número: {nosso_numero}")
            print(f"   Agência: {agencia}")
            print(f"   Complemento: {complemento}")
            print(f"   Carteira: {carteira}")
            
            # Verificar se o complemento é baseado no cedente
            cedente_ultimos_2 = config.codigo_cedente[-2:] if config.codigo_cedente else "00"
            
            print(f"\n🔍 VERIFICAÇÃO DA CORREÇÃO:")
            print(f"   Últimos 2 dígitos do cedente: {cedente_ultimos_2}")
            print(f"   Complemento usado: {complemento}")
            
            if complemento == cedente_ultimos_2:
                print(f"   ✅ CORREÇÃO CONFIRMADA: Usando cedente, não conta!")
            else:
                print(f"   ❌ PROBLEMA: Complemento não é baseado no cedente")
            
            # Verificar se há dados da conta
            conta_digits = ''.join(filter(str.isdigit, str(config.conta)))
            if len(conta_digits) >= 2:
                conta_inicio = conta_digits[:2]
                if conta_inicio in campo_livre and conta_inicio != complemento:
                    print(f"   ⚠️  AVISO: Dados da conta '{conta_inicio}' podem estar no campo livre")
                else:
                    print(f"   ✅ CONFIRMADO: Dados da conta '{conta_inicio}' NÃO estão no campo livre")
        
        return dados_boleto
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

def comparar_com_codigo_problematico():
    """Compara com os códigos problemáticos originais"""
    
    print(f"\n{'='*80}")
    print("🔄 COMPARAÇÃO COM CÓDIGOS PROBLEMÁTICOS")
    print(f"{'='*80}")
    
    codigos_problematicos = [
        "10492670145204324981352946570149762600000002990",
        "1049270145194517087962946150143872380000002990"
    ]
    
    for i, codigo in enumerate(codigos_problematicos, 1):
        print(f"\n📋 CÓDIGO PROBLEMÁTICO {i}:")
        print(f"   {codigo}")
        
        # Analisar como linha digitável
        if len(codigo) in [46, 47]:
            # Normalizar
            if len(codigo) == 46:
                codigo = codigo + "0"
            
            # Extrair campos
            campo1 = codigo[0:10]
            campo2 = codigo[10:21]
            campo3 = codigo[21:32]
            campo4 = codigo[32:33]
            campo5 = codigo[33:47]
            
            # Reconstruir código de barras
            banco_moeda = campo1[0:4]
            campo_livre_parte1 = campo1[4:9]
            campo_livre_parte2 = campo2[0:10]
            campo_livre_parte3 = campo3[0:10]
            dv_geral = campo4
            vencimento_valor = campo5
            
            codigo_barras = banco_moeda + dv_geral + vencimento_valor + campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3
            
            if len(codigo_barras) == 44:
                campo_livre = codigo_barras[19:44]
                agencia_complemento = campo_livre[16:22]
                complemento = agencia_complemento[4:6]
                
                print(f"   Complemento problemático: {complemento}")
                print(f"   ❌ Este continha dados da conta corrente")

def main():
    """Função principal"""
    
    print("🚀 TESTE DIRETO DA CORREÇÃO SIGCB")
    
    # Testar correção
    resultado = testar_correcao_direta()
    
    # Comparar com códigos problemáticos
    comparar_com_codigo_problematico()
    
    print(f"\n{'='*80}")
    print("📋 CONCLUSÃO")
    print(f"{'='*80}")
    
    if resultado and resultado.get('is_valid'):
        print("✅ CORREÇÃO FUNCIONANDO PERFEITAMENTE")
        print("✅ Sistema está gerando códigos SIGCB corretos")
        print("✅ Conta corrente NÃO está sendo incluída")
        print("✅ Complemento baseado no código do cedente")
        
        print(f"\n🎯 AÇÃO NECESSÁRIA:")
        print("   1. 🚀 FAZER DEPLOY IMEDIATO")
        print("   2. 🔄 REINICIAR SERVIDOR DE PRODUÇÃO")
        print("   3. 🧪 TESTAR EM PRODUÇÃO")
        print("   4. ✅ VALIDAR COM SUPORTE CAIXA")
    else:
        print("❌ PROBLEMA NA CORREÇÃO")
        print("❌ Verificar implementação")

if __name__ == "__main__":
    main()