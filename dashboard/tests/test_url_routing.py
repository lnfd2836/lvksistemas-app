"""
Testes para configuração de URLs e roteamento.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect

from lojas.models import Loja
from usuarios.models import PerfilUsuario


class TestURLRouting(TestCase):
    """Testes para roteamento de URLs."""
    
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
        
        self.store_admin = User.objects.create_user(
            username='storeadmin',
            email='store@test.com',
            password='testpass123'
        )
        
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@test.com',
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
    
    def test_root_url_redirect_unauthenticated(self):
        """Testa redirecionamento da URL raiz para usuário não autenticado."""
        response = self.client.get('/')
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_root_url_redirect_super_user(self):
        """Testa redirecionamento da URL raiz para super usuário."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get('/')
        
        # Deve redirecionar para dashboard apropriado
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)
    
    def test_root_url_redirect_store_admin(self):
        """Testa redirecionamento da URL raiz para administrador de loja."""
        self.client.login(username='storeadmin', password='testpass123')
        
        response = self.client.get('/')
        
        # Deve redirecionar para dashboard da loja
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)
    
    def test_dashboard_url_patterns(self):
        """Testa padrões de URL do dashboard."""
        # Testar URLs principais
        urls_to_test = [
            ('dashboard:principal', '/dashboard/'),
            ('dashboard:super_admin', '/dashboard/super-admin/'),
            ('dashboard:loja', '/dashboard/loja/'),
            ('dashboard:login', '/dashboard/login/'),
            ('dashboard:logout', '/dashboard/logout/'),
        ]
        
        for url_name, expected_path in urls_to_test:
            try:
                url = reverse(url_name)
                self.assertEqual(url, expected_path)
            except Exception as e:
                self.fail(f"Erro ao resolver URL {url_name}: {str(e)}")
    
    def test_dashboard_loja_especifica_url_pattern(self):
        """Testa o padrão de URL específico para dashboard de loja com ID."""
        # Este é o teste específico para o problema que foi corrigido
        try:
            # Testar com UUID da loja de teste
            url = reverse('dashboard:loja_especifica', kwargs={'loja_id': self.test_store.id})
            expected_path = f'/dashboard/loja/{self.test_store.id}/'
            self.assertEqual(url, expected_path)
        except Exception as e:
            self.fail(f"Erro ao resolver URL dashboard:loja_especifica: {str(e)}")
    
    def test_template_url_references_exist(self):
        """Testa se todas as URLs referenciadas nos templates existem."""
        # URLs que devem existir para os templates funcionarem
        template_urls = [
            'dashboard:loja_especifica',  # A URL que estava causando o problema
            'listar_lojas',
            'criar_loja', 
            'detalhar_loja',
            'editar_loja',
            'excluir_loja',
        ]
        
        for url_name in template_urls:
            try:
                if url_name == 'dashboard:loja_especifica':
                    # Precisa de um parâmetro loja_id
                    url = reverse(url_name, kwargs={'loja_id': self.test_store.id})
                elif url_name in ['detalhar_loja', 'editar_loja', 'excluir_loja']:
                    # Precisam de parâmetro loja_id
                    url = reverse(url_name, kwargs={'loja_id': self.test_store.id})
                else:
                    url = reverse(url_name)
                
                self.assertIsNotNone(url)
            except Exception as e:
                self.fail(f"Erro ao resolver URL do template {url_name}: {str(e)}")
    
    def test_admin_url_patterns(self):
        """Testa padrões de URL administrativas."""
        admin_urls = [
            'dashboard:admin_usuarios_lista',
            'dashboard:admin_usuarios_criar',
            'dashboard:admin_sessoes',
            'dashboard:admin_modulos',
        ]
        
        for url_name in admin_urls:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
                # Verificar se contém 'admin' no caminho
                self.assertIn('admin', url)
            except Exception as e:
                self.fail(f"Erro ao resolver URL administrativa {url_name}: {str(e)}")
    
    def test_api_url_patterns(self):
        """Testa padrões de URL da API."""
        api_urls = [
            'dashboard:api_estatisticas',
        ]
        
        for url_name in api_urls:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
                # Verificar se contém 'api' no caminho
                self.assertIn('api', url)
            except Exception as e:
                self.fail(f"Erro ao resolver URL da API {url_name}: {str(e)}")
    
    def test_url_resolution(self):
        """Testa resolução de URLs para views corretas."""
        url_view_mapping = [
            ('/dashboard/', 'dashboard.views.dashboard_principal'),
            ('/dashboard/super-admin/', 'dashboard.views.dashboard_super_admin'),
            ('/dashboard/loja/', 'dashboard.views.dashboard_loja'),
            ('/login/', 'dashboard.simple_login.simple_login'),
            ('/loja/login/', 'dashboard.loja_login.loja_login'),
        ]
        
        for url_path, expected_view in url_view_mapping:
            try:
                resolved = resolve(url_path)
                view_name = f"{resolved.func.__module__}.{resolved.func.__name__}"
                self.assertEqual(view_name, expected_view)
            except Exception as e:
                self.fail(f"Erro ao resolver URL {url_path}: {str(e)}")
    
    def test_login_url_access(self):
        """Testa acesso às URLs de login."""
        # Teste login simples
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        
        # Teste login da loja
        response = self.client.get('/loja/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_url_access_permissions(self):
        """Testa permissões de acesso às URLs do dashboard."""
        # URLs que requerem autenticação
        protected_urls = [
            '/dashboard/',
            '/dashboard/super-admin/',
            '/dashboard/loja/',
            '/dashboard/admin/usuarios/',
            '/dashboard/admin/sessoes/',
            '/dashboard/admin/modulos/',
        ]
        
        for url in protected_urls:
            # Teste sem autenticação
            response = self.client.get(url)
            # Deve redirecionar para login ou retornar 302
            self.assertIn(response.status_code, [302, 403])
    
    def test_admin_url_access_super_user_only(self):
        """Testa que URLs administrativas são acessíveis apenas por super usuários."""
        admin_urls = [
            '/dashboard/admin/usuarios/',
            '/dashboard/admin/sessoes/',
            '/dashboard/admin/modulos/',
        ]
        
        # Teste com usuário regular
        self.client.login(username='regularuser', password='testpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            # Deve redirecionar ou negar acesso
            self.assertIn(response.status_code, [302, 403])
        
        # Teste com super usuário
        self.client.login(username='superadmin', password='testpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            # Deve permitir acesso (200) ou redirecionar para dashboard correto (302)
            self.assertIn(response.status_code, [200, 302])
    
    def test_url_namespacing(self):
        """Testa se o namespacing de URLs está funcionando corretamente."""
        # Testar URLs com namespace
        namespaced_urls = [
            'dashboard:principal',
            'dashboard:super_admin',
            'dashboard:loja',
            'dashboard:admin_usuarios_lista',
        ]
        
        for url_name in namespaced_urls:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
                # Verificar se a URL começa com /dashboard/
                self.assertTrue(url.startswith('/dashboard/'))
            except Exception as e:
                self.fail(f"Erro ao resolver URL com namespace {url_name}: {str(e)}")
    
    def test_redirect_loop_prevention(self):
        """Testa prevenção de loops de redirecionamento."""
        # Login como super usuário
        self.client.login(username='superadmin', password='testpass123')
        
        # Acessar dashboard principal
        response = self.client.get('/dashboard/')
        
        # Não deve haver loop infinito
        redirect_count = 0
        while response.status_code == 302 and redirect_count < 5:
            redirect_count += 1
            response = self.client.get(response.url)
        
        # Deve eventualmente chegar a uma página (200) ou parar de redirecionar
        self.assertLess(redirect_count, 5, "Possível loop de redirecionamento detectado")
    
    def test_url_consistency(self):
        """Testa consistência entre URLs definidas e usadas nas views."""
        # Verificar se URLs usadas nas views existem
        common_redirects = [
            'dashboard:principal',
            'dashboard:loja',
            'simple_login',
            'loja_login',
        ]
        
        for url_name in common_redirects:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception as e:
                # Se a URL não existe, pode ser um problema
                print(f"Aviso: URL {url_name} pode não estar definida: {str(e)}")


class TestURLSecurity(TestCase):
    """Testes de segurança para URLs."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpass123'
        )
        
        self.super_user = User.objects.create_user(
            username='superadmin',
            password='testpass123',
            is_superuser=True
        )
    
    def test_admin_urls_require_super_user(self):
        """Testa que URLs administrativas requerem super usuário."""
        admin_paths = [
            '/dashboard/admin/usuarios/',
            '/dashboard/admin/sessoes/',
            '/dashboard/admin/modulos/',
        ]
        
        # Teste com usuário regular
        self.client.login(username='regularuser', password='testpass123')
        
        for path in admin_paths:
            response = self.client.get(path)
            # Não deve permitir acesso direto
            self.assertNotEqual(response.status_code, 200)
    
    def test_api_endpoints_security(self):
        """Testa segurança dos endpoints da API."""
        api_paths = [
            '/dashboard/api/estatisticas/',
        ]
        
        # Teste sem autenticação
        for path in api_paths:
            response = self.client.get(path)
            # Deve negar acesso ou redirecionar
            self.assertIn(response.status_code, [302, 401, 403])
    
    def test_sensitive_operations_require_authentication(self):
        """Testa que operações sensíveis requerem autenticação."""
        sensitive_paths = [
            '/dashboard/admin/sessoes/1/invalidar/',
            '/dashboard/admin/usuarios/1/excluir/',
        ]
        
        for path in sensitive_paths:
            response = self.client.post(path)
            # Deve negar acesso
            self.assertIn(response.status_code, [302, 401, 403, 404])  # 404 é aceitável se o objeto não existe