from django.urls import path, include
from . import views
from . import views_login
from . import views_configuracoes

app_name = 'lojas'

urlpatterns = [
    # Gerenciamento de lojas (apenas super admin)
    path('', views.listar_lojas, name='listar_lojas'),
    path('criar/', views.criar_loja, name='criar_loja'),
    path('<uuid:loja_id>/editar/', views.editar_loja, name='editar_loja'),
    path('<uuid:loja_id>/detalhar/', views.detalhar_loja, name='detalhar_loja'),
    path('<uuid:loja_id>/alterar-status/', views.alterar_status_loja, name='alterar_status_loja'),
    path('<uuid:loja_id>/backup/', views.backup_loja, name='backup_loja'),
    path('<uuid:loja_id>/excluir/', views.excluir_loja, name='excluir_loja'),
    path('<uuid:loja_id>/enviar-credenciais/', views.enviar_credenciais_provisorias, name='enviar_credenciais_provisorias'),
    
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
    
    # Gerenciamento de cardápio (lanchonetes)
    path('cardapio/', views.gerenciar_cardapio, name='gerenciar_cardapio'),
    path('cardapio/adicionar/', views.adicionar_item_cardapio, name='adicionar_item_cardapio'),
    path('cardapio/<int:produto_id>/editar/', views.editar_item_cardapio, name='editar_item_cardapio'),
    
    # Gerenciamento de mesas (lanchonetes)
    path('mesas/', views.gerenciar_mesas, name='gerenciar_mesas'),
    path('mesas/adicionar/', views.adicionar_mesa, name='adicionar_mesa'),
    path('mesas/<int:mesa_id>/editar/', views.editar_mesa, name='editar_mesa'),
    path('mesas/<int:mesa_id>/alterar-status/', views.alterar_status_mesa, name='alterar_status_mesa'),
    
    # Gerenciamento de pedidos (lanchonetes)
    path('pedidos/', views.gerenciar_pedidos, name='gerenciar_pedidos'),
    path('pedidos/novo/', views.novo_pedido, name='novo_pedido'),
    path('pedidos/<int:pedido_id>/detalhar/', views.detalhar_pedido, name='detalhar_pedido'),
    path('pedidos/<int:pedido_id>/alterar-status/', views.alterar_status_pedido, name='alterar_status_pedido'),
    
    # Gerenciamento de funcionários
    path('funcionarios/', include('lojas.urls_funcionarios')),
    
    # URLs administrativas (super admin)
    path('admin/', include('lojas.urls_admin')),
    
    # Configurações individuais por loja
    path('<uuid:loja_id>/configuracoes/', views_configuracoes.gerenciar_configuracoes_loja, name='configuracoes'),
    path('<uuid:loja_id>/configuracoes/produto/', views_configuracoes.salvar_configuracao_produto, name='salvar_config_produto'),
    path('<uuid:loja_id>/configuracoes/cliente/', views_configuracoes.salvar_configuracao_cliente, name='salvar_config_cliente'),
    path('<uuid:loja_id>/configuracoes/venda/', views_configuracoes.salvar_configuracao_venda, name='salvar_config_venda'),
    path('<uuid:loja_id>/configuracoes/dashboard/', views_configuracoes.salvar_configuracao_dashboard, name='salvar_config_dashboard'),
    path('<uuid:loja_id>/configuracoes/preview-dashboard/', views_configuracoes.preview_dashboard, name='preview_dashboard'),
    
    # Login personalizado por loja
    path('<uuid:loja_id>/login/gerenciar/', views_login.gerenciar_login_personalizado, name='gerenciar_login_personalizado'),
    path('<uuid:loja_id>/login/preview/', views_login.preview_login_personalizado, name='preview_login_personalizado'),
    path('<uuid:loja_id>/login/historico/', views_login.historico_login_loja, name='historico_login_loja'),
]
