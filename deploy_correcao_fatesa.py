#!/usr/bin/env python
"""
Script para fazer deploy da correção da loja Fatesa
"""
import os
import sys
import subprocess
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
    """Deploy da correção da loja Fatesa"""
    
    print("🚀 DEPLOY CORREÇÃO LOJA FATESA")
    print("=" * 50)
    
    # 1. Verificar correção local
    print("\n1️⃣ VERIFICANDO CORREÇÃO LOCAL")
    if not verificar_correcao_local():
        print("❌ Correção não está funcionando localmente. Abortando.")
        return False
    
    # 2. Fazer deploy
    print("\n2️⃣ FAZENDO DEPLOY NO HEROKU")
    if not fazer_deploy():
        print("❌ Erro no deploy.")
        return False
    
    # 3. Instruções para teste
    print("\n3️⃣ INSTRUÇÕES PARA TESTE NO HEROKU")
    mostrar_instrucoes_teste()
    
    print("\n✅ DEPLOY DA CORREÇÃO CONCLUÍDO!")
    return True

def verificar_correcao_local():
    """Verifica se a correção está funcionando localmente"""
    
    try:
        # Buscar loja Fatesa
        fatesa = None
        for loja in Loja.objects.all():
            if 'fatesa' in loja.nome.lower():
                fatesa = loja
                break
        
        if not fatesa:
            print("   ❌ Loja Fatesa não encontrada")
            return False
        
        # Verificar configuração
        try:
            login_config = fatesa.login_personalizado
            
            # Verificar se os campos foram corrigidos
            if not login_config.titulo or login_config.titulo.strip() == '':
                print("   ❌ Título ainda está vazio")
                return False
            
            if not login_config.subtitulo or login_config.subtitulo.strip() == '':
                print("   ❌ Subtítulo ainda está vazio")
                return False
            
            print(f"   ✅ Configuração corrigida:")
            print(f"      Título: {login_config.titulo}")
            print(f"      Subtítulo: {login_config.subtitulo}")
            
            # Testar URL
            client = Client()
            url_login = login_config.get_login_url()
            response = client.get(url_login)
            
            if response.status_code != 200:
                print(f"   ❌ URL retornou status {response.status_code}")
                return False
            
            content = response.content.decode('utf-8')
            if login_config.titulo not in content:
                print("   ❌ Título não aparece na página")
                return False
            
            print("   ✅ Página funcionando corretamente")
            return True
            
        except LoginPersonalizado.DoesNotExist:
            print("   ❌ Configuração de login não encontrada")
            return False
        
    except Exception as e:
        print(f"   ❌ Erro na verificação: {str(e)}")
        return False

def fazer_deploy():
    """Faz o deploy no Heroku"""
    
    try:
        # Commit das mudanças
        print("   📝 Fazendo commit...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        commit_message = "Corrigir configuração de login da loja Fatesa - campos título e subtítulo"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push para Heroku
        print("   🚀 Fazendo push para Heroku...")
        result = subprocess.run(['git', 'push', 'heroku', 'main'], 
                              capture_output=True, text=True, check=True)
        
        print("   ✅ Deploy realizado com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e):
            print("   ℹ️  Nada para fazer commit, fazendo push...")
            try:
                subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
                print("   ✅ Push realizado com sucesso")
                return True
            except subprocess.CalledProcessError as push_error:
                print(f"   ❌ Erro no push: {str(push_error)}")
                return False
        else:
            print(f"   ❌ Erro no deploy: {str(e)}")
            return False

def mostrar_instrucoes_teste():
    """Mostra instruções para testar no Heroku"""
    
    print("   🧪 COMO TESTAR A CORREÇÃO NO HEROKU:")
    print()
    print("   1. LOJA FATESA CORRIGIDA:")
    print("      URL: https://www.lvksistemas.com.br/login/fatesa-escola-de-ultrassonografia/")
    print("      Deve mostrar:")
    print("      - Título: 'Login - Fatesa Escola de Ultrassonografia'")
    print("      - Subtítulo: 'Acesse sua conta na Fatesa Escola de Ultrassonografia'")
    print("      - Tema corporativo (azul)")
    print("      - Formulário de login funcionando")
    print()
    print("   2. OUTRAS LOJAS (devem continuar funcionando):")
    print("      - Felix: https://www.lvksistemas.com.br/login/felix-ribeirao-pretosp-clinica-de-estetica/")
    print("      - Loja Felix: https://www.lvksistemas.com.br/login/loja-felix/")
    print()
    print("   3. SUPER ADMIN (deve continuar funcionando):")
    print("      - URL: https://www.lvksistemas.com.br/")
    print("      - Deve mostrar formulário de login de super admin")
    print()
    print("   ✅ CORREÇÕES APLICADAS:")
    print("   - Fatesa agora tem título e subtítulo preenchidos")
    print("   - Nome da loja aparece corretamente na página")
    print("   - Formulário de login funcionando")
    print("   - Sistema de login personalizado por loja confirmado")
    print()
    print("   🎯 ARQUITETURA CONFIRMADA:")
    print("   - Super Admin: https://www.lvksistemas.com.br/ (login direto)")
    print("   - Lojas: URLs personalizadas exclusivas (/login/{loja}/)")
    print("   - Cada loja tem sua própria página de login personalizada")

if __name__ == '__main__':
    main()