#!/usr/bin/env python
"""
Script para diagnosticar o sistema de login personalizado por loja
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.test import Client
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Diagnostica o sistema de login personalizado por loja"""
    
    print("🔍 DIAGNÓSTICO SISTEMA LOGIN PERSONALIZADO POR LOJA")
    print("=" * 60)
    
    # 1. Verificar lojas no sistema
    print("\n1️⃣ VERIFICANDO LOJAS NO SISTEMA")
    lojas_info = verificar_lojas()
    
    # 2. Verificar configurações de login personalizado
    print("\n2️⃣ VERIFICANDO CONFIGURAÇÕES DE LOGIN PERSONALIZADO")
    verificar_configuracoes_login(lojas_info)
    
    # 3. Testar URLs de login personalizado
    print("\n3️⃣ TESTANDO URLS DE LOGIN PERSONALIZADO")
    testar_urls_login(lojas_info)
    
    # 4. Diagnóstico específico da Fatesa
    print("\n4️⃣ DIAGNÓSTICO ESPECÍFICO - FATESA")
    diagnosticar_fatesa()
    
    # 5. Corrigir problemas encontrados
    print("\n5️⃣ CORRIGINDO PROBLEMAS ENCONTRADOS")
    corrigir_problemas()
    
    print("\n✅ DIAGNÓSTICO CONCLUÍDO")

def verificar_lojas():
    """Verifica todas as lojas no sistema"""
    
    try:
        lojas = Loja.objects.all().order_by('nome')
        lojas_info = []
        
        print(f"   📊 Total de lojas: {lojas.count()}")
        
        for loja in lojas:
            info = {
                'loja': loja,
                'id': loja.id,
                'nome': loja.nome,
                'status': loja.status,
                'tem_login': False,
                'login_config': None,
                'url_login': None,
                'problemas': []
            }
            
            print(f"\n   🏪 {loja.nome}")
            print(f"      ID: {loja.id}")
            print(f"      Status: {loja.status}")
            
            # Verificar se tem login personalizado
            try:
                login_config = loja.login_personalizado
                info['tem_login'] = True
                info['login_config'] = login_config
                info['url_login'] = login_config.get_login_url()
                
                print(f"      ✅ Login personalizado: {login_config.ativo}")
                print(f"      🌐 URL: {info['url_login']}")
                print(f"      🎨 Tema: {login_config.tema}")
                
            except LoginPersonalizado.DoesNotExist:
                info['problemas'].append('Sem configuração de login personalizado')
                print(f"      ❌ Sem configuração de login personalizado")
            except Exception as e:
                info['problemas'].append(f'Erro ao acessar login: {str(e)}')
                print(f"      ❌ Erro: {str(e)}")
            
            lojas_info.append(info)
        
        return lojas_info
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar lojas: {str(e)}")
        return []

def verificar_configuracoes_login(lojas_info):
    """Verifica as configurações de login personalizado"""
    
    try:
        total_configs = LoginPersonalizado.objects.count()
        configs_ativas = LoginPersonalizado.objects.filter(ativo=True).count()
        
        print(f"   📊 Total de configurações: {total_configs}")
        print(f"   📊 Configurações ativas: {configs_ativas}")
        
        # Verificar cada configuração
        for info in lojas_info:
            if info['tem_login']:
                config = info['login_config']
                print(f"\n   🔧 {info['nome']}:")
                print(f"      Título: {config.titulo}")
                print(f"      Subtítulo: {config.subtitulo}")
                print(f"      URL personalizada: {config.url_personalizada}")
                print(f"      Ativo: {config.ativo}")
                print(f"      Tema: {config.tema}")
                
                # Verificar se a URL personalizada é válida
                if config.url_personalizada:
                    if ' ' in config.url_personalizada or config.url_personalizada != config.url_personalizada.lower():
                        info['problemas'].append('URL personalizada com formato inválido')
                        print(f"      ⚠️  URL personalizada pode ter formato inválido")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar configurações: {str(e)}")

