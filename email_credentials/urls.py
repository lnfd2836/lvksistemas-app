"""
URLs para o sistema de credenciais por email
"""
from django.urls import path
from . import views

app_name = 'email_credentials'

urlpatterns = [
    # Dashboards
    path('dashboard/', views.dashboard_super_admin, name='dashboard_super_admin'),
    path('dashboard/loja/', views.dashboard_loja_admin, name='dashboard_loja_admin'),
    
    # Gerenciamento de usuários - Super Admin
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/criar/', views.criar_usuario, name='criar_usuario'),
    
    # Gerenciamento de usuários - Loja Admin
    path('loja/usuarios/', views.listar_usuarios_loja, name='listar_usuarios_loja'),
    path('loja/usuarios/criar/', views.criar_usuario_loja, name='criar_usuario_loja'),
    
    # Ações de usuário
    path('usuarios/<int:user_id>/reenviar/', views.reenviar_credenciais, name='reenviar_credenciais'),
    
    # Recuperação de senha
    path('recuperar-senha/', views.recuperar_senha_form, name='recuperar_senha'),
    
    # Logs e monitoramento
    path('logs/', views.logs_email, name='logs_email'),
    
    # APIs
    path('api/gerar-senhas/', views.api_gerar_senhas, name='api_gerar_senhas'),
    path('api/validar-senha/', views.api_validar_senha, name='api_validar_senha'),
]