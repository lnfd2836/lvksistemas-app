#!/usr/bin/env python
"""
Script para criar a loja "Controle de qualidade" e associar as cobranças
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from lojas.models import Loja
from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro, CobrancaAsaas
from usuarios.models import User
from modulos.models import TipoLoja

def criar_loja_controle_qualidade():
    """Cria a loja Controle de qualidade e associa as cobranças"""
    
    try:
        print("🏭 Criando loja 'Controle de qualidade'...")
        
        # Criar usuário para a loja
        username = "controle_qualidade"
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'controle.qualidade@exemplo.com',
                'first_name': 'Controle de Qualidade',
                'is_active': True
            }
        )
        
        if user_created:
            user.set_password('123456')
            user.save()
            print(f"✅ Usuário criado: {username}")
        else:
            print(f"✅ Usuário existente: {username}")
        
        # Buscar tipo de loja Controle de Qualidade
        tipo_loja = TipoLoja.objects.filter(nome='controle_qualidade').first()
        if not tipo_loja:
            print("❌ Tipo de loja 'Controle de Qualidade' não encontrado")
            return None
        
        # Criar loja
        loja, loja_created = Loja.objects.get_or_create(
            cnpj='24.758.458/0001-72',
            defaults={
                'admin_user': user,
                'nome': 'Controle de qualidade',
                'email': 'controle.qualidade@exemplo.com',
                'telefone': '(11) 99999-0001',
                'endereco': 'Rua da Qualidade, 123',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '01234-567',
                'status': 'ativa',
                'db_name': 'controle_qualidade_db'
            }
        )
        
        if loja_created:
            print(f"✅ Loja criada: {loja.nome}")
        else:
            print(f"✅ Loja existente: {loja.nome}")
        
        print(f"   CNPJ: {loja.cnpj}")
        print(f"   ID: {loja.id}")
        
        # Buscar plano padrão
        plano = PlanoFinanceiro.objects.filter(ativo=True).first()
        if not plano:
            print("❌ Nenhum plano ativo encontrado")
            return None
        
        # Criar controle financeiro
        controle, controle_created = ControleFinanceiro.objects.get_or_create(
            loja=loja,
            defaults={
                'plano': plano,
                'data_inicio': timezone.now(),
                'data_vencimento': timezone.now() + timedelta(days=30),
                'valor_mensal': 29.90,  # Valor das cobranças
                'status': 'ativo'
            }
        )
        
        if controle_created:
            print(f"✅ Controle financeiro criado: ID {controle.id}")
        else:
            print(f"✅ Controle financeiro existente: ID {controle.id}")
        
        # Buscar cobranças do Controle de qualidade
        cobrancas_qualidade = CobrancaAsaas.objects.filter(
            descricao__icontains='Controle de qualidade'
        )
        
        print(f"\\n📊 Encontradas {cobrancas_qualidade.count()} cobranças para associar:")
        
        # Associar cobranças ao novo controle
        for cobranca in cobrancas_qualidade:
            print(f"\\n🔄 Associando cobrança {cobranca.asaas_id}")
            print(f"   Descrição: {cobranca.descricao}")
            print(f"   Valor: R$ {cobranca.valor}")
            
            # Atualizar controle financeiro da cobrança
            cobranca.controle_financeiro = controle
            cobranca.save()
            
            print(f"   ✅ Cobrança associada à loja {loja.nome}")
        
        print(f"\\n🎉 Processo concluído!")
        print(f"📊 Resumo:")
        print(f"   - Loja: {loja.nome}")
        print(f"   - CNPJ: {loja.cnpj}")
        print(f"   - Controle: ID {controle.id}")
        print(f"   - Cobranças: {cobrancas_qualidade.count()}")
        
        print(f"\\n🌐 URLs:")
        print(f"   - Controle: https://www.lvksistemas.com.br/financeiro/controles/{controle.id}/")
        print(f"   - Cobranças: https://www.lvksistemas.com.br/financeiro/asaas/cobrancas/")
        
        return loja, controle
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    try:
        resultado = criar_loja_controle_qualidade()
        if resultado:
            print(f"\\n✅ Loja 'Controle de qualidade' criada e cobranças associadas!")
        else:
            print(f"\\n❌ Falha ao criar loja")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        sys.exit(1)