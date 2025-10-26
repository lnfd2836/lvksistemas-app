#!/usr/bin/env python3
"""
Sistema de criação de middlewares exclusivos por grupos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def criar_middleware_super_admin():
    """Cria middleware exclusivo para super admins"""
    
    middleware_content = '''"""
Middleware exclusivo para Super Admins
Acesso total ao sistema com prioridade máxima
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
    - Acesso total ao sistema
    - Prioridade máxima sobre outros middlewares
    - Proteção contra acesso não autorizado
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs exclusivas para super admins
        self.super_admin_exclusive_urls = [
            '/admin/',
            '/super-admin/',
            '/admin-login/',
            '/dashboard/super/',
            '/usuarios/gerenciar/',
            '/lojas/gerenciar/',
            '/financeiro/admin/',
            '/relatorios/sistema/',
            '/configuracoes/sistema/',
        ]
        
        # URLs que super admins podem acessar de qualquer loja
        self.super_admin_override_urls = [
            '/dashboard/loja/',
            '/login/',
            '/avaliacao-qualidade/',
            '/modulos/',
        ]
    
    def __call__(self, request):
        """Processa requisições com prioridade para super admins"""
        
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
    
    def _handle_super_admin_request(self, request):
        """Processa requisições de super admins"""
        
        # Log de acesso super admin
        logger.info(f"Super Admin {request.user.username} acessando: {request.path}")
        
        # Adicionar contexto especial para super admins
        request.is_super_admin_context = True
        request.super_admin_permissions = {
            'can_access_all_stores': True,
            'can_manage_users': True,
            'can_view_system_reports': True,
            'can_modify_system_settings': True,
        }
        
        # Bypass de outros middlewares de autenticação se necessário
        if self._should_bypass_other_middlewares(request.path):
            request.bypass_store_middlewares = True
        
        return self.get_response(request)
    
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
    
    def _should_bypass_other_middlewares(self, path):
        """Determina se deve fazer bypass de outros middlewares"""
        bypass_paths = [
            '/admin/',
            '/dashboard/super/',
            '/usuarios/gerenciar/',
        ]
        return any(path.startswith(bp) for bp in bypass_paths)
'''
    
    # Criar arquivo do middleware
    middleware_path = 'dashboard/middleware/super_admin_exclusivo.py'
    
    try:
        with open(middleware_path, 'w', encoding='utf-8') as f:
            f.write(middleware_content)
        
        print("✅ Middleware Super Admin Exclusivo criado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar middleware Super Admin: {e}")
        return False


def criar_middleware_asaas():
    """Cria middleware exclusivo para integração Asaas"""
    
    middleware_content = '''"""
Middleware exclusivo para integração Asaas
Gerencia webhooks, pagamentos e sincronização
"""
import logging
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

logger = logging.getLogger(__name__)


