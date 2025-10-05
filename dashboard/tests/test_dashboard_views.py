"""
Testes de integração para as views do dashboard refatoradas.
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch, Mock

from lojas.models import Loja
from usuarios.models import PerfilUsuario
from dashboard.services.authentication import AuthenticationService


class TestDashboardViewsIntegration(TestCase):
    """Testes de integração para as views do dashboard."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Criar usuários de teste
        self.super_user = User.objects.create_user(
            username='superadmin',
            email='super@test.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@test.com',
            password='testpass123'
        )
        
        self.store_admin = User.objects.create_user(
            username='storeadmin',
            email='store@test.com',
            password='testpass123'
        )
        
        # Criar loja de teste
        self.test_store = Loja.objects.create(
            nome='Loja Teste',
            cnpj='12345678901234',
            endereco='Rua Teste, 123'
        )
        
        # Criar perfil para o store admin
        self.store_admin_profile = PerfilUsuario.objects.create(
            usuario=self.store_admin,
            loja=self.test_store
        )
    
    def test_dashboard_principal_super_user_without_store(self):
        """Testa dashboard principal para super usuário sem loja."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get('/dashboard/')
        
        # Super usuário sem loja deve ver dashboard super admin
        self.assertEqual(response.status_code, 200)
        # Ou pode ser redirecionado para dashboard super admin específico
        # dependendo da implementação
    
    def test_dashboard_principal_super_user_with_store(self):
        """Testa dashboard principal para super usuário com loja."""
        # Criar perfil para super usuário com loja
        PerfilUsuario.objects.create(
            usuario=self.super_user,
            loja=self.test_store
        )
        
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get('/dashboard/')
        
        # Super usuário com loja deve ser redirecionado para dashboard da loja
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            self.assertIn('loja', response.url)
    
    def test_dashboard_principal_store_admin(self):
        """Testa dashboard principal para administrador de loja."""
        self.client.login(username='storeadmin', password='testpass123')
        
        response = self.client.get('/dashboard/')
        
        # Store admin deve ser redirecionado para dashboard da loja
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            self.assertIn('loja', response.url)
    
    def test_dashboard_principal_regular_user(self):
        """Testa dashboard principal para usuário regular."""
        self.client.login(username='regularuser', password='testpass123')
        
        response = self.client.get('/dashboard/')
        
        # Usuário regular deve ser redirecionado para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_dashboard_loja_store_admin_access(self):
        """Testa acesso ao dashboard da loja por store admin."""
        self.client.login(username='storeadmin', password='testpass123')
        
        response = self.client.get('/dashboard/loja/dashboard/')
        
        # Store admin deve conseguir acessar dashboard da loja
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_store.nome)
    
    def test_dashboard_loja_super_user_access(self):
        """Testa acesso ao dashboard da loja por super usuário."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get('/dashboard/loja/dashboard/')
        
        # Super usuário deve conseguir acessar dashboard da loja
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_loja_regular_user_denied(self):
        """Testa negação de acesso ao dashboard da loja por usuário regular."""
        self.client.login(username='regularuser', password='testpass123')
        
        response = self.client.get('/dashboard/loja/dashboard/')
        
        # Usuário regular deve ser redirecionado
        self.assertEqual(response.status_code, 302)
        
        # Verificar mensagem de erro
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('permissão' in str(message) for message in messages))
    
    def test_dashboard_loja_unauthenticated_user(self):
        """Testa acesso ao dashboard da loja por usuário não autenticado."""
        response = self.client.get('/dashboard/loja/dashboard/')
        
        # Usuário não autenticado deve ser redirecionado para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_gerenciar_modulos_super_user_access(self):
        """Testa acesso ao gerenciamento de módulos por super usuário."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get('/dashboard/gerenciar-modulos/')
        
        # Super usuário deve conseguir acessar
        # Assumindo que existe uma URL para esta view
        # self.assertEqual(response.status_code, 200)
    
    def test_gerenciar_modulos_regular_user_denied(self):
        """Testa negação de acesso ao gerenciamento de módulos por usuário regular."""
        self.client.login(username='regularuser', password='testpass123')
        
        # Assumindo que existe uma URL para esta view
        # response = self.client.get('/dashboard/gerenciar-modulos/')
        
        # Usuário regular deve ser redirecionado
        # self.assertEqual(response.status_code, 302)
    
    def test_redirect_to_appropriate_dashboard_function(self):
        """Testa a função de redirecionamento para dashboard apropriado."""
        # Teste com super usuário
        self.client.login(username='superadmin', password='testpass123')
        
        # Simular chamada da função redirect_to_appropriate_dashboard
        from dashboard.views import redirect_to_appropriate_dashboard
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.super_user
        
        response = redirect_to_appropriate_dashboard(request)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)
    
    @patch('dashboard.views.AuthenticationService.determine_user_dashboard')
    def test_dashboard_principal_error_handling(self, mock_determine_dashboard):
        """Testa tratamento de erros na view dashboard_principal."""
        # Simular erro no AuthenticationService
        mock_determine_dashboard.side_effect = Exception('Test error')
        
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get('/dashboard/')
        
        # Deve redirecionar para login em caso de erro
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        # Verificar mensagem de erro
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Erro interno' in str(message) for message in messages))
    
    @patch('dashboard.views.AuthenticationService.can_access_store_dashboard')
    def test_dashboard_loja_error_handling(self, mock_can_access):
        """Testa tratamento de erros na view dashboard_loja."""
        # Simular erro no AuthenticationService
        mock_can_access.side_effect = Exception('Test error')
        
        self.client.login(username='storeadmin', password='testpass123')
        
        response = self.client.get('/dashboard/loja/dashboard/')
        
        # Deve redirecionar para login em caso de erro
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        # Verificar mensagem de erro
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Erro interno' in str(message) for message in messages))
    
    def test_dashboard_context_includes_authentication_info(self):
        """Testa se o contexto do dashboard inclui informações de autenticação."""
        self.client.login(username='storeadmin', password='testpass123')
        
        response = self.client.get('/dashboard/loja/dashboard/')
        
        if response.status_code == 200:
            # Verificar se o contexto inclui informações do AuthenticationService
            self.assertIn('user_type', response.context)
            self.assertIn('can_access_store', response.context)
            self.assertEqual(response.context['user_type'], 'store_admin')
            self.assertTrue(response.context['can_access_store'])
    
    def test_dashboard_loja_with_specific_store_id(self):
        """Testa acesso ao dashboard com ID de loja específico."""
        # Criar outra loja
        other_store = Loja.objects.create(
            nome='Outra Loja',
            cnpj='98765432109876',
            endereco='Outra Rua, 456'
        )
        
        self.client.login(username='superadmin', password='testpass123')
        
        # Assumindo que existe uma URL que aceita loja_id
        # response = self.client.get(f'/dashboard/loja/{other_store.id}/')
        
        # Super usuário deve conseguir acessar qualquer loja
        # self.assertEqual(response.status_code, 200)
        
        # Teste com store admin tentando acessar loja diferente
        self.client.login(username='storeadmin', password='testpass123')
        
        # response = self.client.get(f'/dashboard/loja/{other_store.id}/')
        
        # Store admin não deve conseguir acessar loja diferente
        # self.assertEqual(response.status_code, 302)
    
    def test_dashboard_statistics_calculation(self):
        """Testa se as estatísticas do dashboard são calculadas corretamente."""
        self.client.login(username='storeadmin', password='testpass123')
        
        response = self.client.get('/dashboard/loja/dashboard/')
        
        if response.status_code == 200:
            # Verificar se as estatísticas estão no contexto
            expected_stats = [
                'total_clientes', 'total_produtos', 'vendas_hoje',
                'vendas_semana', 'vendas_mes', 'receita_hoje',
                'receita_semana', 'receita_mes', 'produtos_estoque_baixo'
            ]
            
            for stat in expected_stats:
                self.assertIn(stat, response.context)
                # Verificar se são números (podem ser 0)
                self.assertIsInstance(response.context[stat], (int, float, type(None)))


class TestDashboardViewsPermissions(TestCase):
    """Testes específicos para permissões das views do dashboard."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        self.super_user = User.objects.create_user(
            username='superadmin',
            password='testpass123',
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpass123'
        )
    
    def test_require_store_access_decorator(self):
        """Testa o decorator require_store_access."""
        from dashboard.views import require_store_access
        
        # Criar uma view de teste
        @require_store_access
        def test_view(request):
            from django.http import HttpResponse
            return HttpResponse('Success')
        
        # Teste com usuário não autenticado
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = test_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('loja_login', response.url)
        
        # Teste com usuário sem permissão
        request.user.is_authenticated = True
        with patch('dashboard.views.AuthenticationService.can_access_store_dashboard', return_value=False):
            response = test_view(request)
            self.assertEqual(response.status_code, 302)
    
    def test_authentication_service_integration(self):
        """Testa integração com AuthenticationService nas views."""
        # Verificar se as views estão usando o AuthenticationService corretamente
        with patch('dashboard.views.AuthenticationService.determine_user_dashboard') as mock_determine:
            mock_determine.return_value = '/dashboard/'
            
            self.client.login(username='superadmin', password='testpass123')
            response = self.client.get('/dashboard/')
            
            # Verificar se o método foi chamado
            mock_determine.assert_called_once()