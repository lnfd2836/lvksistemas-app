#!/usr/bin/env python
"""
Script para excluir todas as lojas do sistema
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


def listar_lojas():
    """Lista todas as lojas do sistema"""
    print("📋 LOJAS EXISTENTES NO SISTEMA")
    print("=" * 50)
    
    lojas = Loja.objects.all().order_by('nome')
    
    if not lojas.exists():
        print("✅ Nenhuma loja encontrada no sistema")
        return []
    
    print(f"📊 Total de lojas: {lojas.count()}")
    print()
    
    for i, loja in enumerate(lojas, 1):
        print(f"{i}. {loja.nome}")
        print(f"   ID: {loja.id}")
        print(f"   CNPJ: {loja.cnpj}")
        print(f"   Admin: {loja.admin_user.username if loja.admin_user else 'Nenhum'}")
        print(f"   Status: {loja.status}")
        print(f"   Tipo: {loja.tipo_loja.get_nome_display() if loja.tipo_loja else 'Não definido'}")
        print(f"   Criada: {loja.data_criacao.strftime('%d/%m/%Y %H:%M')}")
        
        # Estatísticas básicas
        try:
            clientes = Cliente.objects.filter(loja=loja).count()
            produtos = Produto.objects.filter(loja=loja).count()
            vendas = Venda.objects.filter(loja=loja).count()
            funcionarios = Funcionario.objects.filter(loja=loja).count()
            notificacoes = Notificacao.objects.filter(loja=loja).count()
            
            print(f"   📊 Dados: {clientes} clientes, {produtos} produtos, {vendas} vendas, {funcionarios} funcionários, {notificacoes} notificações")
        except Exception as e:
            print(f"   ⚠️  Erro ao coletar estatísticas: {e}")
        
        print("-" * 40)
    
    return list(lojas)


def excluir_loja_completa(loja):
    """Exclui uma loja e todos os seus dados relacionados"""
    print(f"\n🗑️  EXCLUINDO LOJA: {loja.nome}")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            nome_loja = loja.nome
            admin_user = loja.admin_user
            
            # Coletar estatísticas antes da exclusão
            stats = {
                'clientes': Cliente.objects.filter(loja=loja).count(),
                'produtos': Produto.objects.filter(loja=loja).count(),
                'vendas': Venda.objects.filter(loja=loja).count(),
                'funcionarios': Funcionario.objects.filter(loja=loja).count(),
                'notificacoes': Notificacao.objects.filter(loja=loja).count(),
            }
            
            print(f"📊 Dados a serem excluídos:")
            print(f"   - {stats['clientes']} clientes")
            print(f"   - {stats['produtos']} produtos")
            print(f"   - {stats['vendas']} vendas")
            print(f"   - {stats['funcionarios']} funcionários")
            print(f"   - {stats['notificacoes']} notificações")
            
            # 1. Excluir notificações da loja
            notificacoes_removidas = Notificacao.objects.filter(loja=loja).delete()[0]
            print(f"✅ {notificacoes_removidas} notificações removidas")
            
            # 2. Excluir controle financeiro
            try:
                from controle_financeiro.models import ControleFinanceiro
                controle_removido = ControleFinanceiro.objects.filter(loja=loja).delete()[0]
                print(f"✅ {controle_removido} controles financeiros removidos")
            except ImportError:
                print("📋 Módulo controle_financeiro não encontrado")
            
            # 3. Excluir itens de venda (antes das vendas)
            try:
                from lojas.models import ItemVenda
                itens_removidos = ItemVenda.objects.filter(venda__loja=loja).delete()[0]
                print(f"✅ {itens_removidos} itens de venda removidos")
            except Exception as e:
                print(f"⚠️  Erro ao remover itens de venda: {e}")
            
            # 4. Excluir vendas
            vendas_removidas = Venda.objects.filter(loja=loja).delete()[0]
            print(f"✅ {vendas_removidas} vendas removidas")
            
            # 5. Excluir funcionários
            funcionarios_removidos = Funcionario.objects.filter(loja=loja).delete()[0]
            print(f"✅ {funcionarios_removidos} funcionários removidos")
            
            # 6. Excluir produtos
            produtos_removidos = Produto.objects.filter(loja=loja).delete()[0]
            print(f"✅ {produtos_removidos} produtos removidos")
            
            # 7. Excluir clientes
            clientes_removidos = Cliente.objects.filter(loja=loja).delete()[0]
            print(f"✅ {clientes_removidos} clientes removidos")
            
            # 8. Dados específicos por tipo de loja
            if loja.tipo_loja and loja.tipo_loja.nome == 'lanchonete':
                try:
                    from lojas.models import Mesa, Pedido, ItemPedido
                    ItemPedido.objects.filter(pedido__loja=loja).delete()
                    pedidos_removidos = Pedido.objects.filter(loja=loja).delete()[0]
                    mesas_removidas = Mesa.objects.filter(loja=loja).delete()[0]
                    print(f"✅ {pedidos_removidos} pedidos e {mesas_removidas} mesas removidos (lanchonete)")
                except Exception as e:
                    print(f"⚠️  Erro ao remover dados de lanchonete: {e}")
            
            # 9. Excluir a loja (admin_user será preservado devido ao SET_NULL)
            loja.delete()
            
            print(f"\n🎉 LOJA '{nome_loja}' EXCLUÍDA COM SUCESSO!")
            print(f"   👤 Admin preservado: {admin_user.username if admin_user else 'Nenhum'}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERRO ao excluir loja '{loja.nome}': {e}")
        return False


def excluir_todas_lojas():
    """Exclui todas as lojas do sistema"""
    print("🚨 EXCLUSÃO DE TODAS AS LOJAS DO SISTEMA")
    print("=" * 60)
    
    lojas = listar_lojas()
    
    if not lojas:
        print("✅ Nenhuma loja para excluir")
        return
    
    print(f"\n⚠️  ATENÇÃO: Serão excluídas {len(lojas)} loja(s)")
    print("Esta ação é IRREVERSÍVEL!")
    
    # Confirmação
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        confirmar = 'sim'
    else:
        confirmar = input("\nDigite 'CONFIRMO' para prosseguir: ").strip()
    
    if confirmar.upper() != 'CONFIRMO':
        print("❌ Operação cancelada")
        return
    
    # Excluir cada loja
    sucessos = 0
    falhas = 0
    
    for loja in lojas:
        if excluir_loja_completa(loja):
            sucessos += 1
        else:
            falhas += 1
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   ✅ {sucessos} loja(s) excluída(s) com sucesso")
    print(f"   ❌ {falhas} falha(s)")
    
    if sucessos > 0:
        print(f"\n🎯 SISTEMA LIMPO!")
        print("Todas as lojas e seus dados foram removidos do sistema.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'listar':
        listar_lojas()
    else:
        excluir_todas_lojas()