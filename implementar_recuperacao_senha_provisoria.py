#!/usr/bin/env python3
"""
Script para implementar recuperação de senha usando o sistema de senha provisória existente
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def criar_view_recuperacao():
    """Cria view de recuperação de senha para lojas"""
    
    view_content = '''from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from email_credentials.email_credentials_service import EmailCredentialsService
import logging
import json

logger = logging.getLogger(__name__)


def recuperar_senha_loja(request):
    """
    View para recuperação de senha nas páginas de login das lojas
    Usa o sistema de senha provisória existente
    """
    
    if request.method == 'POST':
        email_or_username = request.POST.get('email_or_username', '').strip()
        
        if not email_or_username:
            messages.error(request, 'Digite seu email ou nome de usuário.')
            return render(request, 'auth/recuperar_senha_loja.html')
        
        try:
            # Usar o serviço existente de email credentials
            service = EmailCredentialsService()
            result = service.generate_and_send_recovery(email_or_username)
            
            if result['success']:
                messages.success(
                    request, 
                    'Nova senha provisória enviada por email! '
                    'Verifique sua caixa de entrada e pasta de spam.'
                )
                return render(request, 'auth/recuperar_senha_sucesso.html', {
                    'email': result['user'].email if result.get('user') else email_or_username
                })
            else:
                if result.get('error') == 'USER_NOT_FOUND':
                    messages.error(request, 'Email ou usuário não encontrado.')
                elif result.get('error') == 'RATE_LIMITED':
                    messages.error(request, 'Muitas tentativas. Tente novamente em 1 hora.')
                else:
                    messages.error(request, 'Erro ao enviar email. Tente novamente.')
                
        except Exception as e:
            logger.error(f'Erro na recuperação de senha: {str(e)}')
            messages.error(request, 'Erro interno. Tente novamente mais tarde.')
    
    return render(request, 'auth/recuperar_senha_loja.html')


@csrf_exempt
@require_http_methods(["POST"])
def api_recuperar_senha(request):
    """
    API para recuperação de senha via AJAX
    """
    
    try:
        data = json.loads(request.body)
        email_or_username = data.get('email_or_username', '').strip()
        
        if not email_or_username:
            return JsonResponse({
                'success': False,
                'message': 'Email ou usuário é obrigatório.'
            })
        
        # Usar o serviço existente
        service = EmailCredentialsService()
        result = service.generate_and_send_recovery(email_or_username)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'Nova senha enviada por email!'
            })
        else:
            error_messages = {
                'USER_NOT_FOUND': 'Email ou usuário não encontrado.',
                'RATE_LIMITED': 'Muitas tentativas. Tente novamente em 1 hora.',
            }
            
            return JsonResponse({
                'success': False,
                'message': error_messages.get(result.get('error'), 'Erro ao enviar email.')
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados inválidos.'
        })
    except Exception as e:
        logger.error(f'Erro na API de recuperação: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': 'Erro interno. Tente novamente.'
        })
'''
    
    # Adicionar a view ao arquivo de views de login das lojas
    views_login_path = 'lojas/views_login.py'
    
    try:
        with open(views_login_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem a função
        if 'recuperar_senha_loja' in content:
            print("✅ View de recuperação já existe!")
            return True
        
        # Adicionar import no topo
        if 'from email_credentials.email_credentials_service import EmailCredentialsService' not in content:
            content = content.replace(
                'import logging',
                'import logging\nfrom email_credentials.email_credentials_service import EmailCredentialsService'
            )
        
        # Adicionar as views no final do arquivo
        content += '\n\n' + view_content
        
        # Escrever arquivo atualizado
        with open(views_login_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ View de recuperação adicionada!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar view: {e}")
        return False


def criar_templates_recuperacao():
    """Cria templates para recuperação de senha"""
    
    templates = {
        'templates/auth/recuperar_senha_loja.html': '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperar Senha - LVK Sistemas</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .recovery-card {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            max-width: 450px;
            width: 100%;
        }
        
        .recovery-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .recovery-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }
        
        .recovery-icon i {
            font-size: 36px;
            color: white;
        }
        
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 12px 15px;
            margin-bottom: 20px;
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .btn-recovery {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-weight: 600;
            width: 100%;
            color: white;
        }
        
        .btn-recovery:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        
        .back-link a {
            color: #667eea;
            text-decoration: none;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        .info-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }
        
        .info-box h6 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .info-box ul {
            margin: 0;
            padding-left: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="recovery-card">
        <div class="recovery-header">
            <div class="recovery-icon">
                <i class="fas fa-key"></i>
            </div>
            <h2>Recuperar Senha</h2>
            <p class="text-muted">Digite seu email ou usuário para receber uma nova senha</p>
        </div>
        
        <div class="info-box">
            <h6><i class="fas fa-info-circle me-2"></i>Como funciona:</h6>
            <ul>
                <li>Digite seu email ou nome de usuário</li>
                <li>Uma nova senha provisória será enviada por email</li>
                <li>Use a nova senha para fazer login</li>
                <li>Altere para uma senha de sua escolha após o login</li>
            </ul>
        </div>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {% if message.tags == 'error' or message.tags == 'danger' %}
                        <i class="fas fa-exclamation-triangle me-2"></i>
                    {% elif message.tags == 'success' %}
                        <i class="fas fa-check-circle me-2"></i>
                    {% endif %}
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        <form method="post" id="recoveryForm">
            {% csrf_token %}
            
            <div class="mb-3">
                <label for="email_or_username" class="form-label">
                    <i class="fas fa-envelope me-2"></i>Email ou Usuário
                </label>
                <input type="text" 
                       class="form-control" 
                       id="email_or_username"
                       name="email_or_username"
                       placeholder="Digite seu email ou nome de usuário"
                       required>
            </div>
            
            <button type="submit" class="btn btn-recovery" id="btnRecovery">
                <i class="fas fa-paper-plane me-2"></i>
                Enviar Nova Senha
            </button>
        </form>
        
        <div class="back-link">
            <a href="javascript:history.back()">
                <i class="fas fa-arrow-left me-2"></i>
                Voltar ao Login
            </a>
        </div>
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        document.getElementById('recoveryForm').addEventListener('submit', function(e) {
            const btn = document.getElementById('btnRecovery');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            btn.disabled = true;
        });
    </script>
</body>
</html>''',

        'templates/auth/recuperar_senha_sucesso.html': '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Enviado - LVK Sistemas</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .success-card {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            max-width: 450px;
            width: 100%;
            text-align: center;
        }
        
        .success-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #10b981, #059669);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }
        
        .success-icon i {
            font-size: 36px;
            color: white;
        }
        
        .btn-back {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            color: white;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
        }
        
        .btn-back:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }
        
        .email-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #10b981;
        }
    </style>
</head>
<body>
    <div class="success-card">
        <div class="success-icon">
            <i class="fas fa-check"></i>
        </div>
        
        <h2 class="mb-3">Email Enviado!</h2>
        
        <p class="text-muted mb-4">
            Uma nova senha provisória foi enviada para seu email.
        </p>
        
        {% if email %}
        <div class="email-info">
            <strong><i class="fas fa-envelope me-2"></i>Email:</strong><br>
            {{ email }}
        </div>
        {% endif %}
        
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            <strong>Próximos passos:</strong><br>
            1. Verifique sua caixa de entrada e pasta de spam<br>
            2. Use a nova senha para fazer login<br>
            3. Altere para uma senha de sua escolha
        </div>
        
        <a href="javascript:history.back()" class="btn-back">
            <i class="fas fa-arrow-left me-2"></i>
            Voltar ao Login
        </a>
    </div>
</body>
</html>'''
    }
    
    print("🔧 Criando templates de recuperação...")
    
    created_count = 0
    for template_path, content in templates.items():
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            # Criar arquivo
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Criado: {template_path}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Erro ao criar {template_path}: {e}")
    
    return created_count == len(templates)


def adicionar_urls_recuperacao():
    """Adiciona URLs de recuperação ao urls.py"""
    
    print("🔧 Adicionando URLs de recuperação...")
    
    try:
        urls_path = 'lojad/urls.py'
        
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem as URLs
        if 'recuperar_senha_loja' in content:
            print("✅ URLs de recuperação já existem!")
            return True
        
        # Adicionar import
        if 'from lojas.views_login import' not in content:
            content = content.replace(
                'from lojas.views_login import login_personalizado_loja, api_validar_url_personalizada',
                'from lojas.views_login import login_personalizado_loja, api_validar_url_personalizada, recuperar_senha_loja, api_recuperar_senha'
            )
        else:
            content = content.replace(
                'from lojas.views_login import login_personalizado_loja, api_validar_url_personalizada',
                'from lojas.views_login import login_personalizado_loja, api_validar_url_personalizada, recuperar_senha_loja, api_recuperar_senha'
            )
        
        # Encontrar onde adicionar as URLs
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Adicionar após as URLs de login personalizado
            if 'api_validar_url_personalizada' in line and 'name=' in line:
                new_lines.append('')
                new_lines.append('    # URLs de recuperação de senha')
                new_lines.append("    path('recuperar-senha/', recuperar_senha_loja, name='recuperar_senha_loja'),")
                new_lines.append("    path('api/recuperar-senha/', api_recuperar_senha, name='api_recuperar_senha'),")
        
        # Escrever arquivo atualizado
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ URLs de recuperação adicionadas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar URLs: {e}")
        return False


def restaurar_links_recuperacao():
    """Restaura os links de recuperação nos templates de login"""
    
    print("🔧 Restaurando links de recuperação nos templates...")
    
    templates_para_corrigir = [
        'templates/auth/login_personalizado_fatesa.html',
        'templates/auth/login_personalizado_corporativo_limpo.html',
        'templates/auth/login_personalizado_padrao.html',
        'templates/auth/login_personalizado_moderno.html',
        'templates/auth/login_personalizado_minimalista.html'
    ]
    
    success_count = 0
    
    for template_path in templates_para_corrigir:
        if not os.path.exists(template_path):
            continue
            
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se já tem link de recuperação
            if 'recuperar_senha_loja' in content or 'recuperar-senha' in content:
                print(f"✅ {template_path} já tem link de recuperação")
                success_count += 1
                continue
            
            # Adicionar seção de links antes do rodapé ou após o formulário
            if 'Mensagem do Rodapé' in content:
                content = content.replace(
                    '<!-- Mensagem do Rodapé -->',
                    '''            <!-- Links de recuperação -->
            {% if login_config.mostrar_link_recuperar_senha and not is_preview %}
            <div class="text-center mt-3">
                <a href="{% url 'recuperar_senha_loja' %}" class="text-decoration-none">
                    <i class="fas fa-key me-1"></i>Esqueci minha senha
                </a>
            </div>
            {% endif %}
            
            <!-- Mensagem do Rodapé -->'''
                )
            elif '</form>' in content and 'Bootstrap JS' in content:
                # Adicionar após o formulário
                content = content.replace(
                    '</form>',
                    '''</form>
            
            <!-- Links de recuperação -->
            {% if login_config.mostrar_link_recuperar_senha and not is_preview %}
            <div class="text-center mt-3">
                <a href="{% url 'recuperar_senha_loja' %}" class="text-decoration-none">
                    <i class="fas fa-key me-1"></i>Esqueci minha senha
                </a>
            </div>
            {% endif %}'''
                )
            
            # Escrever arquivo corrigido
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Restaurado link em: {template_path}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Erro ao restaurar {template_path}: {e}")
    
    return success_count > 0


def reativar_links_no_banco():
    """Reativa os links de recuperação no banco de dados"""
    
    print("🔧 Reativando links de recuperação no banco...")
    
    try:
        from lojas.models_login import LoginPersonalizado
        
        configs = LoginPersonalizado.objects.all()
        count = 0
        
        for config in configs:
            if not config.mostrar_link_recuperar_senha:
                config.mostrar_link_recuperar_senha = True
                config.save()
                count += 1
                print(f"  ✅ Reativado para: {config.loja.nome}")
        
        print(f"✅ {count} configurações reativadas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao reativar no banco: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 IMPLEMENTAÇÃO DE RECUPERAÇÃO COM SENHA PROVISÓRIA")
    print("=" * 60)
    print()
    
    print("Implementando recuperação usando o sistema existente de senha provisória...")
    print()
    
    success_count = 0
    
    # Criar view
    if criar_view_recuperacao():
        success_count += 1
        print("✅ View de recuperação criada!")
    else:
        print("❌ Erro ao criar view")
    
    print()
    
    # Criar templates
    if criar_templates_recuperacao():
        success_count += 1
        print("✅ Templates criados!")
    else:
        print("❌ Erro ao criar templates")
    
    print()
    
    # Adicionar URLs
    if adicionar_urls_recuperacao():
        success_count += 1
        print("✅ URLs adicionadas!")
    else:
        print("❌ Erro ao adicionar URLs")
    
    print()
    
    # Restaurar links nos templates
    if restaurar_links_recuperacao():
        success_count += 1
        print("✅ Links restaurados!")
    else:
        print("❌ Erro ao restaurar links")
    
    print()
    
    # Reativar no banco
    if reativar_links_no_banco():
        success_count += 1
        print("✅ Links reativados no banco!")
    else:
        print("❌ Erro ao reativar no banco")
    
    print()
    print("=" * 60)
    print("📋 RESUMO DA IMPLEMENTAÇÃO")
    print("=" * 60)
    
    if success_count >= 4:
        print("✅ IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Funcionalidades implementadas:")
        print("✅ View de recuperação usando sistema de senha provisória")
        print("✅ Templates de recuperação criados")
        print("✅ URLs de recuperação configuradas")
        print("✅ Links restaurados nos templates de login")
        print("✅ Configurações reativadas no banco")
        print()
        print("🌐 URLs disponíveis:")
        print("- Recuperar senha: /recuperar-senha/")
        print("- API recuperação: /api/recuperar-senha/")
        print()
        print("🧪 TESTE:")
        print("1. Acesse a página de login da Fatesa")
        print("2. Clique em 'Esqueci minha senha'")
        print("3. Digite um email válido cadastrado no sistema")
        print("4. Verifique se recebe a nova senha provisória por email")
        print("5. Use a nova senha para fazer login")
        
    else:
        print("❌ IMPLEMENTAÇÃO PARCIAL - Alguns problemas podem persistir")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()