from django.urls import path
from . import views_estetica

urlpatterns = [
    # Dashboard
    path('', views_estetica.dashboard_estetica, name='estetica_dashboard'),
    
    # Agendamentos
    path('agendamentos/', views_estetica.listar_agendamentos, name='estetica_agendamentos'),
    path('agendamentos/criar/', views_estetica.criar_agendamento, name='estetica_criar_agendamento'),
    path('agendamentos/<uuid:agendamento_id>/', views_estetica.agendamento_detalhes, name='estetica_agendamento_detalhes'),
    path('agendamentos/<uuid:agendamento_id>/status/', views_estetica.atualizar_status_agendamento, name='estetica_atualizar_status_agendamento'),
    path('agendamentos/calendario/', views_estetica.calendario_agendamentos, name='estetica_calendario_agendamentos'),
    
    # Serviços
    path('servicos/', views_estetica.listar_servicos, name='estetica_servicos'),
    path('servicos/criar/', views_estetica.criar_servico, name='estetica_criar_servico'),
    path('servicos/<uuid:servico_id>/', views_estetica.servico_detalhes, name='estetica_servico_detalhes'),
    path('servicos/<uuid:servico_id>/editar/', views_estetica.editar_servico, name='estetica_editar_servico'),
    
    # Protocolos
    path('protocolos/', views_estetica.listar_protocolos, name='estetica_protocolos'),
    path('protocolos/criar/', views_estetica.criar_protocolo, name='estetica_criar_protocolo'),
    path('protocolos/<uuid:protocolo_id>/', views_estetica.protocolo_detalhes, name='estetica_protocolo_detalhes'),
    path('protocolos/<uuid:protocolo_id>/editar/', views_estetica.editar_protocolo, name='estetica_editar_protocolo'),
    
    # Clientes
    path('clientes/', views_estetica.listar_clientes, name='estetica_clientes'),
    path('clientes/criar/', views_estetica.criar_cliente, name='estetica_criar_cliente'),
    path('clientes/<uuid:cliente_id>/', views_estetica.cliente_detalhes, name='estetica_cliente_detalhes'),
    path('clientes/<uuid:cliente_id>/anamnese/', views_estetica.ficha_anamnese, name='estetica_ficha_anamnese'),
    path('clientes/<uuid:cliente_id>/evolucao/', views_estetica.evolucao_tratamento, name='estetica_evolucao_tratamento'),
    
    # Pacotes
    path('pacotes/', views_estetica.listar_pacotes, name='estetica_pacotes'),
    path('pacotes/criar/', views_estetica.criar_pacote, name='estetica_criar_pacote'),
    path('pacotes/<uuid:pacote_id>/', views_estetica.pacote_detalhes, name='estetica_pacote_detalhes'),
    path('pacotes/<uuid:pacote_id>/editar/', views_estetica.editar_pacote, name='estetica_editar_pacote'),
    
    # Retornos
    path('retornos/', views_estetica.listar_retornos, name='estetica_retornos'),
    path('retornos/criar/', views_estetica.criar_retorno, name='estetica_criar_retorno'),
    path('retornos/<uuid:retorno_id>/', views_estetica.retorno_detalhes, name='estetica_retorno_detalhes'),
    
    # Relatórios
    path('relatorios/', views_estetica.relatorios_estetica, name='estetica_relatorios'),
]
