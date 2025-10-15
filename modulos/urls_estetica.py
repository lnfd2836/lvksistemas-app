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
    
    # Protocolos
    path('protocolos/', views_estetica.listar_protocolos, name='protocolos'),
    path('protocolos/<uuid:protocolo_id>/', views_estetica.protocolo_detalhes, name='protocolo_detalhes'),
    
    # Clientes
    path('clientes/<uuid:cliente_id>/anamnese/', views_estetica.ficha_anamnese, name='ficha_anamnese'),
    path('clientes/<uuid:cliente_id>/evolucao/', views_estetica.evolucao_tratamento, name='evolucao_tratamento'),
    
    # Relatórios
    path('relatorios/', views_estetica.relatorios_estetica, name='relatorios'),
]
