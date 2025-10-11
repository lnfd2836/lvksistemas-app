#!/usr/bin/env python3
"""
Análise do boleto gerado após deploy v139
"""

def analisar_boleto_pos_deploy_v139():
    """Analisa o novo código gerado após deploy v139"""
    
    codigo = "10492670145211327236402946150144652610000002990"
    
    print("=" * 80)
    print("🔍 ANÁLISE PÓS-DEPLOY V139")
    print("=" * 80)
    print(f"Código: {codigo}")
    print(f"Comprimento: {len(codigo)} dígitos")
    
    if len(codigo) == 47:
        print("📝 TIPO: Linha digitável (47 dígitos)")
        
        # Extrair campos da linha digitável
        campo1 = codigo[0:10]   # 1049267014
        campo2 = codigo[10:21]  # 52113272364
        campo3 = codigo[21:32]  # 02946150144
        campo4 = codigo[32:33]  # 6
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
        campo_livre_parte2 = campo2[0:10]  # 5211327236
        campo_livre_parte3 = campo3[0:10]  # 0294615014
        dv_geral = campo4  # 6
        vencimento_valor = campo5  # 52610000002990
        
        # Separar vencimento e valor corretamente
        vencimento = vencimento_valor[0:4]  # 5261
        valor = vencimento_valor[4:14]  # 0000002990
        campo_livre = campo_livre_parte1 + campo_livre_parte2 + campo_livre_parte3
        
        # Montar código de barras correto
        banco = banco_moeda[0:3]  # 104
        moeda = banco_moeda[3:4]  # 9
        codigo_barras = banco + moeda + dv_geral + vencimento + valor + campo_livre
        
        print(f"\n🔄 CÓDIGO DE BARRAS RECONSTRUÍDO:")
        print(f"   {codigo_barras} ({len(codigo_barras)} dígitos)")
        
        if len(codigo_barras) == 44:
            # Extrair componentes
            banco_cb = codigo_barras[0:3]
            moeda_cb = codigo_barras[3:4]
            dv_cb = codigo_barras[4:5]
            vencimento_cb = codigo_barras[5:9]
            valor_cb = codigo_barras[9:19]
            campo_livre_cb = codigo_barras[19:44]
            
            print(f"\n📊 COMPONENTES DO CÓDIGO DE BARRAS:")
            print(f"   Banco: {banco_cb}")
            print(f"   Moeda: {moeda_cb}")
            print(f"   DV Geral: {dv_cb}")
            print(f"   Vencimento: {vencimento_cb}")
            print(f"   Valor: {valor_cb}")
            print(f"   Campo Livre: {campo_livre_cb} ({len(campo_livre_cb)} dígitos)")
            
            # Analisar campo livre SIGCB
            if len(campo_livre_cb) == 25:
                codigo_cedente = campo_livre_cb[0:6]
                nosso_numero = campo_livre_cb[6:16]
                agencia_complemento = campo_livre_cb[16:22]
                carteira = campo_livre_cb[22:25]
                
                agencia = agencia_complemento[0:4]
                complemento = agencia_complemento[4:6]
                
                print(f"\n🔍 ANÁLISE DO CAMPO LIVRE SIGCB:")
                print(f"   Código Cedente: {codigo_cedente}")
                print(f"   Nosso Número: {nosso_numero}")
                print(f"   Agência: {agencia}")
                print(f"   Complemento: {complemento}")
                print(f"   Carteira: {carteira}")
                
                # Verificar nossa correção
                print(f"\n🔍 VERIFICAÇÃO DA CORREÇÃO:")
                
                if len(codigo_cedente) >= 2:
                    ultimos_2_cedente = codigo_cedente[-2:]
                    print(f"   Código cedente: {codigo_cedente}")
                    print(f"   Últimos 2 dígitos do cedente: {ultimos_2_cedente}")
                    print(f"   Complemento usado: {complemento}")
                    
                    if complemento == ultimos_2_cedente:
                        print(f"   ✅ CORREÇÃO FUNCIONANDO: Complemento baseado no cedente!")
                        correcao_ativa = True
                    else:
                        print(f"   ❌ CORREÇÃO NÃO APLICADA: Complemento não é baseado no cedente")
                        correcao_ativa = False
                else:
                    print(f"   ⚠️  Código cedente muito curto: {codigo_cedente}")
                    correcao_ativa = False
                
                # Verificar DV
                print(f"\n📊 VERIFICAÇÃO DO DV:")
                codigo_sem_dv = banco + moeda + vencimento + valor + campo_livre_cb
                dv_calculado = calcular_dv_febraban(codigo_sem_dv)
                
                print(f"   Código sem DV: {codigo_sem_dv}")
                print(f"   DV no código: {dv_cb}")
                print(f"   DV calculado: {dv_calculado}")
                
                if str(dv_cb) == str(dv_calculado):
                    print(f"   ✅ DV CORRETO!")
                    dv_correto = True
                else:
                    print(f"   ❌ DV INCORRETO! Diferença: {int(dv_cb) - dv_calculado}")
                    dv_correto = False
                
                return {
                    'codigo_cedente': codigo_cedente,
                    'nosso_numero': nosso_numero,
                    'agencia': agencia,
                    'complemento': complemento,
                    'carteira': carteira,
                    'correcao_ativa': correcao_ativa,
                    'dv_correto': dv_correto,
                    'dv_informado': dv_cb,
                    'dv_calculado': dv_calculado
                }
    
    return None

