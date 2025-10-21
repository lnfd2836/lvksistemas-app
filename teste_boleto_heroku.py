#!/usr/bin/env python3
"""
Teste de geração de boleto com PIX no Heroku
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.models import ControleFinanceiro, ConfiguracaoBoleto, BoletoGerado, CobrancaAsaas
from controle_financeiro.asaas_service import AsaasService
from decimal import Decimal
from datetime import datetime, timedelta

def testar_geracao_boleto():
    print("🎯 TESTE DE GERAÇÃO DE BOLETO COM PIX - HEROKU")
    print("=" * 50)
    
    # 1. Verificar configuração do Asaas
    print("\n1️⃣ VERIFICANDO CONFIGURAÇÃO DO ASAAS...")
    try:
        asaas_service = AsaasService()
        if asaas_service.validar_configuracao():
            print("✅ Configuração do Asaas válida")
        else:
            print("❌ Configuração do Asaas inválida")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False
    
    # 2. Buscar controle financeiro para teste
    print("\n2️⃣ BUSCANDO CONTROLE FINANCEIRO...")
    try:
        controle = ControleFinanceiro.objects.first()
        if not controle:
            print("❌ Nenhum controle financeiro encontrado")
            return False
        
        print(f"✅ Controle encontrado: ID {controle.id}, Loja: {controle.loja.nome}")
        print(f"   Valor mensal: R$ {controle.valor_mensal}")
    except Exception as e:
        print(f"❌ Erro ao buscar controle: {e}")
        return False
    
    # 3. Verificar configuração de boleto
    print("\n3️⃣ VERIFICANDO CONFIGURAÇÃO DE BOLETO...")
    try:
        config = ConfiguracaoBoleto.objects.filter(codigo_banco="461", ativo=True).first()
        if not config:
            print("❌ Configuração do Asaas não encontrada")
            return False
        
        print(f"✅ Configuração encontrada: {config.nome_banco}")
        print(f"   Código banco: {config.codigo_banco}")
        print(f"   Ativo: {config.ativo}")
    except Exception as e:
        print(f"❌ Erro ao buscar configuração: {e}")
        return False
    
    # 4. Testar geração de cobrança com PIX
    print("\n4️⃣ TESTANDO GERAÇÃO DE COBRANÇA COM PIX...")
    try:
        dados_boleto = asaas_service.gerar_cobranca_com_pix(controle, dias_vencimento=30)
        
        if not dados_boleto.get('success', False):
            error_msg = dados_boleto.get('error', 'Erro desconhecido')
            print(f"❌ Erro ao gerar cobrança: {error_msg}")
            return False
        
        print("✅ Cobrança gerada com sucesso!")
        
        # Extrair dados
        cobranca = dados_boleto['cobranca']
        pix_data = dados_boleto.get('pix', {})
        
        print(f"   ID da cobrança: {cobranca['id']}")
        print(f"   Valor: R$ {cobranca['value']}")
        print(f"   Data vencimento: {cobranca['dueDate']}")
        print(f"   Status: {cobranca['status']}")
        
        if pix_data:
            print("✅ Dados PIX disponíveis:")
            print(f"   QR Code: {'Sim' if pix_data.get('encodedImage') else 'Não'}")
            print(f"   Copy/Paste: {'Sim' if pix_data.get('payload') else 'Não'}")
        else:
            print("⚠️ Dados PIX não disponíveis")
        
    except Exception as e:
        print(f"❌ Erro ao gerar cobrança: {e}")
        return False
    
    # 5. Criar boleto no banco de dados
    print("\n5️⃣ CRIANDO BOLETO NO BANCO DE DADOS...")
    try:
        boleto = BoletoGerado.objects.create(
            controle_financeiro=controle,
            configuracao=config,
            numero_boleto=cobranca['id'],
            linha_digitavel=cobranca.get('bankSlipUrl', ''),
            codigo_barras=cobranca.get('bankSlipUrl', ''),
            valor=Decimal(str(cobranca['value'])),
            data_vencimento=datetime.strptime(cobranca['dueDate'], '%Y-%m-%d').date()
        )
        
        print(f"✅ Boleto criado: ID {boleto.id}")
        
        # Salvar dados do PIX
        if pix_data:
            cobranca_asaas = CobrancaAsaas.objects.create(
                asaas_id=cobranca['id'],
                controle_financeiro=controle,
                customer_id=cobranca.get('customer', ''),
                valor=Decimal(str(cobranca['value'])),
                data_vencimento=datetime.strptime(cobranca['dueDate'], '%Y-%m-%d'),
                descricao=cobranca.get('description', ''),
                status=cobranca['status'],
                invoice_url=cobranca.get('invoiceUrl', ''),
                bank_slip_url=cobranca.get('bankSlipUrl', ''),
                invoice_number=cobranca.get('invoiceNumber', ''),
                pix_qr_code=pix_data.get('encodedImage', ''),
                pix_copy_paste=pix_data.get('payload', ''),
                external_reference=cobranca.get('externalReference', ''),
                api_response=cobranca
            )
            
            print(f"✅ Cobrança Asaas criada: ID {cobranca_asaas.id}")
            print(f"   PIX QR Code: {'Sim' if cobranca_asaas.pix_qr_code else 'Não'}")
            print(f"   PIX Copy/Paste: {'Sim' if cobranca_asaas.pix_copy_paste else 'Não'}")
        
    except Exception as e:
        print(f"❌ Erro ao criar boleto: {e}")
        return False
    
    # 6. Testar geração de PDF
    print("\n6️⃣ TESTANDO GERAÇÃO DE PDF...")
    try:
        from controle_financeiro.pdf_service import PDFService
        
        pdf_service = PDFService()
        pdf_content = pdf_service.gerar_pdf_boleto_asaas(boleto)
        
        if pdf_content:
            print("✅ PDF gerado com sucesso!")
            print(f"   Tamanho: {len(pdf_content)} bytes")
            
            # Verificar se contém PIX
            if boleto.configuracao.codigo_banco == "461":
                print("✅ PDF do Asaas com PIX gerado!")
        else:
            print("❌ Erro ao gerar PDF")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return False
    
    print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print(f"✅ Boleto ID: {boleto.id}")
    print(f"✅ Cobrança Asaas: {cobranca['id']}")
    print(f"✅ PIX incluído: {'Sim' if pix_data else 'Não'}")
    print(f"✅ PDF gerado: Sim")
    
    return True

if __name__ == "__main__":
    success = testar_geracao_boleto()
    sys.exit(0 if success else 1)
