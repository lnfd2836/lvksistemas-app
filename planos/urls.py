from django.urls import path
from . import views

app_name = 'planos'

urlpatterns = [
    # Teste
    path('teste/', views.teste_planos, name='teste_planos'),
    # Planos comerciais
    path('', views.listar_planos, name='listar_planos'),
    path('novo/', views.criar_plano, name='criar_plano'),
    path('<int:plano_id>/editar/', views.editar_plano, name='editar_plano'),
    path('<int:plano_id>/detalhar/', views.detalhar_plano, name='detalhar_plano'),
    
    # Assinaturas
    path('assinar/<uuid:loja_id>/<int:plano_id>/', views.assinar_plano, name='assinar_plano'),
    
    # Estatísticas
    path('estatisticas/', views.estatisticas_planos, name='estatisticas_planos'),
    
    # API
    path('api/controle-acesso/', views.controle_acesso_ajax, name='controle_acesso_ajax'),
]
