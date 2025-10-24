#!/usr/bin/env python
"""
Script para corrigir automaticamente referências problemáticas
"""

import os
import re

def corrigir_template(filepath, replacements):
    """Corrige um template específico"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigido: {filepath}")
            return True
        else:
            print(f"⚪ Sem mudanças: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao corrigir {filepath}: {e}")
        return False

def corrigir_templates_principais():
    """Corrige os templates principais (não backup)"""
    
    print("🔧 CORRIGINDO TEMPLATES PRINCIPAIS")
    print("=" * 60)
    
    # Mapeamento de substituições
    replacements = {
        # URLs antigas → URLs novas
        "url 'controle_financeiro:gerar_boleto'": "url 'controle_financeiro:gerar_cobranca_asaas'",
        "url 'controle_financeiro:listar_boletos'": "url 'controle_financeiro:listar_cobrancas_asaas'",
        "url 'controle_financeiro:configurar_boletos'": "url 'controle_financeiro:configurar_asaas'",
        "url 'controle_financeiro:marcar_boleto_pago'": "url 'controle_financeiro:listar_cobrancas_asaas'",
        "url 'controle_financeiro:excluir_boleto'": "url 'controle_financeiro:listar_cobrancas_asaas'",
        "url 'controle_financeiro:detalhar_boleto'": "url 'controle_financeiro:visualizar_cobranca_asaas'",
        "url 'controle_financeiro:imprimir_boleto_pdf'": "url 'controle_financeiro:listar_cobrancas_asaas'",
        "url 'controle_financeiro:boletos_cliente'": "url 'dashboard:dashboard'",
        
        # Com {% %}
        "{% url 'controle_financeiro:gerar_boleto'": "{% url 'controle_financeiro:gerar_cobranca_asaas'",
        "{% url 'controle_financeiro:listar_boletos'": "{% url 'controle_financeiro:listar_cobrancas_asaas'",
        "{% url 'controle_financeiro:configurar_boletos'": "{% url 'controle_financeiro:configurar_asaas'",
        "{% url 'controle_financeiro:marcar_boleto_pago'": "{% url 'controle_financeiro:listar_cobrancas_asaas'",
        "{% url 'controle_financeiro:excluir_boleto'": "{% url 'controle_financeiro:listar_cobrancas_asaas'",
        "{% url 'controle_financeiro:detalhar_boleto'": "{% url 'controle_financeiro:visualizar_cobranca_asaas'",
        "{% url 'controle_financeiro:imprimir_boleto_pdf'": "{% url 'controle_financeiro:listar_cobrancas_asaas'",
        "{% url 'controle_financeiro:boletos_cliente'": "{% url 'dashboard:dashboard'",
        
        # Textos e labels
        "Gerar Boleto": "Gerar Cobrança",
        "Ver Boletos": "Ver Cobranças",
        "Configurar Boletos": "Configurar Asaas",
        "Boletos Gerados": "Cobranças Geradas",
        "fa-barcode": "fa-credit-card",
    }
    
    # Templates para corrigir (excluindo backup)
    templates_para_corrigir = [
        'templates/controle_financeiro/dashboard.html',
        'templates/controle_financeiro/listar.html',
        'templates/controle_financeiro/detalhar.html',
        'templates/controle_financeiro/gerar_boleto.html',
        'templates/dashboard/super_admin.html',
        'templates/dashboard/loja.html',
    ]
    
    corrigidos = 0
    
    for template in templates_para_corrigir:
        if os.path.exists(template):
            if corrigir_template(template, replacements):
                corrigidos += 1
        else:
            print(f"⚠️  Template não encontrado: {template}")
    
    print(f"\n📊 Resultado: {corrigidos} templates corrigidos")
    return corrigidos > 0

def corrigir_urls_especificas():
    """Corrige URLs específicas que podem estar causando problemas"""
    
    print("\n🔧 CORRIGINDO URLs ESPECÍFICAS")
    print("=" * 60)
    
    # Adicionar URLs que podem estar faltando
    urls_file = 'controle_financeiro/urls.py'
    
    if not os.path.exists(urls_file):
        print(f"❌ Arquivo {urls_file} não encontrado")
        return False
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # URLs que podem estar faltando
    urls_necessarias = {
        'visualizar_cobranca_asaas': "path('asaas/cobrancas/<uuid:cobranca_id>/', asaas_views.visualizar_cobranca_asaas, name='visualizar_cobranca_asaas'),",
    }
    
    adicionadas = 0
    
    for url_name, url_pattern in urls_necessarias.items():
        if url_name not in content:
            # Adicionar antes da última linha
            lines = content.split('\n')
            # Encontrar a linha com ']'
            for i, line in enumerate(lines):
                if line.strip() == ']':
                    lines.insert(i, f"    {url_pattern}")
                    break
            
            content = '\n'.join(lines)
            adicionadas += 1
            print(f"✅ URL adicionada: {url_name}")
    
    if adicionadas > 0:
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📊 {adicionadas} URLs adicionadas")
        return True
    else:
        print("⚪ Nenhuma URL precisou ser adicionada")
        return False

def main():
    """Executa correções automáticas"""
    
    print("🚀 CORREÇÃO AUTOMÁTICA DE REFERÊNCIAS")
    print("=" * 60)
    print("Corrigindo apenas templates principais (não backup)...")
    print()
    
    resultados = []
    
    # 1. Corrigir templates principais
    resultados.append(corrigir_templates_principais())
    
    # 2. Corrigir URLs específicas
    resultados.append(corrigir_urls_especificas())
    
    print("\n" + "=" * 60)
    
    if any(resultados):
        print("✅ CORREÇÕES APLICADAS!")
        print()
        print("🔄 Próximos passos:")
        print("1. git add .")
        print("2. git commit -m 'fix: Corrigir referências automáticas'")
        print("3. git push origin main")
        print("4. Testar no Heroku")
        return True
    else:
        print("⚪ NENHUMA CORREÇÃO NECESSÁRIA")
        print("Templates já estão corretos")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)