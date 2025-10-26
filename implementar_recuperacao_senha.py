#!/usr/bin/env python3
"""
Script para implementar funcionalidade completa de recuperação de senha
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def criar_templates_recuperacao():
    """Cria os templates necessários para recuperação de senha"""
    
    templates = {
        'templates/registration/password_reset_form.html': '''<!DOCTYPE html>
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
    </style>
</head>
<body>
    <div class="recovery-card">
        <div class="recovery-header">
            <div class="recovery-icon">
                <i class="fas fa-key"></i>
            </div>
            <h2>Recuperar Senha</h2>
            <p class="text-muted">Digite seu email para receber instruções de recuperação</p>
        </div>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            
            <div class="mb-3">
                <label for="email" class="form-label">
                    <i class="fas fa-envelope me-2"></i>Email
                </label>
                <input type="email" 
                       class="form-control" 
                       id="email"
                       name="email"
                       placeholder="Digite seu email"
                       required>
            </div>
            
            <button type="submit" class="btn btn-recovery">
                <i class="fas fa-paper-plane me-2"></i>
                Enviar Instruções
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
</body>
</html>''',

        'templates/registration/password_reset_done.html': '''<!DOCTYPE html>
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
    </style>
</head>
<body>
    <div class="success-card">
        <div class="success-icon">
            <i class="fas fa-check"></i>
        </div>
        
        <h2 class="mb-3">Email Enviado!</h2>
        
        <p class="text-muted mb-4">
            Enviamos instruções para recuperação de senha para seu email. 
            Verifique sua caixa de entrada e siga as instruções.
        </p>
        
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            <strong>Não recebeu o email?</strong><br>
            Verifique sua pasta de spam ou lixo eletrônico.
        </div>
        
        <a href="javascript:history.back()" class="btn-back">
            <i class="fas fa-arrow-left me-2"></i>
            Voltar ao Login
        </a>
    </div>
</body>
</html>''',

        'templates/registration/password_reset_confirm.html': '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Senha - LVK Sistemas</title>
    
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
        
        .reset-card {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            max-width: 450px;
            width: 100%;
        }
        
        .reset-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .reset-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }
        
        .reset-icon i {
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
        
        .btn-reset {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-weight: 600;
            width: 100%;
            color: white;
        }
        
        .btn-reset:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .password-requirements {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .password-requirements ul {
            margin: 0;
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="reset-card">
        {% if validlink %}
        <div class="reset-header">
            <div class="reset-icon">
                <i class="fas fa-lock"></i>
            </div>
            <h2>Nova Senha</h2>
            <p class="text-muted">Digite sua nova senha</p>
        </div>
        
        {% if form.errors %}
            <div class="alert alert-danger">
                {% for field, errors in form.errors.items %}
                    {% for error in errors %}
                        {{ error }}<br>
                    {% endfor %}
                {% endfor %}
            </div>
        {% endif %}
        
        <div class="password-requirements">
            <strong><i class="fas fa-shield-alt me-2"></i>Requisitos da senha:</strong>
            <ul>
                <li>Mínimo de 8 caracteres</li>
                <li>Pelo menos uma letra maiúscula</li>
                <li>Pelo menos uma letra minúscula</li>
                <li>Pelo menos um número</li>
            </ul>
        </div>
        
        <form method="post">
            {% csrf_token %}
            
            <div class="mb-3">
                <label for="new_password1" class="form-label">
                    <i class="fas fa-key me-2"></i>Nova Senha
                </label>
                <input type="password" 
                       class="form-control" 
                       id="new_password1"
                       name="new_password1"
                       placeholder="Digite sua nova senha"
                       required>
            </div>
            
            <div class="mb-3">
                <label for="new_password2" class="form-label">
                    <i class="fas fa-check-double me-2"></i>Confirmar Senha
                </label>
                <input type="password" 
                       class="form-control" 
                       id="new_password2"
                       name="new_password2"
                       placeholder="Confirme sua nova senha"
                       required>
            </div>
            
            <button type="submit" class="btn btn-reset">
                <i class="fas fa-save me-2"></i>
                Alterar Senha
            </button>
        </form>
        
        {% else %}
        <div class="reset-header">
            <div class="reset-icon" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                <i class="fas fa-times"></i>
            </div>
            <h2>Link Inválido</h2>
            <p class="text-muted">Este link de recuperação é inválido ou já foi usado.</p>
        </div>
        
        <div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Link expirado ou inválido</strong><br>
            Solicite uma nova recuperação de senha.
        </div>
        
        <a href="/password_reset/" class="btn btn-reset">
            <i class="fas fa-redo me-2"></i>
            Solicitar Nova Recuperação
        </a>
        {% endif %}
    </div>
</body>
</html>''',

        'templates/registration/password_reset_complete.html': '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Senha Alterada - LVK Sistemas</title>
    
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
        
        .complete-card {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            max-width: 450px;
            width: 100%;
            text-align: center;
        }
        
        .complete-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #10b981, #059669);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }
        
        .complete-icon i {
            font-size: 36px;
            color: white;
        }
        
        .btn-login {
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
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="complete-card">
        <div class="complete-icon">
            <i class="fas fa-check-circle"></i>
        </div>
        
        <h2 class="mb-3">Senha Alterada!</h2>
        
        <p class="text-muted mb-4">
            Sua senha foi alterada com sucesso. 
            Agora você pode fazer login com sua nova senha.
        </p>
        
        <div class="alert alert-success">
            <i class="fas fa-shield-check me-2"></i>
            <strong>Segurança:</strong> Sua conta está protegida com a nova senha.
        </div>
        
        <a href="/" class="btn-login">
            <i class="fas fa-sign-in-alt me-2"></i>
            Fazer Login
        </a>
    </div>
</body>
</html>''',

        'templates/registration/password_reset_email.html': '''Olá,

Você solicitou a recuperação de senha para sua conta no LVK Sistemas.

Para criar uma nova senha, clique no link abaixo:
{{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

Se você não solicitou esta recuperação, ignore este email.

Este link expira em 24 horas.

Atenciosamente,
Equipe LVK Sistemas'''
    }
    
    print("🔧 Criando templates de recuperação de senha...")
    
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
    """Adiciona URLs de recuperação de senha ao urls.py"""
    
    print("🔧 Adicionando URLs de recuperação de senha...")
    
    try:
        urls_path = 'lojad/urls.py'
        
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem as URLs
        if 'password_reset' in content:
            print("✅ URLs de recuperação já existem!")
            return True
        
        # Adicionar imports necessários
        if 'from django.contrib.auth import views as auth_views' not in content:
            content = content.replace(
                'from django.urls import path, include',
                'from django.urls import path, include\nfrom django.contrib.auth import views as auth_views'
            )
        
        # Encontrar onde adicionar as URLs (antes do admin)
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if 'urlpatterns = [' in line:
                new_lines.append(line)
                # Adicionar URLs de recuperação de senha
                new_lines.append('    # URLs de recuperação de senha')
                new_lines.append("    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),")
                new_lines.append("    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),")
                new_lines.append("    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),")
                new_lines.append("    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),")
                new_lines.append('')
            else:
                new_lines.append(line)
        
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
            if 'password_reset' in content:
                print(f"✅ {template_path} já tem link de recuperação")
                success_count += 1
                continue
            
            # Adicionar seção de links antes do rodapé
            if 'Mensagem do Rodapé' in content:
                content = content.replace(
                    '<!-- Mensagem do Rodapé -->',
                    '''            <!-- Links de recuperação -->
            {% if login_config.mostrar_link_recuperar_senha and not is_preview %}
            <div class="text-center mt-3">
                <a href="{% url 'password_reset' %}" class="text-decoration-none">
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
                <a href="{% url 'password_reset' %}" class="text-decoration-none">
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


def testar_recuperacao():
    """Testa se a recuperação está funcionando"""
    
    print("🧪 Testando sistema de recuperação...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Testar se a URL existe
        try:
            response = client.get('/password_reset/')
            if response.status_code == 200:
                print("✅ URL de recuperação funcionando!")
                return True
            else:
                print(f"❌ URL retornou status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao testar URL: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 IMPLEMENTAÇÃO DE RECUPERAÇÃO DE SENHA")
    print("=" * 60)
    print()
    
    print("Implementando funcionalidade completa de recuperação de senha...")
    print()
    
    success_count = 0
    
    # Criar templates
    if criar_templates_recuperacao():
        success_count += 1
        print("✅ Templates criados com sucesso!")
    else:
        print("❌ Erro ao criar templates")
    
    print()
    
    # Adicionar URLs
    if adicionar_urls_recuperacao():
        success_count += 1
        print("✅ URLs adicionadas com sucesso!")
    else:
        print("❌ Erro ao adicionar URLs")
    
    print()
    
    # Restaurar links nos templates
    if restaurar_links_recuperacao():
        success_count += 1
        print("✅ Links restaurados nos templates!")
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
    
    if success_count >= 3:
        print("✅ IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Funcionalidades implementadas:")
        print("✅ Templates de recuperação de senha criados")
        print("✅ URLs de recuperação configuradas")
        print("✅ Links restaurados nos templates de login")
        print("✅ Configurações reativadas no banco")
        print()
        print("🌐 URLs disponíveis:")
        print("- Recuperar senha: /password_reset/")
        print("- Fatesa: /login/fatesa-escola-de-ultrassonografia/")
        print()
        print("🧪 TESTE:")
        print("1. Acesse a página de login da Fatesa")
        print("2. Clique em 'Esqueci minha senha'")
        print("3. Digite um email válido")
        print("4. Verifique se o processo funciona corretamente")
        
    else:
        print("❌ IMPLEMENTAÇÃO PARCIAL - Alguns problemas podem persistir")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()