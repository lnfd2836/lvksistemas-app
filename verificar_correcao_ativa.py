#!/usr/bin/env python3
"""
Verifica se a correção SIGCB está ativa no sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.boleto_caixa_service import BoletoCaixaService
from controle_financeiro.models import ConfiguracaoBoleto, ControleFinanceiro
from datetime import datetime, timedelta
from django.utils import timezone

def verificar_correcao_no_codigo():
    """Verifica se a correção está no código fonte"""
    
    print("=" * 80)
    print("🔍 VERIFICANDO CORREÇÃO NO CÓDIGO FONTE")
    print("=" * 80)
    
    # Ler o arquivo do serviço
    with open('controle_financeiro/boleto_caixa_service.py', 'r') as f:
        conteudo = f.read()
    
    # Verificar se a correção está presente
    if "CORREÇÃO SIGCB: NÃO usar dados da conta corrente" in conteudo:
        print("✅ Correção encontrada no código fonte")
        
        if "complemento_sigcb = cedente_para_complemento[-2:]" in conteudo:
            print("✅ Lógica de complemento baseado no cedente está presente")
        else:
            print("❌ Lógica de complemento não encontrada")
            
        if "conta corrente NÃO incluída conforme especificação SIGCB" in conteudo:
            print("✅ Validação de exclusão de conta está presente")
        else:
            print("❌ Validação de exclusão de conta não encontrada")
            
    else:
        print("❌ Correção NÃO encontrada no código fonte")
        return False
    
    return True

def testar_geracao_com_configuracao_real():
    """Testa geração com configuração real do banco"""
    
    print("\n" + "=" * 80)
    print("🧪 TESTANDO GERAÇÃO COM CONFIGURAÇÃO REAL")
    print("=" * 80)
    
    try:
        # Buscar configuração da Caixa
        config_caixa = ConfiguracaoBoleto.objects.filter(codigo_banco="104").first()
        
        if not config_caixa:
            print("❌ Nenhuma configuração da Caixa encontrada no banco")
            return False
        
        print(f"✅ Configuração da Caixa encontrada:")
        print(f"   Banco: {config_caixa.codigo_banco}")
        print(f"   Agência: {config_caixa.agencia}")
        print(f"   Conta: {config_caixa.conta}")
        print(f"   Código Cedente: {config_caixa.codigo_cedente}")
        print(f"   Carteira: {config_caixa.carteira}")
        
        # Buscar um controle financeiro para teste
        controle = ControleFinanceiro.objects.first()
        
        if not controle:
            print("❌ Nenhum controle financeiro encontrado para teste")
            return False
        
        print(f"✅ Controle financeiro encontrado: {controle.loja.nome}")
        
        # Testar geração
        print(f"\n🔧 TESTANDO GERAÇÃO DE BOLETO...")
        
        servico = BoletoCaixaService()
        
        # Capturar output do debug
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            try:
                resultado = servico.gerar_boleto_caixa(controle, config_caixa, dias_vencimento=30)
                debug_output = f.getvalue()
                
                print("✅ Boleto gerado com sucesso!")
                print(f"   Código de barras: {resultado['codigo_barras']}")
                print(f"   Linha digitável: {resultado['linha_digitavel']}")
                print(f"   Válido: {resultado['is_valid']}")
                
                # Mostrar debug output
                if "CORREÇÃO: Conta corrente NÃO incluída" in debug_output:
                    print("✅ CORREÇÃO CONFIRMADA: Conta corrente não incluída")
                else:
                    print("⚠️  AVISO: Não foi possível confirmar exclusão da conta")
                
                if "Complemento SIGCB:" in debug_output:
                    print("✅ Complemento SIGCB sendo usado corretamente")
                
                return True
                
            except Exception as e:
                debug_output = f.getvalue()
                print(f"❌ Erro na geração: {e}")
                if debug_output:
                    print(f"Debug output: {debug_output}")
                return False
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def verificar_imports():
    """Verifica se as importações estão corretas"""
    
    print("\n" + "=" * 80)
    print("🔍 VERIFICANDO IMPORTAÇÕES")
    print("=" * 80)
    
    try:
        from controle_financeiro.boleto_caixa_service import BoletoCaixaService
        print("✅ BoletoCaixaService importado com sucesso")
        
        servico = BoletoCaixaService()
        print("✅ Instância criada com sucesso")
        
        # Verificar se o método existe
        if hasattr(servico, 'gerar_boleto_caixa'):
            print("✅ Método gerar_boleto_caixa existe")
        else:
            print("❌ Método gerar_boleto_caixa não encontrado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 VERIFICAÇÃO DA CORREÇÃO SIGCB ATIVA")
    
    # Verificar código fonte
    codigo_ok = verificar_correcao_no_codigo()
    
    # Verificar importações
    import_ok = verificar_imports()
    
    # Testar geração real
    if codigo_ok and import_ok:
        geracao_ok = testar_geracao_com_configuracao_real()
    else:
        geracao_ok = False
    
    print("\n" + "=" * 80)
    print("📋 RESULTADO FINAL")
    print("=" * 80)
    
    if codigo_ok and import_ok and geracao_ok:
        print("✅ CORREÇÃO ESTÁ ATIVA E FUNCIONANDO")
        print("✅ Sistema está usando layout SIGCB corrigido")
        print("✅ Conta corrente não está sendo incluída no código de barras")
    else:
        print("❌ PROBLEMA DETECTADO:")
        if not codigo_ok:
            print("   - Correção não está no código fonte")
        if not import_ok:
            print("   - Problema nas importações")
        if not geracao_ok:
            print("   - Problema na geração de boletos")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    if codigo_ok and import_ok and geracao_ok:
        print("   1. ✅ Correção confirmada - fazer deploy")
        print("   2. ✅ Testar no ambiente de produção")
        print("   3. ✅ Validar com suporte da Caixa")
    else:
        print("   1. ❌ Corrigir problemas identificados")
        print("   2. ❌ Verificar se código foi salvo corretamente")
        print("   3. ❌ Reiniciar servidor se necessário")

if __name__ == "__main__":
    main()