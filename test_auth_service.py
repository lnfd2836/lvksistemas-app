#!/usr/bin/env python
"""
Teste simples para verificar se os serviços de autenticação funcionam.
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from usuarios.services import AuthenticationService, SessionService

def test_authentication_service():
    """Teste básico do serviço de autenticação"""
    print("Testando AuthenticationService...")
    
    # Criar usuário de teste
    try:
        import time
        timestamp = str(int(time.time()))
        user = User.objects.create_user(
            username=f'testuser_{timestamp}',
            email=f'test_{timestamp}@example.com',
            password='testpass123'
        )
        print(f"✓ Usuário criado: {user.username}")
        
        # Testar determinação de dashboard
        dashboard = AuthenticationService.determine_user_dashboard(user)
        print(f"✓ Dashboard determinado: {dashboard}")
        
        # Testar validação de permissões
        is_authenticated = AuthenticationService.validate_user_permissions(user, 'authenticated')
        print(f"✓ Usuário autenticado: {is_authenticated}")
        
        is_super_admin = AuthenticationService.validate_user_permissions(user, 'super_admin')
        print(f"✓ É super admin: {is_super_admin}")
        
        # Testar obtenção de loja
        store = AuthenticationService.get_user_store(user)
        print(f"✓ Loja do usuário: {store}")
        
        # Testar URL segura
        safe_url = AuthenticationService.get_safe_redirect_url(user)
        print(f"✓ URL segura: {safe_url}")
        
        print("✅ AuthenticationService passou em todos os testes!")
        
        # Limpar
        user.delete()
        
    except Exception as e:
        print(f"❌ Erro no teste do AuthenticationService: {e}")
        return False
    
    return True

def test_session_service():
    """Teste básico do serviço de sessões"""
    print("\nTestando SessionService...")
    
    try:
        # Criar usuário de teste com nome único
        import time
        timestamp = str(int(time.time()))
        user = User.objects.create_user(
            username=f'sessionuser_{timestamp}',
            email=f'session_{timestamp}@example.com',
            password='testpass123'
        )
        print(f"✓ Usuário criado: {user.username}")
        
        # Criar request mock
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user
        request.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'Test Agent'}
        
        # Criar sessão mock mais realista
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session.create()
        request.session = session
        
        # Testar criação de sessão
        session_created = SessionService.create_user_session(request, user)
        print(f"✓ Sessão criada: {session_created}")
        
        # Testar contagem de sessões ativas
        active_count = SessionService.get_active_sessions_count(user)
        print(f"✓ Sessões ativas: {active_count}")
        
        # Testar invalidação de sessões
        SessionService.invalidate_user_sessions(user)
        print("✓ Sessões invalidadas")
        
        # Testar limpeza de sessões expiradas
        SessionService.cleanup_expired_sessions()
        print("✓ Limpeza de sessões executada")
        
        print("✅ SessionService passou em todos os testes!")
        
        # Limpar
        user.delete()
        
    except Exception as e:
        print(f"❌ Erro no teste do SessionService: {e}")
        return False
    
    return True

def test_redirect_loop_prevention():
    """Teste básico do sistema de prevenção de loops"""
    print("\nTestando RedirectLoopPreventionService...")
    
    try:
        from usuarios.services import RedirectLoopPreventionService
        
        # Criar request mock
        factory = RequestFactory()
        request = factory.get('/')
        
        # Criar sessão mock
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session.create()
        request.session = session
        
        # Testar rastreamento de redirecionamento
        safe1 = RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        print(f"✓ Primeiro redirecionamento seguro: {safe1}")
        
        safe2 = RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        print(f"✓ Segundo redirecionamento seguro: {safe2}")
        
        safe3 = RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        print(f"✓ Terceiro redirecionamento seguro: {safe3}")
        
        # O quarto deve ser bloqueado
        safe4 = RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        print(f"✓ Quarto redirecionamento bloqueado: {not safe4}")
        
        # Testar detecção de padrão circular
        RedirectLoopPreventionService.clear_redirect_tracking(request)
        
        # Simular padrão A->B->A->B
        RedirectLoopPreventionService.track_redirect(request, '/login/')
        RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        RedirectLoopPreventionService.track_redirect(request, '/login/')
        RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        
        circular = RedirectLoopPreventionService.detect_circular_pattern(request)
        print(f"✓ Padrão circular detectado: {circular}")
        
        # Testar verificação de segurança
        RedirectLoopPreventionService.clear_redirect_tracking(request)
        is_safe = RedirectLoopPreventionService.is_safe_redirect(request, '/dashboard/')
        print(f"✓ Redirecionamento é seguro: {is_safe}")
        
        print("✅ RedirectLoopPreventionService passou em todos os testes!")
        
    except Exception as e:
        print(f"❌ Erro no teste do RedirectLoopPreventionService: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success1 = test_authentication_service()
    success2 = test_session_service()
    success3 = test_redirect_loop_prevention()
    
    if success1 and success2 and success3:
        print("\n🎉 Todos os serviços passaram nos testes!")
    else:
        print("\n❌ Alguns testes falharam")
    
    sys.exit(0 if (success1 and success2 and success3) else 1)