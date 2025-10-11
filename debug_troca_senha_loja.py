#!/usr/bin/env python3
"""
Debug específico para troca de senha de usuários de loja
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from lojas.models import Loja

def verificar_usuarios_loja():
    """Verifica usuários de loja e seus perfis"""
    
    print("=" * 80)
    print("🔍 VERIFICAÇÃO DE USUÁRIOS DE LOJA")
    print("=" * 80)
    
    # Buscar todas as lojas
    lojas = Loja.objects.all()
    
    print(f"📊 TOTAL DE LOJAS: {lojas.count()}")
    
    for loja in lojas:
        print(f"\n🏪 LOJA: {loja.nome}")
        print(f"   Email: {loja.email}")
        print(f"   Admin User: {loja.admin_user.username if loja.admin_user else 'Nenhum'}")
        
        if loja.admin_user:
            user = loja.admin_user
            print(f"   👤 USUÁRIO: {user.username}")
            print(f"      Email: {user.email}")
            print(f"      Ativo: {user.is_active}")
            print(f"      Superuser: {user.is_superuser}")
            
            # Verificar perfil
            try:
                perfil = user.perfil
                print(f"      ✅ Tem perfil: ID {perfil.id}")
                print(f"         requires_password_change: {perfil.requires_password_change}")
                print(f"         deve_trocar_senha: {perfil.deve_trocar_senha}")
                print(f"         is_loja_admin: {perfil.is_loja_admin}")
                print(f"         ultimo_acesso: {perfil.ultimo_acesso}")
                print(f"         provisional_password_created: {perfil.provisional_password_created}")
                
                if perfil.requires_password_change or perfil.deve_trocar_senha:
                    print(f"      🔄 PRECISA TROCAR SENHA")
                else:
                    print(f"      ✅ Não precisa trocar senha")
                    
            except PerfilUsuario.DoesNotExist:
                print(f"      ❌ SEM PERFIL - PROBLEMA IDENTIFICADO!")
                
                # Criar perfil para este usuário
                print(f"      🔧 Criando perfil...")
                perfil = PerfilUsuario.objects.create(
                    user=user,
                    requires_password_change=True,
                    deve_trocar_senha=True,
                    is_loja_admin=True,
                    is_super_admin=False,
                    provisional_password_created=loja.data_criacao if hasattr(loja, 'data_criacao') else None
                )
                print(f"      ✅ Perfil criado: ID {perfil.id}")

def testar_middleware_com_usuario_loja():
    """Testa o middleware com usuário de loja"""
    
    print(f"\n{'='*80}")
    print("🧪 TESTANDO MIDDLEWARE COM USUÁRIO DE LOJA")
    print(f"{'='*80}")
    
    # Buscar usuário de loja que precisa trocar senha
    usuarios_loja = User.objects.filter(
        loja_admin__isnull=False,
        perfil__requires_password_change=True
    )
    
    if not usuarios_loja.exists():
        # Buscar qualquer usuário de loja
        lojas = Loja.objects.filter(admin_user__isnull=False)
        if lojas.exists():
            usuario_loja = lojas.first().admin_user
        else:
            print("❌ Nenhum usuário de loja encontrado")
            return
    else:
        usuario_loja = usuarios_loja.first()
    
    print(f"👤 TESTANDO COM: {usuario_loja.username}")
    
    # Testar middleware
    from usuarios.mandatory_password_middleware import MandatoryPasswordChangeMiddleware
    
    def dummy_get_response(request):
        return None
    
    middleware = MandatoryPasswordChangeMiddleware(dummy_get_response)
    needs_change = middleware.user_needs_password_change(usuario_loja)
    
    print(f"🔍 RESULTADO DO TESTE:")
    print(f"   Middleware detecta necessidade: {needs_change}")
    
    if needs_change:
        print(f"   ✅ MIDDLEWARE FUNCIONANDO para usuários de loja")
    else:
        print(f"   ❌ MIDDLEWARE NÃO DETECTA usuários de loja")
        
        # Verificar por que não detecta
        try:
            perfil = usuario_loja.perfil
            print(f"   📋 DEBUG DO PERFIL:")
            print(f"      requires_password_change: {perfil.requires_password_change}")
            print(f"      deve_trocar_senha: {perfil.deve_trocar_senha}")
        except:
            print(f"   ❌ Usuário não tem perfil!")

def verificar_urls_login():
    """Verifica se as URLs de login estão corretas"""
    
    print(f"\n{'='*80}")
    print("🔗 VERIFICAÇÃO DAS URLs DE LOGIN")
    print(f"{'='*80}")
    
    try:
        from django.urls import reverse
        
        # URLs de login
        url_super_admin = reverse('simple_login')
        url_loja = reverse('loja_login')
        url_troca_senha = reverse('change_mandatory_password')
        
        print(f"📋 URLs CONFIGURADAS:")
        print(f"   Super Admin: {url_super_admin}")
        print(f"   Loja: {url_loja}")
        print(f"   Troca Senha: {url_troca_senha}")
        
        # Verificar middleware URLs isentas
        from usuarios.mandatory_password_middleware import MandatoryPasswordChangeMiddleware
        
        def dummy_get_response(request):
            return None
        
        middleware = MandatoryPasswordChangeMiddleware(dummy_get_response)
        
        print(f"\n📋 URLs ISENTAS NO MIDDLEWARE:")
        for url in middleware.exempt_urls:
            print(f"   {url}")
        
        # Verificar se URL de troca está isenta
        if url_troca_senha in middleware.exempt_urls:
            print(f"   ✅ URL de troca está isenta")
        else:
            print(f"   ❌ URL de troca NÃO está isenta - pode causar loop!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar URLs: {e}")

def main():
    """Função principal"""
    
    print("🚀 DEBUG ESPECÍFICO - TROCA DE SENHA PARA USUÁRIOS DE LOJA")
    
    # Verificar usuários de loja
    verificar_usuarios_loja()
    
    # Testar middleware
    testar_middleware_com_usuario_loja()
    
    # Verificar URLs
    verificar_urls_login()
    
    print(f"\n{'='*80}")
    print("📋 DIAGNÓSTICO")
    print(f"{'='*80}")
    
    print("🔍 POSSÍVEIS PROBLEMAS:")
    print("   1. ❌ Usuários de loja sem perfil (CORRIGIDO)")
    print("   2. ❌ Middleware não detecta usuários de loja")
    print("   3. ❌ URL de troca não está isenta (loop)")
    print("   4. ❌ Login da loja não passa pelo middleware")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("   1. 🔧 Corrigir perfis de usuários de loja existentes")
    print("   2. 🧪 Testar login de loja após correção")
    print("   3. 🚀 Deploy da correção")

if __name__ == "__main__":
    main()