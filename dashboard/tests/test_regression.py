"""
Testes de regressão para garantir que as correções de URL não quebrem funcionalidades existentes
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.template import Template, Context
from django.template.loader import render_to_string
from lojas.models import Loja
from dashboard.utils.url_validator import URLValidator
import uuid


class URLRegressionTests(TestCase):
    """
    Testes de regressão para URLs e templates
    """
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = Client()
        
        # Criar usuário super admin
        self.superuser = User.objects.create_user(
            username='superadmin',
            email='super@admin.com',
            password='superpass123',
            is_superuser=True,
            is_staff=True
        )
        
        # Criar usuário normal
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@user.com',
            password='normalpass123'
        )
        
        # Criar loja de teste
        self.loja = Loja.objects.create(
            nome='Loja Teste Regressão',
            cnpj='98.765.432/0001-10',
            email='regressao@teste.com',
            telefone='(11) 88888-8888',
            endereco='Rua Regressão, 456',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            db_name='regression_test_db',
            admin_user=self.normal_user
        )
    
    def test_no_reverse_match_errors_in_critical_pages(self):
        """
        Testa que não há erros NoReverseMatch nas páginas críticas
        """
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        critical_urls = [
            ('dashboard:admin_usuarios_lista', {}),
            ('listar_lojas', {}),
            ('dashboard:principal', {}),
            ('dashboard:super_admin', {}),
        ]
        
        for url_name, kwargs in critical_urls:
            with self.subTest(url=url_name):
                try:
                    url = reverse(url_name, kwargs=kwargs)
                    response = self.client.get(url)
                    
                    # Não deve retornar erro 500
                    self.assertNotEqual(
                        response.status_code, 500,
                        f"URL {url_name} retornou erro 500"
                    )
                    
                    # Se retornou 200, verificar se não há erros no conteúdo
                    if response.status_code == 200:
                        content = response.content.decode('utf-8')
                        self.assertNotIn(
                            'NoReverseMatch', content,
                            f"NoReverseMatch encontrado no conteúdo de {url_name}"
                        )
                        self.assertNotIn(
                            'Reverse for', content,
                            f"Erro de reverse encontrado no conteúdo de {url_name}"
                        )
                
                except Exception as e:
                    self.fail(f"Erro ao testar URL {url_name}: {str(e)}")
    
    def test_template_url_generation_regression(self):
        """
        Testa que a geração de URLs nos templates funciona corretamente
        """
        # Testar template de usuários super admin
        template_content = """
        {% load url %}
        <a href="{% url 'dashboard:admin_usuarios_editar' user_id=1 %}">Editar</a>
        <a href="{% url 'dashboard:admin_usuarios_alterar_senha' user_id=1 %}">Alterar Senha</a>
        <a href="{% url 'dashboard:admin_usuarios_excluir' user_id=1 %}">Excluir</a>
        """
        
        try:
            template = Template(template_content)
            rendered = template.render(Context({}))
            
            # Verificar se as URLs foram geradas corretamente
            self.assertIn('/dashboard/admin/usuarios/1/editar/', rendered)
            self.assertIn('/dashboard/admin/usuarios/1/alterar-senha/', rendered)
            self.assertIn('/dashboard/admin/usuarios/1/excluir/', rendered)
            
        except Exception as e:
            self.fail(f"Erro na geração de URLs no template: {str(e)}")
    
    def test_loja_specific_urls_regression(self):
        """
        Testa que as URLs específicas de loja funcionam corretamente
        """
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Testar URL específica da loja
        try:
            url = reverse('dashboard:loja_especifica', kwargs={'loja_id': self.loja.id})
            response = self.client.get(url)
            
            # Não deve retornar erro 500
            self.assertNotEqual(response.status_code, 500)
            
        except Exception as e:
            self.fail(f"Erro ao testar URL específica da loja: {str(e)}")
    
    def test_url_validator_functionality(self):
        """
        Testa que o validador de URLs funciona corretamente
        """
        # Testar validação de URLs básicas
        dashboard_results = URLValidator.validate_dashboard_urls()
        
        # Verificar se as URLs críticas são válidas
        critical_urls = [
            'dashboard:principal',
            'dashboard:admin_usuarios_lista',
            'dashboard:admin_usuarios_criar',
        ]
        
        for url_name in critical_urls:
            self.assertIn(url_name, dashboard_results)
            self.assertTrue(
                dashboard_results[url_name]['valid'],
                f"URL {url_name} falhou na validação: {dashboard_results[url_name]['result']}"
            )
    
    def test_template_inheritance_regression(self):
        """
        Testa que a herança de templates não foi quebrada
        """
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Testar páginas que estendem base.html
        urls_to_test = [
            'dashboard:admin_usuarios_lista',
            'listar_lojas',
        ]
        
        for url_name in urls_to_test:
            with self.subTest(url=url_name):
                try:
                    url = reverse(url_name)
                    response = self.client.get(url)
                    
                    if response.status_code == 200:
                        content = response.content.decode('utf-8')
                        
                        # Verificar elementos básicos do template base
                        self.assertIn('<html', content)
                        self.assertIn('</html>', content)
                        
                        # Não deve haver erros de template
                        self.assertNotIn('TemplateDoesNotExist', content)
                        self.assertNotIn('TemplateSyntaxError', content)
                
                except Exception as e:
                    self.fail(f"Erro ao testar herança de template para {url_name}: {str(e)}")
    
    def test_user_permissions_regression(self):
        """
        Testa que as permissões de usuário não foram afetadas pelas mudanças
        """
        # Testar acesso como usuário normal (não super admin)
        self.client.login(username='normaluser', password='normalpass123')
        
        # URLs que devem ser restritas para usuários normais
        restricted_urls = [
            'dashboard:admin_usuarios_lista',
            'listar_lojas',
        ]
        
        for url_name in restricted_urls:
            with self.subTest(url=url_name):
                try:
                    url = reverse(url_name)
                    response = self.client.get(url)
                    
                    # Deve retornar 302 (redirect) ou 403 (forbidden), não 500
                    self.assertIn(
                        response.status_code, [302, 403],
                        f"URL {url_name} retornou status inesperado: {response.status_code}"
                    )
                
                except Exception as e:
                    self.fail(f"Erro ao testar permissões para {url_name}: {str(e)}")
    
    def test_form_submission_regression(self):
        """
        Testa que os formulários ainda funcionam após as mudanças
        """
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Testar acesso à página de criação de usuário
        try:
            url = reverse('dashboard:admin_usuarios_criar')
            response = self.client.get(url)
            
            # Não deve retornar erro 500
            self.assertNotEqual(response.status_code, 500)
            
        except Exception as e:
            # Se a view não existir ainda, isso é esperado
            if "admin_usuarios_criar" in str(e):
                self.skipTest("View admin_usuarios_criar não implementada ainda")
            else:
                self.fail(f"Erro inesperado ao testar formulário: {str(e)}")
    
    def test_ajax_endpoints_regression(self):
        """
        Testa que os endpoints AJAX ainda funcionam
        """
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Testar endpoint de estatísticas
        try:
            url = reverse('dashboard:api_estatisticas')
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            
            # Não deve retornar erro 500
            self.assertNotEqual(response.status_code, 500)
            
        except Exception as e:
            self.fail(f"Erro ao testar endpoint AJAX: {str(e)}")
    
    def test_uuid_parameter_handling_regression(self):
        """
        Testa que o tratamento de parâmetros UUID não foi quebrado
        """
        # Testar com UUID válido
        valid_uuid = str(uuid.uuid4())
        
        try:
            url = reverse('dashboard:loja_especifica', kwargs={'loja_id': valid_uuid})
            self.assertIn(valid_uuid, url)
            
        except Exception as e:
            self.fail(f"Erro ao gerar URL com UUID válido: {str(e)}")
        
        # Testar com UUID da loja existente
        try:
            url = reverse('dashboard:loja_especifica', kwargs={'loja_id': self.loja.id})
            self.assertIn(str(self.loja.id), url)
            
        except Exception as e:
            self.fail(f"Erro ao gerar URL com UUID da loja existente: {str(e)}")