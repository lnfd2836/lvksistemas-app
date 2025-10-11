#!/usr/bin/env python3
"""
Análise do código após deploy - verificar se correção está sendo aplicada
"""

def analisar_novo_codigo_pos_deploy():
    """Analisa o código gerado após o deploy"""
    
    codigo = "10492670145203203888852946150146152610000002990"
    
    print("=" * 80)
    print("🔍 ANÁLISE DO CÓDIGO PÓS-DEPLOY")
    print("=" * 80)
    print(f"Código: {codigo}")
    print(f"Comprimento: {len(codigo)} dígitos")
    print(f"Data: 09/11/2025")
    print(f"Nosso Número: 2032038881")
    print(f"Valor: R$ 29,90")
    
    if len(codigo) == 47:
        print("📝 TIPO: Linha digitável (47 dígitos)")
        
        # Extrair campos da linha digitável
        campo1 = codigo[0:10]   # 1049267014
        campo2 = codigo[10:21]  # 52032038888
        campo3 = codigo[21:32]  # 52946150146
        campo4 = codigo[32:33]  # 1
        campo5 = codigo[33:47]  # 52610000002990
        
        print(f"\n📊 CAMPOS DA LINHA DIGITÁVEL:")
        print(f"   Campo 1: {campo1}")
        print(f"   Campo 2: {campo2}")
        print(f"   Campo 3: {campo3}")
        print(f"   Campo 4: {campo4} (DV geral)")
        print(f"   Campo 5: {campo5} (vencimento + valor)")
        
        # Reconstruir código de barras
        banco_moeda = campo1[0:4]  # 1049
        campo_livre_parte1 = campo1[4:9]  # 26701
        campo_livre_parte2 = campo2[0:10]  # 5203203888
        campo_livre_parte3 = campo3[0:10]  # 5294615014
        dv_geral = campo4  # 1
        vencimento_valor = campo5  # 52610000002990
        
        codigo_barras = banco_moeda + dv_geral + vencimento_valor + campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3
        
        print(f"\n🔄 CÓDIGO DE BARRAS RECONSTRUÍDO:")
        print(f"   {codigo_barras} ({len(codigo_barras)} dígitos)")
        
        if len(codigo_barras) == 44:
            # Extrair componentes
            banco = codigo_barras[0:3]
            moeda = codigo_barras[3:4]
            dv = codigo_barras[4:5]
            vencimento = codigo_barras[5:9]
            valor = codigo_barras[9:19]
            campo_livre = codigo_barras[19:44]
            
            print(f"\n📊 COMPONENTES DO CÓDIGO DE BARRAS:")
            print(f"   Banco: {banco} (Caixa)")
            print(f"   Moeda: {moeda} (Real)")
            print(f"   DV Geral: {dv}")
            print(f"   Vencimento: {vencimento}")
            print(f"   Valor: {valor}")
            print(f"   Campo Livre: {campo_livre} ({len(campo_livre)} dígitos)")
            
            # Analisar campo livre SIGCB
            if len(campo_livre) == 25:
                codigo_cedente = campo_livre[0:6]
                nosso_numero = campo_livre[6:16]
                agencia_complemento = campo_livre[16:22]
                carteira = campo_livre[22:25]
                
                agencia = agencia_complemento[0:4]
                complemento = agencia_complemento[4:6]
                
                print(f"\n🔍 ANÁLISE DO CAMPO LIVRE SIGCB:")
                print(f"   Código Cedente: {codigo_cedente}")
                print(f"   Nosso Número: {nosso_numero}")
                print(f"   Agência: {agencia}")
                print(f"   Complemento: {complemento}")
                print(f"   Carteira: {carteira}")
                
                # Verificar se nossa correção foi aplicada
                print(f"\n🔍 VERIFICAÇÃO DA CORREÇÃO:")
                
                # Se o cedente for 267014, os últimos 2 dígitos seriam "14"
                if codigo_cedente == "267014":
                    esperado = "14"
                    if complemento == esperado:
                        print(f"   ✅ CORREÇÃO APLICADA: Complemento '{complemento}' = últimos 2 dígitos do cedente")
                    else:
                        print(f"   ❌ CORREÇÃO NÃO APLICADA: Complemento '{complemento}' ≠ esperado '{esperado}'")
                        print(f"   ❌ AINDA USANDO DADOS DA CONTA!")
                else:
                    print(f"   ⚠️  Código cedente diferente: {codigo_cedente}")
                
                # Verificar se há padrão de conta
                if complemento in ["57", "50", "15", "14"]:
                    if complemento in ["57", "50"]:
                        print(f"   ❌ PROBLEMA: Complemento '{complemento}' parece ser dados da conta")
                    else:
                        print(f"   ✅ OK: Complemento '{complemento}' parece ser baseado no cedente")
                
                return {
                    'codigo_cedente': codigo_cedente,
                    'nosso_numero': nosso_numero,
                    'agencia': agencia,
                    'complemento': complemento,
                    'carteira': carteira,
                    'correcao_aplicada': complemento == codigo_cedente[-2:] if len(codigo_cedente) >= 2 else False
                }
    
    return None

