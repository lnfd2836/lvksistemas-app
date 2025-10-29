from django.urls import path, include
from . import views

app_name = 'modulos'

urlpatterns = [
    path('tipos-loja/', views.listar_tipos_loja, name='listar_tipos_loja'),
    path('tipos-loja/criar/', views.criar_tipo_loja, name='criar_tipo_loja'),
    path('tipos-loja/<uuid:tipo_id>/editar/', views.editar_tipo_loja, name='editar_tipo_loja'),
    path('tipos-loja/<uuid:tipo_id>/excluir/', views.excluir_tipo_loja, name='excluir_tipo_loja'),
    
    # URLs da Clínica de Estética
    path('estetica/', include('modulos.urls_estetica')),
    
    # URLs do CRM de Vendas
    path('crm/', include('modulos.urls_crm')),
    

]
