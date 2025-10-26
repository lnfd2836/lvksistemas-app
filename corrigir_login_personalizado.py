#!/usr/bin/env python3
"""
Script para corrigir problemas de login personalizado nas lojas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from lojas.models import Loja
from lojas.models_login import LoginPersonalizado

def main():
    print("🔧 Corrigindo configurações de login personalizado...")
    
    # Verificar todas as lojas
    lojas = Loja.objects.all()
    print(f"📊 Total de lojas: {lojas.count()}")
    
    lojas_corrigidas = 0
    lojas_criadas = 0
    
    for loja in lojas:
        print(f"\n🏪 Verificando loja: {loja.nome}")
        
        try:
            # Verificar se tem login personalizado
            login_config = loja.login_personalizado
            print(f"  ✅ Login personalizado existe")
            print(f"  📋 Tema: {login_config.tema}")
            print(f"  🌐 URL: {login_config.get_login_url()}")
            
            # Verificar se o tema tem template correspondente
            template_path = login_config.get_template_path()
            print(f"  📄 Template: {template_path}")
            
            # Se o tema não tem template, mudar para um que existe
            temas_disponiveis = ['padrao', 'moderno', 'minimalista', 'corporativo', 'fatesa']
            
            if login_config.tema not in temas_disponiveis:
                print(f"  ⚠️ Tema '{login_config.tema}' não disponível, alterando para 'padrao'")
                login_config.tema = 'padrao'
                login_config.save()
                lojas_corrigidas += 1
                print(f"  ✅ Tema corrigido para 'padrao'")
            
        except LoginPersonalizado.DoesNotExist:
            print(f"  ❌ Login personalizado não existe, criando...")
            
            # Criar login personalizado baseado no tipo de loja
            from lojas.signals_login import obter_configuracao_por_tipo_loja
            
            config = obter_configuracao_por_tipo_loja(loja)
            
            LoginPersonalizado.objects.create(
                loja=loja,
                titulo=config['titulo'],
                subtitulo=config['subtitulo'],
                tema=config['tema'],
                cor_primaria=config['cor_primaria'],
                cor_secundaria=config['cor_secundaria'],
                cor_fundo=config['cor_fundo'],
                cor_texto=config['cor_texto'],
                mensagem_boas_vindas=config['mensagem_boas_vindas'],
                mensagem_rodape=config['mensagem_rodape'],
                css_personalizado=config['css_personalizado'],
                mostrar_logo=config['mostrar_logo'],
                mostrar_nome_loja=config['mostrar_nome_loja'],
                permitir_lembrar_senha=config['permitir_lembrar_senha'],
                mostrar_link_recuperar_senha=config['mostrar_link_recuperar_senha'],
                ativo=True
            )
            
            lojas_criadas += 1
            print(f"  ✅ Login personalizado criado com tema '{config['tema']}'")
            
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
    
    print(f"\n📊 Resumo:")
    print(f"  Lojas verificadas: {lojas.count()}")
    print(f"  Lojas corrigidas: {lojas_corrigidas}")
    print(f"  Lojas com login criado: {lojas_criadas}")
    
    # Testar URLs de login
    print(f"\n🧪 Testando URLs de login personalizado...")
    
    from django.test import Client
    client = Client()
    
    for loja in lojas:
        try:
            login_config = loja.login_personalizado
            url_login = login_config.get_login_url()
            
            response = client.get(url_login)
            
            if response.status_code == 200:
                print(f"  ✅ {loja.nome}: {url_login} - OK")
            else:
                print(f"  ❌ {loja.nome}: {url_login} - Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {loja.nome}: Erro - {str(e)}")
    
    print(f"\n🎉 Correção concluída!")
    
    # Mostrar URLs para acesso
    print(f"\n🌐 URLs de Login Personalizado:")
    for loja in lojas:
        try:
            login_config = loja.login_personalizado
            url_completa = f"http://0.0.0.0:8000{login_config.get_login_url()}"
            print(f"  📱 {loja.nome}: {url_completa}")
        except:
            pass

if __name__ == "__main__":
    main()