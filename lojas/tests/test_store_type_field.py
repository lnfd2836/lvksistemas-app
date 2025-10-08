"""
Testes específicos para o campo tipo_loja no formulário de edição de lojas.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.forms.models import model_to_dict

from lojas.models import Loja
from lojas.forms import LojaForm
from modulos.models import TipoLoja


class TestStoreTypeField(TestCase):
    """Testes para o campo tipo de loja."""
    
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
        
        # Criar tipos de loja para teste
        self.tipo_conveniencia = TipoLoja.objects.create(
            nome='conveniencia',
            descricao='Loja de Conveniência',
            ativo=True
        )
        
        self.tipo_roupas = TipoLoja.objects.create(
            nome='roupas',
            descricao='Loja de Roupas',
            ativo=True
        )
        
        # Criar loja de teste sem tipo
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
        
        # Criar loja com tipo
        self.store_with_type = Loja.objects.create(
            nome='Loja Com Tipo',
            cnpj='98765432109876',
            endereco='Rua Com Tipo, 456',
            cidade='Rio de Janeiro',
            estado='RJ',
            email='comtipo@loja.com',
            telefone='21999999999',
            cep='98765432',
            status='ativa',
            admin_user=self.admin_user,
            tipo_loja=self.tipo_conveniencia
        )
    
    def test_edit_form_includes_tipo_loja_field(self):
        """Testa se o formulário de edição inclui o campo tipo_loja."""
        form = LojaForm(instance=self.test_store)
        
        # Verificar se o campo tipo_loja está presente
        self.assertIn('tipo_loja', form.fields)
        
        # Verificar se o campo tem as configurações corretas
        tipo_loja_field = form.fields['tipo_loja']
        self.assertFalse(tipo_loja_field.required)
        self.assertEqual(tipo_loja_field.empty_label, "Selecione o tipo de atividade da loja")
    
    def test_edit_template_renders_tipo_loja_field(self):
        """Testa se o template de edição renderiza o campo tipo_loja."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:editar_loja', kwargs={'loja_id': self.test_store.id}))
        
        # Deve renderizar com sucesso
        self.assertEqual(response.status_code, 200)
        
        # Deve conter o campo tipo_loja
        self.assertContains(response, 'form.tipo_loja')
        self.assertContains(response, 'tipo_loja')
        
        # Deve conter o label do campo
        self.assertContains(response, 'Tipo de Loja')
    
    def test_edit_form_saves_tipo_loja_correctly(self):
        """Testa se o formulário salva o tipo_loja corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Dados para atualização
        form_data = {
            'nome': self.test_store.nome,
            'cnpj': self.test_store.cnpj,
            'email': self.test_store.email,
            'telefone': self.test_store.telefone,
            'endereco': self.test_store.endereco,
            'cidade': self.test_store.cidade,
            'estado': self.test_store.estado,
            'cep': self.test_store.cep,
            'status': self.test_store.status,
            'tipo_loja': self.tipo_conveniencia.id
        }
        
        # Enviar POST para editar
        response = self.client.post(
            reverse('lojas:editar_loja', kwargs={'loja_id': self.test_store.id}),
            data=form_data
        )
        
        # Deve redirecionar após sucesso
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o tipo foi salvo
        self.test_store.refresh_from_db()
        self.assertEqual(self.test_store.tipo_loja, self.tipo_conveniencia)
    
    def test_edit_form_updates_tipo_loja_correctly(self):
        """Testa se o formulário atualiza o tipo_loja corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Dados para atualização (mudando de conveniencia para roupas)
        form_data = {
            'nome': self.store_with_type.nome,
            'cnpj': self.store_with_type.cnpj,
            'email': self.store_with_type.email,
            'telefone': self.store_with_type.telefone,
            'endereco': self.store_with_type.endereco,
            'cidade': self.store_with_type.cidade,
            'estado': self.store_with_type.estado,
            'cep': self.store_with_type.cep,
            'status': self.store_with_type.status,
            'tipo_loja': self.tipo_roupas.id
        }
        
        # Enviar POST para editar
        response = self.client.post(
            reverse('lojas:editar_loja', kwargs={'loja_id': self.store_with_type.id}),
            data=form_data
        )
        
        # Deve redirecionar após sucesso
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o tipo foi atualizado
        self.store_with_type.refresh_from_db()
        self.assertEqual(self.store_with_type.tipo_loja, self.tipo_roupas)
    
    def test_edit_form_can_remove_tipo_loja(self):
        """Testa se o formulário pode remover o tipo_loja (definir como None)."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Dados para atualização (removendo o tipo)
        form_data = {
            'nome': self.store_with_type.nome,
            'cnpj': self.store_with_type.cnpj,
            'email': self.store_with_type.email,
            'telefone': self.store_with_type.telefone,
            'endereco': self.store_with_type.endereco,
            'cidade': self.store_with_type.cidade,
            'estado': self.store_with_type.estado,
            'cep': self.store_with_type.cep,
            'status': self.store_with_type.status,
            'tipo_loja': ''  # Campo vazio
        }
        
        # Enviar POST para editar
        response = self.client.post(
            reverse('lojas:editar_loja', kwargs={'loja_id': self.store_with_type.id}),
            data=form_data
        )
        
        # Deve redirecionar após sucesso
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o tipo foi removido
        self.store_with_type.refresh_from_db()
        self.assertIsNone(self.store_with_type.tipo_loja)
    
    def test_edit_form_preselects_existing_tipo_loja(self):
        """Testa se o formulário pré-seleciona o tipo_loja existente."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:editar_loja', kwargs={'loja_id': self.store_with_type.id}))
        
        # Deve renderizar com sucesso
        self.assertEqual(response.status_code, 200)
        
        # Deve pré-selecionar o tipo existente
        self.assertContains(response, f'value="{self.tipo_conveniencia.id}" selected')
    
    def test_create_form_includes_tipo_loja_field(self):
        """Testa se o formulário de criação inclui o campo tipo_loja."""
        self.client.login(username='superadmin', password='testpass123')
        
        response = self.client.get(reverse('lojas:criar_loja'))
        
        # Deve renderizar com sucesso
        self.assertEqual(response.status_code, 200)
        
        # Deve conter o campo tipo_loja
        self.assertContains(response, 'tipo_loja')
        self.assertContains(response, 'Tipo de Loja')
    
    def test_create_form_saves_tipo_loja_correctly(self):
        """Testa se o formulário de criação salva o tipo_loja corretamente."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Dados para criação
        form_data = {
            'nome': 'Nova Loja',
            'cnpj': '11111111111111',
            'email': 'nova@loja.com',
            'telefone': '11888888888',
            'endereco': 'Rua Nova, 789',
            'cidade': 'Brasília',
            'estado': 'DF',
            'cep': '11111111',
            'status': 'ativa',
            'tipo_loja': self.tipo_roupas.id
        }
        
        # Enviar POST para criar
        response = self.client.post(reverse('lojas:criar_loja'), data=form_data)
        
        # Deve redirecionar após sucesso
        self.assertEqual(response.status_code, 302)
        
        # Verificar se a loja foi criada com o tipo correto
        nova_loja = Loja.objects.get(cnpj='11111111111111')
        self.assertEqual(nova_loja.tipo_loja, self.tipo_roupas)
    
    def test_form_validation_with_invalid_tipo_loja(self):
        """Testa a validação do formulário com tipo_loja inválido."""
        form_data = {
            'nome': 'Loja Teste',
            'cnpj': '12345678901234',
            'email': 'teste@loja.com',
            'telefone': '11999999999',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01234567',
            'status': 'ativa',
            'tipo_loja': 99999  # ID inválido
        }
        
        form = LojaForm(data=form_data)
        
        # Formulário deve ser inválido
        self.assertFalse(form.is_valid())
        
        # Deve ter erro no campo tipo_loja
        self.assertIn('tipo_loja', form.errors)
    
    def test_form_validation_without_tipo_loja(self):
        """Testa a validação do formulário sem tipo_loja (deve ser válido)."""
        form_data = {
            'nome': 'Loja Teste',
            'cnpj': '12345678901234',
            'email': 'teste@loja.com',
            'telefone': '11999999999',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01234567',
            'status': 'ativa'
            # tipo_loja não fornecido
        }
        
        form = LojaForm(data=form_data)
        
        # Formulário deve ser válido (tipo_loja é opcional)
        self.assertTrue(form.is_valid())
    
    def test_tipo_loja_queryset_only_active_types(self):
        """Testa se o campo tipo_loja mostra apenas tipos ativos."""
        # Criar tipo inativo
        tipo_inativo = TipoLoja.objects.create(
            nome='farmacia',
            descricao='Farmácia',
            ativo=False
        )
        
        form = LojaForm()
        
        # Verificar se apenas tipos ativos estão no queryset
        tipo_loja_field = form.fields['tipo_loja']
        queryset_ids = list(tipo_loja_field.queryset.values_list('id', flat=True))
        
        self.assertIn(self.tipo_conveniencia.id, queryset_ids)
        self.assertIn(self.tipo_roupas.id, queryset_ids)
        self.assertNotIn(tipo_inativo.id, queryset_ids)
    
    def test_edit_template_error_handling(self):
        """Testa se o template de edição lida com erros do campo tipo_loja."""
        self.client.login(username='superadmin', password='testpass123')
        
        # Enviar dados inválidos
        form_data = {
            'nome': '',  # Nome obrigatório vazio
            'cnpj': self.test_store.cnpj,
            'email': 'email_invalido',  # Email inválido
            'telefone': self.test_store.telefone,
            'endereco': self.test_store.endereco,
            'cidade': self.test_store.cidade,
            'estado': self.test_store.estado,
            'cep': self.test_store.cep,
            'status': self.test_store.status,
            'tipo_loja': 99999  # ID inválido
        }
        
        response = self.client.post(
            reverse('lojas:editar_loja', kwargs={'loja_id': self.test_store.id}),
            data=form_data
        )
        
        # Deve retornar o formulário com erros (não redirecionar)
        self.assertEqual(response.status_code, 200)
        
        # Deve conter mensagens de erro
        self.assertContains(response, 'text-danger')
        
        # Deve manter o campo tipo_loja no formulário
        self.assertContains(response, 'tipo_loja')