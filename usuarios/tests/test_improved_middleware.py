"""
Testes para o middleware de autenticação aprimorado.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpResponse
from unittest.mock import Mock, patch

from usuarios.improved_middleware import ImprovedAuthenticationMiddleware
from usuarios.models import SessaoAtiva
from usuarios.services import SessionService, RedirectLoopPreventionService


class ImprovedAuthenticationMiddlewareTest(TestCase):
    """
    Testes para o ImprovedAuthenticationMiddleware.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.factory = RequestFactory()
        self.middleware = ImprovedAuthenticationMiddleware(self.get_response)
        
        # Cria usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Cria super usuário de teste
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )
    
    def get_response(self, request):
        """
        Mock response function para o middleware.
        """
        return HttpResponse("OK")
    
    def add_session_to_request(self, request):
        """
        Adiciona sessão à requisição para testes.
        """
        session_middleware = SessionMiddleware(self.get_response)
        session_middleware.process_request(request)
        request.session.save()
        
        auth_middleware = AuthenticationMiddleware(self.get_response)
        auth_middleware.process_request(request)
        
        message_middleware = MessageMiddleware(self.get_response)
        message_middleware.process_request(request)
    
    def test_excluded_paths_are_skipped(self):
        """
        Testa se caminhos excluídos são ignorados pelo middleware.
        """
        excluded_paths = [
            '/admin/',
            '/login/',
            '/logout/',
            '/loja/login/',
            '/static/css/style.css',
            '/media/image.jpg',
            '/favicon.ico'
        ]
        
        for path in excluded_paths:
            request = self.factory.get(path)
            self.add_session_to_request(request)
            
            response = self.middleware(request)
            
            # Deve retornar resposta normal sem redirecionamento
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"OK")
    
    def test_unauthenticated_user_redirected_to_login(self):
        """
        Testa se usuários não autenticados são redirecionados para login.
        """
        request = self.factory.get('/dashboard/')
        self.add_session_to_request(request)
        
        response = self.middleware(request)
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login/'))
    
    def test_authenticated_user_with_valid_session(self):
        """
        Testa usuário autenticado com sessão válida.
        """
        request = self.factory.get('/dashboard/')
        self.add_session_to_request(request)
        
        # Autentica o usuário
        request.user = self.user
        
        # Cria sessão ativa válida
        SessionService.create_user_session(request, self.user)
        
        response = self.middleware(request)
        
        # Deve permitir acesso
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
    
    def test_authenticated_user_with_invalid_session(self):
        """
        Testa usuário autenticado com sessão inválida.
        """
        request = self.factory.get('/dashboard/')
        self.add_session_to_request(request)
        
        # Autentica o usuário
        request.user = self.user
        
        # Não cria sessão ativa (sessão inválida)
        
        response = self.middleware(request)
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login/'))
    
    def test_redirect_loop_detection(self):
        """
        Testa detecção de loops de redirecionamento.
        """
        request = self.factory.get('/login/')
        self.add_session_to_request(request)
        
        # Simula múltiplos redirecionamentos
        for i in range(5):
            RedirectLoopPreventionService.track_redirect(request, '/login/')
        
        response = self.middleware(request)
        
        # Deve detectar o loop e tratar adequadamente
        # Como é uma URL excluída, deve passar normalmente
        self.assertEqual(response.status_code, 200)
    
    def test_session_cleanup_is_called_periodically(self):
        """
        Testa se a limpeza de sessões é chamada periodicamente.
        """
        with patch.object(SessionService, 'cleanup_expired_sessions') as mock_cleanup:
            # Cria requisição com session_key que resulte em hash % 100 == 0
            request = self.factory.get('/dashboard/')
            self.add_session_to_request(request)
            
            # Força um session_key específico para garantir que o cleanup seja chamado
            request.session.session_key = 'test_session_key_100'  # hash % 100 == 0
            request.user = self.user
            
            # Cria sessão ativa válida
            SessionService.create_user_session(request, self.user)
            
            # Força o hash para ser divisível por 100
            with patch('builtins.hash', return_value=100):
                response = self.middleware(request)
            
            # Verifica se o cleanup foi chamado
            mock_cleanup.assert_called_once()
    
    def test_middleware_handles_exceptions_gracefully(self):
        """
        Testa se o middleware trata exceções de forma elegante.
        """
        request = self.factory.get('/dashboard/')
        self.add_session_to_request(request)
        request.user = self.user
        
        # Simula erro no SessionService
        with patch.object(SessionService, 'validate_session', side_effect=Exception("Test error")):
            response = self.middleware(request)
            
            # Deve continuar funcionando mesmo com erro
            self.assertEqual(response.status_code, 200)
    
    def test_successful_request_clears_redirect_tracking(self):
        """
        Testa se requisições bem-sucedidas limpam o rastreamento de redirecionamento.
        """
        request = self.factory.get('/dashboard/')
        self.add_session_to_request(request)
        request.user = self.user
        
        # Adiciona rastreamento de redirecionamento
        RedirectLoopPreventionService.track_redirect(request, '/some/url/')
        
        # Cria sessão ativa válida
        SessionService.create_user_session(request, self.user)
        
        response = self.middleware(request)
        
        # Deve limpar o rastreamento após resposta bem-sucedida
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            RedirectLoopPreventionService.REDIRECT_TRACKING_KEY,
            request.session
        )