class AsaasExclusivoMiddleware:
    """
    Middleware EXCLUSIVO para integração Asaas
    - Gerencia webhooks com prioridade
    - Valida IPs autorizados
    - Processa pagamentos automaticamente
    - Sincronização em tempo real
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs exclusivas para Asaas
        self.asaas_exclusive_urls = [
            '/webhook/asaas/',
            '/api/asaas/',
            '/financeiro/asaas/',
            '/pagamentos/asaas/',
            '/sync/asaas/',
        ]
        
        # IPs autorizados do Asaas (sandbox e produção)
        self.asaas_authorized_ips = [
            '18.229.47.223',
            '18.231.194.64',
            '52.67.73.224',
            '127.0.0.1',  # Para testes locais
            '0.0.0.0',    # Para desenvolvimento
        ]
        
        # Headers obrigatórios do Asaas
        self.required_asaas_headers = [
            'HTTP_USER_AGENT',
            'HTTP_CONTENT_TYPE',
        ]
    
    def __call__(self, request):
        """Processa requisições Asaas com prioridade máxima"""
        
        try:
            # Verificar se é requisição Asaas
            if self._is_asaas_request(request):
                return self._handle_asaas_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no AsaasExclusivoMiddleware: {str(e)}")
            return HttpResponse("Internal Error", status=500)
    
    def _is_asaas_request(self, path):
        """Verifica se é requisição do Asaas"""
        return any(path.startswith(url) for url in self.asaas_exclusive_urls)
    
    def _handle_asaas_request(self, request):
        """Processa requisições do Asaas"""
        
        # Log detalhado da requisição Asaas
        logger.info(f"Requisição Asaas recebida: {request.method} {request.path}")
        logger.info(f"IP: {self._get_client_ip(request)}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        
        # Validar IP (apenas em produção)
        if not settings.DEBUG and not self._validate_asaas_ip(request):
            logger.warning(f"IP não autorizado tentando acessar Asaas: {self._get_client_ip(request)}")
            return HttpResponse("Forbidden", status=403)
        
        # Validar headers obrigatórios
        if not self._validate_asaas_headers(request):
            logger.warning("Headers obrigatórios ausentes em requisição Asaas")
            return HttpResponse("Bad Request", status=400)
        
        # Adicionar contexto Asaas
        request.is_asaas_request = True
        request.asaas_validated = True
        
        # Bypass de middlewares desnecessários para performance
        request.bypass_auth_middlewares = True
        request.bypass_csrf = True
        
        # Processar webhook se for POST
        if request.method == 'POST' and '/webhook/' in request.path:
            return self._process_asaas_webhook(request)
        
        return self.get_response(request)
    
    def _validate_asaas_ip(self, request):
        """Valida se o IP é autorizado pelo Asaas"""
        client_ip = self._get_client_ip(request)
        return client_ip in self.asaas_authorized_ips
    
    def _validate_asaas_headers(self, request):
        """Valida headers obrigatórios do Asaas"""
        for header in self.required_asaas_headers:
            if not request.META.get(header):
                return False
        return True
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _process_asaas_webhook(self, request):
        """Processa webhook do Asaas"""
        try:
            # Parse do JSON
            webhook_data = json.loads(request.body.decode('utf-8'))
            
            # Log do webhook
            logger.info(f"Webhook Asaas processado: {webhook_data.get('event', 'unknown')}")
            
            # Processar usando serviço existente
            from controle_financeiro.asaas_service import AsaasService
            asaas_service = AsaasService()
            resultado = asaas_service.processar_webhook(webhook_data)
            
            if resultado.get('success'):
                return HttpResponse("OK", status=200)
            else:
                return HttpResponse("Processing Error", status=400)
                
        except json.JSONDecodeError:
            logger.error("Webhook Asaas com JSON inválido")
            return HttpResponse("Invalid JSON", status=400)
        except Exception as e:
            logger.error(f"Erro ao processar webhook Asaas: {str(e)}")
            return HttpResponse("Internal Error", status=500)
'''
    
    # Criar arquivo do middleware
    middleware_path = 'controle_financeiro/middleware/asaas_exclusivo.py'
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(middleware_path), exist_ok=True)
        
        with open(middleware_path, 'w', encoding='utf-8') as f:
            f.write(middleware_content)
        
        print("✅ Middleware Asaas Exclusivo criado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar middleware Asaas: {e}")
        return False


def criar_sistema_middleware_loja():
    """Cria sistema para gerar middlewares exclusivos por loja"""
    
    # 1. Criar gerador de middleware por loja
    gerador_content = '''"""
