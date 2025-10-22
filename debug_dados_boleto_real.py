#!/usr/bin/env python3
"""
Debug dos Dados Reais do Boleto
Simula exatamente os dados que seu sistema está enviando
"""

import os
import sys
import django
from pathlib import Path
import json
from datetime import datetime, timedelta

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

try:
    django.setup()
    
    from controle_financeiro.asaas_service import AsaasService
    from controle_financeiro.models import ControleFinanceiro
    from django.utils import timezone
    
    def debug_dados_reais():
        """Debug com dados reais do sistema"""
        print("🔍 DEBUG DOS DADOS REAIS DO BOLETO")
        print("=" * 60)
        print(f"⏰ Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Busca um controle financeiro para teste (ID 67 mencionado na URL)
        try:
            controle = ControleFinanceiro.objects.get(id=67)
            print(f"✅ Controle Financeiro encontrado: ID {controle.id}")
            print(f"🏪 Loja: {controle.loja.nome}")
            print(f"📋 Plano: {controle.plano.nome}")
            print(f"💰 Valor: R$ {controle.valor_mensal}")
        except ControleFinanceiro.DoesNotExist:
            print("❌ Controle Financeiro ID 67 não encontrado")
            print("📋 Controles disponíveis:")
            for cf in ControleFinanceiro.objects.all()[:5]:
                print(f"  - ID {cf.id}: {cf.loja.nome} - R$ {cf.valor_mensal}")
            
            # Usa o primeiro disponível
            controle = ControleFinanceiro.objects.first()
            if not controle:
                print("❌ Nenhum controle financeiro encontrado")
                return False
            
            print(f"🔄 Usando controle ID {controle.id} para teste")
        
        # Inicializa o serviço Asaas
        asaas_service = AsaasService()
        
        print(f"\n🔧 CONFIGURAÇÕES ASAAS:")
        print(f"🔑 API Key: {asaas_service.api_key[:20] if asaas_service.api_key else 'NÃO CONFIGURADA'}...")
        print(f"🌐 Ambiente: {asaas_service.environment}")
        print(f"📡 URL Base: {asaas_service.base_url}")
        
        # Testa validação da configuração
        print(f"\n🔗 Testando configuração...")
        try:
            config_valida = asaas_service.validar_configuracao()
            if config_valida:
                print("✅ Configuração válida")
            else:
                print("❌ Configuração inválida")
                return False
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False
        
        # Simula criação do cliente
        print(f"\n👤 DADOS DO CLIENTE (LOJA):")
        loja = controle.loja
        print(f"📛 Nome: {loja.nome}")
        print(f"📧 Email: {loja.email}")
        print(f"📱 Telefone: {loja.telefone}")
        print(f"🆔 CNPJ: {loja.cnpj}")
        print(f"📍 Endereço: {loja.endereco}")
        print(f"🏙️ Cidade: {loja.cidade}")
        print(f"🗺️ Estado: {loja.estado}")
        print(f"📮 CEP: {loja.cep}")
        
        # Simula os dados que seriam enviados para criar cliente
        cliente_data = {
            'name': loja.nome,
            'email': loja.email,
            'phone': asaas_service._limpar_telefone(loja.telefone),
            'mobilePhone': asaas_service._limpar_telefone(loja.telefone),
            'cpfCnpj': asaas_service._limpar_cnpj(loja.cnpj),
            'postalCode': asaas_service._limpar_cep(loja.cep),
            'address': loja.endereco,
            'addressNumber': asaas_service._extrair_numero_endereco(loja.endereco),
            'complement': '',
            'province': loja.cidade,
            'city': loja.cidade,
            'state': loja.estado,
            'country': 'Brasil',
            'externalReference': str(loja.id),
            'notificationDisabled': False,
            'additionalEmails': '',
            'municipalInscription': '',
            'stateInscription': '',
            'observations': f'Cliente criado automaticamente - Sistema LVK - Loja ID: {loja.id}'
        }
        
        print(f"\n📤 DADOS DO CLIENTE PARA ASAAS:")
        print(json.dumps(cliente_data, indent=2, ensure_ascii=False))
        
        # Verifica problemas nos dados do cliente
        problemas_cliente = []
        
        if not cliente_data['name']:
            problemas_cliente.append("Nome vazio")
        if not cliente_data['email']:
            problemas_cliente.append("Email vazio")
        if not cliente_data['cpfCnpj']:
            problemas_cliente.append("CNPJ vazio")
        elif len(cliente_data['cpfCnpj']) not in [11, 14]:
            problemas_cliente.append(f"CNPJ com tamanho inválido: {len(cliente_data['cpfCnpj'])}")
        
        if problemas_cliente:
            print(f"\n❌ PROBLEMAS NO CLIENTE:")
            for problema in problemas_cliente:
                print(f"  - {problema}")
        else:
            print(f"\n✅ Dados do cliente parecem válidos")
        
        # Simula os dados da cobrança
        data_vencimento = timezone.now().date() + timedelta(days=30)
        descricao = f"Mensalidade {controle.plano.nome} - {controle.loja.nome}"
        
        # Simula um customer_id (normalmente seria retornado pela criação do cliente)
        customer_id = "cus_000005928840"  # ID de exemplo
        
        cobranca_data = {
            'customer': customer_id,
            'billingType': 'BOLETO',
            'value': float(controle.valor_mensal),
            'dueDate': data_vencimento.strftime('%Y-%m-%d'),
            'description': descricao,
            'externalReference': f"CF_{controle.id}_{int(timezone.now().timestamp())}",
            
            # Configurações do boleto
            'installmentCount': 1,
            'installmentValue': float(controle.valor_mensal),
            
            # Multa e juros
            'fine': {
                'value': 2.00,
                'type': 'PERCENTAGE'
            },
            'interest': {
                'value': 1.00,
                'type': 'PERCENTAGE'
            },
            
            # Desconto
            'discount': {
                'value': 0.00,
                'dueDateLimitDays': 0,
                'type': 'PERCENTAGE'
            },
            
            # Configurações de notificação
            'postalService': False,
        }
        
        print(f"\n📄 DADOS DA COBRANÇA:")
        print(json.dumps(cobranca_data, indent=2, ensure_ascii=False))
        
        # Analisa problemas nos dados da cobrança
        problemas_cobranca = []
        
        if not cobranca_data['customer']:
            problemas_cobranca.append("Customer ID vazio")
        elif not cobranca_data['customer'].startswith('cus_'):
            problemas_cobranca.append("Customer ID não tem formato válido")
        
        if cobranca_data['value'] <= 0:
            problemas_cobranca.append("Valor deve ser maior que zero")
        elif cobranca_data['value'] < 5.00:
            problemas_cobranca.append("Valor mínimo é R$ 5,00")
        
        try:
            due_date = datetime.strptime(cobranca_data['dueDate'], '%Y-%m-%d')
            if due_date.date() < datetime.now().date():
                problemas_cobranca.append("Data de vencimento no passado")
        except ValueError:
            problemas_cobranca.append("Formato de data inválido")
        
        # Verifica campos problemáticos
        campos_problematicos = []
        
        if 'installmentCount' in cobranca_data and cobranca_data['installmentCount'] != 1:
            campos_problematicos.append("installmentCount diferente de 1 pode causar problemas")
        
        if 'installmentValue' in cobranca_data and cobranca_data['installmentValue'] != cobranca_data['value']:
            campos_problematicos.append("installmentValue diferente de value pode causar problemas")
        
        if problemas_cobranca:
            print(f"\n❌ PROBLEMAS NA COBRANÇA:")
            for problema in problemas_cobranca:
                print(f"  - {problema}")
        
        if campos_problematicos:
            print(f"\n⚠️ CAMPOS POTENCIALMENTE PROBLEMÁTICOS:")
            for problema in campos_problematicos:
                print(f"  - {problema}")
        
        if not problemas_cobranca and not campos_problematicos:
            print(f"\n✅ Dados da cobrança parecem válidos")
        
        # Sugestões de correção
        print(f"\n🔧 SUGESTÕES PARA RESOLVER ERRO 400:")
        print("1. REMOVER campos opcionais que podem causar conflito:")
        print("   - installmentCount (deixar apenas para parcelado)")
        print("   - installmentValue (deixar apenas para parcelado)")
        print("   - fine, interest, discount (se não necessários)")
        
        print("\n2. DADOS MÍNIMOS para teste:")
        dados_minimos = {
            'customer': customer_id,
            'billingType': 'BOLETO',
            'value': float(controle.valor_mensal),
            'dueDate': data_vencimento.strftime('%Y-%m-%d'),
            'description': descricao,
            'postalService': False
        }
        print(json.dumps(dados_minimos, indent=2, ensure_ascii=False))
        
        print("\n3. VERIFICAR se o cliente existe antes de criar cobrança")
        print("4. TESTAR com dados mínimos primeiro")
        print("5. ADICIONAR campos extras gradualmente")
        
        return True
        
    # Executa o debug
    if debug_dados_reais():
        print("\n✅ Debug concluído com sucesso!")
    else:
        print("\n❌ Debug falhou!")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Execute este script no diretório do projeto Django")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()