"""
Testes específicos para os filtros de status e tipo no template de listagem de lojas.
Estes testes foram criados para prevenir futuros erros de sintaxe de template.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string

from lojas.models import Loja


class TestTemplateFilters(TestCase):
    """Testes para os filtros de status e tipo no template de lojas."""
    
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
    
    def test_status_filter_selection_active(self):
        """Testa se o filtro de status 'ativa' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'status': 'ativa'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'ativa' como selecionada
        self.assertContains(response, '<option value="ativa" selected>Ativa</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="inativa" selected>')
        self.assertNotContains(response, '<option value="suspensa" selected>')
    
    def test_status_filter_selection_inactive(self):
        """Testa se o filtro de status 'inativa' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'status': 'inativa'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'inativa' como selecionada
        self.assertContains(response, '<option value="inativa" selected>Inativa</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="ativa" selected>')
        self.assertNotContains(response, '<option value="suspensa" selected>')
    
    def test_status_filter_selection_suspended(self):
        """Testa se o filtro de status 'suspensa' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'status': 'suspensa'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'suspensa' como selecionada
        self.assertContains(response, '<option value="suspensa" selected>Suspensa</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="ativa" selected>')
        self.assertNotContains(response, '<option value="inativa" selected>')
    
    def test_tipo_filter_selection_conveniencia(self):
        """Testa se o filtro de tipo 'conveniencia' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'tipo_loja': 'conveniencia'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'conveniencia' como selecionada
        self.assertContains(response, '<option value="conveniencia" selected>Conveniência')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="roupas" selected>')
        self.assertNotContains(response, '<option value="tintas" selected>')
    
    def test_tipo_filter_selection_roupas(self):
        """Testa se o filtro de tipo 'roupas' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'tipo_loja': 'roupas'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'roupas' como selecionada
        self.assertContains(response, '<option value="roupas" selected>Roupas</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="conveniencia" selected>')
        self.assertNotContains(response, '<option value="tintas" selected>')
    
    def test_tipo_filter_selection_tintas(self):
        """Testa se o filtro de tipo 'tintas' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'tipo_loja': 'tintas'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'tintas' como selecionada
        self.assertContains(response, '<option value="tintas" selected>Tintas</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="conveniencia" selected>')
        self.assertNotContains(response, '<option value="roupas" selected>')
    
    def test_tipo_filter_selection_supermercado(self):
        """Testa se o filtro de tipo 'supermercado' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'tipo_loja': 'supermercado'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'supermercado' como selecionada
        self.assertContains(response, '<option value="supermercado" selected>Supermercado')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="conveniencia" selected>')
        self.assertNotContains(response, '<option value="roupas" selected>')
    
    def test_tipo_filter_selection_lanchonete(self):
        """Testa se o filtro de tipo 'lanchonete' é selecionado corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'), {'tipo_loja': 'lanchonete'})
        
        self.assertEqual(response.status_code, 200)
        # Deve marcar a opção 'lanchonete' como selecionada
        self.assertContains(response, '<option value="lanchonete" selected>Lanchonete</option>')
        # Não deve marcar outras opções como selecionadas
        self.assertNotContains(response, '<option value="conveniencia" selected>')
        self.assertNotContains(response, '<option value="roupas" selected>')
    
    def test_no_status_filter_no_selection(self):
        """Testa que nenhuma opção é selecionada quando não há filtro de status."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'))
        
        self.assertEqual(response.status_code, 200)
        # Nenhuma opção de status deve estar selecionada
        self.assertNotContains(response, '<option value="ativa" selected>')
        self.assertNotContains(response, '<option value="inativa" selected>')
        self.assertNotContains(response, '<option value="suspensa" selected>')
    
    def test_no_tipo_filter_no_selection(self):
        """Testa que nenhuma opção é selecionada quando não há filtro de tipo."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:listar_lojas'))
        
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
            {'status': 'suspensa', 'tipo_loja': 'tintas'},
        ]
        
        for params in test_cases:
            with self.subTest(params=params):
                response = self.client.get(reverse('lojas:listar_lojas'), params)
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
    
    def test_combined_filters_work_correctly(self):
        """Testa que filtros combinados funcionam corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Testar filtro combinado de status e tipo
        response = self.client.get(reverse('lojas:listar_lojas'), {
            'status': 'ativa',
            'tipo_loja': 'conveniencia',
            'search': 'Teste'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Deve manter ambos os filtros selecionados
        self.assertContains(response, '<option value="ativa" selected>')
        self.assertContains(response, '<option value="conveniencia" selected>')
        self.assertContains(response, 'value="Teste"')
    
    def test_template_filter_syntax_is_correct(self):
        """Testa especificamente que a sintaxe dos filtros no template está correta."""
        # Renderizar template diretamente para verificar sintaxe
        context = {
            'lojas': [self.test_store],
            'status_filter': 'ativa',
            'tipo_filter': 'conveniencia',
            'search': '',
            'stats_tipos': {
                'conveniencia': 1,
                'roupas': 0,
                'tintas': 0,
                'supermercado': 0,
                'lanchonete': 0,
            },
        }
        
        # Se a sintaxe estiver incorreta, isso gerará uma TemplateSyntaxError
        try:
            rendered = render_to_string('lojas/listar.html', context)
            
            # Verificar que as comparações estão funcionando corretamente
            self.assertIn('selected', rendered)
            
            # Verificar que não há sintaxe malformada no HTML renderizado
            self.assertNotIn("=='", rendered)  # Sintaxe antiga incorreta
            self.assertNotIn("status_filter=='ativa'", rendered)  # Sintaxe antiga incorreta
            
        except Exception as e:
            self.fail(f"Erro de sintaxe no template: {str(e)}")