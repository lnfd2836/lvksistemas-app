"""
Testes para verificar se os templates renderizam corretamente sem erros de URL
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from lojas.models import Loja
import uuid


class TemplateRenderingTests(TestCase):
    """Testes para verificar renderização de templates"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = Client()
        
        # Criar usuário super admin
        self.super_admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='testpass123'
        )
        
        # Criar uma loja de teste
        self.loja = Loja.objects.create(
            id=uuid.uuid4(),
            nome='Loja Teste',
            cnpj='12.345.678/0001-90',
            email='loja@test.com',
            telefone='(11) 99999-9999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            status='ativa'
        )
        
        # Login como super admin
        self.client.login(username='admin_test', password='testpass123')
    
    def test_lojas_listing_page_renders(self):
        """Testa se a página de listagem de lojas renderiza sem erros"""
        url = reverse('lojas:listar_lojas')
        response = self.client.get(url)
        
        # Verifica se não há erro 500
        self.assertNotEqual(response.status_code, 500, 
                           "Página de listagem de lojas retornou erro 500")
        
        # Verifica se a página carregou (200 ou 302 para redirect)
        self.assertIn(response.status_code, [200, 302], 
                     f"Status code inesperado: {response.status_code}")
    
    def test_usuarios_admin_page_renders(self):
        """Testa se a página de usuários admin renderiza sem erros"""
        url = reverse('dashboard:admin_usuarios_lista')
        response = self.client.get(url)
        
        # Verifica se não há erro 500
        self.assertNotEqual(response.status_code, 500, 
                           "Página de usuários admin retornou erro 500")
        
        # Verifica se a página carregou
        self.assertIn(response.status_code, [200, 302], 
                     f"Status code inesperado: {response.status_code}")
    
    def test_dashboard_loja_especifica_renders(self):
        """Testa se o dashboard específico da loja renderiza sem erros"""
        url = reverse('dashboard:loja_especifica', args=[self.loja.id])
        response = self.client.get(url)
        
        # Verifica se não há erro 500
        self.assertNotEqual(response.status_code, 500, 
                           "Dashboard específico da loja retornou erro 500")
        
        # Verifica se a página carregou
        self.assertIn(response.status_code, [200, 302], 
                     f"Status code inesperado: {response.status_code}")
    
    def test_all_action_buttons_have_valid_urls(self):
        """Testa se todos os botões de ação têm URLs válidas"""
        # Testa página de listagem de lojas
        url = reverse('lojas:listar_lojas')
        response = self.client.get(url)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verifica se não há referências a URLs quebradas
            self.assertNotIn('NoReverseMatch', content)
            self.assertNotIn('dashboard_loja_id', content)
            self.assertNotIn('editar_usuario_super_admin', content)
        
        # Testa página de usuários admin
        url = reverse('dashboard:admin_usuarios_lista')
        response = self.client.get(url)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verifica se não há referências a URLs quebradas
            self.assertNotIn('NoReverseMatch', content)
            self.assertNotIn('editar_usuario_super_admin', content)
    
    def test_template_url_generation(self):
        """Testa se as URLs são geradas corretamente nos templates"""
        # URLs que devem funcionar
        test_urls = [
            ('lojas:listar_lojas', []),
            ('lojas:criar_loja', []),
            ('dashboard:admin_usuarios_lista', []),
            ('dashboard:admin_usuarios_criar', []),
            ('dashboard:loja_especifica', [self.loja.id]),
        ]
        
        for url_name, args in test_urls:
            with self.subTest(url_name=url_name):
                try:
                    url = reverse(url_name, args=args)
                    response = self.client.get(url)
                    # Não deve retornar erro 500
                    self.assertNotEqual(response.status_code, 500, 
                                       f"URL {url_name} retornou erro 500")
                except Exception as e:
                    self.fail(f"Erro ao acessar URL {url_name}: {e}")