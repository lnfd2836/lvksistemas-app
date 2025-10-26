from django.urls import path
from . import views

app_name = 'avaliacao_qualidade'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_avaliacao, name='dashboard_avaliacao'),
    
    # === GESTÃO DE CURSOS ===
    path('cursos/', views.listar_cursos, name='listar_cursos'),
    path('cursos/criar/', views.criar_curso, name='criar_curso'),
    path('cursos/<uuid:curso_id>/editar/', views.editar_curso, name='editar_curso'),
    
    # === GESTÃO DE COORDENADORES ===
    path('coordenadores/', views.listar_coordenadores, name='listar_coordenadores'),
    path('coordenadores/criar/', views.criar_coordenador, name='criar_coordenador'),
    
    # === GESTÃO DE PROFESSORES ===
    path('professores/', views.listar_professores, name='listar_professores'),
    path('professores/criar/', views.criar_professor, name='criar_professor'),
    
    # === GESTÃO DE AVALIAÇÕES ===
    path('avaliacoes/', views.listar_avaliacoes, name='listar_avaliacoes'),
    path('avaliacoes/criar/', views.criar_avaliacao, name='criar_avaliacao'),
    path('avaliacoes/<uuid:avaliacao_id>/', views.detalhar_avaliacao, name='detalhar_avaliacao'),
    
    # === FORMULÁRIO PÚBLICO ===
    path('avaliar/<str:token>/', views.formulario_aluno, name='formulario_aluno'),
    
    # === DASHBOARDS ===
    path('dashboard/coordenacao/', views.dashboard_coordenacao, name='dashboard_coordenacao'),
    path('dashboard/professor/', views.dashboard_professor, name='dashboard_professor'),
    path('dashboard/diretoria/', views.dashboard_diretoria, name='dashboard_diretoria'),
    
    # === REDIRECIONAMENTO AUTOMÁTICO ===
    path('dashboard/redirect/', views.dashboard_redirect_by_profile, name='dashboard_redirect'),
    
    # === RELATÓRIOS ===
    path('relatorios/<uuid:avaliacao_id>/pdf/', views.exportar_relatorio_pdf, name='exportar_relatorio_pdf'),
    path('relatorios/<uuid:avaliacao_id>/excel/', views.exportar_relatorio_excel, name='exportar_relatorio_excel'),
    
    # === AJAX ===
    path('ajax/estatisticas/', views.ajax_estatisticas, name='ajax_estatisticas'),
    
    # === GERENCIAMENTO DE USUÁRIOS ===
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/senha/', views.alterar_senha_usuario, name='alterar_senha_usuario'),
    path('usuarios/<int:user_id>/desativar/', views.desativar_usuario, name='desativar_usuario'),
    
    # === PERFIL DO USUÁRIO ===
    path('meu-perfil/', views.meu_perfil, name='meu_perfil'),
    path('alterar-senha/', views.alterar_minha_senha, name='alterar_minha_senha'),
    
    # === CADASTRO PÚBLICO ===
    path('cadastro/', views.cadastro_publico, name='cadastro_publico'),
]