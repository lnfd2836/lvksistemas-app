#!/usr/bin/env python3
"""
Cria middleware de exemplo para demonstrar o conceito
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def criar_middleware_fatesa():
    """Cria middleware específico para Fatesa como exemplo"""
    
    middleware_content = '''"""
Middleware exclusivo para Fatesa Escola de Ultrassonografia
Exemplo de middleware gerado automaticamente
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from lojas.models import Loja

logger = logging.getLogger(__name__)


class LojaFatesaMiddleware:
    """
    Middleware EXCLUSIVO para Fatesa Escola de Ultrassonografia
    - Controla acesso apenas para admin e funcionários da Fatesa
    - Módulos específicos: avaliação de qualidade, cursos, professores
    - Tema corporativo azul
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurações específicas da Fatesa
        self.loja_nome = 'Fatesa Escola de Ultrassonografia'
        self.loja_tipo = 'controle_qualidade'
        
        # URLs exclusivas da Fatesa
        self.fatesa_exclusive_urls = [
            '/login/fatesa-escola-de-ultrassonografia/',
            '/avaliacao-qualidade/',
            '/fatesa/',
        ]
        
        # Módulos disponíveis para Fatesa
        self.fatesa_modulos = [
            'avaliacao_qualidade',
            'cursos',
            'professores',
            'relatorios_academicos'
        ]
        
        # Configurações de acesso
        self.require_fatesa_permission = True
        self.allow_super_admin_override = True
    
    def __call__(self, request):
        """Processa requisições específicas da Fatesa"""
        
        try:
            # Verificar se é requisição da Fatesa
            if self._is_fatesa_request(request):
                return self._handle_fatesa_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no middleware da Fatesa: {str(e)}")
            return self.get_response(request)
    
    def _is_fatesa_request(self, request):
        """Verifica se é requisição da Fatesa"""
        path = request.path
        return any(path.startswith(url) for url in self.fatesa_exclusive_urls)
    
    def _handle_fatesa_request(self, request):
        """Processa requisições da Fatesa"""
        
        # Log de acesso
        logger.info(f"Acesso à Fatesa: {request.path} por {request.user}")
        
        # Verificar permissões
        if not self._has_fatesa_permission(request):
            return self._deny_fatesa_access(request)
        
        # Adicionar contexto da Fatesa
        request.fatesa_context = {
            'loja_nome': self.loja_nome,
            'loja_tipo': self.loja_tipo,
            'modulos_disponiveis': self.fatesa_modulos,
            'tema': 'corporativo_azul',
            'is_fatesa_exclusive': True,
        }
        
        # Configurar sessão da Fatesa
        request.session['current_loja_tipo'] = 'fatesa'
        request.session['tema_ativo'] = 'corporativo'
        
        return self.get_response(request)
    
    def _has_fatesa_permission(self, request):
        """Verifica se usuário tem permissão para acessar a Fatesa"""
        
        # Super admin sempre pode acessar
        if self.allow_super_admin_override and request.user.is_superuser:
            logger.info(f"Super admin {request.user.username} acessando Fatesa")
            return True
        
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é admin da Fatesa
        try:
            fatesa = Loja.objects.get(nome__icontains='Fatesa')
            if fatesa.admin_user == request.user:
                logger.info(f"Admin da Fatesa {request.user.username} acessando")
                return True
        except Loja.DoesNotExist:
            logger.warning("Loja Fatesa não encontrada")
            return False
        
        # Verificar se é funcionário da Fatesa
        if hasattr(request.user, 'funcionario'):
            funcionario = request.user.funcionario
            if funcionario.loja.nome == self.loja_nome:
                logger.info(f"Funcionário da Fatesa {request.user.username} acessando")
                return True
        
        # Verificar se tem perfil específico da Fatesa
        if hasattr(request.user, 'perfil_fatesa'):
            logger.info(f"Usuário com perfil Fatesa {request.user.username} acessando")
            return True
        
        return False
    
    def _deny_fatesa_access(self, request):
        """Nega acesso à Fatesa"""
        
        logger.warning(f"Acesso negado à Fatesa para usuário: {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Você não tem permissão para acessar a Fatesa Escola de Ultrassonografia'
            }, status=403)
        
        messages.error(
            request, 
            'Acesso negado. Você não tem permissão para acessar a Fatesa Escola de Ultrassonografia.'
        )
        return redirect('root_redirect')
'''
    
    # Criar arquivo do middleware
    middleware_path = 'lojas/middleware/loja_fatesa_middleware.py'
    
    try:
        with open(middleware_path, 'w', encoding='utf-8') as f:
            f.write(middleware_content)
        
        print("✅ Middleware da Fatesa criado como exemplo!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar middleware da Fatesa: {e}")
        return False


def criar_middleware_felix():
    """Cria middleware específico para Felix como exemplo"""
    
    middleware_content = '''"""
Middleware exclusivo para Loja Felix - Clínica de Estética
Exemplo de middleware gerado automaticamente
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from lojas.models import Loja

