from django.urls import path
from . import views
from .simple_login import simple_login
from .loja_login import loja_login, loja_logout

urlpatterns = [
    path('', views.dashboard_principal, name='dashboard'),
    path('super-admin/', views.dashboard_super_admin, name='dashboard_super_admin'),
    path('login/', simple_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('loja/login/', loja_login, name='loja_login'),
    path('loja/logout/', loja_logout, name='loja_logout'),
    path('loja/dashboard/', views.dashboard_loja, name='dashboard_loja'),
    path('loja/<uuid:loja_id>/', views.dashboard_loja, name='dashboard_loja_id'),
    path('notificacao/<int:notificacao_id>/marcar-lida/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    path('estatisticas/', views.estatisticas_ajax, name='estatisticas_ajax'),
    
    # Gerenciamento de usuários super administradores
    path('usuarios-super-admin/', views.listar_usuarios_super_admin, name='listar_usuarios_super_admin'),
    path('usuarios-super-admin/criar/', views.criar_usuario_super_admin, name='criar_usuario_super_admin'),
    path('usuarios-super-admin/<int:user_id>/editar/', views.editar_usuario_super_admin, name='editar_usuario_super_admin'),
    path('usuarios-super-admin/<int:user_id>/alterar-senha/', views.alterar_senha_usuario_super_admin, name='alterar_senha_usuario_super_admin'),
    path('usuarios-super-admin/<int:user_id>/excluir/', views.excluir_usuario_super_admin, name='excluir_usuario_super_admin'),
    
    # Gerenciamento de sessões
    path('sessoes/', views.gerenciar_sessoes, name='gerenciar_sessoes'),
    path('sessoes/<int:sessao_id>/invalidar/', views.invalidar_sessao, name='invalidar_sessao'),
    
    # Gerenciamento de módulos
    path('modulos/', views.gerenciar_modulos, name='gerenciar_modulos'),
]
