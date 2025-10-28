"""
URLs específicas para o módulo CRM de Vendas
"""
from django.urls import path
from . import views_crm

app_name = 'modulos_crm'

urlpatterns = [
    # Dashboard CRM
    path('', views_crm.dashboard_crm_modulo, name='dashboard'),
    
    # Leads
    path('leads/', views_crm.listar_leads_modulo, name='listar_leads'),
    path('leads/novo/', views_crm.criar_lead_modulo, name='criar_lead'),
    path('leads/<uuid:lead_id>/', views_crm.detalhar_lead_modulo, name='detalhar_lead'),
    
    # Orçamentos
    path('orcamentos/', views_crm.listar_orcamentos_modulo, name='listar_orcamentos'),
    path('orcamentos/novo/', views_crm.criar_orcamento_modulo, name='criar_orcamento'),
    path('orcamentos/<uuid:orcamento_id>/enviar/', views_crm.enviar_orcamento_modulo, name='enviar_orcamento'),
    
    # Propostas
    path('propostas/', views_crm.listar_propostas_modulo, name='listar_propostas'),
    path('propostas/nova/', views_crm.criar_proposta_modulo, name='criar_proposta'),
    
    # Contratos
    path('contratos/', views_crm.listar_contratos_modulo, name='listar_contratos'),
    path('contratos/novo/', views_crm.criar_contrato_modulo, name='criar_contrato'),
    
    # Relatórios
    path('relatorios/', views_crm.relatorios_crm_modulo, name='relatorios'),
    path('relatorios/funil/', views_crm.relatorio_funil_modulo, name='relatorio_funil'),
    
    # Configurações
    path('configuracoes/', views_crm.configuracoes_crm_modulo, name='configuracoes'),
]