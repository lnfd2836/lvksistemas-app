"""
URLs do CRM de Vendas
"""
from django.urls import path
from . import views

app_name = 'crm_vendas'

urlpatterns = [
    # Dashboard CRM
    path('', views.dashboard_crm, name='dashboard'),
    
    # Leads
    path('leads/', views.listar_leads, name='listar_leads'),
    path('leads/novo/', views.criar_lead, name='criar_lead'),
    path('leads/<uuid:lead_id>/', views.detalhar_lead, name='detalhar_lead'),
    path('leads/<uuid:lead_id>/editar/', views.editar_lead, name='editar_lead'),
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
    path('propostas/<uuid:proposta_id>/enviar/', views.enviar_proposta, name='enviar_proposta'),
    
    # Contratos
    path('contratos/', views.listar_contratos, name='listar_contratos'),
    path('contratos/novo/', views.criar_contrato, name='criar_contrato'),
    path('contratos/<uuid:contrato_id>/', views.detalhar_contrato, name='detalhar_contrato'),
    path('contratos/<uuid:contrato_id>/enviar/', views.enviar_contrato, name='enviar_contrato'),
    
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
]