Gerador automático de middlewares exclusivos por loja
"""
import os
import logging
from django.template import Template, Context

logger = logging.getLogger(__name__)


class MiddlewareLojaGenerator:
    """
    Gerador automático de middlewares exclusivos por loja
    Cada loja terá seu próprio middleware com regras específicas
    """
    
    def __init__(self):
        self.template_middleware = self._get_template_middleware()
    
    def gerar_middleware_loja(self, loja):
        """Gera middleware exclusivo para uma loja"""
        
        try:
            # Preparar contexto
            context = {
                'loja_nome': loja.nome,
                'loja_id': str(loja.id),
                'loja_slug': self._generate_slug(loja.nome),
                'loja_tipo': loja.tipo_loja.nome if loja.tipo_loja else 'padrao',
                'loja_cidade': loja.cidade,
                'loja_estado': loja.estado,
                'loja_cnpj': loja.cnpj,
            }
            
            # Renderizar template
            template = Template(self.template_middleware)
            middleware_code = template.render(Context(context))
            
            # Criar arquivo do middleware
            middleware_path = f'lojas/middleware/loja_{context["loja_slug"]}_middleware.py'
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(middleware_path), exist_ok=True)
            
            # Escrever arquivo
            with open(middleware_path, 'w', encoding='utf-8') as f:
                f.write(middleware_code)
            
            logger.info(f"Middleware exclusivo criado para loja: {loja.nome}")
            
            return {
                'success': True,
                'middleware_path': middleware_path,
                'middleware_class': f'Loja{context["loja_slug"].title()}Middleware'
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar middleware para loja {loja.nome}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_slug(self, nome):
        """Gera slug para nome da loja"""
        import re
        slug = re.sub(r'[^a-zA-Z0-9]', '_', nome.lower())
        slug = re.sub(r'_+', '_', slug)
        return slug.strip('_')
    
    def _get_template_middleware(self):
        """Template para middleware de loja"""
        return """\"\"\"
Middleware exclusivo para {{ loja_nome }}
Gerado automaticamente pelo sistema
\"\"\"
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from lojas.models import Loja

logger = logging.getLogger(__name__)


class Loja{{ loja_slug|title }}Middleware:
    \"\"\"
    Middleware EXCLUSIVO para {{ loja_nome }}
    - ID da Loja: {{ loja_id }}
    - Tipo: {{ loja_tipo }}
    - Localização: {{ loja_cidade }}/{{ loja_estado }}
    - CNPJ: {{ loja_cnpj }}
    \"\"\"
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurações específicas da loja
        self.loja_id = '{{ loja_id }}'
        self.loja_nome = '{{ loja_nome }}'
        self.loja_tipo = '{{ loja_tipo }}'
        self.loja_slug = '{{ loja_slug }}'
        
        # URLs exclusivas desta loja
        self.loja_exclusive_urls = [
            '/login/{{ loja_slug }}/',
            '/dashboard/loja/{{ loja_id }}/',
            '/{{ loja_slug }}/',
        ]
        
        # Módulos disponíveis para esta loja
        self.loja_modulos = self._get_modulos_por_tipo()
        
        # Configurações de acesso
        self.require_loja_permission = True
        self.allow_super_admin_override = True
    
    def __call__(self, request):
        \"\"\"Processa requisições específicas desta loja\"\"\"
        
        try:
            # Verificar se é requisição desta loja
            if self._is_loja_request(request):
                return self._handle_loja_request(request)
            
            # Continuar processamento normal
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"Erro no middleware da loja {{ loja_nome }}: {str(e)}")
            return self.get_response(request)
    
    def _is_loja_request(self, request):
        \"\"\"Verifica se é requisição desta loja\"\"\"
        path = request.path
        return any(path.startswith(url) for url in self.loja_exclusive_urls)
    
    def _handle_loja_request(self, request):
        \"\"\"Processa requisições desta loja\"\"\"
        
        # Log de acesso
        logger.info(f"Acesso à loja {{ loja_nome }}: {request.path} por {request.user}")
        
        # Verificar permissões
        if not self._has_loja_permission(request):
            return self._deny_access(request)
        
        # Adicionar contexto da loja
        request.loja_context = {
            'loja_id': self.loja_id,
            'loja_nome': self.loja_nome,
            'loja_tipo': self.loja_tipo,
            'loja_modulos': self.loja_modulos,
            'is_loja_exclusive': True,
        }
        
        # Configurar sessão da loja
        request.session['current_loja_id'] = self.loja_id
        request.session['current_loja_nome'] = self.loja_nome
        
        return self.get_response(request)
    
    def _has_loja_permission(self, request):
        \"\"\"Verifica se usuário tem permissão para acessar esta loja\"\"\"
        
        # Super admin sempre pode acessar
        if self.allow_super_admin_override and request.user.is_superuser:
            return True
        
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é admin desta loja
        try:
            loja = Loja.objects.get(id=self.loja_id)
            if loja.admin_user == request.user:
                return True
        except Loja.DoesNotExist:
            return False
        
        # Verificar se é funcionário desta loja
        if hasattr(request.user, 'funcionario'):
            funcionario = request.user.funcionario
            if str(funcionario.loja.id) == self.loja_id:
                return True
        
        return False
    
    def _deny_access(self, request):
        \"\"\"Nega acesso à loja\"\"\"
        
        logger.warning(f"Acesso negado à loja {{ loja_nome }} para usuário: {request.user}")
        
        if request.is_ajax() or 'api' in request.path:
            return JsonResponse({
                'error': 'Acesso negado',
                'message': f'Você não tem permissão para acessar {{ loja_nome }}'
            }, status=403)
        
        messages.error(request, f'Acesso negado. Você não tem permissão para acessar {{ loja_nome }}.')
        return redirect('root_redirect')
    
    def _get_modulos_por_tipo(self):
        \"\"\"Retorna módulos disponíveis baseado no tipo da loja\"\"\"
        
        modulos_por_tipo = {
            'controle_qualidade': ['avaliacao', 'cursos', 'professores', 'relatorios'],
            'clinica_estetica': ['agendamento', 'procedimentos', 'clientes', 'produtos'],
            'lanchonete': ['pedidos', 'mesas', 'cardapio', 'estoque'],
            'padrao': ['vendas', 'clientes', 'produtos', 'relatorios'],
        }
        
        return modulos_por_tipo.get(self.loja_tipo, modulos_por_tipo['padrao'])
