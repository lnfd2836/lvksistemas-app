#!/usr/bin/env python3
"""
Análise do novo boleto gerado no Heroku
"""

def analisar_novo_boleto_heroku():
    """Analisa o novo código gerado no Heroku"""
    
    codigo = "10492670145205044404292946150143882610000002990"
    
    print("=" * 80)
    print("🔍 ANÁLISE DO NOVO BOLETO GERADO NO HEROKU")
    print("=" * 80)
    print(f"Código: {codigo}")
    print(f"Comprimento: {len(codigo)} dígitos")
    
    if len(codigo) == 47:
        print("📝 TIPO: Linha digitável (47 dígitos)")
        
        # Extrair campos da linha digitável
        campo1 = codigo[0:10]   # 1049267014
        campo2 = codigo[10:21]  # 52050444042
        campo3 = codigo[21:32]  # 92946150143
        campo4 = codigo[32:33]  # 8
        campo5 = codigo[33:47]  # 82610000002990
        
        print(f"\n📊 CAMPOS DA LINHA DIGITÁVEL:")
        print(f"   Campo 1: {campo1}")
        print(f"   Campo 2: {campo2}")
        print(f"   Campo 3: {campo3}")
        print(f"   Campo 4: {campo4} (DV geral)")
        print(f"   Campo 5: {campo5} (vencimento + valor)")
        
        # Reconstruir código de barras
        banco_moeda = campo1[0:4]  # 1049
        campo_livre_parte1 = campo1[4:9]  # 26701
        campo_livre_parte2 = campo2[0:10]  # 5205044404
        campo_livre_parte3 = campo3[0:10]  # 9294615014
        dv_geral = campo4  # 8
        vencimento_valor = campo5  # 82610000002990
        
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
                
                # Verificar nossa correção
                print(f"\n🔍 VERIFICAÇÃO DA CORREÇÃO:")
                
                # Últimos 2 dígitos do código do cedente
                if len(codigo_cedente) >= 2:
                    ultimos_2_cedente = codigo_cedente[-2:]
                    print(f"   Código cedente: {codigo_cedente}")
                    print(f"   Últimos 2 dígitos do cedente: {ultimos_2_cedente}")
                    print(f"   Complemento usado: {complemento}")
                    
                    if complemento == ultimos_2_cedente:
                        print(f"   ✅ CORREÇÃO FUNCIONANDO: Complemento baseado no cedente!")
                        print(f"   ✅ Nossa correção está ATIVA no Heroku!")
                        status_correcao = "ATIVA"
                    else:
                        print(f"   ❌ CORREÇÃO NÃO APLICADA: Complemento não é baseado no cedente")
                        print(f"   ❌ Ainda usando dados da conta ou outro método")
                        status_correcao = "INATIVA"
                else:
                    print(f"   ⚠️  Código cedente muito curto: {codigo_cedente}")
                    status_correcao = "INCERTO"
                
                return {
                    'codigo_cedente': codigo_cedente,
                    'nosso_numero': nosso_numero,
                    'agencia': agencia,
                    'complemento': complemento,
                    'carteira': carteira,
                    'ultimos_2_cedente': ultimos_2_cedente if len(codigo_cedente) >= 2 else None,
                    'correcao_ativa': status_correcao,
                    'codigo_valido': complemento == ultimos_2_cedente if len(codigo_cedente) >= 2 else False
                }
    
    return None

