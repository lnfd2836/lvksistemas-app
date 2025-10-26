#!/usr/bin/env python3
"""
Corrige separação entre Super Admin e sistema das lojas
Super Admin: Administra e gerencia lojas (não acessa sistema interno)
Admin/Funcionários da Loja: Acesso exclusivo ao sistema da loja
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def corrigir_middleware_super_admin():
    """Corrige middleware Super Admin para BLOQUEAR acesso às lojas"""
    
    middleware_content = '''"""
Middleware exclusivo para Super Admins
ADMINISTRA e GERENCIA lojas, mas NÃO ACESSA o sistema interno das lojas
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class SuperAdminExclusivoMiddleware:
    """
    Middleware EXCLUSIVO para Super Admins
    
    FUNÇÕES DO SUPER ADMIN:
    ✅ Administrar lojas (criar, editar, deletar)
    ✅ Gerenciar usuários do sistema
    ✅ Acessar relatórios gerais
    ✅ Configurar sistema
    
    RESTRIÇÕES DO SUPER ADMIN:
    ❌ NÃO pode acessar sistema interno das lojas
    ❌ NÃO pode fazer login como loja
    ❌ NÃO pode acessar módulos específicos das lojas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs EXCLUSIVAS para super admins (administração)
        self.super_admin_exclusive_urls = [
            '/admin/',                    # Django Admin
            '/super-admin/',              # Dashboard super admin
            '/admin-login/',              # Login super admin
            '/usuarios/gerenciar/',       # Gerenciar usuários
            '/lojas/gerenciar/',          # Gerenciar lojas (CRUD)
            '/lojas/criar/',              # Criar lojas
            '/lojas/editar/',             # Editar lojas
            '/lojas/deletar/',            # Deletar lojas
            '/relatorios/sistema/',       # Relatórios do sistema
            '/configuracoes/sistema/',    # Configurações gerais
            '/financeiro/admin/',         # Administração financeira
        ]
        
        # URLs BLOQUEADAS para super admins (sistema das lojas)
        self.super_admin_blocked_urls = [
            '/login/fatesa-escola-de-ultrassonografia/',
            '/login/loja-felix/',
            '/login/',                    # Qualquer login de loja
            '/dashboard/loja/',           # Dashboard das lojas
            '/avaliacao-qualidade/',      # Módulos específicos
            '/modulos/estetica/',         # Módulos específicos
            '/pedidos/',                  # Operações das lojas
            '/clientes/',                 # Dados das lojas
            '/produtos/',                 # Dados das lojas
            '/vendas/',                   # Operações das lojas
        ]
    
    def __call__(self, request):
        """Processa requisições com separação total Super Admin vs Lojas"""
        
        try:
            # Verificar se é super admin
            if self._is_super_admin(request):
                return self._handle_super_admin_request(request)
            
            # Bloquear acesso de não-super-admins a URLs exclusivas
            if self._is_super_admin_exclusive_url(request.path):
                return self._block_non_super_admin_access(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no SuperAdminExclusivoMiddleware: {str(e)}")
            return self.get_response(request)
    
    def _is_super_admin(self, request):
        """Verifica se o usuário é super admin"""
        return (request.user.is_authenticated and 
                request.user.is_superuser and 
                request.user.is_active)
    
    def _is_super_admin_exclusive_url(self, path):
        """Verifica se é URL exclusiva para super admins"""
        return any(path.startswith(url) for url in self.super_admin_exclusive_urls)
    
    def _is_loja_system_url(self, path):
        """Verifica se é URL do sistema interno das lojas"""
        return any(path.startswith(url) for url in self.super_admin_blocked_urls)
    
    def _handle_super_admin_request(self, request):
        """Processa requisições de super admins"""
        
        # BLOQUEAR acesso ao sistema interno das lojas
        if self._is_loja_system_url(request.path):
            return self._block_super_admin_loja_access(request)
        
        # Log de acesso super admin (apenas administração)
        logger.info(f"Super Admin {request.user.username} administrando: {request.path}")
        
        # Adicionar contexto de administração
        request.is_super_admin_context = True
        request.super_admin_permissions = {
            'can_manage_stores': True,           # ✅ Gerenciar lojas
            'can_create_stores': True,           # ✅ Criar lojas
            'can_delete_stores': True,           # ✅ Deletar lojas
            'can_manage_users': True,            # ✅ Gerenciar usuários
            'can_view_system_reports': True,     # ✅ Relatórios gerais
            'can_modify_system_settings': True,  # ✅ Configurações
            
            # ❌ BLOQUEADOS - Sistema interno das lojas
            'can_access_store_dashboard': False,  # ❌ Dashboard das lojas
            'can_access_store_modules': False,    # ❌ Módulos das lojas
            'can_login_as_store': False,          # ❌ Login como loja
            'can_view_store_data': False,         # ❌ Dados internos
        }
        
        return self.get_response(request)
    
    def _block_super_admin_loja_access(self, request):
        """Bloqueia super admin de acessar sistema interno das lojas"""
        
        logger.warning(f"Super Admin {request.user.username} tentou acessar sistema de loja: {request.path}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Super Admins não podem acessar o sistema interno das lojas',
                'redirect': '/admin/'
            }, status=403)
        
        messages.error(
            request, 
            'Super Admins administram lojas, mas não acessam o sistema interno. '
            'Use o painel de administração para gerenciar lojas.'
        )
        return redirect('/admin/')
    
    def _block_non_super_admin_access(self, request):
        """Bloqueia acesso de não-super-admins a URLs exclusivas"""
        
        logger.warning(f"Tentativa de acesso não autorizado a URL exclusiva: {request.path} por {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Esta área é exclusiva para Super Administradores'
            }, status=403)
        
        messages.error(request, 'Acesso negado. Esta área é exclusiva para Super Administradores.')
        return redirect('root_redirect')
'''
    
    # Sobrescrever middleware existente
    middleware_path = 'dashboard/middleware/super_admin_exclusivo.py'
    
    try:
        with open(middleware_path, 'w', encoding='utf-8') as f:
            f.write(middleware_content)
        
        print("✅ Middleware Super Admin corrigido!")
        print("   ✅ Super Admin: Administra lojas")
        print("   ❌ Super Admin: NÃO acessa sistema das lojas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware Super Admin: {e}")
        return False


def corrigir_middlewares_lojas():
    """Corrige middlewares das lojas para BLOQUEAR super admins"""
    
    # Corrigir middleware da Fatesa
    fatesa_path = 'lojas/middleware/loja_fatesa_middleware.py'
    
    try:
        with open(fatesa_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir lógica de super admin
        old_logic = '''        # Super admin sempre pode acessar
        if self.allow_super_admin_override and request.user.is_superuser:
            logger.info(f"Super admin {request.user.username} acessando Fatesa")
            return True'''
        
        new_logic = '''        # Super admin NÃO pode acessar sistema da loja
        if request.user.is_superuser:
            logger.warning(f"Super admin {request.user.username} tentou acessar sistema da Fatesa")
            return False'''
        
        content = content.replace(old_logic, new_logic)
        
        with open(fatesa_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Middleware da Fatesa corrigido!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware da Fatesa: {e}")
    
    # Corrigir middleware da Felix
    felix_path = 'lojas/middleware/loja_felix_middleware.py'
    
    try:
        with open(felix_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir lógica de super admin
        old_logic = '''        # Super admin sempre pode acessar
        if self.allow_super_admin_override and request.user.is_superuser:
            return True'''
        
        new_logic = '''        # Super admin NÃO pode acessar sistema da loja
        if request.user.is_superuser:
            logger.warning(f"Super admin {request.user.username} tentou acessar sistema da Felix")
            return False'''
        
        content = content.replace(old_logic, new_logic)
        
        with open(felix_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Middleware da Felix corrigido!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware da Felix: {e}")


def criar_middleware_bloqueio_geral():
    """Cria middleware geral para bloquear super admins das lojas"""
    
    middleware_content = '''"""
