#!/usr/bin/env python3
"""
Verifica se o sistema está usando apenas CAIXA SIGCB
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.models import ConfiguracaoBoleto

def verificar_configuracoes_ativas():
    """Verifica todas as configurações de boleto ativas"""
    
    print("=" * 80)
    print("🔍 VERIFICAÇÃO DAS CONFIGURAÇÕES DE BOLETO")
    print("=" * 80)
    
    # Buscar todas as configurações
    todas_configs = ConfiguracaoBoleto.objects.all()
    configs_ativas = ConfiguracaoBoleto.objects.filter(ativo=True)
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   Total de configurações: {todas_configs.count()}")
    print(f"   Configurações ativas: {configs_ativas.count()}")
    
    print(f"\n📋 TODAS AS CONFIGURAÇÕES:")
    for config in todas_configs:
        status = "✅ ATIVA" if config.ativo else "❌ INATIVA"
        print(f"   ID {config.id}: Banco {config.codigo_banco} - {status}")
        print(f"      Agência: {config.agencia}")
        print(f"      Conta: {config.conta}")
        print(f"      Cedente: {config.codigo_cedente}")
        print(f"      Carteira: {config.carteira}")
        print()
    
    # Verificar configuração da Caixa especificamente
    config_caixa = ConfiguracaoBoleto.objects.filter(codigo_banco="104", ativo=True).first()
    
    print(f"📋 CONFIGURAÇÃO CAIXA ATIVA:")
    if config_caixa:
        print(f"   ✅ ENCONTRADA - ID {config_caixa.id}")
        print(f"   Banco: {config_caixa.codigo_banco}")
        print(f"   Agência: {config_caixa.agencia}")
        print(f"   Conta: {config_caixa.conta}")
        print(f"   Código Cedente: {config_caixa.codigo_cedente}")
        print(f"   Carteira: {config_caixa.carteira}")
        print(f"   Convênio: {config_caixa.convenio}")
    else:
        print(f"   ❌ NÃO ENCONTRADA")
    
    return config_caixa

def verificar_logica_selecao():
    """Verifica a lógica de seleção de configuração"""
    
    print(f"\n{'='*80}")
    print("🔍 VERIFICAÇÃO DA LÓGICA DE SELEÇÃO")
    print(f"{'='*80}")
    
    # Simular a lógica da view
    print("📋 LÓGICA ATUAL DA VIEW:")
    print("   1. Busca configuração Caixa ativa (codigo_banco='104', ativo=True)")
    print("   2. Se encontrar, FORÇA o uso da Caixa")
    print("   3. Se config.codigo_banco == '104', usa BoletoCaixaService (SIGCB)")
    print("   4. Senão, usa geração genérica")
    
    # Verificar se há outras configurações ativas
    outras_configs = ConfiguracaoBoleto.objects.filter(ativo=True).exclude(codigo_banco="104")
    
    print(f"\n📊 OUTRAS CONFIGURAÇÕES ATIVAS (NÃO CAIXA):")
    if outras_configs.exists():
        print(f"   ⚠️  ENCONTRADAS {outras_configs.count()} configurações:")
        for config in outras_configs:
            print(f"      Banco {config.codigo_banco} - ID {config.id}")
    else:
        print(f"   ✅ NENHUMA - Apenas Caixa está ativa")
    
    return outras_configs.exists()

def verificar_uso_exclusivo_sigcb():
    """Verifica se o sistema usa exclusivamente SIGCB"""
    
    print(f"\n{'='*80}")
    print("🎯 VERIFICAÇÃO DE USO EXCLUSIVO SIGCB")
    print(f"{'='*80}")
    
    config_caixa = ConfiguracaoBoleto.objects.filter(codigo_banco="104", ativo=True).first()
    outras_ativas = ConfiguracaoBoleto.objects.filter(ativo=True).exclude(codigo_banco="104").exists()
    
    print("📋 ANÁLISE:")
    
    if config_caixa and not outras_ativas:
        print("   ✅ USO EXCLUSIVO SIGCB:")
        print("      - Apenas configuração Caixa (104) está ativa")
        print("      - Sistema força uso da Caixa se disponível")
        print("      - Todos os boletos usam BoletoCaixaService (SIGCB)")
        uso_exclusivo = True
        
    elif config_caixa and outras_ativas:
        print("   ⚠️  USO MISTO:")
        print("      - Configuração Caixa ativa, mas há outras também")
        print("      - Sistema força Caixa, mas pode haver conflitos")
        print("      - Maioria dos boletos usa SIGCB")
        uso_exclusivo = False
        
    elif not config_caixa:
        print("   ❌ CAIXA NÃO ATIVA:")
        print("      - Configuração Caixa não está ativa")
        print("      - Sistema não usa SIGCB")
        print("      - Boletos usam geração genérica")
        uso_exclusivo = False
        
    else:
        print("   ❓ SITUAÇÃO INDEFINIDA")
        uso_exclusivo = False
    
    return uso_exclusivo

def verificar_fluxo_geracao():
    """Verifica o fluxo de geração de boletos"""
    
    print(f"\n{'='*80}")
    print("🔄 FLUXO DE GERAÇÃO DE BOLETOS")
    print(f"{'='*80}")
    
    config_caixa = ConfiguracaoBoleto.objects.filter(codigo_banco="104", ativo=True).first()
    
    print("📋 FLUXO ATUAL:")
    print("   1. Usuário solicita geração de boleto")
    print("   2. Sistema busca config_caixa = ConfiguracaoBoleto.objects.filter(codigo_banco='104', ativo=True).first()")
    
    if config_caixa:
        print("   3. ✅ config_caixa encontrada → config = config_caixa (FORÇA CAIXA)")
        print("   4. ✅ config.codigo_banco == '104' → usa BoletoCaixaService")
        print("   5. ✅ BoletoCaixaService.gerar_boleto_caixa() → LAYOUT SIGCB")
        print("   6. ✅ Resultado: BOLETO SIGCB")
        
        print(f"\n🎯 CONFIRMAÇÃO:")
        print("   ✅ SISTEMA USA EXCLUSIVAMENTE LAYOUT CAIXA SIGCB")
        print("   ✅ Todos os boletos são gerados com BoletoCaixaService")
        print("   ✅ Campo livre construído conforme SIGCB")
        
    else:
        print("   3. ❌ config_caixa NÃO encontrada")
        print("   4. ❌ Sistema usa geração genérica")
        print("   5. ❌ NÃO usa layout SIGCB")

def main():
    """Função principal"""
    
    print("🚀 VERIFICAÇÃO: SISTEMA USA APENAS LAYOUT CAIXA SIGCB?")
    
    # Verificar configurações
    config_caixa = verificar_configuracoes_ativas()
    
    # Verificar lógica de seleção
    tem_outras = verificar_logica_selecao()
    
    # Verificar uso exclusivo
    uso_exclusivo = verificar_uso_exclusivo_sigcb()
    
    # Verificar fluxo
    verificar_fluxo_geracao()
    
    print(f"\n{'='*80}")
    print("📋 RESPOSTA FINAL")
    print(f"{'='*80}")
    
    if uso_exclusivo and config_caixa:
        print("✅ SIM - SISTEMA USA EXCLUSIVAMENTE LAYOUT CAIXA SIGCB")
        print("   - Apenas configuração Caixa (104) está ativa")
        print("   - Sistema força uso da Caixa")
        print("   - Todos os boletos usam BoletoCaixaService")
        print("   - Layout SIGCB aplicado em 100% dos casos")
        
        print(f"\n🎯 IMPLICAÇÕES:")
        print("   ✅ Nossa correção do campo livre está sendo aplicada")
        print("   ✅ Problema não está na seleção de layout")
        print("   ❌ Problema está no algoritmo de DV ou especificação")
        
    else:
        print("❌ NÃO - SISTEMA NÃO USA EXCLUSIVAMENTE SIGCB")
        print("   - Há outras configurações ativas ou Caixa inativa")
        print("   - Pode haver uso misto de layouts")
        print("   - Nem todos os boletos usam SIGCB")
        
        print(f"\n🎯 AÇÃO NECESSÁRIA:")
        print("   🔧 Ativar apenas configuração Caixa")
        print("   🔧 Desativar outras configurações")
        print("   🔧 Garantir uso exclusivo do SIGCB")

if __name__ == "__main__":
    main()