def calcular_dv_febraban(codigo):
    """Calcula DV usando algoritmo FEBRABAN"""
    
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
        dv = 11 - resto
        if dv == 10:
            return 0
        return dv

def comparar_evolucao_codigos():
    """Compara a evolução dos códigos gerados"""
    
    print(f"\n{'='*80}")
    print("📈 EVOLUÇÃO DOS CÓDIGOS GERADOS")
    print(f"{'='*80}")
    
    codigos = [
        {
            'versao': 'Antes da correção',
            'codigo': '10492670145204324981352946570149762600000002990',
            'complemento': '57',
            'dv': '7',
            'status': '❌ INVÁLIDO (dados da conta)'
        },
        {
            'versao': 'Pós-deploy v138',
            'codigo': '10492670145205044404292946150143882610000002990',
            'complemento': '15',
            'dv': '8',
            'status': '❌ INVÁLIDO (DV incorreto)'
        },
        {
            'versao': 'Pós-deploy v139 (NOVO)',
            'codigo': '10492670145211327236402946150144652610000002990',
            'complemento': '15',
            'dv': '6',
            'status': '🔍 ANALISANDO...'
        }
    ]
    
    for codigo_info in codigos:
        print(f"\n📋 {codigo_info['versao']}:")
        print(f"   Complemento: {codigo_info['complemento']}")
        print(f"   DV: {codigo_info['dv']}")
        print(f"   Status: {codigo_info['status']}")
    
    print(f"\n🔍 OBSERVAÇÕES:")
    print(f"   - Complemento '15' mantido (correção ativa)")
    print(f"   - DV mudou de '8' para '6' (possível melhoria)")
    print(f"   - Precisa verificar se DV '6' está correto")

def diagnosticar_problema_persistente():
    """Diagnostica por que o problema persiste"""
    
    print(f"\n{'='*80}")
    print("🔧 DIAGNÓSTICO DO PROBLEMA PERSISTENTE")
    print(f"{'='*80}")
    
    print("📋 POSSÍVEIS CAUSAS:")
    print("   1. ❌ DV ainda sendo calculado incorretamente")
    print("   2. ❌ Algoritmo de validação da Caixa mudou")
    print("   3. ❌ Problema em outro campo (vencimento, valor, etc.)")
    print("   4. ❌ Especificação SIGCB diferente da implementada")
    print("   5. ❌ Cache do navegador ou sistema da Caixa")
    
    print(f"\n🔍 PRÓXIMAS INVESTIGAÇÕES:")
    print("   1. Verificar se DV está sendo calculado corretamente")
    print("   2. Comparar com especificação oficial SIGCB")
    print("   3. Testar com outros valores/datas")
    print("   4. Validar com ferramenta externa de boletos")
    print("   5. Contatar suporte Caixa novamente")

def main():
    """Função principal"""
    
    print("🚀 ANÁLISE PÓS-DEPLOY V139 - PROBLEMA PERSISTE")
    
    # Analisar novo código
    resultado = analisar_boleto_pos_deploy_v139()
    
    # Comparar evolução
    comparar_evolucao_codigos()
    
    # Diagnosticar problema
    diagnosticar_problema_persistente()
    
    print(f"\n{'='*80}")
    print("📋 CONCLUSÃO")
    print(f"{'='*80}")
    
    if resultado:
        print(f"✅ Campo livre: {'CORRETO' if resultado.get('correcao_ativa') else 'INCORRETO'}")
        print(f"✅ DV: {'CORRETO' if resultado.get('dv_correto') else 'INCORRETO'}")
        
        if resultado.get('correcao_ativa') and resultado.get('dv_correto'):
            print(f"\n🎉 CÓDIGO DEVERIA ESTAR VÁLIDO!")
            print(f"   - Campo livre correto (complemento baseado no cedente)")
            print(f"   - DV correto")
            print(f"   - Problema pode ser na validação da Caixa ou especificação")
        elif resultado.get('correcao_ativa') and not resultado.get('dv_correto'):
            print(f"\n❌ PROBLEMA NO DV PERSISTE!")
            print(f"   - Campo livre correto")
            print(f"   - DV ainda incorreto: {resultado.get('dv_informado')} ≠ {resultado.get('dv_calculado')}")
        else:
            print(f"\n❌ MÚLTIPLOS PROBLEMAS!")
            print(f"   - Verificar implementação completa")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    if resultado and resultado.get('correcao_ativa') and resultado.get('dv_correto'):
        print("   1. 📞 Contatar suporte Caixa com código 'válido'")
        print("   2. 🔍 Verificar se especificação SIGCB mudou")
        print("   3. 🧪 Testar com ferramenta externa")
    else:
        print("   1. 🔧 Investigar algoritmo de DV mais profundamente")
        print("   2. 📋 Comparar com especificação oficial")
        print("   3. 🧪 Testar com diferentes configurações")

if __name__ == "__main__":
    main()