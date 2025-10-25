from django.urls import path
from . import views
from . import asaas_views
from . import asaas_sync_views

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
    path('executar-rotinas-financeiras/', views.executar_rotinas_financeiras, name='executar_rotinas_financeiras'),
    
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
    
    # === SINCRONIZAÇÃO EM TEMPO REAL ===
    path('sync/', asaas_sync_views.dashboard_sincronizacao, name='dashboard_sincronizacao'),
    path('sync/iniciar/', asaas_sync_views.iniciar_sincronizacao, name='iniciar_sincronizacao'),
    path('sync/parar/', asaas_sync_views.parar_sincronizacao, name='parar_sincronizacao'),
    path('sync/forcar/', asaas_sync_views.forcar_sincronizacao, name='forcar_sincronizacao'),
    path('sync/testar/', asaas_sync_views.testar_conectividade, name='testar_conectividade'),
    path('sync/teste/', asaas_sync_views.teste_sincronizacao, name='teste_sincronizacao'),
    path('sync/funcionalidades-existentes/', asaas_sync_views.sincronizar_usando_funcionalidades_existentes, name='sincronizar_funcionalidades_existentes'),
    path('sync/cobranca/<str:asaas_id>/', asaas_sync_views.sincronizar_cobranca, name='sincronizar_cobranca'),
    path('sync/resetar/', asaas_sync_views.resetar_estatisticas, name='resetar_estatisticas'),

    path('sync/problemas/', asaas_sync_views.listar_cobrancas_problemas, name='listar_cobrancas_problemas'),
    
    # APIs de Sincronização
    path('api/sync/status/', asaas_sync_views.api_sync_status, name='api_sync_status'),
    path('api/sync/stats/', asaas_sync_views.api_cobrancas_stats, name='api_cobrancas_stats'),
    path('api/sync/webhook/', asaas_sync_views.webhook_sync_trigger, name='webhook_sync_trigger'),
]