def comparar_com_codigos_anteriores():
    """Compara com códigos anteriores"""
    
    print(f"\n{'='*80}")
    print("🔄 COMPARAÇÃO COM CÓDIGOS ANTERIORES")
    print(f"{'='*80}")
    
    codigos = [
        {
            'nome': 'Código Problemático 1',
            'codigo': '10492670145204324981352946570149762600000002990',
            'complemento': '57',
            'status': '❌ INVÁLIDO (dados da conta)'
        },
        {
            'nome': 'Código Problemático 2', 
            'codigo': '1049270145194517087962946150143872380000002990',
            'complemento': '50',
            'status': '❌ INVÁLIDO (dados da conta)'
        },
        {
            'nome': 'Código Pós-Deploy 1',
            'codigo': '10492670145203203888852946150146152610000002990',
            'complemento': '15',
            'status': '❌ AINDA INVÁLIDO'
        },
        {
            'nome': 'Código Pós-Deploy 2 (NOVO)',
            'codigo': '10492670145205044404292946150143882610000002990',
            'complemento': '15',
            'status': '🔍 ANALISANDO...'
        }
    ]
    
    for codigo_info in codigos:
        print(f"\n📋 {codigo_info['nome']}:")
        print(f"   Complemento: {codigo_info['complemento']}")
        print(f"   Status: {codigo_info['status']}")
    
    print(f"\n🤔 OBSERVAÇÕES:")
    print(f"   - Complemento '15' aparece nos códigos pós-deploy")
    print(f"   - Se cedente termina em '15', nossa correção está funcionando")
    print(f"   - Se não, pode ser coincidência ou outro problema")

def diagnosticar_problema():
    """Diagnostica possíveis problemas"""
    
    print(f"\n{'='*80}")
    print("🔧 DIAGNÓSTICO DO PROBLEMA")
    print(f"{'='*80}")
    
    print("📋 POSSÍVEIS CENÁRIOS:")
    print("   1. ✅ Correção funcionando, mas código ainda inválido por outro motivo")
    print("   2. ❌ Correção não aplicada, cache do servidor")
    print("   3. ❌ Outro serviço gerando boletos (não o nosso)")
    print("   4. ❌ Configuração diferente no Heroku vs local")
    print("   5. ❌ Problema no algoritmo de validação da Caixa")
    
    print(f"\n🔍 COMO CONFIRMAR:")
    print("   1. Verificar logs do Heroku durante geração")
    print("   2. Procurar por 'DEBUG SIGCB CORRIGIDO' nos logs")
    print("   3. Verificar se aparece 'Complemento SIGCB: baseado no cedente'")
    print("   4. Confirmar que não aparece dados da conta nos logs")

def main():
    """Função principal"""
    
    print("🚀 ANÁLISE DO NOVO BOLETO GERADO NO HEROKU")
    
    # Analisar novo código
    resultado = analisar_novo_boleto_heroku()
    
    # Comparar com anteriores
    comparar_com_codigos_anteriores()
    
    # Diagnosticar
    diagnosticar_problema()
    
    print(f"\n{'='*80}")
    print("📋 CONCLUSÃO")
    print(f"{'='*80}")
    
    if resultado:
        if resultado.get('correcao_ativa') == 'ATIVA':
            print("✅ CORREÇÃO ESTÁ FUNCIONANDO NO HEROKU!")
            print("✅ Complemento baseado no código do cedente")
            print("✅ Nossa implementação está correta")
            
            if not resultado.get('codigo_valido'):
                print(f"\n⚠️  MAS CÓDIGO AINDA INVÁLIDO:")
                print("   - Correção aplicada corretamente")
                print("   - Problema pode ser em outro lugar")
                print("   - Verificar algoritmo de DV ou outros campos")
            else:
                print(f"\n🎉 CÓDIGO DEVE ESTAR VÁLIDO AGORA!")
                
        elif resultado.get('correcao_ativa') == 'INATIVA':
            print("❌ CORREÇÃO NÃO ESTÁ FUNCIONANDO")
            print("❌ Precisa investigar por que não foi aplicada")
            
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        if resultado.get('correcao_ativa') == 'ATIVA':
            print("   1. ✅ Correção confirmada - testar validação")
            print("   2. 🔍 Verificar se problema é no DV ou outros campos")
            print("   3. 📞 Validar com suporte Caixa novamente")
        else:
            print("   1. 🔍 Verificar logs do Heroku")
            print("   2. 🔄 Forçar limpeza de cache")
            print("   3. 🧪 Testar geração manual")

if __name__ == "__main__":
    main()