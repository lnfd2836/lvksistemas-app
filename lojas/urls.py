from django.urls import path
from . import views

urlpatterns = [
    # Gerenciamento de lojas (apenas super admin)
    path('', views.listar_lojas, name='listar_lojas'),
    path('criar/', views.criar_loja, name='criar_loja'),
    path('<uuid:loja_id>/editar/', views.editar_loja, name='editar_loja'),
    path('<uuid:loja_id>/detalhar/', views.detalhar_loja, name='detalhar_loja'),
    path('<uuid:loja_id>/alterar-status/', views.alterar_status_loja, name='alterar_status_loja'),
    path('<uuid:loja_id>/backup/', views.backup_loja, name='backup_loja'),
    path('<uuid:loja_id>/excluir/', views.excluir_loja, name='excluir_loja'),
    
    # Gerenciamento de clientes
    path('clientes/', views.gerenciar_clientes, name='gerenciar_clientes'),
    path('clientes/adicionar/', views.adicionar_cliente, name='adicionar_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    
    # Gerenciamento de produtos
    path('produtos/', views.gerenciar_produtos, name='gerenciar_produtos'),
    path('produtos/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('produtos/<int:produto_id>/editar/', views.editar_produto, name='editar_produto'),
    
    # Gerenciamento de vendas
    path('vendas/', views.gerenciar_vendas, name='gerenciar_vendas'),
    path('vendas/nova/', views.nova_venda, name='nova_venda'),
    path('vendas/<int:venda_id>/detalhar/', views.detalhar_venda, name='detalhar_venda'),
]
