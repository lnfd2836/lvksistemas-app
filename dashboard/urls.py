from django.urls import path
from . import views
from . import views_debug
from .simple_login import simple_login
from .loja_login import loja_login, loja_logout

# Nome da aplicação para namespacing
app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal - redireciona automaticamente baseado no usuário
    path('', views.dashboard_principal, name='principal'),
    
    # Dashboards específicos
    path('super-admin/', views.dashboard_super_admin, name='super_admin'),
    path('loja/', views.dashboard_loja, name='loja'),
    path('loja/<uuid:loja_id>/', views.dashboard_loja, name='loja_especifica'),
    
    # Autenticação - mantido para compatibilidade
    path('login/', simple_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('loja/login/', loja_login, name='loja_login'),
    path('loja/logout/', loja_logout, name='loja_logout'),
    
    # APIs e AJAX
    path('api/estatisticas/', views.estatisticas_ajax, name='api_estatisticas'),
    path('api/notificacao/<int:notificacao_id>/marcar-lida/', 
         views.marcar_notificacao_lida, name='api_marcar_notificacao_lida'),
    
    # Administração - Super Admin apenas
    path('admin/usuarios/', views.listar_usuarios_super_admin, name='admin_usuarios_lista'),
    path('admin/usuarios/criar/', views.criar_usuario_super_admin, name='admin_usuarios_criar'),
    path('admin/usuarios/<int:user_id>/editar/', 
         views.editar_usuario_super_admin, name='admin_usuarios_editar'),
    path('admin/usuarios/<int:user_id>/alterar-senha/', 
         views.alterar_senha_usuario_super_admin, name='admin_usuarios_alterar_senha'),
    path('admin/usuarios/<int:user_id>/excluir/', 
         views.excluir_usuario_super_admin, name='admin_usuarios_excluir'),
    
    # Gerenciamento de sessões
    path('admin/sessoes/', views.gerenciar_sessoes, name='admin_sessoes'),
    path('admin/sessoes/<int:sessao_id>/invalidar/', 
         views.invalidar_sessao, name='admin_sessoes_invalidar'),
    
    # Gerenciamento de módulos
    path('admin/modulos/', views.gerenciar_modulos, name='admin_modulos'),
    
    # Redirecionamento inteligente
    path('redirect/', views.redirect_to_appropriate_dashboard, name='redirect_inteligente'),
    
    # Debug URLs (apenas em desenvolvimento)
    path('debug/test-500/', views_debug.test_500_error, name='debug_test_500'),
    path('debug/test-auth/', views_debug.test_auth_error, name='debug_test_auth'),
    path('debug/test-middleware/', views_debug.test_middleware_error, name='debug_test_middleware'),
    path('debug/info/', views_debug.debug_info, name='debug_info'),
]
