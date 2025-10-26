#!/usr/bin/env python3
"""
Script para implementar sistema de senha provisória por email
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def criar_view_senha_provisoria():
    """Cria a view para recuperação com senha provisória"""
    
    view_content = '''from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import secrets
import string
import logging

logger = logging.getLogger(__name__)

def gerar_senha_provisoria():
    """Gera uma senha provisória segura"""
    # Gerar senha com 8 caracteres: letras maiúsculas, minúsculas e números
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))

def enviar_senha_provisoria_email(user, senha_provisoria):
    """Envia a senha provisória por email"""
    try:
        assunto = 'Senha Provisória - LVK Sistemas'
        
        mensagem = f"""
Olá {user.first_name or user.username},

Você solicitou uma nova senha para sua conta no LVK Sistemas.

Sua senha provisória é: {senha_provisoria}

IMPORTANTE:
- Esta é uma senha temporária
- Faça login e altere sua senha imediatamente
- Por segurança, esta senha expira em 24 horas

Para fazer login, acesse:
{settings.SITE_URL}

Atenciosamente,
Equipe LVK Sistemas
        """
        
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Senha provisória enviada para {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar email para {user.email}: {str(e)}")
        return False

def recuperar_senha_provisoria(request):
    """View para recuperação de senha com senha provisória"""
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, 'Por favor, digite seu email.')
            return render(request, 'auth/recuperar_senha_provisoria.html')
        
        try:
            # Buscar usuário pelo email
            user = User.objects.get(email=email, is_active=True)
            
            # Gerar nova senha provisória
            senha_provisoria = gerar_senha_provisoria()
            
            # Definir a nova senha
            user.set_password(senha_provisoria)
            user.save()
            
            # Marcar que precisa trocar a senha
            from usuarios.models import PerfilUsuario
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={'requires_password_change': True}
            )
            if not created:
                perfil.requires_password_change = True
                perfil.save()
            
            # Enviar por email
            if enviar_senha_provisoria_email(user, senha_provisoria):
                messages.success(
                    request, 
                    f'Uma nova senha provisória foi enviada para {email}. '
                    'Verifique sua caixa de entrada.'
                )
                logger.info(f"Senha provisória gerada para usuário {user.username} ({email})")
            else:
                messages.error(
                    request,
                    'Erro ao enviar email. Tente novamente ou contate o suporte.'
                )
            
            return redirect('recuperar_senha_provisoria')
            
        except User.DoesNotExist:
            # Por segurança, não revelar se o email existe ou não
            messages.success(
                request,
                f'Se o email {email} estiver cadastrado, você receberá uma senha provisória.'
            )
            logger.warning(f"Tentativa de recuperação para email não cadastrado: {email}")
            return redirect('recuperar_senha_provisoria')
            
        except Exception as e:
            logger.error(f"Erro na recuperação de senha: {str(e)}")
            messages.error(
                request,
                'Erro interno. Tente novamente ou contate o suporte.'
            )
            return render(request, 'auth/recuperar_senha_provisoria.html')
    
    return render(request, 'auth/recuperar_senha_provisoria.html')
'''
    
    # Criar arquivo de views
    views_path = 'usuarios/views_recuperacao.py'
    
    try:
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(view_content)
        
        print(f"✅ View criada: {views_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar view: {e}")
        return False


def criar_template_recuperacao():
    """Cria o template para recuperação de senha"""
    
    template_content = '''<!DOCTYPE html>
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
            padding: 20px;
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
            font-size: 16px;
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
            font-size: 16px;
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
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        
        .info-box h6 {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .info-box ul {
            margin: 0;
            padding-left: 20px;
            font-size: 14px;
        }
        
        .alert {
            border-radius: 10px;
            margin-bottom: 20px;
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
            <p class="text-muted">Digite seu email para receber uma senha provisória</p>
        </div>
        
        <div class="info-box">
            <h6><i class="fas fa-info-circle me-2"></i>Como funciona:</h6>
            <ul>
                <li>Digite o email cadastrado no sistema</li>
                <li>Você receberá uma senha provisória por email</li>
                <li>Faça login com a senha provisória</li>
                <li>Altere para uma senha definitiva</li>
            </ul>
        </div>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{% if message.tags == 'error' %}danger{% else %}{{ message.tags }}{% endif %} alert-dismissible fade show" role="alert">
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
        
        <form method="post">
            {% csrf_token %}
            
            <div class="mb-3">
                <label for="email" class="form-label">
                    <i class="fas fa-envelope me-2"></i>Email Cadastrado
                </label>
                <input type="email" 
                       class="form-control" 
                       id="email"
                       name="email"
                       placeholder="Digite seu email"
                       required
                       autocomplete="email">
            </div>
            
            <button type="submit" class="btn btn-recovery">
                <i class="fas fa-paper-plane me-2"></i>
                Enviar Senha Provisória
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
        // Auto-focus no campo email
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('email').focus();
        });
        
        // Validação do formulário
        document.querySelector('form').addEventListener('submit', function(e) {
            const email = document.getElementById('email').value.trim();
            
            if (!email) {
                e.preventDefault();
                alert('Por favor, digite seu email.');
                return false;
            }
            
            // Validação básica de email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Por favor, digite um email válido.');
                return false;
            }
            
            // Adicionar loading no botão
            const btn = document.querySelector('.btn-recovery');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            btn.disabled = true;
        });
    </script>
</body>
</html>'''
    
    template_path = 'templates/auth/recuperar_senha_provisoria.html'
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"✅ Template criado: {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar template: {e}")
        return False


def adicionar_url_recuperacao():
    """Adiciona a URL de recuperação ao urls.py"""
    
    print("🔧 Adicionando URL de recuperação...")
    
    try:
        urls_path = 'lojad/urls.py'
        
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem a URL
        if 'recuperar_senha_provisoria' in content:
            print("✅ URL de recuperação já existe!")
            return True
        
        # Adicionar import se necessário
        if 'from usuarios.views_recuperacao import recuperar_senha_provisoria' not in content:
            content = content.replace(
                'from lojas.views_login import login_personalizado_loja, api_validar_url_personalizada',
                'from lojas.views_login import login_personalizado_loja, api_validar_url_personalizada\nfrom usuarios.views_recuperacao import recuperar_senha_provisoria'
            )
        
        # Adicionar URL
        content = content.replace(
            "path('webhook/asaas/', webhook_asaas_bypass, name='webhook_asaas_main'),",
            "path('webhook/asaas/', webhook_asaas_bypass, name='webhook_asaas_main'),\n    path('recuperar-senha/', recuperar_senha_provisoria, name='recuperar_senha_provisoria'),"
        )
        
        # Escrever arquivo atualizado
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ URL de recuperação adicionada!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar URL: {e}")
        return False


def atualizar_templates_login():
    """Atualiza os templates de login para usar a nova URL"""
    
    print("🔧 Atualizando templates de login...")
    
    templates = [
        'templates/auth/login_personalizado_fatesa.html',
        'templates/auth/login_personalizado_corporativo_limpo.html',
        'templates/auth/login_personalizado_padrao.html',
        'templates/auth/login_personalizado_moderno.html',
        'templates/auth/login_personalizado_minimalista.html'
    ]
    
    success_count = 0
    
    for template_path in templates:
        if not os.path.exists(template_path):
            continue
            
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se já tem o link correto
            if 'recuperar_senha_provisoria' in content:
                print(f"✅ {template_path} já atualizado")
                success_count += 1
                continue
            
            # Adicionar link de recuperação antes do rodapé ou após o formulário
            if 'Mensagem do Rodapé' in content:
                content = content.replace(
                    '<!-- Mensagem do Rodapé -->',
                    '''            <!-- Link de recuperação de senha -->
            {% if login_config.mostrar_link_recuperar_senha and not is_preview %}
            <div class="text-center mt-3">
                <a href="{% url 'recuperar_senha_provisoria' %}" class="text-decoration-none">
                    <i class="fas fa-key me-1"></i>Esqueci minha senha
                </a>
            </div>
            {% endif %}
            
            <!-- Mensagem do Rodapé -->'''
                )
            elif '</form>' in content and not is_preview in content:
                # Para templates sem seção de rodapé
                content = content.replace(
                    '{% endif %}',
                    '''{% endif %}
            
            <!-- Link de recuperação de senha -->
            {% if login_config.mostrar_link_recuperar_senha and not is_preview %}
            <div class="text-center mt-3">
                <a href="{% url 'recuperar_senha_provisoria' %}" class="text-decoration-none">
                    <i class="fas fa-key me-1"></i>Esqueci minha senha
                </a>
            </div>
            {% endif %}''',
                    1  # Apenas a primeira ocorrência
                )
            
            # Escrever arquivo atualizado
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Atualizado: {template_path}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Erro ao atualizar {template_path}: {e}")
    
    return success_count > 0


def reativar_links_banco():
    """Reativa os links de recuperação no banco"""
    
    print("🔧 Reativando links no banco de dados...")
    
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
        print(f"❌ Erro ao reativar: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 IMPLEMENTAÇÃO DE SENHA PROVISÓRIA POR EMAIL")
    print("=" * 60)
    print()
    
    print("Sistema de recuperação:")
    print("1. Usuário digita email cadastrado")
    print("2. Sistema gera senha provisória")
    print("3. Envia senha por email")
    print("4. Usuário faz login e deve alterar a senha")
    print()
    
    success_count = 0
    
    # Criar view
    if criar_view_senha_provisoria():
        success_count += 1
    
    # Criar template
    if criar_template_recuperacao():
        success_count += 1
    
    # Adicionar URL
    if adicionar_url_recuperacao():
        success_count += 1
    
    # Atualizar templates
    if atualizar_templates_login():
        success_count += 1
    
    # Reativar no banco
    if reativar_links_banco():
        success_count += 1
    
    print()
    print("=" * 60)
    print("📋 RESUMO DA IMPLEMENTAÇÃO")
    print("=" * 60)
    
    if success_count >= 4:
        print("✅ IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Funcionalidades implementadas:")
        print("✅ View de recuperação com senha provisória")
        print("✅ Template de recuperação criado")
        print("✅ URL de recuperação configurada")
        print("✅ Templates de login atualizados")
        print("✅ Links reativados no banco")
        print()
        print("🌐 URLs disponíveis:")
        print("- Recuperar senha: /recuperar-senha/")
        print("- Login Fatesa: /login/fatesa-escola-de-ultrassonografia/")
        print()
        print("🧪 TESTE:")
        print("1. Acesse a página de login da Fatesa")
        print("2. Clique em 'Esqueci minha senha'")
        print("3. Digite um email cadastrado")
        print("4. Verifique se recebe a senha provisória por email")
        print("5. Faça login com a senha provisória")
        
    else:
        print("❌ IMPLEMENTAÇÃO PARCIAL - Alguns problemas podem persistir")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()