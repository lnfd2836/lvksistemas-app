#!/usr/bin/env python3
"""
Teste final da correção com nosso número específico
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

def testar_correcao_final():
    """Testa a correção com o nosso número específico do boleto problemático"""
    
    print("🔧 TESTE FINAL DA CORREÇÃO")
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
    
    # Criar controle financeiro de teste (mock)
    class MockControleFinanceiro:
        def __init__(self):
            self.valor_mensal = 29.90
    
    controle_financeiro = MockControleFinanceiro()
    
    # Testar geração do boleto
    print('\n🔧 Testando geração do boleto...')
    
    try:
        service = BoletoCaixaService()
        
        # Sobrescrever o método de geração do nosso número para usar o número específico
        def gerar_nosso_numero_especifico(configuracao):
            return "2043249817"  # Nosso número específico do boleto problemático
        
        service._gerar_nosso_numero_caixa = gerar_nosso_numero_especifico
        
        resultado = service.gerar_boleto_caixa(
            controle_financeiro, 
            configuracao, 
            dias_vencimento=30
        )
        
        print('\n✅ BOLETO GERADO COM NOSSO NÚMERO ESPECÍFICO!')
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
        
        # Gerar o código correto esperado
        print(f"\n" + "=" * 50)
        print("🔧 CÓDIGO CORRETO ESPERADO")
        print("=" * 50)
        
        # Dados corretos baseados no boleto
        banco = "104"
        moeda = "9"
        fator_vencimento = "2600"  # 08/11/2025
        valor_centavos = "0000002990"  # R$ 29,90
        nosso_numero = "2043249817"
        agencia = "2946"
        conta_parte = "12"  # Primeiros 2 dígitos da conta
        carteira = "014"  # Carteira 14 formatada como 014
        codigo_cedente = "267015"  # Últimos 6 dígitos do código do cedente
        
        # Montar campo livre
        campo_livre = f"{codigo_cedente}{nosso_numero}{agencia}{conta_parte}{carteira}"
        
        # Calcular DV geral
        codigo_sem_dv = f"{banco}{moeda}{fator_vencimento}{valor_centavos}{campo_livre}"
        dv_geral = calcular_dv_modulo11_febraban(codigo_sem_dv)
        
        # Montar código de barras
        codigo_barras_correto = f"{banco}{moeda}{dv_geral}{fator_vencimento}{valor_centavos}{campo_livre}"
        
        print(f"Campo Livre: {campo_livre}")
        print(f"DV Geral: {dv_geral}")
        print(f"Código de Barras Correto: {codigo_barras_correto}")
        
        # Gerar linha digitável correta
        linha_digitavel_correta = gerar_linha_digitavel_correta(codigo_barras_correto)
        print(f"Linha Digitável Correta: {linha_digitavel_correta}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar boleto: {str(e)}")
        import traceback
        traceback.print_exc()

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

if __name__ == "__main__":
    testar_correcao_final()
