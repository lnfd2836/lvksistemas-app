"""
Testes unitários para os serviços de autenticação.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import Mock, patch
from usuarios.services import AuthenticationService
from lojas.models import Loja


class AuthenticationServiceTest(TestCase):
    """Testes para o AuthenticationService"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.factory = RequestFactory()
        
        # Criar usuário super admin
        self.super_admin = User.objects.create_user(
            username='superadmin',
            email='super@test.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        # Criar usuário comum
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@test.com',
            password='testpass123'
        )
        
        # Criar loja
        self.loja = Loja.objects.create(
            nome='Loja Teste',
            cnpj='12.345.678/0001-90',
            email='loja@test.com',
            telefone='11999999999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            cep='01234-567',
            admin_user=self.regular_user
        )
    
    def test_determine_user_dashboard_super_admin_with_store(self):
        """Testa determinação de dashboard para super admin com loja"""
        # Super admin com loja associada
        super_admin_with_store = User.objects.create_user(
            username='superadmin_store',
            email='superstore@test.com',
            password='testpass123',
            is_superuser=True
        )
        
        loja_super = Loja.objects.create(
            nome='Loja Super Admin',
            cnpj='98.765.432/0001-10',
            email='superstore@test.com',
            telefone='11888888888',
            endereco='Rua Super, 456',
            cidade='São Paulo',
            cep='01234-567',
            admin_user=super_admin_with_store
        )
        
        result = AuthenticationService.determine_user_dashboard(super_admin_with_store)
        self.assertEqual(result, 'dashboard_loja')
    
    def test_determine_user_dashboard_super_admin_without_store(self):
        """Testa determinação de dashboard para super admin sem loja"""
        result = AuthenticationService.determine_user_dashboard(self.super_admin)
        self.assertEqual(result, 'dashboard_super_admin')
    
    def test_determine_user_dashboard_regular_user_with_store(self):
        """Testa determinação de dashboard para usuário comum com loja"""
        result = AuthenticationService.determine_user_dashboard(self.regular_user)
        self.assertEqual(result, 'dashboard_loja')
    
    def test_determine_user_dashboard_regular_user_without_store(self):
        """Testa determinação de dashboard para usuário comum sem loja"""
        user_without_store = User.objects.create_user(
            username='nostore',
            email='nostore@test.com',
            password='testpass123'
        )
        
        result = AuthenticationService.determine_user_dashboard(user_without_store)
        self.assertEqual(result, 'login')
    
    def test_can_access_store_dashboard_super_admin(self):
        """Testa acesso ao dashboard de loja para super admin"""
        can_access, message = AuthenticationService.can_access_store_dashboard(self.super_admin)
        self.assertTrue(can_access)
        self.assertEqual(message, "")
    
    def test_can_access_store_dashboard_store_owner(self):
        """Testa acesso ao dashboard para dono da loja"""
        can_access, message = AuthenticationService.can_access_store_dashboard(
            self.regular_user, self.loja
        )
        self.assertTrue(can_access)
        self.assertEqual(message, "")
    
    def test_can_access_store_dashboard_wrong_store(self):
        """Testa acesso negado para loja errada"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='testpass123'
        )
        
        other_loja = Loja.objects.create(
            nome='Outra Loja',
            cnpj='11.111.111/0001-11',
            email='other@test.com',
            telefone='11777777777',
            endereco='Rua Outra, 789',
            cidade='São Paulo',
            cep='01234-567',
            admin_user=other_user
        )
        
        can_access, message = AuthenticationService.can_access_store_dashboard(
            self.regular_user, other_loja
        )
        self.assertFalse(can_access)
        self.assertIn("não tem permissão", message)
    
    def test_can_access_store_dashboard_unauthenticated(self):
        """Testa acesso negado para usuário não autenticado"""
        unauthenticated_user = Mock()
        unauthenticated_user.is_authenticated = False
        
        can_access, message = AuthenticationService.can_access_store_dashboard(unauthenticated_user)
        self.assertFalse(can_access)
        self.assertEqual(message, "Usuário não autenticado")
    
    def test_get_user_store_success(self):
        """Testa obtenção da loja do usuário com sucesso"""
        store = AuthenticationService.get_user_store(self.regular_user)
        self.assertEqual(store, self.loja)
    
    def test_get_user_store_no_store(self):
        """Testa obtenção da loja para usuário sem loja"""
        store = AuthenticationService.get_user_store(self.super_admin)
        self.assertIsNone(store)
    
    def test_validate_user_permissions_super_admin(self):
        """Testa validação de permissões para super admin"""
        self.assertTrue(
            AuthenticationService.validate_user_permissions(self.super_admin, 'super_admin')
        )
        self.assertTrue(
            AuthenticationService.validate_user_permissions(self.super_admin, 'authenticated')
        )
    
    def test_validate_user_permissions_store_admin(self):
        """Testa validação de permissões para admin de loja"""
        self.assertFalse(
            AuthenticationService.validate_user_permissions(self.regular_user, 'super_admin')
        )
        self.assertTrue(
            AuthenticationService.validate_user_permissions(self.regular_user, 'store_admin')
        )
        self.assertTrue(
            AuthenticationService.validate_user_permissions(self.regular_user, 'authenticated')
        )
    
    def test_validate_user_permissions_unauthenticated(self):
        """Testa validação de permissões para usuário não autenticado"""
        unauthenticated_user = Mock()
        unauthenticated_user.is_authenticated = False
        
        self.assertFalse(
            AuthenticationService.validate_user_permissions(unauthenticated_user, 'authenticated')
        )
    
    def test_get_safe_redirect_url_authenticated(self):
        """Testa obtenção de URL segura para usuário autenticado"""
        url = AuthenticationService.get_safe_redirect_url(self.regular_user)
        self.assertEqual(url, 'dashboard_loja')
    
    def test_get_safe_redirect_url_unauthenticated(self):
        """Testa obtenção de URL segura para usuário não autenticado"""
        unauthenticated_user = Mock()
        unauthenticated_user.is_authenticated = False
        
        url = AuthenticationService.get_safe_redirect_url(unauthenticated_user)
        self.assertEqual(url, 'login')
    
    def test_handle_authentication_error(self):
        """Testa manipulação de erros de autenticação"""
        request = self.factory.get('/')
        request.session = {}
        
        # Adicionar suporte a mensagens
        messages = FallbackStorage(request)
        request._messages = messages
        
        response = AuthenticationService.handle_authentication_error(
            request, "Erro de teste", "login"
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login/'))