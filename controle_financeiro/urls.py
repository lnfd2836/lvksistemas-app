from django.urls import path
from . import views

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
    path('boletos/configurar-caixa/', views.configurar_caixa, name='configurar_caixa'),
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
    ]
