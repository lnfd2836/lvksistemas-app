#!/usr/bin/env python3
"""
Teste específico para o boleto problemático
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.boleto_caixa_service import BoletoCaixaService
from controle_financeiro.models import ConfiguracaoBoleto
from datetime import datetime, timedelta
from django.utils import timezone

def testar_boleto_problematico():
    """Testa o boleto específico que está com problema"""
    
    print("🔧 TESTE DO BOLETO PROBLEMÁTICO")
    print("=" * 50)
    
    # Criar configuração baseada nos dados do boleto problemático
    configuracao = ConfiguracaoBoleto(
        nome_banco="Caixa Econômica Federal",
        codigo_banco="104",
        agencia="2946",
        conta="1267015",  # Código do cedente completo
        carteira="14",
        codigo_cedente="1267015",
        convenio="1267015",
        nome_beneficiario="FELIX REPRESENTAÇÕES",
        cnpj_beneficiario="00.000.000/0001-00",
        endereco_beneficiario="Rua Teste, 123 - Centro - Ribeirão Preto/SP - CEP: 14030-400",
        instrucoes="Não receber após o vencimento. Em caso de dúvidas, entre em contato conosco.",
        multa=2.00,
        juros=5.00,
        desconto=0.00,
        ativo=True
    )
    
    print(f"✅ Configuração criada:")
    print(f"   Agência: {configuracao.agencia}")
    print(f"   Conta: {configuracao.conta}")
    print(f"   Carteira: {configuracao.carteira}")
    print(f"   Código Cedente: {configuracao.codigo_cedente}")
    
    # Criar controle financeiro de teste (mock)
    class MockControleFinanceiro:
        def __init__(self):
            self.valor_mensal = 29.90
    
    controle_financeiro = MockControleFinanceiro()
    
    # Testar geração do boleto
    print('\n🔧 Testando geração do boleto...')
    
    try:
        service = BoletoCaixaService()
        resultado = service.gerar_boleto_caixa(
            controle_financeiro, 
            configuracao, 
            dias_vencimento=30
        )
        
        print('\n✅ BOLETO GERADO!')
        print('=' * 50)
        print(f"📋 Número do Boleto: {resultado['numero_boleto']}")
        print(f"💰 Valor: R$ {resultado['valor']:.2f}")
        print(f"📅 Vencimento: {resultado['data_vencimento'].strftime('%d/%m/%Y')}")
        print(f"🔢 Fator Vencimento: {resultado['fator_vencimento']}")
        
        print(f"\n📊 CÓDIGO DE BARRAS:")
        print(f"   {resultado['codigo_barras']}")
        
        print(f"\n📊 LINHA DIGITÁVEL:")
        print(f"   {resultado['linha_digitavel']}")
        
        # Comparar com o código problemático
        print(f"\n" + "=" * 50)
        print("📊 COMPARAÇÃO COM CÓDIGO PROBLEMÁTICO")
        print("=" * 50)
        
        codigo_problematico = "10492670145204324981352946570149762600000002990"
        
        print(f"Código Problemático: {codigo_problematico}")
        print(f"Código Gerado:       {resultado['linha_digitavel']}")
        
        # Verificar se o nosso número está correto
        nosso_numero_esperado = "2043249817"
        if resultado['numero_boleto'] == nosso_numero_esperado:
            print(f"✅ Nosso número correto: {resultado['numero_boleto']}")
        else:
            print(f"❌ Nosso número incorreto: esperado {nosso_numero_esperado}, gerado {resultado['numero_boleto']}")
        
        # Verificar fator de vencimento
        if resultado['fator_vencimento'] == "2600":
            print(f"✅ Fator de vencimento correto: {resultado['fator_vencimento']}")
        else:
            print(f"❌ Fator de vencimento incorreto: esperado 2600, gerado {resultado['fator_vencimento']}")
        
        # Verificar valor
        if resultado['valor'] == 29.90:
            print(f"✅ Valor correto: R$ {resultado['valor']:.2f}")
        else:
            print(f"❌ Valor incorreto: esperado R$ 29.90, gerado R$ {resultado['valor']:.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar boleto: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_boleto_problematico()
