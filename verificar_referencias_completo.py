#!/usr/bin/env python
"""
Script para verificar todas as referências a views removidas
"""

import os
import re

def verificar_referencias_templates():
    """Verifica referências problemáticas em templates"""
    
    print("🔍 VERIFICANDO REFERÊNCIAS EM TEMPLATES")
    print("=" * 60)
    
    # Views removidas que podem estar sendo referenciadas
    views_removidas = [
        'listar_boletos',
        'gerar_boletos_automaticos',
        'criar_boleto_manual',
        'configurar_boletos',
        'gerar_boleto',
        'marcar_boleto_pago',
        'excluir_boleto',
        'detalhar_boleto',
        'imprimir_boleto_pdf',
        'boletos_cliente',
        'editar_configuracao_boleto',
    ]
    
    templates_dir = 'templates'
    problemas = []
    
    # Percorrer todos os templates
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar cada view removida
                    for view in views_removidas:
                        patterns = [
                            f"url 'controle_financeiro:{view}'",
                            "{% url 'controle_financeiro:" + view + "'",
                            f"'controle_financeiro:{view}'",
                        ]
                        
                        for pattern in patterns:
                            if pattern in content:
                                problemas.append({
                                    'arquivo': filepath,
                                    'view': view,
                                    'pattern': pattern
                                })
                                print(f"❌ {filepath}: {view}")
                
                except Exception as e:
                    print(f"⚠️  Erro ao ler {filepath}: {e}")
    
    if not problemas:
        print("✅ Nenhuma referência problemática encontrada!")
        return True
    else:
        print(f"\n❌ Encontradas {len(problemas)} referências problemáticas:")
        for problema in problemas:
            print(f"   {problema['arquivo']}: {problema['view']}")
        return False

def verificar_urls():
    """Verifica se todas as URLs necessárias existem"""
    
    print("\n🔍 VERIFICANDO URLs")
    print("=" * 60)
    
    urls_file = 'controle_financeiro/urls.py'
    
    if not os.path.exists(urls_file):
        print(f"❌ Arquivo {urls_file} não encontrado")
        return False
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # URLs que devem existir
    urls_necessarias = [
        'dashboard_financeiro',
        'listar_cobrancas_asaas',
        'configurar_asaas',
        'criar_cobranca_asaas',
        'executar_rotinas_financeiras',
        # Redirecionamentos
        'redirect_boletos_to_asaas',
        'redirect_configurar_boletos_to_asaas',
    ]
    
    problemas = []
    
    for url in urls_necessarias:
        if url not in content:
            problemas.append(url)
            print(f"❌ URL não encontrada: {url}")
        else:
            print(f"✅ URL encontrada: {url}")
    
    return len(problemas) == 0

def verificar_views():
    """Verifica se as views de redirecionamento existem"""
    
    print("\n🔍 VERIFICANDO VIEWS")
    print("=" * 60)
    
    views_file = 'controle_financeiro/views.py'
    
    if not os.path.exists(views_file):
        print(f"❌ Arquivo {views_file} não encontrado")
        return False
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Views que devem existir
    views_necessarias = [
        'def dashboard_financeiro',
        'def redirect_boletos_to_asaas',
        'def redirect_configurar_boletos_to_asaas',
        'def executar_rotinas_financeiras',
    ]
    
    problemas = []
    
    for view in views_necessarias:
        if view not in content:
            problemas.append(view)
            print(f"❌ View não encontrada: {view}")
        else:
            print(f"✅ View encontrada: {view}")
    
    return len(problemas) == 0

def sugerir_correcoes():
    """Sugere correções para problemas encontrados"""
    
    print("\n💡 SUGESTÕES DE CORREÇÃO")
    print("=" * 60)
    
    print("Se encontrou problemas:")
    print("1. Substitua referências antigas por novas:")
    print("   - listar_boletos → listar_cobrancas_asaas")
    print("   - configurar_boletos → configurar_asaas")
    print("   - criar_boleto_manual → criar_cobranca_asaas")
    print("   - gerar_boletos_automaticos → executar_rotinas_financeiras")
    print()
    print("2. Para modais e formulários:")
    print("   - Redirecione para páginas Asaas")
    print("   - Use redirecionamentos automáticos")
    print()
    print("3. Teste após cada correção:")
    print("   - git add .")
    print("   - git commit -m 'fix: Corrigir referência X'")
    print("   - git push origin main")

def main():
    """Executa verificação completa"""
    
    print("🚀 VERIFICAÇÃO COMPLETA DE REFERÊNCIAS")
    print("=" * 60)
    print("Procurando por referências a views removidas...")
    print()
    
    resultados = []
    
    # 1. Verificar templates
    resultados.append(verificar_referencias_templates())
    
    # 2. Verificar URLs
    resultados.append(verificar_urls())
    
    # 3. Verificar views
    resultados.append(verificar_views())
    
    print("\n" + "=" * 60)
    
    if all(resultados):
        print("🎉 VERIFICAÇÃO COMPLETA - TUDO OK!")
        print("✅ Nenhuma referência problemática encontrada")
        print("✅ Todas as URLs necessárias existem")
        print("✅ Todas as views necessárias existem")
        print()
        print("🚀 Sistema pronto para produção!")
        return True
    else:
        print("❌ PROBLEMAS ENCONTRADOS")
        print("🔧 Corrija os itens marcados com ❌")
        sugerir_correcoes()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)