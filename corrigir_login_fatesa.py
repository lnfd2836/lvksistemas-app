#!/usr/bin/env python
"""
Script para corrigir especificamente o login da loja Fatesa
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
    """Corrige especificamente o login da loja Fatesa"""
    
    print("🔧 CORREÇÃO ESPECÍFICA - LOJA FATESA")
    print("=" * 50)
    
    # 1. Encontrar e corrigir a loja Fatesa
    print("\n1️⃣ CORRIGINDO CONFIGURAÇÃO DA FATESA")
    corrigir_fatesa()
    
    # 2. Testar a correção
    print("\n2️⃣ TESTANDO CORREÇÃO")
    testar_correcao()
    
    # 3. Verificar todas as lojas
    print("\n3️⃣ VERIFICAÇÃO FINAL DE TODAS AS LOJAS")
    verificar_todas_lojas()
    
    print("\n✅ CORREÇÃO CONCLUÍDA")

def corrigir_fatesa():
    """Corrige a configuração de login da Fatesa"""
    
    try:
        # Buscar loja Fatesa
        fatesa = None
        for loja in Loja.objects.all():
            if 'fatesa' in loja.nome.lower() or 'ultrassonografia' in loja.nome.lower():
                fatesa = loja
                break
        
        if not fatesa:
            print("   ❌ Loja Fatesa não encontrada")
            return False
        
        print(f"   🏥 Loja encontrada: {fatesa.nome}")
        
        # Buscar configuração de login
        try:
            login_config = fatesa.login_personalizado
            
            print(f"   📋 Configuração atual:")
            print(f"      Título: '{login_config.titulo}'")
            print(f"      Subtítulo: '{login_config.subtitulo}'")
            print(f"      Tema: {login_config.tema}")
            print(f"      Ativo: {login_config.ativo}")
            
            # Corrigir campos vazios
            campos_alterados = []
            
            if not login_config.titulo or login_config.titulo.strip() == '':
                login_config.titulo = f"Login - {fatesa.nome}"
                campos_alterados.append('título')
            
            if not login_config.subtitulo or login_config.subtitulo.strip() == '':
                login_config.subtitulo = f"Acesse sua conta na {fatesa.nome}"
                campos_alterados.append('subtítulo')
            
            if not login_config.mensagem_boas_vindas or login_config.mensagem_boas_vindas.strip() == '':
                login_config.mensagem_boas_vindas = f"Bem-vindo(a) à {fatesa.nome}!"
                campos_alterados.append('mensagem de boas-vindas')
            
            # Garantir que está ativo
            if not login_config.ativo:
                login_config.ativo = True
                campos_alterados.append('status ativo')
            
            # Salvar alterações
            if campos_alterados:
                login_config.save()
                print(f"   ✅ Campos corrigidos: {', '.join(campos_alterados)}")
                
                print(f"   📋 Nova configuração:")
                print(f"      Título: '{login_config.titulo}'")
                print(f"      Subtítulo: '{login_config.subtitulo}'")
                print(f"      Mensagem: '{login_config.mensagem_boas_vindas}'")
                print(f"      URL: {login_config.get_login_url()}")
            else:
                print("   ℹ️  Nenhuma correção necessária")
            
            return True
            
        except LoginPersonalizado.DoesNotExist:
            print("   ❌ Configuração de login não encontrada")
            
            # Criar nova configuração
            print("   🔧 Criando nova configuração...")
            login_config = LoginPersonalizado.objects.create(
                loja=fatesa,
                titulo=f"Login - {fatesa.nome}",
                subtitulo=f"Acesse sua conta na {fatesa.nome}",
                mensagem_boas_vindas=f"Bem-vindo(a) à {fatesa.nome}!",
                tema='corporativo',
                ativo=True
            )
            
            print(f"   ✅ Nova configuração criada:")
            print(f"      URL: {login_config.get_login_url()}")
            return True
        
    except Exception as e:
        print(f"   ❌ Erro ao corrigir Fatesa: {str(e)}")
        return False

def testar_correcao():
    """Testa se a correção funcionou"""
    
    try:
        # Buscar loja Fatesa
        fatesa = None
        for loja in Loja.objects.all():
            if 'fatesa' in loja.nome.lower():
                fatesa = loja
                break
        
        if not fatesa:
            print("   ❌ Loja Fatesa não encontrada")
            return
        
        # Testar URL de login
        try:
            login_config = fatesa.login_personalizado
            url_login = login_config.get_login_url()
            
            print(f"   🧪 Testando URL: {url_login}")
            
            client = Client()
            response = client.get(url_login)
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Verificar se o nome da loja aparece agora
                if fatesa.nome in content or 'Fatesa' in content:
                    print("      ✅ Nome da loja presente na página")
                else:
                    print("      ⚠️  Nome da loja ainda não aparece")
                
                # Verificar elementos essenciais
                if 'form' in content:
                    print("      ✅ Formulário presente")
                if 'username' in content and 'password' in content:
                    print("      ✅ Campos de login presentes")
                if login_config.titulo in content:
                    print("      ✅ Título presente na página")
                if login_config.subtitulo in content:
                    print("      ✅ Subtítulo presente na página")
                    
            else:
                print(f"      ❌ Status inesperado: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Erro no teste: {str(e)}")
    
    except Exception as e:
        print(f"   ❌ Erro geral no teste: {str(e)}")

def verificar_todas_lojas():
    """Verificação final de todas as lojas"""
    
    try:
        lojas = Loja.objects.filter(status='ativa').order_by('nome')
        
        print(f"   📊 Verificando {lojas.count()} lojas ativas:")
        
        for loja in lojas:
            print(f"\n   🏪 {loja.nome}")
            
            try:
                login_config = loja.login_personalizado
                url_login = login_config.get_login_url()
                
                print(f"      ✅ Login configurado: {url_login}")
                print(f"      📋 Título: '{login_config.titulo}'")
                print(f"      📋 Subtítulo: '{login_config.subtitulo}'")
                print(f"      🎨 Tema: {login_config.tema}")
                print(f"      🔄 Ativo: {login_config.ativo}")
                
                # Teste rápido
                client = Client()
                response = client.get(url_login)
                if response.status_code == 200:
                    print(f"      ✅ URL funcionando")
                else:
                    print(f"      ❌ URL com problema: Status {response.status_code}")
                
            except LoginPersonalizado.DoesNotExist:
                print(f"      ❌ Sem configuração de login")
            except Exception as e:
                print(f"      ❌ Erro: {str(e)}")
    
    except Exception as e:
        print(f"   ❌ Erro na verificação final: {str(e)}")

if __name__ == '__main__':
    main()