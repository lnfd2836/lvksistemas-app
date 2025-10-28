from django.urls import path
from . import views

app_name = 'controle_qualidade_comercial'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_controle_qualidade, name='dashboard'),
    
    # APIs para o dashboard
    path('api/metricas/', views.api_metricas, name='api_metricas'),
    path('api/vendas-diarias/', views.api_vendas_diarias, name='api_vendas_diarias'),
    path('api/top-produtos/', views.api_top_produtos, name='api_top_produtos'),
    path('api/reclamacoes-tipo/', views.api_reclamacoes_tipo, name='api_reclamacoes_tipo'),
    path('api/evolucao-qualidade/', views.api_evolucao_qualidade, name='api_evolucao_qualidade'),
    
    # CRUD - Produtos
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produtos/criar/', views.criar_produto, name='criar_produto'),
    path('produtos/<uuid:produto_id>/', views.detalhar_produto, name='detalhar_produto'),
    path('produtos/<uuid:produto_id>/editar/', views.editar_produto, name='editar_produto'),
    path('produtos/<uuid:produto_id>/excluir/', views.excluir_produto, name='excluir_produto'),
    
    # CRUD - Vendas
    path('vendas/', views.listar_vendas, name='listar_vendas'),
    path('vendas/criar/', views.criar_venda, name='criar_venda'),
    path('vendas/<uuid:venda_id>/', views.detalhar_venda, name='detalhar_venda'),
    path('vendas/<uuid:venda_id>/editar/', views.editar_venda, name='editar_venda'),
    path('vendas/<uuid:venda_id>/adicionar-item/', views.adicionar_item_venda, name='adicionar_item_venda'),
    
    # CRUD - Controle de Qualidade
    path('qualidade/', views.listar_controle_qualidade, name='listar_controle_qualidade'),
    path('qualidade/criar/', views.criar_inspecao_qualidade, name='criar_inspecao_qualidade'),
    path('qualidade/<uuid:inspecao_id>/', views.detalhar_inspecao_qualidade, name='detalhar_inspecao_qualidade'),
    path('qualidade/<uuid:inspecao_id>/editar/', views.editar_inspecao_qualidade, name='editar_inspecao_qualidade'),
    path('qualidade/<uuid:inspecao_id>/excluir/', views.excluir_inspecao_qualidade, name='excluir_inspecao_qualidade'),
    
    # CRUD - Reclamações
    path('reclamacoes/', views.listar_reclamacoes, name='listar_reclamacoes'),
    path('reclamacoes/criar/', views.criar_reclamacao, name='criar_reclamacao'),
    path('reclamacoes/<uuid:reclamacao_id>/', views.detalhar_reclamacao, name='detalhar_reclamacao'),
    path('reclamacoes/<uuid:reclamacao_id>/editar/', views.editar_reclamacao, name='editar_reclamacao'),
    path('reclamacoes/<uuid:reclamacao_id>/atualizar/', views.atualizar_reclamacao, name='atualizar_reclamacao'),
    path('reclamacoes/<uuid:reclamacao_id>/excluir/', views.excluir_reclamacao, name='excluir_reclamacao'),
    
    # CRUD - Metas de Qualidade
    path('metas/', views.listar_metas, name='listar_metas'),
    path('metas/criar/', views.criar_meta, name='criar_meta'),
    path('metas/<uuid:meta_id>/', views.detalhar_meta, name='detalhar_meta'),
    path('metas/<uuid:meta_id>/editar/', views.editar_meta, name='editar_meta'),
    path('metas/<uuid:meta_id>/excluir/', views.excluir_meta, name='excluir_meta'),
    path('metas/<uuid:meta_id>/atualizar-progresso/', views.atualizar_progresso_meta, name='atualizar_progresso_meta'),
    
    # CRUD - Categorias
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
    path('categorias/<uuid:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<uuid:categoria_id>/excluir/', views.excluir_categoria, name='excluir_categoria'),
    
    # CRUD - Fornecedores
    path('fornecedores/', views.listar_fornecedores, name='listar_fornecedores'),
    path('fornecedores/criar/', views.criar_fornecedor, name='criar_fornecedor'),
    path('fornecedores/<uuid:fornecedor_id>/editar/', views.editar_fornecedor, name='editar_fornecedor'),
    path('fornecedores/<uuid:fornecedor_id>/excluir/', views.excluir_fornecedor, name='excluir_fornecedor'),
    
    # Relatórios
    path('relatorios/', views.relatorios_dashboard, name='relatorios_dashboard'),
    path('api/relatorio-vendas/', views.api_relatorio_vendas, name='api_relatorio_vendas'),
    path('api/relatorio-qualidade/', views.api_relatorio_qualidade, name='api_relatorio_qualidade'),
    
    # Views Utilitárias
    path('ajax/buscar-produtos/', views.buscar_produtos_ajax, name='buscar_produtos_ajax'),
    path('ajax/buscar-vendas/', views.buscar_vendas_ajax, name='buscar_vendas_ajax'),
    path('estatisticas/', views.estatisticas_gerais, name='estatisticas_gerais'),
    path('exportar/<str:tipo>/', views.exportar_dados, name='exportar_dados'),
    path('configuracoes/', views.configuracoes_sistema, name='configuracoes_sistema'),
    path('backup/', views.backup_dados, name='backup_dados'),
]