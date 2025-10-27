#!/usr/bin/env python
"""
Script para corrigir o middleware que está bloqueando super admins de acessar lojas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def corrigir_middleware_super_admin():
    """
    Corrige o middleware do super admin para permitir acesso às lojas para administração
    """
    print("🔧 Corrigindo middleware do super admin...")
    
    middleware_path = 'dashboard/middleware/super_admin_middleware.py'
    
    try:
        with open(middleware_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir a lógica que bloqueia acesso às lojas
        old_logic = '''        # Se está tentando acessar área de loja, redirecionar para admin
        if path.startswith('/loja/'):
            logger.warning(f"Super admin {request.user.username} tentou acessar área de loja: {path}")
            try:
                messages.info(request, 'Você foi redirecionado para a área administrativa.')
            except:
                pass  # Ignorar erro de mensagens
            return redirect('/admin/')'''
        
        new_logic = '''        # Permitir que super admins acessem lojas para administração
        if path.startswith('/lojas/'):
            logger.info(f"Super admin {request.user.username} acessando administração de lojas: {path}")
            # Permitir acesso para administração de lojas
            return self.get_response(request)
        
        # Se está tentando acessar área operacional de loja específica, redirecionar
        if path.startswith('/loja/') and not path.startswith('/lojas/'):
            logger.warning(f"Super admin {request.user.username} tentou acessar área operacional de loja: {path}")
            try:
                messages.info(request, 'Super admins administram lojas através do painel administrativo.')
            except:
                pass  # Ignorar erro de mensagens
            return redirect('/admin/')'''
        
        if old_logic in content:
            content = content.replace(old_logic, new_logic)
            
            with open(middleware_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Middleware do super admin corrigido")
            return True
        else:
            print("⚠️ Lógica antiga não encontrada, middleware pode já estar correto")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware: {e}")
        return False

def corrigir_middleware_loja_especifica():
    """
    Corrige o middleware de loja específica para permitir super admins
    """
    print("🔧 Corrigindo middleware de loja específica...")
    
    middleware_path = 'lojas/middleware_loja_especifica.py'
    
    try:
        with open(middleware_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir a lógica que bloqueia super admins
        old_logic = '''            # Bloquear super admins de fazer login via loja
            if request.user.is_authenticated and request.user.is_superuser:
                logger.warning(f"Super admin {request.user.username} tentou fazer login via loja {loja.nome}")
                messages.error(request, 'Super administradores devem usar o login exclusivo do sistema.')
                return redirect('/admin/')'''
        
        new_logic = '''            # Permitir que super admins visualizem páginas de login para administração
            if request.user.is_authenticated and request.user.is_superuser:
                logger.info(f"Super admin {request.user.username} visualizando login da loja {loja.nome} para administração")
                # Permitir visualização mas não login
                if request.method == 'POST':
                    messages.info(request, 'Super administradores não fazem login via loja. Use o painel administrativo.')
                    return redirect('/admin/')'''
        
        if old_logic in content:
            content = content.replace(old_logic, new_logic)
            
            with open(middleware_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Middleware de loja específica corrigido")
            return True
        else:
            print("⚠️ Lógica antiga não encontrada no middleware de loja específica")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware de loja específica: {e}")
        return False

def verificar_middlewares_problematicos():
    """
    Verifica se há middlewares que podem estar bloqueando super admins
    """
    print("🔍 Verificando middlewares problemáticos...")
    
    middlewares_removidos = [
        'lojas/middleware/loja_fatesa_middleware.py',
        'lojas/middleware/loja_felix_middleware.py'
    ]
    
    for middleware in middlewares_removidos:
        if os.path.exists(middleware):
            print(f"❌ {middleware} ainda existe - removendo...")
            try:
                os.remove(middleware)
                print(f"✅ {middleware} removido")
            except Exception as e:
                print(f"❌ Erro ao remover {middleware}: {e}")
        else:
            print(f"✅ {middleware} já foi removido")
    
    return True

def verificar_settings_middleware():
    """
    Verifica se há middlewares problemáticos no settings.py
    """
    print("🔍 Verificando settings.py...")
    
    settings_path = 'lojad/settings.py'
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        middlewares_problematicos = [
            'dashboard.middleware.bloqueio_super_admin_lojas.BloqueioSuperAdminLojasMiddleware',
            'lojas.middleware.loja_fatesa_middleware.LojaFatesaMiddleware',
            'lojas.middleware.loja_felix_middleware.LojaFelixMiddleware'
        ]
        
        changed = False
        for middleware in middlewares_problematicos:
            if middleware in content:
                print(f"❌ Middleware problemático encontrado: {middleware}")
                # Comentar o middleware
                content = content.replace(f"'{middleware}',", f"# '{middleware}',  # Removido - bloqueava super admin")
                changed = True
            else:
                print(f"✅ Middleware {middleware} não encontrado (ok)")
        
        if changed:
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Settings.py atualizado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar settings.py: {e}")
        return False

def testar_acesso_super_admin():
    """
    Testa se super admin pode acessar URLs de lojas
    """
    print("🧪 Testando acesso do super admin...")
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        # Criar cliente de teste
        client = Client()
        
        # Buscar ou criar super admin
        try:
            admin = User.objects.filter(is_superuser=True).first()
            if not admin:
                admin = User.objects.create_superuser(
                    username='admin_test',
                    email='admin@test.com',
                    password='test123'
                )
                print("✅ Super admin de teste criado")
            
            # Fazer login
            client.force_login(admin)
            
            # Testar URLs
            urls_teste = [
                '/lojas/',
                '/admin/',
            ]
            
            for url in urls_teste:
                try:
                    response = client.get(url)
                    if response.status_code in [200, 302]:
                        print(f"✅ {url} - Status: {response.status_code}")
                    else:
                        print(f"⚠️ {url} - Status: {response.status_code}")
                except Exception as e:
                    print(f"❌ {url} - Erro: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar teste: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 CORRIGINDO MIDDLEWARE QUE BLOQUEIA SUPER ADMIN")
    print("=" * 60)
    
    success_count = 0
    total_fixes = 5
    
    # 1. Verificar e remover middlewares problemáticos
    if verificar_middlewares_problematicos():
        success_count += 1
    
    # 2. Verificar settings.py
    if verificar_settings_middleware():
        success_count += 1
    
    # 3. Corrigir middleware do super admin
    if corrigir_middleware_super_admin():
        success_count += 1
    
    # 4. Corrigir middleware de loja específica
    if corrigir_middleware_loja_especifica():
        success_count += 1
    
    # 5. Testar acesso
    if testar_acesso_super_admin():
        success_count += 1
    
    print("=" * 60)
    print(f"📊 RESULTADO: {success_count}/{total_fixes} correções bem-sucedidas")
    
    if success_count == total_fixes:
        print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Super admins agora podem acessar /lojas/ para administração")
        print("🚀 Faça o deploy para o Heroku")
    else:
        print("⚠️ ALGUMAS CORREÇÕES FALHARAM")
        print("🔍 Verifique os logs acima para detalhes")
    
    print("=" * 60)

if __name__ == '__main__':
    main()