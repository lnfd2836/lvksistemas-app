from django.urls import path
from . import views
from . import asaas_views

app_name = 'controle_financeiro'

urlpatterns = [
    # Dashboard Super Admin
    path('', views.dashboard_financeiro, name='dashboard_financeiro'),
    path('controles/', views.listar_controles_financeiros, name='listar_controles'),
    path('controles/<int:controle_id>/', views.detalhar_controle_financeiro, name='detalhar_controle'),
    
    # Ações de pagamento
    path('pagamentos/<uuid:pagamento_id>/aprovar/', views.aprovar_pagamento, name='aprovar_pagamento'),
    path('pagamentos/<uuid:pagamento_id>/rejeitar/', views.rejeitar_pagamento, name='rejeitar_pagamento'),
    
    # Ações de bloqueio
    path('controles/<int:controle_id>/bloquear/', views.bloquear_loja, name='bloquear_loja'),
    path('controles/<int:controle_id>/desbloquear/', views.desbloquear_loja, name='desbloquear_loja'),
    
    # Utilitários
    path('verificar-vencimentos/', views.verificar_vencimentos, name='verificar_vencimentos'),
    
    # Cliente (loja)
    path('pagamento/', views.pagamento_cliente, name='pagamento_cliente'),
    
    # === REDIRECIONAMENTOS (COMPATIBILIDADE) ===
    # Boletos antigos -> Cobranças Asaas
    path('boletos/', views.redirect_boletos_to_asaas, name='listar_boletos'),
    path('boletos/configurar/', views.redirect_configurar_boletos_to_asaas, name='configurar_boletos'),
    path('boletos/gerar/<int:controle_id>/', views.redirect_gerar_boleto_to_asaas, name='gerar_boleto'),
    path('boletos-cliente/', views.redirect_boletos_cliente_to_asaas, name='boletos_cliente'),
    
    # === INTEGRAÇÃO ASAAS (PRINCIPAL) ===
    path('asaas/gerar/<int:controle_id>/', asaas_views.gerar_cobranca_asaas, name='gerar_cobranca_asaas'),
    path('asaas/cobrancas/', asaas_views.listar_cobrancas_asaas, name='listar_cobrancas_asaas'),
    path('asaas/cobrancas/criar/', asaas_views.criar_cobranca_asaas, name='criar_cobranca_asaas'),
    path('asaas/cobrancas/<uuid:cobranca_id>/', asaas_views.visualizar_cobranca_asaas, name='visualizar_cobranca_asaas'),
    path('asaas/cobrancas/<uuid:cobranca_id>/excluir/', asaas_views.excluir_cobranca_asaas, name='excluir_cobranca_asaas'),
    path('asaas/webhook/', asaas_views.webhook_asaas, name='webhook_asaas'),
    path('asaas/webhook-debug/', asaas_views.webhook_debug, name='webhook_debug'),
    path('asaas/webhook-test/', asaas_views.webhook_test, name='webhook_test'),
    path('asaas/callback/success/', asaas_views.callback_success_asaas, name='callback_success_asaas'),
    path('asaas/configurar/', asaas_views.configurar_asaas, name='configurar_asaas'),
    path('asaas/testar/', asaas_views.testar_asaas, name='testar_asaas'),
    
    # PDF Asaas
    path('asaas/pdf/<str:cobranca_id>/', views.pdf_asaas_redirect, name='pdf_asaas_redirect'),
    path('asaas/pdf-direto/<str:asaas_id>/', views.pdf_asaas_direto, name='pdf_asaas_direto'),
]