def testar_urls_login(lojas_info):
    """Testa as URLs de login personalizado"""
    
    try:
        client = Client()
        
        for info in lojas_info:
            if info['tem_login'] and info['url_login']:
                print(f"\n   🧪 Testando {info['nome']}: {info['url_login']}")
                
                try:
                    response = client.get(info['url_login'])
                    print(f"      Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.content.decode('utf-8')
                        
                        # Verificar se é realmente uma página de login
                        if 'form' in content and 'password' in content:
                            print(f"      ✅ Página de login funcionando")
                        else:
                            info['problemas'].append('Página não parece ser de login')
                            print(f"      ❌ Página não parece ser de login")
                            
                        # Verificar se tem o nome da loja
                        if info['nome'] in content:
                            print(f"      ✅ Nome da loja presente na página")
                        else:
                            print(f"      ⚠️  Nome da loja não encontrado na página")
                            
                    elif response.status_code == 302:
                        print(f"      🔄 Redirecionamento para: {response.url}")
                        info['problemas'].append(f'Redirecionamento inesperado para {response.url}')
                    else:
                        info['problemas'].append(f'Status HTTP {response.status_code}')
                        print(f"      ❌ Status inesperado: {response.status_code}")
                        
                except Exception as e:
                    info['problemas'].append(f'Erro ao testar URL: {str(e)}')
                    print(f"      ❌ Erro ao testar: {str(e)}")
        
    except Exception as e:
        print(f"   ❌ Erro nos testes de URL: {str(e)}")

def diagnosticar_fatesa():
    """Diagnóstico específico da loja Fatesa"""
    
    try:
        # Buscar loja Fatesa
        fatesa = None
        for loja in Loja.objects.all():
            if 'fatesa' in loja.nome.lower() or 'ultrassonografia' in loja.nome.lower():
                fatesa = loja
                break
        
        if not fatesa:
            print("   ❌ Loja Fatesa não encontrada")
            return
        
        print(f"   🏥 Loja encontrada: {fatesa.nome}")
        print(f"   📋 ID: {fatesa.id}")
        print(f"   📊 Status: {fatesa.status}")
        
        # Verificar configuração de login
        try:
            login_config = fatesa.login_personalizado
            print(f"\n   🔧 Configuração de Login:")
            print(f"      Título: {login_config.titulo}")
            print(f"      Subtítulo: {login_config.subtitulo}")
            print(f"      URL personalizada: {login_config.url_personalizada}")
            print(f"      Ativo: {login_config.ativo}")
            print(f"      Tema: {login_config.tema}")
            print(f"      URL completa: {login_config.get_login_url()}")
            
            # Testar a URL específica
            client = Client()
            url_login = login_config.get_login_url()
            
            print(f"\n   🧪 Testando URL: {url_login}")
            response = client.get(url_login)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                print("      ✅ Página carregando corretamente")
                
                # Verificar conteúdo
                content = response.content.decode('utf-8')
                if 'Fatesa' in content:
                    print("      ✅ Nome da loja presente")
                if 'form' in content:
                    print("      ✅ Formulário presente")
                if 'username' in content and 'password' in content:
                    print("      ✅ Campos de login presentes")
                    
            elif response.status_code == 302:
                print(f"      ❌ PROBLEMA: Redirecionamento para {response.url}")
            else:
                print(f"      ❌ PROBLEMA: Status {response.status_code}")
            
        except LoginPersonalizado.DoesNotExist:
            print("   ❌ PROBLEMA: Fatesa não tem configuração de login personalizado")
            print("   🔧 Será criada automaticamente...")
            
            # Criar configuração padrão
            try:
                login_config = LoginPersonalizado.objects.create(
                    loja=fatesa,
                    titulo=f"Login - {fatesa.nome}",
                    subtitulo=f"Acesse sua conta na {fatesa.nome}",
                    mensagem_boas_vindas=f"Bem-vindo(a) à {fatesa.nome}!",
                    tema='padrao',
                    ativo=True
                )
                print(f"   ✅ Configuração criada: {login_config.get_login_url()}")
                
            except Exception as e:
                print(f"   ❌ Erro ao criar configuração: {str(e)}")
        
    except Exception as e:
        print(f"   ❌ Erro no diagnóstico da Fatesa: {str(e)}")

def corrigir_problemas():
    """Corrige problemas encontrados automaticamente"""
    
    try:
        print("   🔧 Verificando e corrigindo problemas...")
        
        # 1. Criar configurações de login para lojas sem configuração
        lojas_sem_login = Loja.objects.filter(status='ativa').exclude(
            id__in=LoginPersonalizado.objects.values_list('loja_id', flat=True)
        )
        
        if lojas_sem_login.exists():
            print(f"   📝 Criando configurações para {lojas_sem_login.count()} lojas...")
            
            for loja in lojas_sem_login:
                try:
                    login_config = LoginPersonalizado.objects.create(
                        loja=loja,
                        titulo=f"Login - {loja.nome}",
                        subtitulo=f"Acesse sua conta na {loja.nome}",
                        mensagem_boas_vindas=f"Bem-vindo(a) à {loja.nome}!",
                        tema='padrao',
                        ativo=True
                    )
                    print(f"      ✅ {loja.nome}: {login_config.get_login_url()}")
                    
                except Exception as e:
                    print(f"      ❌ Erro ao criar para {loja.nome}: {str(e)}")
        
        # 2. Ativar configurações inativas de lojas ativas
        configs_inativas = LoginPersonalizado.objects.filter(
            loja__status='ativa',
            ativo=False
        )
        
        if configs_inativas.exists():
            print(f"   🔄 Ativando {configs_inativas.count()} configurações...")
            configs_inativas.update(ativo=True)
            print("      ✅ Configurações ativadas")
        
        # 3. Verificar URLs personalizadas duplicadas
        urls_duplicadas = LoginPersonalizado.objects.values('url_personalizada').annotate(
            count=models.Count('url_personalizada')
        ).filter(count__gt=1, url_personalizada__isnull=False)
        
        if urls_duplicadas:
            print(f"   ⚠️  Encontradas {len(urls_duplicadas)} URLs duplicadas")
            for item in urls_duplicadas:
                print(f"      URL duplicada: {item['url_personalizada']}")
        
        print("   ✅ Correções aplicadas")
        
    except Exception as e:
        print(f"   ❌ Erro nas correções: {str(e)}")

if __name__ == '__main__':
    main()