"""
    
    def remover_middleware_loja(self, loja):
        """Remove middleware de uma loja"""
        
        try:
            loja_slug = self._generate_slug(loja.nome)
            middleware_path = f'lojas/middleware/loja_{loja_slug}_middleware.py'
            
            if os.path.exists(middleware_path):
                os.remove(middleware_path)
                logger.info(f"Middleware removido para loja: {loja.nome}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover middleware da loja {loja.nome}: {str(e)}")
            return False
'''
    
    # Criar arquivo do gerador
    gerador_path = 'lojas/middleware/gerador_middleware_loja.py'
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(gerador_path), exist_ok=True)
        
        with open(gerador_path, 'w', encoding='utf-8') as f:
            f.write(gerador_content)
        
        print("✅ Sistema gerador de middleware por loja criado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar sistema gerador: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 80)
    print("🏗️  CRIAÇÃO DE GRUPOS EXCLUSIVOS DE MIDDLEWARE")
    print("=" * 80)
    print()
    
    success_count = 0
    
    # 1. Criar middleware Super Admin exclusivo
    print("1️⃣  Criando Middleware Super Admin Exclusivo...")
    if criar_middleware_super_admin():
        success_count += 1
    print()
    
    # 2. Criar middleware Asaas exclusivo
    print("2️⃣  Criando Middleware Asaas Exclusivo...")
    if criar_middleware_asaas():
        success_count += 1
    print()
    
    # 3. Criar sistema de middleware por loja
    print("3️⃣  Criando Sistema de Middleware por Loja...")
    if criar_sistema_middleware_loja():
        success_count += 1
    print()
    
    print("=" * 80)
    print("📋 RESUMO DA CRIAÇÃO")
    print("=" * 80)
    
    if success_count >= 3:
        print("✅ TODOS OS GRUPOS DE MIDDLEWARE CRIADOS COM SUCESSO!")
        print()
        print("🎯 Grupos criados:")
        print("  1. ✅ Super Admin Exclusivo - Acesso total ao sistema")
        print("  2. ✅ Asaas Exclusivo - Webhooks e pagamentos")
        print("  3. ✅ Sistema por Loja - Middleware automático para cada loja")
        print()
        print("🔧 Próximos passos:")
        print("  1. Adicionar middlewares ao settings.py")
        print("  2. Testar cada grupo individualmente")
        print("  3. Configurar geração automática para novas lojas")
        
    else:
        print("⚠️  CRIAÇÃO PARCIAL - Alguns middlewares podem ter falhado")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()