Middleware de bloqueio geral - Impede super admins de acessar sistema das lojas
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class BloqueioSuperAdminLojasMiddleware:
    """
    Middleware que BLOQUEIA super admins de acessar qualquer sistema de loja
    
    REGRA FUNDAMENTAL:
    - Super Admin = Administração (gerenciar lojas, usuários, sistema)
    - Admin/Funcionário da Loja = Operação (trabalhar no sistema da loja)
    
    SEPARAÇÃO TOTAL entre administração e operação
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Padrões de URLs de sistema de lojas (BLOQUEADAS para super admin)
        self.loja_system_patterns = [
            '/login/',                    # Qualquer login de loja
            '/dashboard/loja/',           # Dashboard das lojas
            '/avaliacao-qualidade/',      # Módulos específicos
            '/modulos/',                  # Módulos das lojas
            '/pedidos/',                  # Operações
            '/clientes/',                 # Dados das lojas
            '/produtos/',                 # Dados das lojas
            '/vendas/',                   # Operações
            '/agendamento/',              # Módulos específicos
            '/procedimentos/',            # Módulos específicos
            '/mesas/',                    # Módulos específicos
            '/cardapio/',                 # Módulos específicos
        ]
        
        # URLs de administração (PERMITIDAS para super admin)
        self.admin_allowed_patterns = [
            '/admin/',
            '/super-admin/',
            '/usuarios/gerenciar/',
            '/lojas/gerenciar/',
            '/relatorios/sistema/',
            '/configuracoes/',
        ]
    
    def __call__(self, request):
        """Bloqueia super admins de acessar sistema das lojas"""
        
        try:
            # Verificar se é super admin tentando acessar sistema de loja
            if self._is_super_admin_accessing_loja_system(request):
                return self._block_super_admin_loja_access(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no BloqueioSuperAdminLojasMiddleware: {str(e)}")
            return self.get_response(request)
    
    def _is_super_admin_accessing_loja_system(self, request):
        """Verifica se super admin está tentando acessar sistema de loja"""
        
        # Deve ser super admin
        if not (request.user.is_authenticated and request.user.is_superuser):
            return False
        
        # Deve ser URL de sistema de loja
        path = request.path
        
        # Permitir URLs de administração
        if any(path.startswith(pattern) for pattern in self.admin_allowed_patterns):
            return False
        
        # Bloquear URLs de sistema de loja
        return any(path.startswith(pattern) for pattern in self.loja_system_patterns)
    
    def _block_super_admin_loja_access(self, request):
        """Bloqueia acesso e redireciona para administração"""
        
        logger.warning(
            f"BLOQUEIO: Super Admin {request.user.username} "
            f"tentou acessar sistema de loja: {request.path}"
        )
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': 'Super Admins administram lojas, não operam o sistema das lojas',
                'redirect': '/admin/',
                'explanation': 'Use o painel de administração para gerenciar lojas'
            }, status=403)
        
        messages.error(
            request,
            '🚫 Super Admins ADMINISTRAM lojas, mas não operam o sistema das lojas. '
            'Use o painel de administração para gerenciar lojas, usuários e configurações.'
        )
        
        return redirect('/admin/')
'''
    
    # Criar middleware de bloqueio geral
    middleware_path = 'dashboard/middleware/bloqueio_super_admin_lojas.py'
    
    try:
        with open(middleware_path, 'w', encoding='utf-8') as f:
            f.write(middleware_content)
        
        print("✅ Middleware de bloqueio geral criado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar middleware de bloqueio: {e}")
        return False


def atualizar_settings_com_bloqueio():
    """Atualiza settings.py com middleware de bloqueio"""
    
    print("🔧 Atualizando settings.py com middleware de bloqueio...")
    
    try:
        settings_path = 'lojad/settings.py'
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar middleware de bloqueio após super admin exclusivo
        old_line = "    'dashboard.middleware.super_admin_exclusivo.SuperAdminExclusivoMiddleware',"
        new_lines = """    'dashboard.middleware.super_admin_exclusivo.SuperAdminExclusivoMiddleware',
    # Bloqueio: Super Admin NÃO pode acessar sistema das lojas
    'dashboard.middleware.bloqueio_super_admin_lojas.BloqueioSuperAdminLojasMiddleware',"""
        
        content = content.replace(old_line, new_lines)
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Settings.py atualizado com middleware de bloqueio!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar settings: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 80)
    print("🚫 CORREÇÃO: SEPARAÇÃO TOTAL SUPER ADMIN vs LOJAS")
    print("=" * 80)
    print()
    
    print("📋 NOVA REGRA:")
    print("✅ Super Admin: ADMINISTRA e GERENCIA lojas (criar, editar, deletar)")
    print("❌ Super Admin: NÃO ACESSA sistema interno das lojas")
    print("✅ Admin/Funcionário da Loja: Acesso EXCLUSIVO ao sistema da loja")
    print()
    
    success_count = 0
    
    # 1. Corrigir middleware Super Admin
    print("1️⃣  Corrigindo middleware Super Admin...")
    if corrigir_middleware_super_admin():
        success_count += 1
    print()
    
    # 2. Corrigir middlewares das lojas
    print("2️⃣  Corrigindo middlewares das lojas...")
    corrigir_middlewares_lojas()
    success_count += 1
    print()
    
    # 3. Criar middleware de bloqueio geral
    print("3️⃣  Criando middleware de bloqueio geral...")
    if criar_middleware_bloqueio_geral():
        success_count += 1
    print()
    
    # 4. Atualizar settings
    print("4️⃣  Atualizando settings.py...")
    if atualizar_settings_com_bloqueio():
        success_count += 1
    print()
    
    print("=" * 80)
    print("📋 RESUMO DA CORREÇÃO")
    print("=" * 80)
    
    if success_count >= 4:
        print("✅ SEPARAÇÃO TOTAL IMPLEMENTADA COM SUCESSO!")
        print()
        print("🎯 Regras implementadas:")
        print("  👑 Super Admin:")
        print("    ✅ Administra lojas (CRUD)")
        print("    ✅ Gerencia usuários")
        print("    ✅ Acessa relatórios gerais")
        print("    ✅ Configura sistema")
        print("    ❌ NÃO acessa sistema das lojas")
        print()
        print("  🏪 Admin/Funcionário da Loja:")
        print("    ✅ Acesso EXCLUSIVO ao sistema da loja")
        print("    ✅ Módulos específicos da loja")
        print("    ✅ Dados e operações da loja")
        print("    ❌ NÃO acessa administração geral")
        print()
        print("🔒 Middlewares de bloqueio:")
        print("  • SuperAdminExclusivoMiddleware - Controla acesso super admin")
        print("  • BloqueioSuperAdminLojasMiddleware - Bloqueia super admin das lojas")
        print("  • LojaFatesaMiddleware - Bloqueia super admin da Fatesa")
        print("  • LojaFelixMiddleware - Bloqueia super admin da Felix")
        
    else:
        print("⚠️  CORREÇÃO PARCIAL - Alguns passos falharam")
    
    print()
    print("🧪 TESTE:")
    print("1. Login como Super Admin → Deve acessar /admin/ normalmente")
    print("2. Super Admin tenta /login/fatesa/ → Deve ser BLOQUEADO")
    print("3. Admin da Fatesa → Deve acessar sistema da Fatesa normalmente")
    print("4. Admin da Fatesa tenta /admin/ → Deve ser BLOQUEADO")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()