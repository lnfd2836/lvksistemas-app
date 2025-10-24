#!/usr/bin/env python
"""
Script simples para verificar se a otimização foi aplicada corretamente
"""

import os
import re

def verificar_urls():
    """Verifica se as URLs foram otimizadas"""
    
    print("🔍 Verificando URLs...")
    
    urls_file = 'controle_financeiro/urls.py'
    
    if not os.path.exists(urls_file):
        print(f"❌ Arquivo {urls_file} não encontrado")
        return False
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se contém redirecionamentos
    checks = [
        ('redirect_boletos_to_asaas', 'Redirecionamento de boletos'),
        ('redirect_configurar_boletos_to_asaas', 'Redirecionamento de configuração'),
        ('listar_cobrancas_asaas', 'URL de cobranças Asaas'),
        ('configurar_asaas', 'URL de configuração Asaas'),
    ]
    
    resultados = []
    
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc} -> OK")
            resultados.append(True)
        else:
            print(f"❌ {desc} -> Não encontrado")
            resultados.append(False)
    
    return all(resultados)

def verificar_views():
    """Verifica se as views foram otimizadas"""
    
    print("\n🔄 Verificando views...")
    
    views_file = 'controle_financeiro/views.py'
    
    if not os.path.exists(views_file):
        print(f"❌ Arquivo {views_file} não encontrado")
        return False
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se as views de redirecionamento existem
    redirect_views = [
        'def redirect_boletos_to_asaas',
        'def redirect_gerar_boleto_to_asaas',
        'def redirect_boletos_cliente_to_asaas',
        'def redirect_configurar_boletos_to_asaas',
    ]
    
    resultados = []
    
    for view in redirect_views:
        if view in content:
            print(f"✅ {view} -> OK")
            resultados.append(True)
        else:
            print(f"❌ {view} -> Não encontrado")
            resultados.append(False)
    
    # Verificar se views antigas foram removidas
    old_views = [
        'def listar_boletos(request):',
        'def configurar_boletos(request):',
        'def gerar_boleto(request, controle_id):',
    ]
    
    print("\n📋 Verificando remoção de views antigas:")
    
    for view in old_views:
        if view not in content:
            print(f"✅ {view} -> Removida")
            resultados.append(True)
        else:
            print(f"❌ {view} -> Ainda existe")
            resultados.append(False)
    
    return all(resultados)

def verificar_templates():
    """Verifica se os templates foram movidos para backup"""
    
    print("\n📁 Verificando templates...")
    
    backup_dir = 'templates/controle_financeiro/backup_boletos'
    
    if not os.path.exists(backup_dir):
        print(f"❌ Diretório de backup {backup_dir} não encontrado")
        return False
    
    templates_esperados = [
        'listar_boletos.html',
        'boletos_cliente.html',
        'configurar_boletos.html',
        'editar_configuracao_boleto.html',
        'boleto_detalhes.html',
    ]
    
    resultados = []
    
    for template in templates_esperados:
        backup_path = os.path.join(backup_dir, template)
        original_path = f'templates/controle_financeiro/{template}'
        
        if os.path.exists(backup_path):
            print(f"✅ {template} -> Backup criado")
            resultados.append(True)
        else:
            print(f"❌ {template} -> Backup não encontrado")
            resultados.append(False)
        
        # Verificar se foi removido do local original
        if not os.path.exists(original_path):
            print(f"✅ {template} -> Removido do original")
        else:
            print(f"⚠️  {template} -> Ainda existe no original")
    
    return all(resultados)

def verificar_documentacao():
    """Verifica se a documentação foi criada"""
    
    print("\n📄 Verificando documentação...")
    
    doc_file = 'OTIMIZACAO_BOLETOS_CONCLUIDA.md'
    
    if os.path.exists(doc_file):
        print(f"✅ {doc_file} -> Criado")
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'CONCLUÍDA' in content:
            print("✅ Status de conclusão -> OK")
            return True
        else:
            print("❌ Status de conclusão -> Não encontrado")
            return False
    else:
        print(f"❌ {doc_file} -> Não encontrado")
        return False

def main():
    """Executa todas as verificações"""
    
    print("🚀 Verificando otimização do sistema de boletos...")
    print("=" * 60)
    
    testes = [
        ("URLs", verificar_urls),
        ("Views", verificar_views),
        ("Templates", verificar_templates),
        ("Documentação", verificar_documentacao),
    ]
    
    resultados = []
    
    for nome, teste in testes:
        print(f"\n📋 {nome}:")
        resultado = teste()
        resultados.append(resultado)
    
    print("\n" + "=" * 60)
    
    if all(resultados):
        print("🎉 OTIMIZAÇÃO VERIFICADA COM SUCESSO!")
        print()
        print("✅ Todas as mudanças foram aplicadas corretamente:")
        print("   • URLs redirecionam para Asaas")
        print("   • Views antigas removidas")
        print("   • Views de redirecionamento criadas")
        print("   • Templates movidos para backup")
        print("   • Documentação criada")
        print()
        print("🔄 Próximos passos:")
        print("   1. Reiniciar o servidor Django")
        print("   2. Testar no navegador")
        print("   3. Verificar se os redirecionamentos funcionam")
        print("   4. Monitorar logs por alguns dias")
        
        return True
    else:
        print("❌ ALGUMAS VERIFICAÇÕES FALHARAM")
        print("🔧 Revise os itens marcados com ❌")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)