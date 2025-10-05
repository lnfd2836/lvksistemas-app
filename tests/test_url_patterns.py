"""
Testes para validação de padrões de URL
"""
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from lojas.models import Loja
import uuid


class URLPatternTests(TestCase):
    """Testes para verificar se todos os padrões de URL estão funcionando corretamente"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário super admin para testes
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
    
    def test_dashboard_url_patterns(self):
        """Testa se todos os padrões de URL do dashboard estão funcionando"""
        # URLs básicas do dashboard
        urls_to_test = [
            ('dashboard:principal', []),
            ('dashboard:super_admin', []),
            ('dashboard:loja', []),
            ('dashboard:loja_especifica', [self.loja.id]),
            ('dashboard:admin_usuarios_lista', []),
            ('dashboard:admin_usuarios_criar', []),
            ('dashboard:admin_usuarios_editar', [self.super_admin.id]),
            ('dashboard:admin_usuarios_alterar_senha', [self.super_admin.id]),
            ('dashboard:admin_usuarios_excluir', [self.super_admin.id]),
        ]
        
        for url_name, args in urls_to_test:
            with self.subTest(url_name=url_name):
                try:
                    url = reverse(url_name, args=args)
                    self.assertIsNotNone(url)
                    self.assertTrue(url.startswith('/'))
                except NoReverseMatch as e:
                    self.fail(f"URL pattern '{url_name}' não encontrado: {e}")
    
    def test_lojas_url_patterns(self):
        """Testa se todos os padrões de URL de lojas estão funcionando"""
        urls_to_test = [
            ('lojas:listar_lojas', []),
            ('lojas:criar_loja', []),
            ('lojas:editar_loja', [self.loja.id]),
            ('lojas:detalhar_loja', [self.loja.id]),
            ('lojas:alterar_status_loja', [self.loja.id]),
            ('lojas:excluir_loja', [self.loja.id]),
        ]
        
        for url_name, args in urls_to_test:
            with self.subTest(url_name=url_name):
                try:
                    url = reverse(url_name, args=args)
                    self.assertIsNotNone(url)
                    self.assertTrue(url.startswith('/'))
                except NoReverseMatch as e:
                    self.fail(f"URL pattern '{url_name}' não encontrado: {e}")
    
    def test_url_generation_with_parameters(self):
        """Testa se URLs com parâmetros são geradas corretamente"""
        # Teste com UUID da loja
        loja_url = reverse('dashboard:loja_especifica', args=[self.loja.id])
        self.assertIn(str(self.loja.id), loja_url)
        
        # Teste com ID do usuário
        user_url = reverse('dashboard:admin_usuarios_editar', args=[self.super_admin.id])
        self.assertIn(str(self.super_admin.id), user_url)
    
    def test_namespace_resolution(self):
        """Testa se os namespaces estão sendo resolvidos corretamente"""
        # Teste namespace dashboard
        dashboard_url = reverse('dashboard:principal')
        self.assertTrue(dashboard_url.startswith('/dashboard/'))
        
        # Teste namespace lojas
        lojas_url = reverse('lojas:listar_lojas')
        self.assertTrue(lojas_url.startswith('/lojas/'))