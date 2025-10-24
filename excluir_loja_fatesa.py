#!/usr/bin/env python
"""
Script específico para excluir a loja FATESA - Demo problemática
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import transaction
from lojas.models import Loja, Cliente, Produto, Venda, Funcionario
from dashboard.models import Notificacao
import logging

logger = logging.getLogger(__name__)


def excluir_loja_fatesa():
    """Exclui especificamente a loja FATESA - Demo"""
    print("🗑️  EXCLUINDO LOJA FATESA - DEMO")
    print("=" * 50)
    
    try:
        # Buscar a loja FATESA - Demo
        loja = Loja.objects.filter(nome='FATESA - Demo').first()
        
        if not loja:
            print("❌ Loja 'FATESA - Demo' não encontrada")
            return False
        
        print(f"✅ Loja encontrada: {loja.nome}")
        print(f"   ID: {loja.id}")
        print(f"   Admin: {loja.admin_user.username if loja.admin_user else 'Nenhum'}")
        print(f"   Status: {loja.status}")
        
        with transaction.atomic():
            nome_loja = loja.nome
            admin_user = loja.admin_user
            
            # Coletar estatísticas
            stats = {
                'clientes': Cliente.objects.filter(loja=loja).count(),
                'produtos': Produto.objects.filter(loja=loja).count(),
                'vendas': Venda.objects.filter(loja=loja).count(),
                'funcionarios': Funcionario.objects.filter(loja=loja).count(),
                'notificacoes': Notificacao.objects.filter(loja=loja).count(),
            }
            
            print(f"\n📊 Dados encontrados:")
            for key, value in stats.items():
                print(f"   - {value} {key}")
            
            # 1. Limpar notificações da loja
            notificacoes_removidas = Notificacao.objects.filter(loja=loja).delete()[0]
            print(f"✅ {notificacoes_removidas} notificações removidas")
            
            # 2. Limpar controle financeiro
            try:
                from controle_financeiro.models import ControleFinanceiro
                controle_removido = ControleFinanceiro.objects.filter(loja=loja).delete()[0]
                print(f"✅ {controle_removido} controles financeiros removidos")
            except ImportError:
                print("📋 Módulo controle_financeiro não encontrado")
            except Exception as e:
                print(f"⚠️  Erro ao remover controle financeiro: {e}")
            
            # 3. Limpar itens de venda
            try:
                from lojas.models import ItemVenda
                itens_removidos = ItemVenda.objects.filter(venda__loja=loja).delete()[0]
                print(f"✅ {itens_removidos} itens de venda removidos")
            except Exception as e:
                print(f"⚠️  Erro ao remover itens de venda: {e}")
            
            # 4. Limpar vendas
            vendas_removidas = Venda.objects.filter(loja=loja).delete()[0]
            print(f"✅ {vendas_removidas} vendas removidas")
            
            # 5. Limpar funcionários
            funcionarios_removidos = Funcionario.objects.filter(loja=loja).delete()[0]
            print(f"✅ {funcionarios_removidos} funcionários removidos")
            
            # 6. Limpar produtos
            produtos_removidos = Produto.objects.filter(loja=loja).delete()[0]
            print(f"✅ {produtos_removidos} produtos removidos")
            
            # 7. Limpar clientes
            clientes_removidos = Cliente.objects.filter(loja=loja).delete()[0]
            print(f"✅ {clientes_removidos} clientes removidos")
            
            # 8. Limpar dados específicos do FATESA
            try:
                from avaliacao_qualidade.models import AvaliacaoResposta, Curso, Coordenador, Professor
                # Se houver filtros por loja, aplicar aqui
                print("📋 Verificando dados específicos do FATESA...")
            except ImportError:
                print("📋 Módulo avaliacao_qualidade não encontrado")
            
            # 9. Limpar dashboard stats
            try:
                from dashboard.models import DashboardStats
                stats_removidas = DashboardStats.objects.filter(loja=loja).delete()[0]
                print(f"✅ {stats_removidas} estatísticas de dashboard removidas")
            except Exception as e:
                print(f"⚠️  Erro ao remover estatísticas: {e}")
            
            # 10. Finalmente, excluir a loja
            print(f"\n🗑️  Excluindo a loja '{nome_loja}'...")
            loja.delete()
            
            print(f"\n🎉 LOJA '{nome_loja}' EXCLUÍDA COM SUCESSO!")
            print(f"   👤 Admin preservado: {admin_user.username if admin_user else 'Nenhum'}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERRO ao excluir loja FATESA: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_loja_removida():
    """Verifica se a loja foi realmente removida"""
    print("\n🔍 VERIFICANDO REMOÇÃO...")
    
    loja = Loja.objects.filter(nome='FATESA - Demo').first()
    
    if loja:
        print(f"❌ Loja ainda existe: {loja.nome} (ID: {loja.id})")
        return False
    else:
        print("✅ Loja removida com sucesso do banco de dados")
        return True


def main():
    print("🚀 SCRIPT DE EXCLUSÃO ESPECÍFICA - LOJA FATESA")
    print("=" * 60)
    
    if excluir_loja_fatesa():
        if verificar_loja_removida():
            print("\n🎯 MISSÃO CUMPRIDA!")
            print("A loja FATESA - Demo foi completamente removida do sistema.")
        else:
            print("\n⚠️  ATENÇÃO: Loja ainda existe no banco!")
    else:
        print("\n❌ FALHA na exclusão da loja")


if __name__ == "__main__":
    main()