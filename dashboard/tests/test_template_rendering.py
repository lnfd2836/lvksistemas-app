"""
Testes para renderização de templates do dashboard
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from lojas.models import Loja
from modulos.models import TipoLoja


class TemplateRenderingTests(TestCase):
    """Testes para verificar se os templates renderizam sem erros"""
    
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
        
        # Criar tipo de loja (se o modelo existir)
        try:
            self.tipo_loja = TipoLoja.objects.create(
                nome='conveniencia',
                descricao='Loja de Conveniência'
            )
        except:
            self.tipo_loja = None
        
        # Criar loja de teste
        loja_data = {
            'nome': 'Loja Teste',
            'cnpj': '12.345.678/0001-90',
            'email': 'loja@teste.com',
            'telefone': '(11) 99999-9999',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01234-567',
            'db_name': 'test_db',
            'admin_user': self.normal_user
        }
        
        if self.tipo_loja:
            loja_data['tipo_loja'] = self.tipo_loja
            
        self.loja = Loja.objects.create(**loja_data)
    
    def test_dashboard_usuarios_super_admin_renders(self):
        """Testa se a página de usuários super admin renderiza sem erros"""
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Acessar a página
        url = reverse('dashboard:admin_usuarios_lista')
        response = self.client.get(url)
        
        # Verificar se não há erro 500
        self.assertNotEqual(response.status_code, 500)
        
        # Se o usuário tem permissão, deve retornar 200
        if response.status_code == 200:
            # Verificar se o template foi renderizado corretamente
            self.assertContains(response, 'Usuários Super Administradores')
            self.assertContains(response, 'dashboard:admin_usuarios_criar')
            
            # Verificar se as URLs dos botões estão corretas
            self.assertContains(response, 'dashboard:admin_usuarios_editar')
            self.assertContains(response, 'dashboard:admin_usuarios_alterar_senha')
            self.assertContains(response, 'dashboard:admin_usuarios_excluir')
    
    def test_lojas_listar_renders(self):
        """Testa se a página de listagem de lojas renderiza sem erros"""
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Acessar a página
        url = reverse('listar_lojas')
        response = self.client.get(url)
        
        # Verificar se não há erro 500
        self.assertNotEqual(response.status_code, 500)
        
        # Se o usuário tem permissão, deve retornar 200
        if response.status_code == 200:
            # Verificar se o template foi renderizado corretamente
            self.assertContains(response, 'Gerenciar Lojas')
            self.assertContains(response, 'Nova Loja')
            
            # Verificar se a loja aparece na listagem
            self.assertContains(response, self.loja.nome)
            
            # Verificar se as URLs dos botões estão corretas
            self.assertContains(response, 'dashboard:loja_especifica')
    
    def test_dashboard_loja_especifica_renders(self):
        """Testa se o dashboard específico da loja renderiza sem erros"""
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Acessar o dashboard da loja específica
        url = reverse('dashboard:loja_especifica', kwargs={'loja_id': self.loja.id})
        response = self.client.get(url)
        
        # Verificar se não há erro 500
        self.assertNotEqual(response.status_code, 500)
        
        # Verificar se retorna uma resposta válida (200, 302, etc.)
        self.assertIn(response.status_code, [200, 302, 403])
    
    def test_url_generation_in_templates(self):
        """Testa se a geração de URLs nos templates funciona corretamente"""
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Testar página de usuários
        url = reverse('dashboard:admin_usuarios_lista')
        response = self.client.get(url)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar se não há erros de NoReverseMatch no conteúdo
            self.assertNotIn('NoReverseMatch', content)
            self.assertNotIn('Reverse for', content)
            self.assertNotIn('not found', content)
        
        # Testar página de lojas
        url = reverse('listar_lojas')
        response = self.client.get(url)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar se não há erros de NoReverseMatch no conteúdo
            self.assertNotIn('NoReverseMatch', content)
            self.assertNotIn('Reverse for', content)
            self.assertNotIn('not found', content)
    
    def test_template_context_variables(self):
        """Testa se as variáveis de contexto estão sendo passadas corretamente"""
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Testar página de lojas
        url = reverse('listar_lojas')
        response = self.client.get(url)
        
        if response.status_code == 200:
            # Verificar se as variáveis de contexto estão presentes
            self.assertIn('lojas', response.context)
            
            # Verificar se a loja criada está no contexto
            lojas = response.context['lojas']
            self.assertIn(self.loja, lojas)
    
    def test_error_handling_for_invalid_urls(self):
        """Testa o tratamento de erros para URLs inválidas"""
        # Login como super admin
        self.client.login(username='superadmin', password='superpass123')
        
        # Testar URL com UUID inválido
        invalid_uuid = '12345678-1234-1234-1234-123456789012'
        url = f'/dashboard/loja/{invalid_uuid}/'
        response = self.client.get(url)
        
        # Deve retornar 404 ou outro erro apropriado, não 500
        self.assertNotEqual(response.status_code, 500)
        
        # Testar URL com ID de usuário inválido
        url = '/dashboard/admin/usuarios/99999/editar/'
        response = self.client.get(url)
        
        # Deve retornar 404 ou outro erro apropriado, não 500
        self.assertNotEqual(response.status_code, 500)