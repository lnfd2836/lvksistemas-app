#!/usr/bin/env python
"""
Script para criar o tipo de loja "Controle de Qualidade"
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from modulos.models import TipoLoja

def criar_tipo_controle_qualidade():
    """Cria o tipo de loja Controle de Qualidade"""
    
    dados_tipo = {
        'nome': 'controle_qualidade',
        'descricao': 'Sistema de controle de qualidade para laboratórios, indústrias e empresas que precisam gerenciar processos de qualidade, certificações, auditorias e conformidade.',
        'icone': 'fas fa-clipboard-check',
        'cor_primaria': '#6610f2',
        'cor_secundaria': '#17a2b8',
        
        # Configurações específicas para controle de qualidade
        'tem_categoria_produto': True,  # Categorias de testes/processos
        'tem_marca_produto': False,     # Não relevante para controle de qualidade
        'tem_tamanho_produto': False,   # Não relevante
        'tem_cor_produto': False,       # Não relevante
        'tem_peso_produto': True,       # Peso pode ser importante em testes
        'tem_volume_produto': True,     # Volume pode ser importante
        'tem_data_validade': True,      # Validade de certificações/testes
        'tem_codigo_barras': True,      # Códigos de rastreabilidade
        'tem_estoque_minimo': True,     # Estoque de materiais/equipamentos
        
        # Configurações de cliente específicas para controle de qualidade
        'tem_data_nascimento_cliente': False,  # Não relevante para empresas
        'tem_sexo_cliente': False,             # Não relevante para empresas
        'tem_cpf_cliente': False,              # Foco em empresas
        'tem_rg_cliente': False,               # Não relevante
        'tem_cnpj_cliente': True,              # Empresas clientes
        'tem_crm_cliente': True,               # Profissionais certificados
        
        # Configurações de venda/serviço
        'tem_desconto_venda': True,      # Descontos em serviços
        'tem_taxa_entrega': True,        # Taxa de deslocamento para auditorias
        'tem_mesa_venda': False,         # Não relevante
        'tem_garcom_venda': False,       # Não relevante
        
        'ativo': True
    }
    
    try:
        tipo, created = TipoLoja.objects.get_or_create(
            nome=dados_tipo['nome'],
            defaults=dados_tipo
        )
        
        if created:
            print(f"✅ Tipo criado: {tipo.get_nome_display()}")
            print(f"   Descrição: {tipo.descricao[:80]}...")
            print(f"   Ícone: {tipo.icone}")
            print(f"   Cor: {tipo.cor_primaria}")
            
            print(f"\n📋 Configurações aplicadas:")
            print(f"   ✅ Categoria de produto: {tipo.tem_categoria_produto}")
            print(f"   ✅ Peso: {tipo.tem_peso_produto}")
            print(f"   ✅ Volume: {tipo.tem_volume_produto}")
            print(f"   ✅ Data de validade: {tipo.tem_data_validade}")
            print(f"   ✅ Código de barras: {tipo.tem_codigo_barras}")
            print(f"   ✅ CNPJ cliente: {tipo.tem_cnpj_cliente}")
            print(f"   ✅ CRM cliente: {tipo.tem_crm_cliente}")
            print(f"   ✅ Taxa de entrega: {tipo.tem_taxa_entrega}")
            
        else:
            print(f"✅ Tipo já existe: {tipo.get_nome_display()}")
        
        print(f"\n🌐 Acesse:")
        print(f"   Lista: https://www.lvksistemas.com.br/modulos/tipos-loja/")
        print(f"   Criar: https://www.lvksistemas.com.br/modulos/tipos-loja/criar/")
        print(f"   Editar: https://www.lvksistemas.com.br/modulos/tipos-loja/{tipo.id}/editar/")
        
        return tipo
        
    except Exception as e:
        print(f"❌ Erro ao criar tipo: {str(e)}")
        return None

if __name__ == '__main__':
    try:
        tipo = criar_tipo_controle_qualidade()
        if tipo:
            print(f"\n🎉 Tipo 'Controle de Qualidade' criado com sucesso!")
            print(f"📊 Total de tipos no sistema: {TipoLoja.objects.count()}")
        else:
            print(f"\n❌ Falha ao criar tipo")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        sys.exit(1)