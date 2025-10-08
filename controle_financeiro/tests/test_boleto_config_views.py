"""
Tests for boleto configuration views with new UI improvements
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

from controle_financeiro.models import ConfiguracaoBoleto


class BoletoConfigurationViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create superuser
        self.superuser = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        # Create test configuration
        self.config = ConfiguracaoBoleto.objects.create(
            nome_banco='Banco Teste',
            codigo_banco='001',
            agencia='1234',
            conta='12345678',
            carteira='18',
            nome_beneficiario='Empresa Teste',
            cnpj_beneficiario='12.345.678/0001-90',
            endereco_beneficiario='Rua Teste, 123',
            multa=Decimal('2.00'),
            juros=Decimal('1.00'),
            desconto=Decimal('0.00'),
            ativo=True
        )
    
    def test_configurar_boletos_view_with_existing_config(self):
        """Test that form is hidden when configurations exist"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('controle_financeiro:configurar_boletos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'config-form-container')
        self.assertTrue(response.context['has_configurations'])
        self.assertFalse(response.context['show_form'])
        self.assertIsNotNone(response.context['configuracao_ativa'])
    
    def test_configurar_boletos_view_without_config(self):
        """Test that form is shown when no configurations exist"""
        # Delete existing config
        ConfiguracaoBoleto.objects.all().delete()
        
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('controle_financeiro:configurar_boletos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_configurations'])
        self.assertTrue(response.context['show_form'])
        self.assertIsNone(response.context['configuracao_ativa'])
    
    def test_configurar_boletos_view_with_show_form_param(self):
        """Test that form is shown when show_form parameter is true"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(
            reverse('controle_financeiro:configurar_boletos') + '?show_form=true'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_form'])
    
    def test_successful_form_submission(self):
        """Test successful form submission hides form"""
        self.client.login(username='admin', password='testpass123')
        
        form_data = {
            'nome_banco': 'Novo Banco',
            'codigo_banco': '002',
            'agencia': '5678',
            'conta': '87654321',
            'carteira': '17',
            'nome_beneficiario': 'Nova Empresa',
            'cnpj_beneficiario': '98.765.432/0001-10',
            'endereco_beneficiario': 'Nova Rua, 456',
            'multa': '2.50',
            'juros': '1.50',
            'desconto': '0.00',
            'ativo': 'on'
        }
        
        response = self.client.post(
            reverse('controle_financeiro:configurar_boletos'),
            data=form_data
        )
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Check that new config was created
        new_config = ConfiguracaoBoleto.objects.filter(nome_banco='Novo Banco').first()
        self.assertIsNotNone(new_config)
        self.assertTrue(new_config.ativo)
        
        # Check that old config was deactivated
        old_config = ConfiguracaoBoleto.objects.get(id=self.config.id)
        self.assertFalse(old_config.ativo)
    
    def test_form_validation_errors_show_form(self):
        """Test that validation errors force form to be shown"""
        self.client.login(username='admin', password='testpass123')
        
        # Submit form with missing required fields
        form_data = {
            'nome_banco': '',  # Required field missing
            'codigo_banco': '002',
        }
        
        response = self.client.post(
            reverse('controle_financeiro:configurar_boletos'),
            data=form_data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_errors'])
        self.assertTrue(response.context['show_form'])
    
    def test_edit_configuration_view(self):
        """Test edit configuration view"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(
            reverse('controle_financeiro:editar_configuracao_boleto', 
                   kwargs={'config_id': self.config.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['config'], self.config)
        self.assertContains(response, 'Banco Teste')
        self.assertContains(response, 'config-form-container')
    
    def test_edit_configuration_submission(self):
        """Test editing configuration"""
        self.client.login(username='admin', password='testpass123')
        
        form_data = {
            'nome_banco': 'Banco Editado',
            'codigo_banco': '001',
            'agencia': '1234',
            'conta': '12345678',
            'carteira': '18',
            'nome_beneficiario': 'Empresa Editada',
            'cnpj_beneficiario': '12.345.678/0001-90',
            'endereco_beneficiario': 'Rua Editada, 123',
            'multa': '3.00',
            'juros': '2.00',
            'desconto': '1.00',
            'ativo': 'on'
        }
        
        response = self.client.post(
            reverse('controle_financeiro:editar_configuracao_boleto', 
                   kwargs={'config_id': self.config.id}),
            data=form_data
        )
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Check that config was updated
        updated_config = ConfiguracaoBoleto.objects.get(id=self.config.id)
        self.assertEqual(updated_config.nome_banco, 'Banco Editado')
        self.assertEqual(updated_config.nome_beneficiario, 'Empresa Editada')
        self.assertEqual(updated_config.multa, Decimal('3.00'))
    
    def test_non_superuser_access_denied(self):
        """Test that non-superusers cannot access configuration views"""
        # Create regular user
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='testpass123'
        )
        
        self.client.login(username='regular', password='testpass123')
        
        # Test main configuration view
        response = self.client.get(reverse('controle_financeiro:configurar_boletos'))
        self.assertEqual(response.status_code, 302)  # Redirect to login or forbidden
        
        # Test edit configuration view
        response = self.client.get(
            reverse('controle_financeiro:editar_configuracao_boleto', 
                   kwargs={'config_id': self.config.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login or forbidden
    
    def test_context_variables_present(self):
        """Test that all required context variables are present"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('controle_financeiro:configurar_boletos'))
        
        required_context_vars = [
            'configuracoes',
            'configuracao_ativa',
            'show_form',
            'form_errors',
            'form_success',
            'has_configurations'
        ]
        
        for var in required_context_vars:
            self.assertIn(var, response.context)
    
    def test_javascript_data_in_template(self):
        """Test that JavaScript data is properly embedded in template"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('controle_financeiro:configurar_boletos'))
        
        self.assertContains(response, 'window.boletoConfigData')
        self.assertContains(response, 'hasConfigurations')
        self.assertContains(response, 'showForm')
        self.assertContains(response, 'formErrors')
    
    def test_css_and_js_files_included(self):
        """Test that CSS and JS files are properly included"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('controle_financeiro:configurar_boletos'))
        
        self.assertContains(response, 'boleto-config.css')
        self.assertContains(response, 'boleto-config.js')