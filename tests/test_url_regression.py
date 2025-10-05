"""
Testes de regressão para URL routing
Estes testes garantem que os problemas de URL não voltem a ocorrer
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.template import Template, Context
from django.template.loader import get_template
from lojas.models import Loja
import uuid


class URLRegressionTests(TestCase):
    """
    Testes de regressão para prevenir problemas de URL routing
    """
    
    def setUp(self):
        """Configuração inicial"""
        self.client = Client()
        
        # Criar usuário super admin
        self.super_admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='testpass123'
        )
        
        # Criar loja de teste
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
        
        self.client.login(username='admin_test', password='testpass123')
    
    def test_no_reverse_match_errors_in_templates(self):
        """
        Testa que não há erros NoReverseMatch nos templates principais
        """
        # Lista de URLs críticas que devem funcionar
        critical_urls = [
            'lojas:listar_lojas',
            'dashboard:admin_usuarios_lista',
            'dashboard:principal',
        ]
        
        for url_name in critical_urls:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                
                # Não deve haver erro 500
                self.assertNotEqual(response.status_code, 500,
                                   f"URL {url_name} retornou erro 500")
                
                # Se retornou 200, verifica o conteúdo
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    self.assertNotIn('NoReverseMatch', content,
                                    f"Template de {url_name} contém erro NoReverseMatch")
    
    def test_template_url_references_are_correct(self):
        """
        Testa que todas as referências de URL nos templates estão corretas
        """
        # Template de listagem de lojas
        template_content = '''
        {% load url %}
        <a href="{% url 'lojas:listar_lojas' %}">Listar</a>
        <a href="{% url 'lojas:criar_loja' %}">Criar</a>
        <a href="{% url 'lojas:editar_loja' loja_id %}">Editar</a>
        <a href="{% url 'dashboard:loja_especifica' loja_id %}">Dashboard</a>
        '''
        
        template = Template(template_content)
        context = Context({'loja_id': self.loja.id})
        
        try:
            rendered = template.render(context)
            self.assertIsNotNone(rendered)
        except Exception as e:
            self.fail(f"Erro ao renderizar template: {e}")
    
    def test_dashboard_template_url_references(self):
        """
        Testa referências de URL no template do dashboard
        """
        template_content = '''
        {% load url %}
        <a href="{% url 'dashboard:admin_usuarios_lista' %}">Listar Usuários</a>
        <a href="{% url 'dashboard:admin_usuarios_criar' %}">Criar Usuário</a>
        <a href="{% url 'dashboard:admin_usuarios_editar' user_id %}">Editar</a>
        <a href="{% url 'dashboard:admin_usuarios_alterar_senha' user_id %}">Alterar Senha</a>
        <a href="{% url 'dashboard:admin_usuarios_excluir' user_id %}">Excluir</a>
        '''
        
        template = Template(template_content)
        context = Context({'user_id': self.super_admin.id})
        
        try:
            rendered = template.render(context)
            self.assertIsNotNone(rendered)
        except Exception as e:
            self.fail(f"Erro ao renderizar template do dashboard: {e}")
    
    def test_all_namespaced_urls_resolve(self):
        """
        Testa que todas as URLs com namespace são resolvidas corretamente
        """
        namespaced_urls = [
            # Dashboard URLs
            ('dashboard:principal', []),
            ('dashboard:super_admin', []),
            ('dashboard:loja', []),
            ('dashboard:loja_especifica', [self.loja.id]),
            ('dashboard:admin_usuarios_lista', []),
            ('dashboard:admin_usuarios_criar', []),
            ('dashboard:admin_usuarios_editar', [self.super_admin.id]),
            
            # Lojas URLs
            ('lojas:listar_lojas', []),
            ('lojas:criar_loja', []),
            ('lojas:editar_loja', [self.loja.id]),
            ('lojas:detalhar_loja', [self.loja.id]),
        ]
        
        for url_name, args in namespaced_urls:
            with self.subTest(url_name=url_name):
                try:
                    url = reverse(url_name, args=args)
                    self.assertTrue(url.startswith('/'),
                                   f"URL {url_name} não começa com /")
                except Exception as e:
                    self.fail(f"Erro ao resolver URL {url_name}: {e}")
    
    def test_template_inheritance_works(self):
        """
        Testa que a herança de templates funciona corretamente
        """
        try:
            # Tenta carregar templates que estendem base.html
            template = get_template('lojas/listar.html')
            self.assertIsNotNone(template)
            
            template = get_template('dashboard/usuarios_super_admin.html')
            self.assertIsNotNone(template)
            
        except Exception as e:
            self.fail(f"Erro na herança de templates: {e}")
    
    def test_critical_pages_load_without_errors(self):
        """
        Testa que páginas críticas carregam sem erros
        """
        critical_pages = [
            '/lojas/',
            '/dashboard/',
            '/dashboard/admin/usuarios/',
        ]
        
        for page_url in critical_pages:
            with self.subTest(page_url=page_url):
                response = self.client.get(page_url)
                
                # Não deve ser erro 500
                self.assertNotEqual(response.status_code, 500,
                                   f"Página {page_url} retornou erro 500")
                
                # Deve ser sucesso ou redirect
                self.assertIn(response.status_code, [200, 301, 302],
                             f"Página {page_url} retornou status inesperado: {response.status_code}")
    
    def test_url_parameters_validation(self):
        """
        Testa validação de parâmetros de URL
        """
        # Testa com UUID válido
        valid_uuid = str(self.loja.id)
        url = reverse('dashboard:loja_especifica', args=[valid_uuid])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 500)
        
        # Testa com ID de usuário válido
        valid_user_id = self.super_admin.id
        url = reverse('dashboard:admin_usuarios_editar', args=[valid_user_id])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 500)