def verificar_se_correcao_esta_ativa():
    """Verifica se nossa correção está realmente ativa no sistema"""
    
    print(f"\n{'='*80}")
    print("🔍 VERIFICANDO SE CORREÇÃO ESTÁ ATIVA")
    print(f"{'='*80}")
    
    print("📋 POSSÍVEIS CAUSAS DO PROBLEMA:")
    print("   1. ❌ Deploy não aplicou a correção")
    print("   2. ❌ Cache do servidor não foi limpo")
    print("   3. ❌ Código antigo ainda sendo usado")
    print("   4. ❌ Configuração diferente sendo usada")
    print("   5. ❌ Outro serviço gerando boletos")
    
    print(f"\n🔧 AÇÕES NECESSÁRIAS:")
    print("   1. 🔍 Verificar logs do Heroku")
    print("   2. 🔄 Reiniciar servidor novamente")
    print("   3. 🧪 Testar geração local vs produção")
    print("   4. 📋 Verificar qual serviço está sendo usado")

def comparar_com_teste_local():
    """Compara com o que testamos localmente"""
    
    print(f"\n{'='*80}")
    print("🔄 COMPARAÇÃO COM TESTE LOCAL")
    print(f"{'='*80}")
    
    print("📋 TESTE LOCAL (FUNCIONOU):")
    print("   Código cedente: 267015")
    print("   Complemento: 15 (últimos 2 dígitos do cedente)")
    print("   Status: ✅ VÁLIDO")
    
    print(f"\n📋 PRODUÇÃO (PROBLEMA):")
    print("   Código cedente: 267014")
    print("   Complemento: 15 (pode ser coincidência)")
    print("   Status: ❌ INVÁLIDO")
    
    print(f"\n🤔 ANÁLISE:")
    print("   - Códigos cedentes diferentes (267015 vs 267014)")
    print("   - Complemento igual (15) pode ser coincidência")
    print("   - Precisa verificar se correção está sendo aplicada")

def main():
    """Função principal"""
    
    print("🚀 ANÁLISE PÓS-DEPLOY - CÓDIGO AINDA INVÁLIDO")
    
    # Analisar novo código
    resultado = analisar_novo_codigo_pos_deploy()
    
    # Verificar se correção está ativa
    verificar_se_correcao_esta_ativa()
    
    # Comparar com teste local
    comparar_com_teste_local()
    
    print(f"\n{'='*80}")
    print("📋 CONCLUSÃO")
    print(f"{'='*80}")
    
    if resultado and not resultado.get('correcao_aplicada'):
        print("❌ PROBLEMA CONFIRMADO:")
        print("   - Deploy foi feito mas correção não está sendo aplicada")
        print("   - Sistema ainda gerando códigos inválidos")
        print("   - Necessário investigar mais profundamente")
        
        print(f"\n🎯 PRÓXIMOS PASSOS URGENTES:")
        print("   1. 🔍 Verificar logs do Heroku em tempo real")
        print("   2. 🔄 Forçar restart completo do servidor")
        print("   3. 🧪 Testar geração de boleto manualmente")
        print("   4. 📋 Verificar se está usando BoletoCaixaService")
        print("   5. 🚨 Investigar cache ou código antigo")
    else:
        print("⚠️  SITUAÇÃO INCERTA:")
        print("   - Precisa de mais investigação")
        print("   - Verificar se correção está realmente ativa")

if __name__ == "__main__":
    main()