from django.urls import path
from . import views_funcionarios

app_name = 'funcionarios'

urlpatterns = [
    # Lista e visualização
    path('', views_funcionarios.funcionario_list, name='list'),
    path('<uuid:funcionario_id>/', views_funcionarios.funcionario_detail, name='detail'),
    
    # Criação e edição
    path('novo/', views_funcionarios.funcionario_create, name='create'),
    path('<uuid:funcionario_id>/editar/', views_funcionarios.funcionario_edit, name='edit'),
    
    # Ações
    path('<uuid:funcionario_id>/toggle-status/', views_funcionarios.funcionario_toggle_status, name='toggle_status'),
    path('<uuid:funcionario_id>/reset-password/', views_funcionarios.funcionario_reset_password, name='reset_password'),
]