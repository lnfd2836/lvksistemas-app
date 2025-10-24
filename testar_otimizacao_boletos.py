#!/usr/bin/env python
"""
Script para testar a otimização do sistema de boletos
Verifica se os redirecionamentos estão funcionando corretamente
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def criar_usuario_teste():
    """Cria um usuário superuser para teste"""
    try:
        user = User.objects.get(username='admin')
        return user
    except User.DoesNotExist:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        return user

def testar_redirecionamentos():
    """Testa se os redirecionamentos estão funcionando"""
    
    print("🧪 Testando redirecionamentos...")
    
    client = Client()
    user = criar_usuario_teste()
    client.force_login(user)
    
    # URLs para testar
    urls_teste = [
        ('controle_financeiro:listar_boletos', 'controle_financeiro:listar_cobrancas_asaas'),
        ('controle_financeiro:configurar_boletos', 'controle_financeiro:configurar_asaas'),
    ]
    
    resultados = []
    
    for url_antiga, url_esperada in urls_teste:
        try:
            # Fazer requisição para URL antiga
            response = client.get(reverse(url_antiga))
            
            # Verificar se houve redirecionamento
            if response.status_code == 302:
                print(f"✅ {url_antiga} -> Redirecionamento OK")
                resultados.append(True)
            else:
                print(f"❌ {url_antiga} -> Status: {response.status_code}")
                resultados.append(False)
                
        except Exception as e:
            print(f"❌ {url_antiga} -> Erro: {e}")
            resultados.append(False)
    
    return all(resultados)

def verificar_urls_existentes():
    """Verifica se as URLs necessárias existem"""
    
    print("🔍 Verificando URLs...")
    
    from django.urls import reverse
    
    urls_necessarias = [
        'controle_financeiro:dashboard_financeiro',
        'controle_financeiro:listar_cobrancas_asaas',
        'controle_financeiro:configurar_asaas',
        'controle_financeiro:listar_boletos',  # Deve redirecionar
        'controle_financeiro:configurar_boletos',  # Deve redirecionar
    ]
    
    resultados = []
    
    for url in urls_necessarias:
        try:
            reverse(url)
            print(f"✅ {url} -> OK")
            resultados.append(True)
        except Exception as e:
            print(f"❌ {url} -> Erro: {e}")
            resultados.append(False)
    
    return all(resultados)

def verificar_templates_backup():
    """Verifica se os templates foram movidos para backup"""
    
    print("📁 Verificando backup de templates...")
    
    backup_dir = 'templates/controle_financeiro/backup_boletos'
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
        if os.path.exists(backup_path):
            print(f"✅ {template} -> Backup OK")
            resultados.append(True)
        else:
            print(f"❌ {template} -> Backup não encontrado")
            resultados.append(False)
    
    return all(resultados)

def verificar_views_redirecionamento():
    """Verifica se as views de redirecionamento foram criadas"""
    
    print("🔄 Verificando views de redirecionamento...")
    
    from controle_financeiro import views
    
    views_esperadas = [
        'redirect_boletos_to_asaas',
        'redirect_gerar_boleto_to_asaas',
        'redirect_boletos_cliente_to_asaas',
        'redirect_configurar_boletos_to_asaas',
    ]
    
    resultados = []
    
    for view_name in views_esperadas:
        if hasattr(views, view_name):
            print(f"✅ {view_name} -> OK")
            resultados.append(True)
        else:
            print(f"❌ {view_name} -> Não encontrada")
            resultados.append(False)
    
    return all(resultados)

def main():
    """Executa todos os testes"""
    
    print("🚀 Iniciando testes da otimização...")
    print("=" * 50)
    
    testes = [
        ("URLs existentes", verificar_urls_existentes),
        ("Views de redirecionamento", verificar_views_redirecionamento),
        ("Backup de templates", verificar_templates_backup),
        ("Redirecionamentos funcionais", testar_redirecionamentos),
    ]
    
    resultados = []
    
    for nome, teste in testes:
        print(f"\n📋 {nome}:")
        resultado = teste()
        resultados.append(resultado)
        print(f"Status: {'✅ PASSOU' if resultado else '❌ FALHOU'}")
    
    print("\n" + "=" * 50)
    
    if all(resultados):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Otimização funcionando corretamente")
        print()
        print("🔄 Próximos passos:")
        print("   1. Reiniciar o servidor Django")
        print("   2. Testar manualmente no navegador")
        print("   3. Verificar logs de acesso")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)