logger = logging.getLogger(__name__)


class LojaFelixMiddleware:
    """
    Middleware EXCLUSIVO para Loja Felix - Clínica de Estética
    - Controla acesso apenas para admin e funcionários da Felix
    - Módulos específicos: agendamento, procedimentos, clientes
    - Tema moderno
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurações específicas da Felix
        self.loja_nome = 'Loja Felix'
        self.loja_tipo = 'clinica_estetica'
        
        # URLs exclusivas da Felix
        self.felix_exclusive_urls = [
            '/login/loja-felix/',
            '/modulos/estetica/',
            '/felix/',
        ]
        
        # Módulos disponíveis para Felix
        self.felix_modulos = [
            'agendamento',
            'procedimentos',
            'clientes',
            'produtos_esteticos'
        ]
        
        # Configurações de acesso
        self.require_felix_permission = True
        self.allow_super_admin_override = True
    
    def __call__(self, request):
        """Processa requisições específicas da Felix"""
        
        try:
            # Verificar se é requisição da Felix
            if self._is_felix_request(request):
                return self._handle_felix_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no middleware da Felix: {str(e)}")
            return self.get_response(request)
    
    def _is_felix_request(self, request):
        """Verifica se é requisição da Felix"""
        path = request.path
        return any(path.startswith(url) for url in self.felix_exclusive_urls)
    
    def _handle_felix_request(self, request):
        """Processa requisições da Felix"""
        
        # Log de acesso
        logger.info(f"Acesso à Felix: {request.path} por {request.user}")
        
        # Verificar permissões
        if not self._has_felix_permission(request):
            return self._deny_felix_access(request)
        
        # Adicionar contexto da Felix
        request.felix_context = {
            'loja_nome': self.loja_nome,
            'loja_tipo': self.loja_tipo,
            'modulos_disponiveis': self.felix_modulos,
            'tema': 'moderno',
            'is_felix_exclusive': True,
        }
        
        # Configurar sessão da Felix
        request.session['current_loja_tipo'] = 'felix'
        request.session['tema_ativo'] = 'moderno'
        
        return self.get_response(request)
    
    def _has_felix_permission(self, request):
        """Verifica se usuário tem permissão para acessar a Felix"""
        
        # Super admin sempre pode acessar
        if self.allow_super_admin_override and request.user.is_superuser:
            return True
        
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é admin da Felix
        try:
            felix = Loja.objects.get(nome__icontains='Felix')
            if felix.admin_user == request.user:
                return True
        except Loja.DoesNotExist:
            return False
        
        # Verificar se é funcionário da Felix
        if hasattr(request.user, 'funcionario'):
            funcionario = request.user.funcionario
            if 'felix' in funcionario.loja.nome.lower():
                return True
        
        return False
    
    def _deny_felix_access(self, request):
        """Nega acesso à Felix"""
        
        logger.warning(f"Acesso negado à Felix para usuário: {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Você não tem permissão para acessar a Loja Felix'
            }, status=403)
        
        messages.error(request, 'Acesso negado. Você não tem permissão para acessar a Loja Felix.')
        return redirect('root_redirect')
'''
    
    # Criar arquivo do middleware
    middleware_path = 'lojas/middleware/loja_felix_middleware.py'
    
    try:
        with open(middleware_path, 'w', encoding='utf-8') as f:
            f.write(middleware_content)
        
        print("✅ Middleware da Felix criado como exemplo!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar middleware da Felix: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 80)
    print("🏭 CRIAÇÃO DE MIDDLEWARES DE EXEMPLO POR LOJA")
    print("=" * 80)
    print()
    
    success_count = 0
    
    # Criar middleware da Fatesa
    print("1️⃣  Criando middleware da Fatesa...")
    if criar_middleware_fatesa():
        success_count += 1
    print()
    
    # Criar middleware da Felix
    print("2️⃣  Criando middleware da Felix...")
    if criar_middleware_felix():
        success_count += 1
    print()
    
    print("=" * 80)
    print("📋 RESUMO DOS MIDDLEWARES DE EXEMPLO")
    print("=" * 80)
    
    if success_count >= 2:
        print("✅ MIDDLEWARES DE EXEMPLO CRIADOS COM SUCESSO!")
        print()
        print("🎯 Middlewares criados:")
        print("  1. ✅ LojaFatesaMiddleware - Controle exclusivo da Fatesa")
        print("  2. ✅ LojaFelixMiddleware - Controle exclusivo da Felix")
        print()
        print("🔧 Características:")
        print("  • Acesso exclusivo para admin e funcionários da loja")
        print("  • Módulos específicos por tipo de loja")
        print("  • Temas personalizados")
        print("  • Logs detalhados de acesso")
        print("  • Super admin pode acessar qualquer loja")
        
    else:
        print("⚠️  CRIAÇÃO PARCIAL - Alguns middlewares falharam")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()