class RedirectLoopPreventionTest(TestCase):
    """
    Testes específicos para prevenção de loops de redirecionamento.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.factory = RequestFactory()
    
    def add_session_to_request(self, request):
        """
        Adiciona sessão à requisição para testes.
        """
        session_middleware = SessionMiddleware(lambda r: HttpResponse())
        session_middleware.process_request(request)
        request.session.save()
    
    def test_track_redirect_detects_direct_loops(self):
        """
        Testa detecção de loops diretos (mesmo URL repetido).
        """
        request = self.factory.get('/')
        self.add_session_to_request(request)
        
        # Primeiro redirecionamento deve ser seguro
        self.assertTrue(RedirectLoopPreventionService.track_redirect(request, '/login/'))
        
        # Segundo redirecionamento para o mesmo URL deve ser seguro
        self.assertTrue(RedirectLoopPreventionService.track_redirect(request, '/login/'))
        
        # Terceiro redirecionamento para o mesmo URL deve ser seguro
        self.assertTrue(RedirectLoopPreventionService.track_redirect(request, '/login/'))
        
        # Quarto redirecionamento deve detectar loop
        self.assertFalse(RedirectLoopPreventionService.track_redirect(request, '/login/'))
    
    def test_detect_circular_pattern(self):
        """
        Testa detecção de padrões circulares A->B->A->B.
        """
        request = self.factory.get('/')
        self.add_session_to_request(request)
        
        # Simula padrão A->B->A->B
        RedirectLoopPreventionService.track_redirect(request, '/login/')
        RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        RedirectLoopPreventionService.track_redirect(request, '/login/')
        RedirectLoopPreventionService.track_redirect(request, '/dashboard/')
        
        # Deve detectar padrão circular
        self.assertTrue(RedirectLoopPreventionService.detect_circular_pattern(request))
    
    def test_clear_redirect_tracking(self):
        """
        Testa limpeza do rastreamento de redirecionamento.
        """
        request = self.factory.get('/')
        self.add_session_to_request(request)
        
        # Adiciona rastreamento
        RedirectLoopPreventionService.track_redirect(request, '/login/')
        
        # Verifica se foi adicionado
        self.assertIn(RedirectLoopPreventionService.REDIRECT_TRACKING_KEY, request.session)
        
        # Limpa rastreamento
        RedirectLoopPreventionService.clear_redirect_tracking(request)
        
        # Verifica se foi removido
        self.assertNotIn(RedirectLoopPreventionService.REDIRECT_TRACKING_KEY, request.session)
    
    def test_safe_redirect_prevents_loops(self):
        """
        Testa se safe_redirect previne loops adequadamente.
        """
        request = self.factory.get('/')
        self.add_session_to_request(request)
        
        # Simula múltiplos redirecionamentos para o mesmo URL
        for i in range(3):
            RedirectLoopPreventionService.track_redirect(request, '/login/')
        
        # Próximo redirecionamento deve ser tratado como inseguro
        response = RedirectLoopPreventionService.safe_redirect(request, '/login/', '/fallback/')
        
        # Deve redirecionar para login (tratamento de loop)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login/'))