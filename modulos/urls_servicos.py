"""
URLs para gerenciamento de serviços
"""
from django.urls import path
from . import views_servicos

urlpatterns = [
    # Listagem e CRUD de serviços
    path('', views_servicos.listar_servicos, name='listar_servicos'),
    path('criar/', views_servicos.criar_servico, name='criar_servico'),
    path('<uuid:servico_id>/', views_servicos.detalhes_servico, name='detalhes_servico'),
    path('<uuid:servico_id>/editar/', views_servicos.editar_servico, name='editar_servico'),
    path('<uuid:servico_id>/excluir/', views_servicos.excluir_servico, name='excluir_servico'),
    
    # AJAX
    path('<uuid:servico_id>/toggle-ativo/', views_servicos.toggle_ativo_servico, name='toggle_ativo_servico'),
]