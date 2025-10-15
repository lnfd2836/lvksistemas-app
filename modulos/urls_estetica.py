from django.urls import path
from . import views_estetica

app_name = 'estetica'

urlpatterns = [
    # Dashboard
    path('', views_estetica.dashboard_estetica, name='dashboard'),
    
    # Agendamentos
    path('agendamentos/', views_estetica.listar_agendamentos, name='agendamentos'),
    path('agendamentos/criar/', views_estetica.criar_agendamento, name='criar_agendamento'),
    path('agendamentos/<uuid:agendamento_id>/', views_estetica.agendamento_detalhes, name='agendamento_detalhes'),
    path('agendamentos/<uuid:agendamento_id>/status/', views_estetica.atualizar_status_agendamento, name='atualizar_status_agendamento'),
    path('agendamentos/calendario/', views_estetica.calendario_agendamentos, name='calendario_agendamentos'),
    
    # Serviços
    path('servicos/', views_estetica.listar_servicos, name='servicos'),
    path('servicos/criar/', views_estetica.criar_servico, name='criar_servico'),
    path('servicos/<uuid:servico_id>/', views_estetica.servico_detalhes, name='servico_detalhes'),
    path('servicos/<uuid:servico_id>/editar/', views_estetica.editar_servico, name='editar_servico'),
    
    # Protocolos
    path('protocolos/', views_estetica.listar_protocolos, name='protocolos'),
    path('protocolos/criar/', views_estetica.criar_protocolo, name='criar_protocolo'),
    path('protocolos/<uuid:protocolo_id>/', views_estetica.protocolo_detalhes, name='protocolo_detalhes'),
    path('protocolos/<uuid:protocolo_id>/editar/', views_estetica.editar_protocolo, name='editar_protocolo'),
    
    # Clientes
    path('clientes/', views_estetica.listar_clientes, name='clientes'),
    path('clientes/<uuid:cliente_id>/', views_estetica.cliente_detalhes, name='cliente_detalhes'),
    path('clientes/<uuid:cliente_id>/anamnese/', views_estetica.ficha_anamnese, name='ficha_anamnese'),
    path('clientes/<uuid:cliente_id>/evolucao/', views_estetica.evolucao_tratamento, name='evolucao_tratamento'),
    
    # Pacotes
    path('pacotes/', views_estetica.listar_pacotes, name='pacotes'),
    path('pacotes/criar/', views_estetica.criar_pacote, name='criar_pacote'),
    path('pacotes/<uuid:pacote_id>/', views_estetica.pacote_detalhes, name='pacote_detalhes'),
    path('pacotes/<uuid:pacote_id>/editar/', views_estetica.editar_pacote, name='editar_pacote'),
    
    # Retornos
    path('retornos/', views_estetica.listar_retornos, name='retornos'),
    path('retornos/criar/', views_estetica.criar_retorno, name='criar_retorno'),
    path('retornos/<uuid:retorno_id>/', views_estetica.retorno_detalhes, name='retorno_detalhes'),
    
    # Relatórios
    path('relatorios/', views_estetica.relatorios_estetica, name='relatorios'),
]
