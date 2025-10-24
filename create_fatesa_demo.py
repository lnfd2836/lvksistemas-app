#!/usr/bin/env python
"""
Script para criar loja FATESA de demonstração
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.db import transaction
from lojas.models import Loja
from modulos.models import TipoLoja
from django.contrib.auth.models import User
from django.utils import timezone


def criar_loja_fatesa_demo():
    """Cria uma loja FATESA de demonstração"""
    try:
        with transaction.atomic():
            # Buscar tipo de loja controle_qualidade
            try:
                tipo_controle = TipoLoja.objects.get(nome='controle_qualidade')
                print(f"✅ Tipo de loja encontrado: {tipo_controle.get_nome_display()}")
            except TipoLoja.DoesNotExist:
                print("❌ Tipo de loja 'controle_qualidade' não encontrado!")
                return False
            
            # Buscar usuário admin
            try:
                admin_user = User.objects.get(username='admin')
                print(f"✅ Usuário admin encontrado: {admin_user.username}")
            except User.DoesNotExist:
                print("❌ Usuário admin não encontrado!")
                return False
            
            # Verificar se já existe loja demo
            if Loja.objects.filter(nome='FATESA - Demo').exists():
                loja = Loja.objects.get(nome='FATESA - Demo')
                print(f"✅ Loja demo já existe: {loja.nome} (ID: {loja.id})")
                return loja
            
            # Criar loja FATESA demo
            loja = Loja.objects.create(
                nome='FATESA - Demo',
                cnpj='12345678000199',
                email='demo@fatesa.edu.br',
                telefone='(85) 3456-7890',
                endereco='Rua da Educação, 123',
                cidade='Fortaleza',
                estado='CE',
                cep='60000-000',
                admin_user=admin_user,
                tipo_loja=tipo_controle,
                status='ativa',
                descricao='Loja de demonstração do sistema FATESA - Controle de Qualidade Educacional'
            )
            
            print(f"✅ Loja FATESA demo criada com sucesso!")
            print(f"   ID: {loja.id}")
            print(f"   Nome: {loja.nome}")
            print(f"   Tipo: {loja.tipo_loja.get_nome_display()}")
            print(f"   Admin: {loja.admin_user.username}")
            print(f"   Status: {loja.status}")
            
            return loja
            
    except Exception as e:
        print(f"❌ Erro ao criar loja FATESA demo: {e}")
        return False


def criar_dados_exemplo():
    """Cria dados de exemplo para a loja FATESA"""
    try:
        loja = Loja.objects.get(nome='FATESA - Demo')
        
        # Criar alguns "produtos" (na verdade cursos/disciplinas para FATESA)
        from lojas.models import Produto, Categoria
        
        # Criar categoria para cursos
        categoria, created = Categoria.objects.get_or_create(
            nome='Cursos Superiores',
            loja=loja,
            defaults={'descricao': 'Cursos de graduação oferecidos pela FATESA'}
        )
        
        if created:
            print(f"✅ Categoria criada: {categoria.nome}")
        
        # Criar alguns cursos como "produtos"
        cursos = [
            {
                'nome': 'Administração',
                'descricao': 'Curso de Bacharelado em Administração',
                'preco': 800.00,
                'codigo': 'ADM001'
            },
            {
                'nome': 'Ciências Contábeis',
                'descricao': 'Curso de Bacharelado em Ciências Contábeis',
                'preco': 750.00,
                'codigo': 'CCO001'
            },
            {
                'nome': 'Engenharia Civil',
                'descricao': 'Curso de Bacharelado em Engenharia Civil',
                'preco': 1200.00,
                'codigo': 'ECV001'
            },
            {
                'nome': 'Pedagogia',
                'descricao': 'Curso de Licenciatura em Pedagogia',
                'preco': 650.00,
                'codigo': 'PED001'
            }
        ]
        
        cursos_criados = 0
        for curso_data in cursos:
            produto, created = Produto.objects.get_or_create(
                nome=curso_data['nome'],
                loja=loja,
                defaults={
                    'descricao': curso_data['descricao'],
                    'preco': curso_data['preco'],
                    'codigo': curso_data['codigo'],
                    'categoria': categoria,
                    'estoque': 100,  # Vagas disponíveis
                    'ativo': True
                }
            )
            
            if created:
                cursos_criados += 1
                print(f"✅ Curso criado: {produto.nome}")
        
        print(f"✅ {cursos_criados} cursos criados como exemplo")
        
        # Criar alguns clientes exemplo (estudantes)
        from lojas.models import Cliente
        
        estudantes = [
            {
                'nome': 'Maria Silva Santos',
                'email': 'maria.santos@email.com',
                'telefone': '(85) 99999-1111',
                'cpf': '123.456.789-01'
            },
            {
                'nome': 'João Pedro Oliveira',
                'email': 'joao.oliveira@email.com',
                'telefone': '(85) 99999-2222',
                'cpf': '987.654.321-02'
            },
            {
                'nome': 'Ana Carolina Lima',
                'email': 'ana.lima@email.com',
                'telefone': '(85) 99999-3333',
                'cpf': '456.789.123-03'
            }
        ]
        
        estudantes_criados = 0
        for estudante_data in estudantes:
            cliente, created = Cliente.objects.get_or_create(
                email=estudante_data['email'],
                loja=loja,
                defaults=estudante_data
            )
            
            if created:
                estudantes_criados += 1
                print(f"✅ Estudante criado: {cliente.nome}")
        
        print(f"✅ {estudantes_criados} estudantes criados como exemplo")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        return False


def main():
    print("🎓 CRIANDO LOJA FATESA DE DEMONSTRAÇÃO")
    print("=" * 50)
    
    # Criar loja
    loja = criar_loja_fatesa_demo()
    if not loja:
        print("❌ Falha ao criar loja FATESA demo")
        return
    
    # Criar dados de exemplo
    print("\n📚 Criando dados de exemplo...")
    if criar_dados_exemplo():
        print("✅ Dados de exemplo criados com sucesso!")
    else:
        print("❌ Falha ao criar dados de exemplo")
    
    print(f"\n🎯 LOJA FATESA DEMO CRIADA COM SUCESSO!")
    print(f"   • Nome: FATESA - Demo")
    print(f"   • Tipo: Controle de Qualidade")
    print(f"   • Admin: admin")
    print(f"   • Status: Ativa")
    print(f"   • URL Admin: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
    print(f"   • Credenciais: admin / Admin123!LVK")


if __name__ == "__main__":
    main()