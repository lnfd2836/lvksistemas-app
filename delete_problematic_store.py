#!/usr/bin/env python
"""
Script para excluir loja problemática e resolver constraint issues
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import transaction
from lojas.models import Loja
from django.contrib.auth.models import User


def excluir_loja_problematica():
    """Exclui a loja problemática que está causando issues"""
    try:
        # ID da loja problemática
        loja_id = "d70d4da8-0889-4d78-bd12-849c62764f46"
        
        with transaction.atomic():
            try:
                loja = Loja.objects.get(id=loja_id)
                print(f"🏪 Loja encontrada: {loja.nome}")
                print(f"   ID: {loja.id}")
                print(f"   Status: {loja.status}")
                print(f"   Admin: {loja.admin_user.username if loja.admin_user else 'Nenhum'}")
                
                # Limpar referências da loja
                print("\n🧹 Limpando referências da loja...")
                
                # Clientes da loja
                from lojas.models import Cliente
                clientes = Cliente.objects.filter(loja=loja)
                clientes_count = clientes.count()
                if clientes_count > 0:
                    clientes.delete()
                    print(f"   ✅ {clientes_count} clientes removidos")
                
                # Produtos da loja
                from lojas.models import Produto
                produtos = Produto.objects.filter(loja=loja)
                produtos_count = produtos.count()
                if produtos_count > 0:
                    produtos.delete()
                    print(f"   ✅ {produtos_count} produtos removidos")
                
                # Vendas da loja
                from lojas.models import Venda
                vendas = Venda.objects.filter(loja=loja)
                vendas_count = vendas.count()
                if vendas_count > 0:
                    vendas.delete()
                    print(f"   ✅ {vendas_count} vendas removidas")
                
                # Funcionários da loja
                from lojas.models import Funcionario
                funcionarios = Funcionario.objects.filter(loja=loja)
                funcionarios_count = funcionarios.count()
                if funcionarios_count > 0:
                    funcionarios.delete()
                    print(f"   ✅ {funcionarios_count} funcionários removidos")
                
                # Notificações da loja
                from dashboard.models import Notificacao
                notificacoes = Notificacao.objects.filter(loja=loja)
                notificacoes_count = notificacoes.count()
                if notificacoes_count > 0:
                    notificacoes.delete()
                    print(f"   ✅ {notificacoes_count} notificações removidas")
                
                # Controle financeiro
                try:
                    from controle_financeiro.models import ControleFinanceiro
                    controle = ControleFinanceiro.objects.filter(loja=loja)
                    controle_count = controle.count()
                    if controle_count > 0:
                        controle.delete()
                        print(f"   ✅ {controle_count} controles financeiros removidos")
                except ImportError:
                    print("   📋 Módulo controle_financeiro não encontrado")
                
                # Excluir a loja
                nome_loja = loja.nome
                loja.delete()
                
                print(f"\n✅ Loja '{nome_loja}' excluída com sucesso!")
                return True
                
            except Loja.DoesNotExist:
                print(f"❌ Loja com ID {loja_id} não encontrada")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao excluir loja: {e}")
        return False


def criar_novo_superuser():
    """Cria um novo superusuário definitivo"""
    try:
        with transaction.atomic():
            # Verificar se já existe
            if User.objects.filter(username='admin').exists():
                user = User.objects.get(username='admin')
                print(f"✅ Usuário admin já existe: ID {user.id}")
                return user
            
            # Criar usuário definitivo
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@lvksistemas.com',
                password='Admin123!LVK',
                first_name='Administrador',
                last_name='Sistema',
                is_superuser=True,
                is_staff=True,
                is_active=True
            )
            
            print(f"✅ Usuário admin criado com sucesso!")
            print(f"   ID: {admin_user.id}")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Senha: Admin123!LVK")
            
            return admin_user
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        return None


def main():
    print("🗑️ EXCLUINDO LOJA PROBLEMÁTICA E CRIANDO ADMIN DEFINITIVO")
    print("=" * 60)
    
    # Excluir loja problemática
    if excluir_loja_problematica():
        print("\n✅ Loja problemática excluída com sucesso!")
    else:
        print("\n❌ Falha ao excluir loja problemática")
    
    # Criar usuário admin definitivo
    print("\n👤 Criando usuário admin definitivo...")
    if criar_novo_superuser():
        print("\n✅ Usuário admin definitivo criado!")
    else:
        print("\n❌ Falha ao criar usuário admin")
    
    print("\n🎯 Agora você pode excluir os usuários temporários com segurança!")


if __name__ == "__main__":
    main()