"""
Testes para validação de padrões de URL do dashboard
"""
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from lojas.models import Loja
import uuid


class DashboardURLTests(TestCase):
    """Testes para URLs do dashboard"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar uma loja de teste
        self.loja = Loja.objects.create(
            nome='Loja Teste',
            cnpj='12.345.678/0001-90',
            email='loja@teste.com',
            telefone='(11) 99999-9999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            db_name='test_db',
            admin_user=self.user
        )
    
    def test_dashboard_principal_url(self):
        """Testa se a URL principal do dashboard resolve corretamente"""
        url = reverse('dashboard:principal')
        self.assertEqual(url, '/dashboard/')
        
        # Testa se a URL resolve para a view correta
        resolver = resolve('/dashboard/')
        self.assertEqual(resolver.view_name, 'dashboard:principal')
    
    def test_dashboard_super_admin_url(self):
        """Testa se a URL do dashboard super admin resolve corretamente"""
        url = reverse('dashboard:super_admin')
        self.assertEqual(url, '/dashboard/super-admin/')
        
        resolver = resolve('/dashboard/super-admin/')
        self.assertEqual(resolver.view_name, 'dashboard:super_admin')
    
    def test_dashboard_loja_url(self):
        """Testa se a URL do dashboard da loja resolve corretamente"""
        url = reverse('dashboard:loja')
        self.assertEqual(url, '/dashboard/loja/')
        
        resolver = resolve('/dashboard/loja/')
        self.assertEqual(resolver.view_name, 'dashboard:loja')
    
    def test_dashboard_loja_especifica_url(self):
        """Testa se a URL específica da loja resolve corretamente"""
        url = reverse('dashboard:loja_especifica', kwargs={'loja_id': self.loja.id})
        expected_url = f'/dashboard/loja/{self.loja.id}/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.view_name, 'dashboard:loja_especifica')
        self.assertEqual(resolver.kwargs['loja_id'], self.loja.id)
    
    def test_admin_usuarios_urls(self):
        """Testa se as URLs de administração de usuários resolvem corretamente"""
        # Lista de usuários
        url = reverse('dashboard:admin_usuarios_lista')
        self.assertEqual(url, '/dashboard/admin/usuarios/')
        
        # Criar usuário
        url = reverse('dashboard:admin_usuarios_criar')
        self.assertEqual(url, '/dashboard/admin/usuarios/criar/')
        
        # Editar usuário
        url = reverse('dashboard:admin_usuarios_editar', kwargs={'user_id': 1})
        self.assertEqual(url, '/dashboard/admin/usuarios/1/editar/')
        
        # Alterar senha
        url = reverse('dashboard:admin_usuarios_alterar_senha', kwargs={'user_id': 1})
        self.assertEqual(url, '/dashboard/admin/usuarios/1/alterar-senha/')
        
        # Excluir usuário
        url = reverse('dashboard:admin_usuarios_excluir', kwargs={'user_id': 1})
        self.assertEqual(url, '/dashboard/admin/usuarios/1/excluir/')
    
    def test_api_urls(self):
        """Testa se as URLs da API resolvem corretamente"""
        # API de estatísticas
        url = reverse('dashboard:api_estatisticas')
        self.assertEqual(url, '/dashboard/api/estatisticas/')
        
        # API de notificações
        url = reverse('dashboard:api_marcar_notificacao_lida', kwargs={'notificacao_id': 1})
        self.assertEqual(url, '/dashboard/api/notificacao/1/marcar-lida/')
    
    def test_url_parameters_validation(self):
        """Testa se os parâmetros das URLs são validados corretamente"""
        # Testa UUID válido para loja
        valid_uuid = str(uuid.uuid4())
        url = reverse('dashboard:loja_especifica', kwargs={'loja_id': valid_uuid})
        self.assertIn(valid_uuid, url)
        
        # Testa ID inteiro para usuário
        url = reverse('dashboard:admin_usuarios_editar', kwargs={'user_id': 123})
        self.assertIn('123', url)


class LojaURLTests(TestCase):
    """Testes para URLs de lojas"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.loja = Loja.objects.create(
            nome='Loja Teste',
            cnpj='12.345.678/0001-90',
            email='loja@teste.com',
            telefone='(11) 99999-9999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            db_name='test_db',
            admin_user=self.user
        )
    
    def test_listar_lojas_url(self):
        """Testa se a URL de listagem de lojas resolve corretamente"""
        url = reverse('listar_lojas')
        self.assertEqual(url, '/lojas/')
        
        resolver = resolve('/lojas/')
        self.assertEqual(resolver.view_name, 'listar_lojas')
    
    def test_loja_management_urls(self):
        """Testa se as URLs de gerenciamento de lojas resolvem corretamente"""
        # Criar loja
        url = reverse('criar_loja')
        self.assertEqual(url, '/lojas/criar/')
        
        # Editar loja
        url = reverse('editar_loja', kwargs={'loja_id': self.loja.id})
        expected_url = f'/lojas/{self.loja.id}/editar/'
        self.assertEqual(url, expected_url)
        
        # Detalhar loja
        url = reverse('detalhar_loja', kwargs={'loja_id': self.loja.id})
        expected_url = f'/lojas/{self.loja.id}/detalhar/'
        self.assertEqual(url, expected_url)
        
        # Excluir loja
        url = reverse('excluir_loja', kwargs={'loja_id': self.loja.id})
        expected_url = f'/lojas/{self.loja.id}/excluir/'
        self.assertEqual(url, expected_url)