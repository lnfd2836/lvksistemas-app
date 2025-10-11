#!/usr/bin/env python3
"""
Debug do sistema de troca obrigatória de senha
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario

def verificar_usuarios_com_troca_obrigatoria():
    """Verifica usuários que precisam trocar senha"""
    
    print("=" * 80)
    print("🔍 VERIFICAÇÃO DE USUÁRIOS COM TROCA OBRIGATÓRIA")
    print("=" * 80)
    
    # Buscar todos os usuários
    usuarios = User.objects.all()
    
    print(f"📊 TOTAL DE USUÁRIOS: {usuarios.count()}")
    
    usuarios_com_troca = []
    usuarios_sem_perfil = []
    
    for user in usuarios:
        print(f"\n👤 USUÁRIO: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Superuser: {user.is_superuser}")
        
        # Verificar se tem perfil
        try:
            perfil = user.perfil
            print(f"   ✅ Tem perfil: ID {perfil.id}")
            print(f"   requires_password_change: {perfil.requires_password_change}")
            print(f"   deve_trocar_senha: {perfil.deve_trocar_senha}")
            print(f"   ultimo_acesso: {perfil.ultimo_acesso}")
            print(f"   provisional_password_created: {perfil.provisional_password_created}")
            
            if perfil.requires_password_change or perfil.deve_trocar_senha:
                usuarios_com_troca.append(user)
                print(f"   🔄 PRECISA TROCAR SENHA")
            else:
                print(f"   ✅ Não precisa trocar senha")
                
        except PerfilUsuario.DoesNotExist:
            usuarios_sem_perfil.append(user)
            print(f"   ❌ SEM PERFIL")
    
    print(f"\n📋 RESUMO:")
    print(f"   Usuários com troca obrigatória: {len(usuarios_com_troca)}")
    print(f"   Usuários sem perfil: {len(usuarios_sem_perfil)}")
    
    return usuarios_com_troca, usuarios_sem_perfil

def criar_usuario_teste():
    """Cria um usuário de teste para verificar o fluxo"""
    
    print(f"\n{'='*80}")
    print("🧪 CRIANDO USUÁRIO DE TESTE")
    print(f"{'='*80}")
    
    # Verificar se já existe
    username = "teste_troca_senha"
    
    try:
        user_existente = User.objects.get(username=username)
        print(f"⚠️  Usuário {username} já existe. Removendo...")
        user_existente.delete()
    except User.DoesNotExist:
        pass
    
    # Criar novo usuário
    user = User.objects.create_user(
        username=username,
        email="teste@exemplo.com",
        password="senha123",
        first_name="Teste",
        last_name="Troca Senha"
    )
    
    print(f"✅ Usuário criado: {user.username}")
    
    # Criar perfil com troca obrigatória
    perfil = PerfilUsuario.objects.create(
        user=user,
        requires_password_change=True,
        deve_trocar_senha=True,
        is_super_admin=True
    )
    
    print(f"✅ Perfil criado com troca obrigatória")
    print(f"   requires_password_change: {perfil.requires_password_change}")
    print(f"   deve_trocar_senha: {perfil.deve_trocar_senha}")
    
    return user

def testar_middleware():
    """Testa se o middleware está funcionando"""
    
    print(f"\n{'='*80}")
    print("🔧 TESTANDO MIDDLEWARE")
    print(f"{'='*80}")
    
    from usuarios.mandatory_password_middleware import MandatoryPasswordChangeMiddleware
    
    # Criar instância do middleware
    def dummy_get_response(request):
        return None
    
    middleware = MandatoryPasswordChangeMiddleware(dummy_get_response)
    
    print(f"✅ Middleware instanciado")
    print(f"   URLs isentas: {len(middleware.exempt_urls)}")
    print(f"   Prefixos isentos: {len(middleware.exempt_prefixes)}")
    
    # Testar com usuário que precisa trocar senha
    usuarios_com_troca, _ = verificar_usuarios_com_troca_obrigatoria()
    
    if usuarios_com_troca:
        user = usuarios_com_troca[0]
        needs_change = middleware.user_needs_password_change(user)
        print(f"\n🧪 TESTE COM {user.username}:")
        print(f"   Middleware detecta necessidade: {needs_change}")
    else:
        print(f"\n⚠️  Nenhum usuário com troca obrigatória para testar")

def verificar_configuracao():
    """Verifica se tudo está configurado corretamente"""
    
    print(f"\n{'='*80}")
    print("⚙️  VERIFICAÇÃO DE CONFIGURAÇÃO")
    print(f"{'='*80}")
    
    # Verificar middleware no settings
    from django.conf import settings
    
    middlewares = settings.MIDDLEWARE
    middleware_troca = 'usuarios.mandatory_password_middleware.MandatoryPasswordChangeMiddleware'
    
    if middleware_troca in middlewares:
        print(f"✅ Middleware configurado no settings")
        posicao = middlewares.index(middleware_troca)
        print(f"   Posição: {posicao + 1} de {len(middlewares)}")
    else:
        print(f"❌ Middleware NÃO configurado no settings")
    
    # Verificar URLs
    try:
        from django.urls import reverse
        url_troca = reverse('change_mandatory_password')
        print(f"✅ URL de troca configurada: {url_troca}")
    except Exception as e:
        print(f"❌ Erro na URL de troca: {e}")
    
    # Verificar template
    import os
    template_path = 'templates/usuarios/change_mandatory_password.html'
    if os.path.exists(template_path):
        print(f"✅ Template existe: {template_path}")
    else:
        print(f"❌ Template não encontrado: {template_path}")

def main():
    """Função principal"""
    
    print("🚀 DEBUG DO SISTEMA DE TROCA OBRIGATÓRIA DE SENHA")
    
    # Verificar configuração
    verificar_configuracao()
    
    # Verificar usuários existentes
    usuarios_com_troca, usuarios_sem_perfil = verificar_usuarios_com_troca_obrigatoria()
    
    # Criar usuário de teste se necessário
    if not usuarios_com_troca:
        print(f"\n🧪 Criando usuário de teste...")
        criar_usuario_teste()
    
    # Testar middleware
    testar_middleware()
    
    print(f"\n{'='*80}")
    print("📋 DIAGNÓSTICO")
    print(f"{'='*80}")
    
    if usuarios_com_troca:
        print("✅ Há usuários que precisam trocar senha")
        print("✅ Sistema deveria estar redirecionando para troca")
        
        print(f"\n🎯 TESTE MANUAL:")
        print(f"   1. Faça login com: {usuarios_com_troca[0].username}")
        print(f"   2. Deveria ser redirecionado para /usuarios/change-mandatory-password/")
        print(f"   3. Se não for redirecionado, há problema no middleware")
        
    else:
        print("⚠️  Nenhum usuário precisa trocar senha")
        print("🧪 Usuário de teste criado para verificação")
    
    if usuarios_sem_perfil:
        print(f"\n⚠️  {len(usuarios_sem_perfil)} usuários sem perfil:")
        for user in usuarios_sem_perfil:
            print(f"   - {user.username}")

if __name__ == "__main__":
    main()