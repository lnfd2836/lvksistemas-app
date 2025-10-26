#!/usr/bin/env python3
"""
Script para recriar a tabela CobrancaAsaas com a estrutura correta
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import connection


def recreate_cobranca_table():
    """Recria a tabela CobrancaAsaas com estrutura correta"""
    
    print("🔧 Recriando tabela CobrancaAsaas...")
    
    cursor = connection.cursor()
    
    try:
        # 1. Fazer backup dos dados existentes
        print("📋 Fazendo backup dos dados existentes...")
        cursor.execute("SELECT * FROM controle_financeiro_cobrancaasaas")
        existing_data = cursor.fetchall()
        print(f"✅ {len(existing_data)} registros encontrados")
        
        # 2. Renomear tabela atual
        print("🔄 Renomeando tabela atual...")
        cursor.execute("ALTER TABLE controle_financeiro_cobrancaasaas RENAME TO controle_financeiro_cobrancaasaas_backup")
        
        # 3. Criar nova tabela com estrutura correta
        print("🆕 Criando nova tabela...")
        create_table_sql = """
            CREATE TABLE controle_financeiro_cobrancaasaas (
                id char(32) NOT NULL PRIMARY KEY,
                asaas_id varchar(100) NOT NULL UNIQUE,
                customer_id varchar(100) NOT NULL,
                valor decimal NOT NULL,
                data_vencimento datetime NOT NULL,
                descricao TEXT NOT NULL,
                status varchar(30) NOT NULL,
                data_pagamento datetime,
                invoice_url varchar(200) DEFAULT '',
                bank_slip_url varchar(200) DEFAULT '',
                invoice_number varchar(100) DEFAULT '',
                pix_qr_code TEXT DEFAULT '',
                pix_copy_paste TEXT DEFAULT '',
                pix_expires_date datetime,
                api_response TEXT DEFAULT '{}',
                external_reference varchar(200) DEFAULT '',
                observacoes TEXT DEFAULT '',
                data_criacao datetime NOT NULL,
                data_atualizacao datetime NOT NULL,
                controle_financeiro_id bigint NOT NULL,
                FOREIGN KEY (controle_financeiro_id) REFERENCES controle_financeiro_controlefinanceiro (id)
            )
        """
        cursor.execute(create_table_sql)
        
        # 4. Restaurar dados existentes
        if existing_data:
            print("📥 Restaurando dados existentes...")
            
            insert_sql = """
                INSERT INTO controle_financeiro_cobrancaasaas (
                    id, asaas_id, customer_id, valor, data_vencimento, descricao,
                    status, data_pagamento, invoice_url, bank_slip_url, invoice_number,
                    pix_qr_code, pix_copy_paste, pix_expires_date, api_response,
                    external_reference, observacoes, data_criacao, data_atualizacao,
                    controle_financeiro_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for row in existing_data:
                # Garantir que campos opcionais tenham valores padrão
                row_list = list(row)
                
                # Índices dos campos que podem ser NULL/vazios
                optional_fields = [8, 9, 10, 11, 12, 15, 16]  # invoice_url, bank_slip_url, etc.
                
                for idx in optional_fields:
                    if row_list[idx] is None or row_list[idx] == 'None':
                        row_list[idx] = ''
                
                # api_response
                if row_list[14] is None or row_list[14] == 'None':
                    row_list[14] = '{}'
                
                cursor.execute(insert_sql, row_list)
            
            print(f"✅ {len(existing_data)} registros restaurados")
        
        # 5. Remover tabela de backup
        print("🗑️ Removendo tabela de backup...")
        cursor.execute("DROP TABLE controle_financeiro_cobrancaasaas_backup")
        
        print("✅ Tabela recriada com sucesso!")
        return True
        
    except Exception as e:
        print(f"💥 Erro: {str(e)}")
        
        # Tentar restaurar tabela original se algo deu errado
        try:
            cursor.execute("DROP TABLE IF EXISTS controle_financeiro_cobrancaasaas")
            cursor.execute("ALTER TABLE controle_financeiro_cobrancaasaas_backup RENAME TO controle_financeiro_cobrancaasaas")
            print("🔄 Tabela original restaurada")
        except:
            pass
        
        return False


def test_new_structure():
    """Testa a nova estrutura da tabela"""
    print("\n🧪 Testando nova estrutura...")
    
    try:
        from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro
        from decimal import Decimal
        from django.utils import timezone
        import uuid
        
        # Buscar um controle financeiro existente
        controle = ControleFinanceiro.objects.first()
        
        if not controle:
            print("❌ Nenhum controle financeiro encontrado para teste")
            return False
        
        # Tentar criar uma cobrança de teste
        cobranca_teste = CobrancaAsaas.objects.create(
            asaas_id='test_' + str(int(timezone.now().timestamp())),
            controle_financeiro=controle,
            customer_id='test_customer',
            valor=Decimal('10.00'),
            data_vencimento=timezone.now(),
            descricao='Teste de inserção',
            status='PENDING'
            # Não especificar campos opcionais - devem usar valores padrão
        )
        
        print("✅ Teste de inserção bem-sucedido!")
        
        # Remover o teste
        cobranca_teste.delete()
        print("🗑️ Cobrança de teste removida")
        
        return True
        
    except Exception as e:
        print(f"❌ Teste falhou: {str(e)}")
        return False


def main():
    print("🚀 Recriando tabela CobrancaAsaas com estrutura correta...")
    
    # Recriar tabela
    if recreate_cobranca_table():
        # Testar nova estrutura
        if test_new_structure():
            print("\n🎯 Recriação concluída com sucesso!")
            print("💡 Agora você pode executar o script fix_orphan_charges.py")
        else:
            print("\n⚠️ Tabela recriada, mas teste falhou")
    else:
        print("\n❌ Falha na recriação da tabela")


if __name__ == '__main__':
    main()