"""
Teste simples para verificar a sintaxe do template de listagem de lojas.
Este teste verifica especificamente se os filtros de status e tipo estão com sintaxe correta.
"""
import os
import django
from django.test import TestCase
from django.template.loader import get_template, render_to_string
from django.template import Context, Template


class TestTemplateSyntax(TestCase):
    """Testes básicos de sintaxe do template."""
    
    def test_template_loads_without_syntax_error(self):
        """Testa se o template carrega sem erros de sintaxe."""
        try:
            template = get_template('lojas/listar.html')
            self.assertIsNotNone(template)
        except Exception as e:
            self.fail(f"Erro de sintaxe no template: {str(e)}")
    
    def test_template_renders_with_basic_context(self):
        """Testa se o template renderiza com contexto básico."""
        context = {
            'lojas': [],
            'status_filter': None,
            'tipo_filter': None,
            'search': '',
            'stats_tipos': {
                'conveniencia': 0,
                'roupas': 0,
                'tintas': 0,
                'supermercado': 0,
                'lanchonete': 0,
            },
        }
        
        try:
            rendered = render_to_string('lojas/listar.html', context)
            self.assertIsNotNone(rendered)
            self.assertIn('Gerenciar Lojas', rendered)
        except Exception as e:
            self.fail(f"Erro ao renderizar template: {str(e)}")
    
    def test_status_filter_syntax_is_correct(self):
        """Testa se a sintaxe dos filtros de status está correta."""
        context = {
            'lojas': [],
            'status_filter': 'ativa',
            'tipo_filter': None,
            'search': '',
            'stats_tipos': {
                'conveniencia': 0,
                'roupas': 0,
                'tintas': 0,
                'supermercado': 0,
                'lanchonete': 0,
            },
        }
        
        try:
            rendered = render_to_string('lojas/listar.html', context)
            self.assertIsNotNone(rendered)
            # Deve conter a opção selecionada
            self.assertIn('selected', rendered)
            # Não deve conter a sintaxe antiga incorreta
            self.assertNotIn("=='", rendered)
        except Exception as e:
            self.fail(f"Erro ao renderizar template com status_filter: {str(e)}")
    
    def test_tipo_filter_syntax_is_correct(self):
        """Testa se a sintaxe dos filtros de tipo está correta."""
        context = {
            'lojas': [],
            'status_filter': None,
            'tipo_filter': 'conveniencia',
            'search': '',
            'stats_tipos': {
                'conveniencia': 0,
                'roupas': 0,
                'tintas': 0,
                'supermercado': 0,
                'lanchonete': 0,
            },
        }
        
        try:
            rendered = render_to_string('lojas/listar.html', context)
            self.assertIsNotNone(rendered)
            # Deve conter a opção selecionada
            self.assertIn('selected', rendered)
            # Não deve conter a sintaxe antiga incorreta
            self.assertNotIn("=='", rendered)
        except Exception as e:
            self.fail(f"Erro ao renderizar template com tipo_filter: {str(e)}")
    
    def test_all_status_values_work(self):
        """Testa se todos os valores de status funcionam corretamente."""
        status_values = ['ativa', 'inativa', 'suspensa']
        
        for status in status_values:
            with self.subTest(status=status):
                context = {
                    'lojas': [],
                    'status_filter': status,
                    'tipo_filter': None,
                    'search': '',
                    'stats_tipos': {
                        'conveniencia': 0,
                        'roupas': 0,
                        'tintas': 0,
                        'supermercado': 0,
                        'lanchonete': 0,
                    },
                }
                
                try:
                    rendered = render_to_string('lojas/listar.html', context)
                    self.assertIsNotNone(rendered)
                    self.assertIn('selected', rendered)
                except Exception as e:
                    self.fail(f"Erro ao renderizar template com status '{status}': {str(e)}")
    
    def test_all_tipo_values_work(self):
        """Testa se todos os valores de tipo funcionam corretamente."""
        tipo_values = ['conveniencia', 'roupas', 'tintas', 'supermercado', 'lanchonete']
        
        for tipo in tipo_values:
            with self.subTest(tipo=tipo):
                context = {
                    'lojas': [],
                    'status_filter': None,
                    'tipo_filter': tipo,
                    'search': '',
                    'stats_tipos': {
                        'conveniencia': 0,
                        'roupas': 0,
                        'tintas': 0,
                        'supermercado': 0,
                        'lanchonete': 0,
                    },
                }
                
                try:
                    rendered = render_to_string('lojas/listar.html', context)
                    self.assertIsNotNone(rendered)
                    self.assertIn('selected', rendered)
                except Exception as e:
                    self.fail(f"Erro ao renderizar template com tipo '{tipo}': {str(e)}")
    
    def test_template_does_not_contain_old_syntax(self):
        """Testa que o template não contém a sintaxe antiga que causava erro."""
        # Ler o arquivo do template diretamente
        template_path = 'templates/lojas/listar.html'
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar que não contém a sintaxe antiga problemática
            self.assertNotIn("status_filter=='ativa'", content)
            self.assertNotIn("status_filter=='inativa'", content)
            self.assertNotIn("status_filter=='suspensa'", content)
            self.assertNotIn("tipo_filter=='conveniencia'", content)
            self.assertNotIn("tipo_filter=='roupas'", content)
            self.assertNotIn("tipo_filter=='tintas'", content)
            self.assertNotIn("tipo_filter=='supermercado'", content)
            self.assertNotIn("tipo_filter=='lanchonete'", content)
            
            # Verificar que contém a sintaxe correta
            self.assertIn('status_filter == "ativa"', content)
            self.assertIn('status_filter == "inativa"', content)
            self.assertIn('status_filter == "suspensa"', content)
            self.assertIn('tipo_filter == "conveniencia"', content)
            self.assertIn('tipo_filter == "roupas"', content)
            
        except FileNotFoundError:
            self.fail(f"Template não encontrado: {template_path}")
        except Exception as e:
            self.fail(f"Erro ao ler template: {str(e)}")