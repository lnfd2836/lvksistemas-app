#!/usr/bin/env python
"""
Script para testar geração de boletos no Heroku
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.models import ControleFinanceiro, ConfiguracaoBoleto, BoletoGerado, CobrancaAsaas
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.pdf_service import BoletoPDFService
from decimal import Decimal
from datetime import datetime
from django.utils import timezone

def testar_geracao_boleto():
    print('=== TESTE DE GERAÇÃO DE BOLETOS ===')
    
    # Buscar controle financeiro
    controle = ControleFinanceiro.objects.first()
    if not controle:
        print('❌ Nenhum controle financeiro encontrado')
        return
    
    print(f'✅ Controle: {controle.id} - {controle.loja.nome}')
    print(f'   Valor mensal: R$ {controle.valor_mensal}')
    
    # Buscar configuração do Asaas
    config = ConfiguracaoBoleto.objects.filter(codigo_banco='461', ativo=True).first()
    if not config:
        print('❌ Configuração do Asaas não encontrada')
        return
    
    print(f'✅ Configuração: {config.codigo_banco} - {config.nome_banco}')
    
    # Testar API do Asaas
    asaas_service = AsaasService()
    if not asaas_service.validar_configuracao():
        print('❌ Configuração da API inválida')
        return
    
    print('✅ Configuração da API válida')
    
    # Tentar gerar cobrança
    try:
        print('\n--- GERANDO COBRANÇA ---')
        dados_boleto = asaas_service.gerar_cobranca_com_pix(controle, dias_vencimento=30)
        
        if dados_boleto.get('success'):
            print('✅ Cobrança criada com sucesso!')
            cobranca = dados_boleto['cobranca']
            pix_data = dados_boleto.get('pix', {})
            
            print(f'   ID: {cobranca["id"]}')
            print(f'   Valor: R$ {cobranca["value"]}')
            print(f'   Status: {cobranca["status"]}')
            print(f'   Vencimento: {cobranca["dueDate"]}')
            
            if pix_data:
                print(f'   ✅ PIX gerado: {bool(pix_data.get("encodedImage"))}')
                print(f'   ✅ PIX payload: {bool(pix_data.get("payload"))}')
            else:
                print('   ❌ PIX não gerado')
            
            # Criar boleto no banco
            print('\n--- CRIANDO BOLETO NO BANCO ---')
            boleto = BoletoGerado.objects.create(
                controle_financeiro=controle,
                configuracao=config,
                numero_boleto=cobranca['id'],
                linha_digitavel=cobranca.get('bankSlipUrl', ''),
                codigo_barras=cobranca.get('bankSlipUrl', ''),
                valor=Decimal(str(cobranca['value'])),
                data_vencimento=datetime.strptime(cobranca['dueDate'], '%Y-%m-%d').date()
            )
            print(f'✅ Boleto criado: {boleto.id}')
            
            # Salvar dados do PIX
            if pix_data:
                CobrancaAsaas.objects.create(
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
                print('✅ Dados do PIX salvos')
            
            # Testar geração do PDF
            print('\n--- TESTANDO GERAÇÃO DE PDF ---')
            pdf_service = BoletoPDFService()
            try:
                pdf_response = pdf_service.gerar_pdf_boleto_asaas(boleto)
                print('✅ PDF gerado com sucesso!')
                print(f'   Tamanho: {len(pdf_response.content)} bytes')
            except Exception as e:
                print(f'❌ Erro ao gerar PDF: {str(e)}')
                import traceback
                traceback.print_exc()
            
        else:
            print(f'❌ Erro ao criar cobrança: {dados_boleto.get("error")}')
            
    except Exception as e:
        print(f'❌ Exceção: {str(e)}')
        import traceback
        traceback.print_exc()
    
    print('\n=== TESTE CONCLUÍDO ===')

if __name__ == '__main__':
    testar_geracao_boleto()
