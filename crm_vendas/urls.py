"""
URLs do CRM de Vendas
"""
from django.urls import path
from . import views
from .dashboard_view import dashboard_crm_simples

app_name = 'crm_vendas'

urlpatterns = [
    # Dashboard CRM
    path('', dashboard_crm_simples, name='dashboard'),
    
    # Leads
    path('leads/', views.listar_leads, name='listar_leads'),
    path('leads/novo/', views.criar_lead_melhorado, name='criar_lead'),
    path('leads/<uuid:lead_id>/', views.detalhar_lead, name='detalhar_lead'),
    path('leads/<uuid:lead_id>/editar/', views.editar_lead, name='editar_lead'),
    path('leads/<uuid:lead_id>/excluir/', views.excluir_lead, name='excluir_lead'),
    path('leads/<uuid:lead_id>/contato/', views.registrar_contato, name='registrar_contato'),
    
    # Orçamentos
    path('orcamentos/', views.listar_orcamentos, name='listar_orcamentos'),
    path('orcamentos/novo/', views.criar_orcamento, name='criar_orcamento'),
    path('orcamentos/<uuid:orcamento_id>/', views.detalhar_orcamento, name='detalhar_orcamento'),
    path('orcamentos/<uuid:orcamento_id>/editar/', views.editar_orcamento, name='editar_orcamento'),
    path('orcamentos/<uuid:orcamento_id>/enviar/', views.enviar_orcamento, name='enviar_orcamento'),
    path('orcamentos/<uuid:orcamento_id>/pdf/', views.gerar_pdf_orcamento, name='pdf_orcamento'),
    
    # Propostas
    path('propostas/', views.listar_propostas, name='listar_propostas'),
    path('propostas/nova/', views.criar_proposta, name='criar_proposta'),
    path('propostas/<uuid:proposta_id>/', views.detalhar_proposta, name='detalhar_proposta'),
    path('propostas/<uuid:proposta_id>/editar/', views.editar_proposta, name='editar_proposta'),
    path('propostas/<uuid:proposta_id>/enviar/', views.enviar_proposta, name='enviar_proposta'),
    path('propostas/<uuid:proposta_id>/pdf/', views.gerar_pdf_proposta, name='pdf_proposta'),
    
    # Contratos
    path('contratos/', views.listar_contratos, name='listar_contratos'),
    path('contratos/novo/', views.criar_contrato, name='criar_contrato'),
    path('contratos/<uuid:contrato_id>/', views.detalhar_contrato, name='detalhar_contrato'),
    path('contratos/<uuid:contrato_id>/editar/', views.editar_contrato, name='editar_contrato'),
    path('contratos/<uuid:contrato_id>/enviar/', views.enviar_contrato, name='enviar_contrato'),
    path('contratos/<uuid:contrato_id>/pdf/', views.gerar_pdf_contrato, name='pdf_contrato'),
    
    # URLs públicas (para clientes)
    path('orcamento/<uuid:orcamento_id>/visualizar/', views.visualizar_orcamento_publico, name='visualizar_orcamento_publico'),
    path('orcamento/<uuid:orcamento_id>/aprovar/', views.aprovar_orcamento_publico, name='aprovar_orcamento_publico'),
    path('proposta/<uuid:proposta_id>/visualizar/', views.visualizar_proposta_publico, name='visualizar_proposta_publico'),
    path('contrato/<uuid:contrato_id>/assinar/', views.assinar_contrato_publico, name='assinar_contrato_publico'),
    
    # Email tracking
    path('email/track/<uuid:orcamento_id>/', views.track_email_abertura, name='track_email'),
    path('email/click/<uuid:token>/', views.track_email_clique, name='track_click'),
    
    # Relatórios
    path('relatorios/', views.relatorios_crm, name='relatorios'),
    path('relatorios/funil/', views.relatorio_funil_vendas, name='relatorio_funil'),
    path('relatorios/performance/', views.relatorio_performance, name='relatorio_performance'),
    
    # Configurações
    path('configuracoes/', views.configuracoes_crm, name='configuracoes'),
    
    # ============================================================================
    # NOVAS URLS PARA FLUXO COMPLETO
    # ============================================================================
    
    # Produtos e Serviços
    path('produtos-servicos/', views.listar_produtos_servicos, name='listar_produtos_servicos'),
    path('produtos-servicos/novo/', views.criar_produto_servico, name='criar_produto_servico'),
    path('produtos-servicos/<uuid:produto_id>/editar/', views.editar_produto_servico, name='editar_produto_servico'),
    
    # Leads melhorados
    path('leads/novo-melhorado/', views.criar_lead_melhorado, name='criar_lead_melhorado'),
    
    # Orçamentos melhorados
    path('orcamentos/novo-melhorado/', views.criar_orcamento_melhorado, name='criar_orcamento_melhorado'),
    path('orcamentos/<uuid:orcamento_id>/itens/', views.editar_orcamento_itens, name='editar_orcamento_itens'),
    
    # Assinatura Digital
    path('assinatura/<str:tipo_documento>/<uuid:documento_id>/', views.solicitar_assinatura, name='solicitar_assinatura'),
    path('assinatura-empresa/<str:tipo_documento>/<uuid:documento_id>/', views.solicitar_assinatura_empresa, name='solicitar_assinatura_empresa'),
    path('assinar/<uuid:token>/', views.assinar_documento_publico, name='assinar_documento_publico'),
    
    # Relatórios
    path('relatorios/vendas/', views.relatorios_vendas, name='relatorios_vendas'),
    
    # APIs
    path('api/produto-servico/<uuid:produto_id>/', views.api_produto_servico_detalhes, name='api_produto_servico_detalhes'),
]