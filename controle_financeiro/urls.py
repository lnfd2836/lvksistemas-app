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
    
    # Configuração de boletos
    path('boletos/configurar/', views.configurar_boletos, name='configurar_boletos'),
    path('boletos/configurar/<int:config_id>/', views.editar_configuracao_boleto, name='editar_configuracao_boleto'),
    path('boletos/gerar/<int:controle_id>/', views.gerar_boleto, name='gerar_boleto'),
    path('boletos/', views.listar_boletos, name='listar_boletos'),
    path('boletos/<int:boleto_id>/pago/', views.marcar_boleto_pago, name='marcar_boleto_pago'),
    
        # Cliente (loja) - boletos
        path('boletos-cliente/', views.boletos_cliente, name='boletos_cliente'),
        
        # Detalhes do boleto
        path('boletos/<int:boleto_id>/detalhes/', views.detalhar_boleto, name='detalhar_boleto'),
        
        # Automação financeira
        path('gerar-boletos-automaticos/', views.gerar_boletos_automaticos, name='gerar_boletos_automaticos'),
        path('executar-rotinas-financeiras/', views.executar_rotinas_financeiras, name='executar_rotinas_financeiras'),
        
        # Gerenciamento manual de boletos
        path('boletos/criar-manual/', views.criar_boleto_manual, name='criar_boleto_manual'),
        path('boletos/<int:boleto_id>/excluir/', views.excluir_boleto, name='excluir_boleto'),
        
        # PDF e pagamento
        path('boletos/<int:boleto_id>/pdf/', views.imprimir_boleto_pdf, name='imprimir_boleto_pdf'),
        path('asaas/pdf/<str:cobranca_id>/', views.pdf_asaas_redirect, name='pdf_asaas_redirect'),
        
        # Integração Asaas
        path('asaas/gerar/<int:controle_id>/', asaas_views.gerar_cobranca_asaas, name='gerar_cobranca_asaas'),
        path('asaas/cobrancas/', asaas_views.listar_cobrancas_asaas, name='listar_cobrancas_asaas'),
        path('asaas/cobrancas/<uuid:cobranca_id>/', asaas_views.visualizar_cobranca_asaas, name='visualizar_cobranca_asaas'),
        path('asaas/webhook/', asaas_views.webhook_asaas, name='webhook_asaas'),
        path('asaas/webhook-debug/', asaas_views.webhook_debug, name='webhook_debug'),
        path('asaas/webhook-test/', asaas_views.webhook_test, name='webhook_test'),
        path('asaas/callback/success/', asaas_views.callback_success_asaas, name='callback_success_asaas'),
        path('asaas/configurar/', asaas_views.configurar_asaas, name='configurar_asaas'),
        path('asaas/testar/', asaas_views.testar_asaas, name='testar_asaas'),
    ]
