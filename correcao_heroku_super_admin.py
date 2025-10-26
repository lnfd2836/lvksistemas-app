#!/usr/bin/env python
"""
Script de correção específica para o problema do super admin no Heroku
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from lojas.models import Loja
from lojas.models_login import LoginPersonalizado

def main():
    print("🔧 CORREÇÃO ESPECÍFICA HEROKU - SUPER ADMIN")
    print("=" * 50)
    
    # 1. Verificar se há apenas uma loja ativa
    lojas_ativas = Loja.objects.filter(status='ativa')
    print(f"Lojas ativas: {lojas_ativas.count()}")
    
    if lojas_ativas.count() == 1:
        loja = lojas_ativas.first()
        print(f"Loja única: {loja.nome}")
        
        # Verificar se é a Fatesa
        if 'fatesa' in loja.nome.lower():
            print("✅ Loja Fatesa detectada - isso explica o redirecionamento")
            
            # Verificar configuração de login
            try:
                login_config = loja.login_personalizado
                print(f"URL de login: {login_config.get_login_url()}")
                
                # A correção pode ser criar mais lojas ou ajustar a lógica
                print("💡 SOLUÇÕES POSSÍVEIS:")
                print("1. Criar mais lojas ativas para forçar seleção")
                print("2. Ajustar lógica do smart_redirect")
                print("3. Verificar se super admin está sendo detectado corretamente")
                
            except LoginPersonalizado.DoesNotExist:
                print("❌ Loja sem configuração de login")
    
    # 2. Verificar super admins
    super_admins = User.objects.filter(is_superuser=True, is_active=True)
    print(f"\nSuper admins ativos: {super_admins.count()}")
    
    for admin in super_admins:
        print(f"- {admin.username}")
        
        # Testar AuthenticationService
        from dashboard.services.authentication import AuthenticationService
        try:
            dashboard_url = AuthenticationService.determine_user_dashboard(admin)
            print(f"  Dashboard URL: {dashboard_url}")
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")

if __name__ == '__main__':
    main()
