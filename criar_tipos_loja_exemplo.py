#!/usr/bin/env python
"""
Script para criar tipos de loja de exemplo
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from modulos.models import TipoLoja

def criar_tipos_exemplo():
    """Cria tipos de loja de exemplo"""
    
    tipos_exemplo = [
        {
            'nome': 'conveniencia',
            'descricao': 'Loja de conveniência com produtos básicos do dia a dia, bebidas, lanches e itens de primeira necessidade.',
            'icone': 'fas fa-store',
            'cor_primaria': '#28a745',
            'cor_secundaria': '#20c997',
            'tem_categoria_produto': True,
            'tem_marca_produto': True,
            'tem_tamanho_produto': False,
            'tem_cor_produto': False,
            'tem_peso_produto': False,
            'tem_volume_produto': True,
            'tem_data_validade': True,
            'tem_codigo_barras': True,
            'tem_estoque_minimo': True,
            'tem_data_nascimento_cliente': True,
            'tem_sexo_cliente': True,
            'tem_cpf_cliente': True,
            'tem_rg_cliente': False,
            'tem_cnpj_cliente': False,
            'tem_desconto_venda': True,
            'tem_taxa_entrega': False,
            'tem_mesa_venda': False,
            'tem_garcom_venda': False,
        },
        {
            'nome': 'roupas',
            'descricao': 'Loja de roupas e acessórios de moda, com variedade de tamanhos, cores e estilos.',
            'icone': 'fas fa-tshirt',
            'cor_primaria': '#e83e8c',
            'cor_secundaria': '#fd7e14',
            'tem_categoria_produto': True,
            'tem_marca_produto': True,
            'tem_tamanho_produto': True,
            'tem_cor_produto': True,
            'tem_peso_produto': False,
            'tem_volume_produto': False,
            'tem_data_validade': False,
            'tem_codigo_barras': True,
            'tem_estoque_minimo': True,
            'tem_data_nascimento_cliente': True,
            'tem_sexo_cliente': True,
            'tem_cpf_cliente': True,
            'tem_rg_cliente': False,
            'tem_cnpj_cliente': False,
            'tem_desconto_venda': True,
            'tem_taxa_entrega': True,
            'tem_mesa_venda': False,
            'tem_garcom_venda': False,
        },
        {
            'nome': 'lanchonete',
            'descricao': 'Lanchonete com sistema de mesas, garçons e controle de pedidos para atendimento no local.',
            'icone': 'fas fa-hamburger',
            'cor_primaria': '#ffc107',
            'cor_secundaria': '#fd7e14',
            'tem_categoria_produto': True,
            'tem_marca_produto': False,
            'tem_tamanho_produto': True,
            'tem_cor_produto': False,
            'tem_peso_produto': True,
            'tem_volume_produto': True,
            'tem_data_validade': True,
            'tem_codigo_barras': False,
            'tem_estoque_minimo': True,
            'tem_data_nascimento_cliente': False,
            'tem_sexo_cliente': False,
            'tem_cpf_cliente': False,
            'tem_rg_cliente': False,
            'tem_cnpj_cliente': False,
            'tem_desconto_venda': True,
            'tem_taxa_entrega': True,
            'tem_mesa_venda': True,
            'tem_garcom_venda': True,
        },
        {
            'nome': 'clinica_estetica',
            'descricao': 'Clínica de estética com agendamentos, protocolos de tratamento e controle de evolução dos clientes.',
            'icone': 'fas fa-spa',
            'cor_primaria': '#6f42c1',
            'cor_secundaria': '#e83e8c',
            'tem_categoria_produto': True,
            'tem_marca_produto': True,
            'tem_tamanho_produto': False,
            'tem_cor_produto': False,
            'tem_peso_produto': False,
            'tem_volume_produto': False,
            'tem_data_validade': True,
            'tem_codigo_barras': False,
            'tem_estoque_minimo': True,
            'tem_data_nascimento_cliente': True,
            'tem_sexo_cliente': True,
            'tem_cpf_cliente': True,
            'tem_rg_cliente': True,
            'tem_cnpj_cliente': False,
            'tem_desconto_venda': True,
            'tem_taxa_entrega': False,
            'tem_mesa_venda': False,
            'tem_garcom_venda': False,
        },
        {
            'nome': 'farmacia',
            'descricao': 'Farmácia com controle rigoroso de medicamentos, datas de validade e estoque mínimo.',
            'icone': 'fas fa-pills',
            'cor_primaria': '#17a2b8',
            'cor_secundaria': '#20c997',
            'tem_categoria_produto': True,
            'tem_marca_produto': True,
            'tem_tamanho_produto': False,
            'tem_cor_produto': False,
            'tem_peso_produto': False,
            'tem_volume_produto': True,
            'tem_data_validade': True,
            'tem_codigo_barras': True,
            'tem_estoque_minimo': True,
            'tem_data_nascimento_cliente': True,
            'tem_sexo_cliente': True,
            'tem_cpf_cliente': True,
            'tem_rg_cliente': True,
            'tem_cnpj_cliente': False,
            'tem_desconto_venda': True,
            'tem_taxa_entrega': True,
            'tem_mesa_venda': False,
            'tem_garcom_venda': False,
        }
    ]
    
    tipos_criados = []
    
    for dados_tipo in tipos_exemplo:
        tipo, created = TipoLoja.objects.get_or_create(
            nome=dados_tipo['nome'],
            defaults=dados_tipo
        )
        
        if created:
            tipos_criados.append(tipo)
            print(f"✅ Tipo criado: {tipo.get_nome_display()}")
        else:
            print(f"✅ Tipo existente: {tipo.get_nome_display()}")
    
    print(f"\n🎉 Processo concluído!")
    print(f"📊 Total de tipos criados: {len(tipos_criados)}")
    print(f"📊 Total de tipos no sistema: {TipoLoja.objects.count()}")
    
    print(f"\n🌐 Acesse: https://www.lvksistemas.com.br/modulos/tipos-loja/")
    print(f"🌐 Criar novo: https://www.lvksistemas.com.br/modulos/tipos-loja/criar/")
    
    return tipos_criados

if __name__ == '__main__':
    try:
        tipos = criar_tipos_exemplo()
        print(f"\n✅ Script executado com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        sys.exit(1)