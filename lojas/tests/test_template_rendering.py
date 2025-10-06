"""
Testes para renderização de templates da aplicação lojas.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string
from django.template import Context, Template

from lojas.models import Loja
from usuarios.models import PerfilUsuario


class TestTemplateRendering(TestCase):
    """Testes para renderização de templates."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Criar usuário super admin
        self.super_user = User.objects.create_user(
            username='superadmin',
            email='super@test.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        # Criar usuário admin para a loja
        self.admin_user = User.objects.create_user(
            username='admin_loja',
            email='admin@loja.com',
            password='testpass123'
        )
        
        # Criar loja de teste
        self.test_store = Loja.objects.create(
            nome='Loja Teste',
            cnpj='12345678901234',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            email='teste@loja.com',
            telefone='11999999999',
            cep='01234567',
            status='ativa',
            admin_user=self.admin_user
        )
        
        # Criar outro usuário admin
        self.admin_user2 = User.objects.create_user(
            username='admin_loja2',
            email='admin2@loja.com',
            password='testpass123'
        )
        
        # Criar loja sem tipo para testar edge cases
        self.store_without_type = Loja.objects.create(
            nome='Loja Sem Tipo',
            cnpj='98765432109876',
            endereco='Rua Sem Tipo, 456',
            cidade='Rio de Janeiro',
            estado='RJ',
            email='semtipo@loja.com',
            telefone='21999999999',
            cep='98765432',
            status='inativa',
            admin_user=self.admin_user2
        )
    
    def test_listar_lojas_template_renders_without_errors(self):
        """Testa se o template de listagem de lojas renderiza sem erros."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Deve renderizar com sucesso
        self.assertEqual(response.status_code, 200)
        
        # Deve conter o nome da loja
        self.assertContains(response, self.test_store.nome)
        
        # Deve conter o botão de dashboard para loja com tipo
        self.assertContains(response, 'Dashboard da loja')
        
        # Deve conter informações da loja
        self.assertContains(response, self.test_store.cnpj)
        self.assertContains(response, self.test_store.email)
    
    def test_dashboard_url_in_template_resolves_correctly(self):
        """Testa se a URL do dashboard no template resolve corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Verificar se a URL do dashboard está presente e correta
        expected_dashboard_url = reverse('dashboard:loja_especifica', kwargs={'loja_id': self.test_store.id})
        self.assertContains(response, expected_dashboard_url)
    
    def test_template_handles_store_without_type(self):
        """Testa se o template lida corretamente com lojas sem tipo."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Deve renderizar sem erros mesmo com loja sem tipo
        self.assertEqual(response.status_code, 200)
        
        # Deve conter a loja sem tipo
        self.assertContains(response, self.store_without_type.nome)
        
        # Deve mostrar "Não definido" para tipo de loja
        self.assertContains(response, 'Não definido')
        
        # Não deve mostrar botão de dashboard para loja sem tipo
        # (o botão só aparece se loja.tipo_loja existe)
        dashboard_button_html = f'href="{reverse("dashboard:loja_especifica", kwargs={"loja_id": self.store_without_type.id})}"'
        self.assertNotContains(response, dashboard_button_html)
    
    def test_template_url_references_are_valid(self):
        """Testa se todas as referências de URL no template são válidas."""
        # Simular contexto do template
        context = {
            'lojas': [self.test_store, self.store_without_type],
            'stats_tipos': {
                'conveniencia': 1,
                'roupas': 0,
                'tintas': 0,
                'supermercado': 0,
                'lanchonete': 0,
            },
            'search': '',
            'status_filter': '',
            'tipo_filter': '',
        }
        
        # Tentar renderizar o template
        try:
            rendered = render_to_string('lojas/listar.html', context)
            self.assertIsNotNone(rendered)
            self.assertIn(self.test_store.nome, rendered)
        except Exception as e:
            self.fail(f"Erro ao renderizar template: {str(e)}")
    
    def test_template_csrf_tokens_present(self):
        """Testa se os tokens CSRF estão presentes nos formulários."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Deve conter tokens CSRF nos formulários de exclusão
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_template_bootstrap_classes_present(self):
        """Testa se as classes Bootstrap estão presentes no template."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Verificar algumas classes Bootstrap importantes
        bootstrap_classes = [
            'btn btn-primary',
            'btn btn-sm btn-outline-primary',
            'btn btn-sm btn-outline-warning',
            'btn btn-sm btn-outline-info',
            'btn btn-sm btn-outline-danger',
            'table table-hover',
            'card',
            'form-control',
            'form-select',
        ]
        
        for css_class in bootstrap_classes:
            self.assertContains(response, css_class)
    
    def test_template_icons_present(self):
        """Testa se os ícones estão presentes no template."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Verificar alguns ícones importantes
        icons = [
            'bi bi-plus-circle',  # Nova loja
            'bi bi-eye',          # Ver detalhes
            'bi bi-pencil',       # Editar
            'bi bi-speedometer2', # Dashboard
            'bi bi-trash',        # Excluir
            'bi bi-search',       # Buscar
            'bi bi-x-circle',     # Limpar
        ]
        
        for icon in icons:
            self.assertContains(response, icon)
    
    def test_template_modals_present(self):
        """Testa se os modais de confirmação estão presentes."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Deve conter modais de exclusão para cada loja
        self.assertContains(response, f'modalExcluir{self.test_store.id}')
        self.assertContains(response, f'modalExcluir{self.store_without_type.id}')
        
        # Deve conter elementos do modal
        self.assertContains(response, 'modal-dialog')
        self.assertContains(response, 'modal-content')
        self.assertContains(response, 'modal-header')
        self.assertContains(response, 'modal-body')
        self.assertContains(response, 'modal-footer')
    
    def test_template_statistics_display(self):
        """Testa se as estatísticas são exibidas corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Deve conter cards de estatísticas
        stat_types = ['Conveniência', 'Roupas', 'Tintas', 'Supermercado', 'Lanchonete', 'Total']
        
        for stat_type in stat_types:
            self.assertContains(response, stat_type)
    
    def test_template_filters_form(self):
        """Testa se o formulário de filtros está presente e funcional."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Testar com filtros
        response = self.client.get(reverse('listar_lojas'), {
            'search': 'Teste',
            'status': 'ativa',
            'tipo_loja': 'conveniencia'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Deve manter os valores dos filtros no formulário
        self.assertContains(response, 'value="Teste"')
        self.assertContains(response, 'selected')
    
    def test_status_filter_selection_active(self):
        """Testa se o filtro de status 'ativa' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'), {'status': 'ativa'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'ativa' como selecionada
        self.assertContains(response, '<option value="ativa" selected>Ativa</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="inativa" selected>')
        self.assertNotContains(response, '<option value="suspensa" selected>')
    
    def test_status_filter_selection_inactive(self):
        """Testa se o filtro de status 'inativa' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'), {'status': 'inativa'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'inativa' como selecionada
        self.assertContains(response, '<option value="inativa" selected>Inativa</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="ativa" selected>')
        self.assertNotContains(response, '<option value="suspensa" selected>')
    
    def test_status_filter_selection_suspended(self):
        """Testa se o filtro de status 'suspensa' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'), {'status': 'suspensa'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'suspensa' como selecionada
        self.assertContains(response, '<option value="suspensa" selected>Suspensa</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="ativa" selected>')
        self.assertNotContains(response, '<option value="inativa" selected>')
    
    def test_tipo_filter_selection_conveniencia(self):
        """Testa se o filtro de tipo 'conveniencia' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'), {'tipo_loja': 'conveniencia'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'conveniencia' como selecionada
        self.assertContains(response, '<option value="conveniencia" selected>Conveniência')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="roupas" selected>')
        self.assertNotContains(response, '<option value="tintas" selected>')
    
    def test_tipo_filter_selection_roupas(self):
        """Testa se o filtro de tipo 'roupas' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'), {'tipo_loja': 'roupas'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'roupas' como selecionada
        self.assertContains(response, '<option value="roupas" selected>Roupas</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="conveniencia" selected>')
        self.assertNotContains(response, '<option value="tintas" selected>')
    
    def test_no_status_filter_no_selection(self):
        """Testa que nenhuma opção é selecionada quando não há filtro de status."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        self.assertEqual(response.status_code, 200)
        # Nenhuma opção de status deve estar selecionada
        self.assertNotContains(response, '<option value="ativa" selected>')
        self.assertNotContains(response, '<option value="inativa" selected>')
        self.assertNotContains(response, '<option value="suspensa" selected>')
    
    def test_no_tipo_filter_no_selection(self):
        """Testa que nenhuma opção é selecionada quando não há filtro de tipo."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        self.assertEqual(response.status_code, 200)
        # Nenhuma opção de tipo deve estar selecionada
        self.assertNotContains(response, '<option value="conveniencia" selected>')
        self.assertNotContains(response, '<option value="roupas" selected>')
        self.assertNotContains(response, '<option value="tintas" selected>')
        self.assertNotContains(response, '<option value="supermercado" selected>')
        self.assertNotContains(response, '<option value="lanchonete" selected>')
    
    def test_template_syntax_error_prevention(self):
        """Testa que o template não contém erros de sintaxe que causariam TemplateSyntaxError."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Testar com diferentes combinações de filtros para garantir que a sintaxe está correta
        test_cases = [
            {'status': 'ativa'},
            {'status': 'inativa'},
            {'status': 'suspensa'},
            {'tipo_loja': 'conveniencia'},
            {'tipo_loja': 'roupas'},
            {'tipo_loja': 'tintas'},
            {'tipo_loja': 'supermercado'},
            {'tipo_loja': 'lanchonete'},
            {'status': 'ativa', 'tipo_loja': 'conveniencia'},
            {'status': 'inativa', 'tipo_loja': 'roupas'},
        ]
        
        for params in test_cases:
            with self.subTest(params=params):
                response = self.client.get(reverse('listar_lojas'), params)
                # Se houver erro de sintaxe, o status seria 500
                self.assertEqual(response.status_code, 200, 
                    f"TemplateSyntaxError com parâmetros: {params}")
    
    def test_template_renders_with_context_variables(self):
        """Testa que o template renderiza corretamente com todas as variáveis de contexto."""
        context = {
            'lojas': [self.test_store],
            'status_filter': 'ativa',
            'tipo_filter': 'conveniencia',
            'search': 'teste',
            'stats_tipos': {
                'conveniencia': 1,
                'roupas': 0,
                'tintas': 0,
                'supermercado': 0,
                'lanchonete': 0,
            },
        }
        
        try:
            rendered = render_to_string('lojas/listar.html', context)
            self.assertIsNotNone(rendered)
            # Deve conter os valores dos filtros
            self.assertIn('selected', rendered)
            self.assertIn('value="teste"', rendered)
        except Exception as e:
            self.fail(f"Erro ao renderizar template com contexto: {str(e)}")
    
    def test_template_empty_state(self):
        """Testa se o estado vazio é exibido corretamente quando não há lojas."""
        # Remover todas as lojas
        Loja.objects.all().delete()
        
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('listar_lojas'))
        
        # Deve mostrar mensagem de nenhuma loja encontrada
        self.assertContains(response, 'Nenhuma loja encontrada')
        self.assertContains(response, 'bi bi-shop')  # Ícone de loja vazia


class TestTemplateURLValidation(TestCase):
    """Testes específicos para validação de URLs em templates."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar loja de teste
        self.test_store = Loja.objects.create(
            nome='Loja Teste',
            cnpj='12345678901234',
            endereco='Rua Teste, 123'
        )
    
    def test_all_template_urls_can_be_reversed(self):
        """Testa se todas as URLs usadas no template podem ser resolvidas."""
        # URLs que devem existir no template listar.html
        urls_to_test = [
            ('criar_loja', {}),
            ('listar_lojas', {}),
            ('detalhar_loja', {'loja_id': self.test_store.id}),
            ('editar_loja', {'loja_id': self.test_store.id}),
            ('excluir_loja', {'loja_id': self.test_store.id}),
            ('dashboard:loja_especifica', {'loja_id': self.test_store.id}),
        ]
        
        for url_name, kwargs in urls_to_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                self.assertIsNotNone(url)
                self.assertTrue(url.startswith('/'))
            except Exception as e:
                self.fail(f"Erro ao resolver URL {url_name}: {str(e)}")
    
    def test_dashboard_url_with_uuid_parameter(self):
        """Testa especificamente a URL do dashboard com parâmetro UUID."""
        try:
            url = reverse('dashboard:loja_especifica', kwargs={'loja_id': self.test_store.id})
            self.assertIn(str(self.test_store.id), url)
            self.assertTrue(url.startswith('/dashboard/loja/'))
        except Exception as e:
            self.fail(f"Erro ao resolver URL dashboard:loja_especifica: {str(e)}")
    
    def test_template_url_patterns_match_urlconf(self):
        """Testa se os padrões de URL no template correspondem à configuração de URLs."""
        # Verificar se o padrão usado no template existe na configuração
        from django.urls import get_resolver
        
        resolver = get_resolver()
        
        # Verificar se dashboard:loja_especifica existe
        try:
            pattern = resolver.reverse_dict.get(('dashboard:loja_especifica', ()))
            self.assertIsNotNone(pattern, "Padrão dashboard:loja_especifica não encontrado")
        except Exception as e:
            self.fail(f"Erro ao verificar padrão de URL: {str(e)}")