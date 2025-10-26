from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Curso, Coordenador, Professor, AvaliacaoConfig, 
    AvaliacaoResposta, RelatorioEstatisticas
)
from .forms import (
    AvaliacaoConfigForm, AvaliacaoRespostaForm,
    CursoForm, CoordenadorForm, ProfessorForm
)
from .utils import gerar_relatorio_pdf, gerar_relatorio_excel
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard_avaliacao(request):
    """Dashboard principal do sistema de avaliação"""
    
    # Estatísticas gerais
    total_cursos = Curso.objects.filter(ativo=True).count()
    total_coordenadores = Coordenador.objects.filter(ativo=True).count()
    total_professores = Professor.objects.filter(ativo=True).count()
    
    # Avaliações
    avaliacoes_ativas = AvaliacaoConfig.objects.filter(status='ativa').count()
    total_respostas = AvaliacaoResposta.objects.count()
    
    # Avaliações recentes
    avaliacoes_recentes = AvaliacaoConfig.objects.all().order_by('-data_criacao')[:10]
    
    # Respostas recentes
    respostas_recentes = AvaliacaoResposta.objects.all().order_by('-data_resposta')[:10]
    
    # Estatísticas por período
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    respostas_mes = AvaliacaoResposta.objects.filter(
        data_resposta__date__gte=inicio_mes
    ).count()
    
    # Médias gerais
    medias = AvaliacaoResposta.objects.aggregate(
        media_professor=Avg('nota_relacionamento_professor'),
        media_didatica=Avg('nota_didatica_professor'),
        media_dominio=Avg('nota_dominio_assunto'),
        media_teorico=Avg('nota_conteudo_teorico'),
        media_pratico=Avg('nota_atividade_pratica'),
        media_administracao=Avg('nota_portaria')
    )
    
    context = {
        'total_cursos': total_cursos,
        'total_coordenadores': total_coordenadores,
        'total_professores': total_professores,
        'avaliacoes_ativas': avaliacoes_ativas,
        'total_respostas': total_respostas,
        'respostas_mes': respostas_mes,
        'avaliacoes_recentes': avaliacoes_recentes,
        'respostas_recentes': respostas_recentes,
        'medias': medias,
    }
    
    return render(request, 'avaliacao_qualidade/dashboard_fatesa.html', context)


# === GESTÃO DE CURSOS ===

@login_required
def listar_cursos(request):
    """Lista todos os cursos"""
    
    cursos = Curso.objects.all().order_by('nome')
    
    # Filtros
    search = request.GET.get('search')
    if search:
        cursos = cursos.filter(
            Q(nome__icontains=search) |
            Q(codigo__icontains=search)
        )
    
    ativo_filter = request.GET.get('ativo')
    if ativo_filter is not None:
        cursos = cursos.filter(ativo=ativo_filter == 'true')
    
    # Paginação
    paginator = Paginator(cursos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'ativo_filter': ativo_filter,
    }
    
    return render(request, 'avaliacao_qualidade/cursos/listar.html', context)


@login_required
def criar_curso(request):
    """Cria um novo curso"""
    
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save()
            messages.success(request, f'Curso "{curso.nome}" criado com sucesso!')
            return redirect('avaliacao_qualidade:listar_cursos')
    else:
        form = CursoForm()
    
    return render(request, 'avaliacao_qualidade/cursos/criar.html', {'form': form})


@login_required
def editar_curso(request, curso_id):
    """Edita um curso existente"""
    
    curso = get_object_or_404(Curso, id=curso_id)
    
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            curso = form.save()
            messages.success(request, f'Curso "{curso.nome}" atualizado com sucesso!')
            return redirect('avaliacao_qualidade:listar_cursos')
    else:
        form = CursoForm(instance=curso)
    
    return render(request, 'avaliacao_qualidade/cursos/editar.html', {
        'form': form, 
        'curso': curso
    })


# === GESTÃO DE COORDENADORES ===

@login_required
def listar_coordenadores(request):
    """Lista todos os coordenadores"""
    
    coordenadores = Coordenador.objects.all().order_by('nome')
    
    # Filtros
    search = request.GET.get('search')
    if search:
        coordenadores = coordenadores.filter(nome__icontains=search)
    
    ativo_filter = request.GET.get('ativo')
    if ativo_filter is not None:
        coordenadores = coordenadores.filter(ativo=ativo_filter == 'true')
    
    # Paginação
    paginator = Paginator(coordenadores, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'ativo_filter': ativo_filter,
    }
    
    return render(request, 'avaliacao_qualidade/coordenadores/listar.html', context)


@login_required
def criar_coordenador(request):
    """Cria um novo coordenador"""
    
    if request.method == 'POST':
        form = CoordenadorForm(request.POST)
        if form.is_valid():
            coordenador = form.save()
            messages.success(request, f'Coordenador "{coordenador.nome}" criado com sucesso!')
            return redirect('avaliacao_qualidade:listar_coordenadores')
    else:
        form = CoordenadorForm()
    
    return render(request, 'avaliacao_qualidade/coordenadores/criar.html', {'form': form})


# === GESTÃO DE PROFESSORES ===

@login_required
def listar_professores(request):
    """Lista todos os professores"""
    
    professores = Professor.objects.all().order_by('nome')
    
    # Filtros
    search = request.GET.get('search')
    if search:
        professores = professores.filter(
            Q(nome__icontains=search) |
            Q(especialidade__icontains=search)
        )
    
    ativo_filter = request.GET.get('ativo')
    if ativo_filter is not None:
        professores = professores.filter(ativo=ativo_filter == 'true')
    
    # Paginação
    paginator = Paginator(professores, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'ativo_filter': ativo_filter,
    }
    
    return render(request, 'avaliacao_qualidade/professores/listar.html', context)


@login_required
def criar_professor(request):
    """Cria um novo professor"""
    
    if request.method == 'POST':
        form = ProfessorForm(request.POST)
        if form.is_valid():
            professor = form.save()
            messages.success(request, f'Professor "{professor.nome}" criado com sucesso!')
            return redirect('avaliacao_qualidade:listar_professores')
    else:
        form = ProfessorForm()
    
    return render(request, 'avaliacao_qualidade/professores/criar.html', {'form': form})


# === GESTÃO DE AVALIAÇÕES ===

@login_required
def listar_avaliacoes(request):
    """Lista todas as configurações de avaliação"""
    
    avaliacoes = AvaliacaoConfig.objects.all().order_by('-data_criacao')
    
    # Filtros
    search = request.GET.get('search')
    if search:
        avaliacoes = avaliacoes.filter(
            Q(curso__nome__icontains=search) |
            Q(turma__icontains=search) |
            Q(coordenador__nome__icontains=search)
        )
    
    status_filter = request.GET.get('status')
    if status_filter:
        avaliacoes = avaliacoes.filter(status=status_filter)
    
    # Paginação
    paginator = Paginator(avaliacoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
    }
    
    return render(request, 'avaliacao_qualidade/avaliacoes/listar.html', context)


@login_required
def criar_avaliacao(request):
    """Cria uma nova configuração de avaliação"""
    
    if request.method == 'POST':
        form = AvaliacaoConfigForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.criado_por = request.user
            avaliacao.save()
            form.save_m2m()  # Salva os professores (ManyToMany)
            
            # Gerar link
            link_completo = request.build_absolute_uri(avaliacao.get_link_avaliacao())
            
            messages.success(
                request, 
                f'Avaliação criada com sucesso! '
                f'Link gerado: <a href="{link_completo}" target="_blank">{link_completo}</a>'
            )
            return redirect('avaliacao_qualidade:detalhar_avaliacao', avaliacao_id=avaliacao.id)
    else:
        form = AvaliacaoConfigForm()
    
    # Buscar professores ativos
    professores = Professor.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'form': form,
        'professores': professores
    }
    
    return render(request, 'avaliacao_qualidade/avaliacoes/criar.html', context)


@login_required
def detalhar_avaliacao(request, avaliacao_id):
    """Detalha uma configuração de avaliação"""
    
    avaliacao = get_object_or_404(AvaliacaoConfig, id=avaliacao_id)
    
    # Respostas da avaliação
    respostas = avaliacao.respostas.all().order_by('-data_resposta')
    
    # Estatísticas
    if respostas.exists():
        stats = respostas.aggregate(
            media_professor=Avg('nota_relacionamento_professor'),
            media_didatica=Avg('nota_didatica_professor'),
            media_dominio=Avg('nota_dominio_assunto'),
            media_teorico=Avg('nota_conteudo_teorico'),
            media_pratico=Avg('nota_atividade_pratica'),
            media_administracao=Avg('nota_portaria')
        )
    else:
        stats = {}
    
    # Link completo
    link_completo = request.build_absolute_uri(avaliacao.get_link_avaliacao())
    
    context = {
        'avaliacao': avaliacao,
        'respostas': respostas,
        'stats': stats,
        'link_completo': link_completo,
    }
    
    return render(request, 'avaliacao_qualidade/avaliacoes/detalhar.html', context)


def formulario_aluno(request, token):
    """Formulário público para o aluno responder a avaliação"""
    
    # Buscar configuração da avaliação
    try:
        avaliacao_config = AvaliacaoConfig.objects.get(
            link_token=token,
            status='ativa'
        )
    except AvaliacaoConfig.DoesNotExist:
        return render(request, 'avaliacao_qualidade/formulario_erro.html', {
            'erro': 'Link de avaliação inválido ou expirado.'
        })
    
    if request.method == 'POST':
        form = AvaliacaoRespostaForm(request.POST)
        if form.is_valid():
            resposta = form.save(commit=False)
            resposta.avaliacao_config = avaliacao_config
            resposta.ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
            resposta.user_agent = request.META.get('HTTP_USER_AGENT', '')
            resposta.save()
            
            logger.info(f"Nova avaliação recebida para {avaliacao_config.curso.nome} - {avaliacao_config.turma}")
            
            return render(request, 'avaliacao_qualidade/formulario_sucesso.html', {
                'avaliacao_config': avaliacao_config
            })
    else:
        form = AvaliacaoRespostaForm()
    
    context = {
        'form': form,
        'avaliacao_config': avaliacao_config,
    }
    
    return render(request, 'avaliacao_qualidade/formulario_aluno.html', context)


# === RELATÓRIOS E DASHBOARDS ===

@login_required
def dashboard_coordenacao(request):
    """Dashboard para coordenadores"""
    
    # Verificar se o usuário é coordenador
    try:
        coordenador = request.user.coordenador_fatesa
    except:
        coordenador = None
    
    # Se não é coordenador, mostrar todos os dados (para admin)
    if coordenador:
        # Filtrar apenas avaliações dos cursos deste coordenador
        avaliacoes = AvaliacaoConfig.objects.filter(coordenador=coordenador)
    else:
        # Admin vê tudo
        avaliacoes = AvaliacaoConfig.objects.all()
    
    # Filtros
    curso_filter = request.GET.get('curso')
    if curso_filter:
        avaliacoes = avaliacoes.filter(curso_id=curso_filter)
    
    professor_filter = request.GET.get('professor')
    if professor_filter:
        avaliacoes = avaliacoes.filter(professores__id=professor_filter)
    
    periodo_filter = request.GET.get('periodo')
    if periodo_filter:
        if periodo_filter == '30':
            data_inicio = timezone.now() - timedelta(days=30)
            avaliacoes = avaliacoes.filter(data_criacao__gte=data_inicio)
        elif periodo_filter == '90':
            data_inicio = timezone.now() - timedelta(days=90)
            avaliacoes = avaliacoes.filter(data_criacao__gte=data_inicio)
    
    # Estatísticas
    total_avaliacoes = avaliacoes.count()
    total_respostas = AvaliacaoResposta.objects.filter(
        avaliacao_config__in=avaliacoes
    ).count()
    
    # Médias por curso
    cursos_stats = []
    for avaliacao in avaliacoes:
        respostas = avaliacao.respostas.all()
        if respostas.exists():
            stats = respostas.aggregate(
                media_geral=Avg('nota_relacionamento_professor'),
                total_respostas=Count('id')
            )
            cursos_stats.append({
                'curso': avaliacao.curso.nome,
                'turma': avaliacao.turma,
                'media_geral': stats['media_geral'],
                'total_respostas': stats['total_respostas'],
                'avaliacao_id': avaliacao.id
            })
    
    # Listas para filtros
    cursos = Curso.objects.filter(ativo=True).order_by('nome')
    professores = Professor.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'coordenador': coordenador,
        'total_avaliacoes': total_avaliacoes,
        'total_respostas': total_respostas,
        'cursos_stats': cursos_stats,
        'cursos': cursos,
        'professores': professores,
        'curso_filter': curso_filter,
        'professor_filter': professor_filter,
        'periodo_filter': periodo_filter,
    }
    
    return render(request, 'avaliacao_qualidade/dashboards/coordenacao.html', context)


@login_required
def dashboard_professor(request):
    """Dashboard para professores"""
    
    # Verificar se o usuário é professor
    try:
        professor = request.user.professor_fatesa
    except:
        professor = None
    
    if not professor:
        messages.error(request, 'Acesso restrito a professores.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    # Buscar avaliações onde este professor participou
    avaliacoes = AvaliacaoConfig.objects.filter(professores=professor)
    
    # Filtros
    periodo_filter = request.GET.get('periodo')
    if periodo_filter:
        if periodo_filter == '30':
            data_inicio = timezone.now() - timedelta(days=30)
            avaliacoes = avaliacoes.filter(data_criacao__gte=data_inicio)
        elif periodo_filter == '90':
            data_inicio = timezone.now() - timedelta(days=90)
            avaliacoes = avaliacoes.filter(data_criacao__gte=data_inicio)
    
    # Estatísticas do professor
    total_turmas = avaliacoes.count()
    total_respostas = AvaliacaoResposta.objects.filter(
        avaliacao_config__in=avaliacoes
    ).count()
    
    # Médias do professor
    respostas_professor = AvaliacaoResposta.objects.filter(
        avaliacao_config__in=avaliacoes
    )
    
    if respostas_professor.exists():
        medias = respostas_professor.aggregate(
            media_relacionamento=Avg('nota_relacionamento_professor'),
            media_didatica=Avg('nota_didatica_professor'),
            media_dominio=Avg('nota_dominio_assunto')
        )
    else:
        medias = {}
    
    # Avaliações por turma
    turmas_stats = []
    for avaliacao in avaliacoes:
        respostas = avaliacao.respostas.all()
        if respostas.exists():
            stats = respostas.aggregate(
                media_relacionamento=Avg('nota_relacionamento_professor'),
                media_didatica=Avg('nota_didatica_professor'),
                media_dominio=Avg('nota_dominio_assunto'),
                total_respostas=Count('id')
            )
            turmas_stats.append({
                'curso': avaliacao.curso.nome,
                'turma': avaliacao.turma,
                'coordenador': avaliacao.coordenador.nome,
                'stats': stats,
                'avaliacao_id': avaliacao.id
            })
    
    context = {
        'professor': professor,
        'total_turmas': total_turmas,
        'total_respostas': total_respostas,
        'medias': medias,
        'turmas_stats': turmas_stats,
        'periodo_filter': periodo_filter,
    }
    
    return render(request, 'avaliacao_qualidade/dashboards/professor.html', context)


@login_required
def dashboard_diretoria(request):
    """Dashboard para diretoria"""
    
    # Verificar permissão (apenas superuser ou staff)
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'Acesso restrito à diretoria.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    # Estatísticas gerais
    total_cursos = Curso.objects.filter(ativo=True).count()
    total_professores = Professor.objects.filter(ativo=True).count()
    total_avaliacoes = AvaliacaoConfig.objects.count()
    total_respostas = AvaliacaoResposta.objects.count()
    
    # Média geral institucional
    if total_respostas > 0:
        media_institucional = AvaliacaoResposta.objects.aggregate(
            media_geral=Avg('nota_relacionamento_professor')
        )['media_geral']
    else:
        media_institucional = 0
    
    # Ranking de cursos
    ranking_cursos = []
    for curso in Curso.objects.filter(ativo=True):
        respostas = AvaliacaoResposta.objects.filter(
            avaliacao_config__curso=curso
        )
        if respostas.exists():
            stats = respostas.aggregate(
                media_geral=Avg('nota_relacionamento_professor'),
                total_respostas=Count('id')
            )
            ranking_cursos.append({
                'curso': curso.nome,
                'media_geral': stats['media_geral'],
                'total_respostas': stats['total_respostas']
            })
    
    # Ordenar por média
    ranking_cursos.sort(key=lambda x: x['media_geral'] or 0, reverse=True)
    
    # Ranking de professores
    ranking_professores = []
    for professor in Professor.objects.filter(ativo=True):
        respostas = AvaliacaoResposta.objects.filter(
            avaliacao_config__professores=professor
        )
        if respostas.exists():
            stats = respostas.aggregate(
                media_relacionamento=Avg('nota_relacionamento_professor'),
                media_didatica=Avg('nota_didatica_professor'),
                media_dominio=Avg('nota_dominio_assunto'),
                total_respostas=Count('id')
            )
            media_professor = (
                (stats['media_relacionamento'] or 0) +
                (stats['media_didatica'] or 0) +
                (stats['media_dominio'] or 0)
            ) / 3
            
            ranking_professores.append({
                'professor': professor.nome,
                'media_geral': media_professor,
                'total_respostas': stats['total_respostas']
            })
    
    # Ordenar por média
    ranking_professores.sort(key=lambda x: x['media_geral'] or 0, reverse=True)
    
    # Alertas (notas < 7.0)
    alertas = []
    for resposta in AvaliacaoResposta.objects.all():
        if resposta.get_media_geral() < 7.0:
            alertas.append({
                'curso': resposta.avaliacao_config.curso.nome,
                'turma': resposta.avaliacao_config.turma,
                'media': resposta.get_media_geral(),
                'data': resposta.data_resposta
            })
    
    context = {
        'total_cursos': total_cursos,
        'total_professores': total_professores,
        'total_avaliacoes': total_avaliacoes,
        'total_respostas': total_respostas,
        'media_institucional': media_institucional,
        'ranking_cursos': ranking_cursos[:10],  # Top 10
        'ranking_professores': ranking_professores[:10],  # Top 10
        'alertas': alertas[:20],  # Últimos 20 alertas
    }
    
    return render(request, 'avaliacao_qualidade/dashboards/diretoria.html', context)


# === EXPORTAÇÃO DE RELATÓRIOS ===

@login_required
def exportar_relatorio_pdf(request, avaliacao_id):
    """Exporta relatório em PDF"""
    
    avaliacao = get_object_or_404(AvaliacaoConfig, id=avaliacao_id)
    
    try:
        pdf_content = gerar_relatorio_pdf(avaliacao)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_{avaliacao.curso.nome}_{avaliacao.turma}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        messages.error(request, 'Erro ao gerar relatório PDF.')
        return redirect('avaliacao_qualidade:detalhar_avaliacao', avaliacao_id=avaliacao_id)


@login_required
def exportar_relatorio_excel(request, avaliacao_id):
    """Exporta relatório em Excel"""
    
    avaliacao = get_object_or_404(AvaliacaoConfig, id=avaliacao_id)
    
    try:
        excel_content = gerar_relatorio_excel(avaliacao)
        
        response = HttpResponse(
            excel_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="relatorio_{avaliacao.curso.nome}_{avaliacao.turma}.xlsx"'
        
        return response
        
    except Exception as e:
        logger.error(f"Erro ao gerar Excel: {str(e)}")
        messages.error(request, 'Erro ao gerar relatório Excel.')
        return redirect('avaliacao_qualidade:detalhar_avaliacao', avaliacao_id=avaliacao_id)


# === AJAX ===

@login_required
def ajax_estatisticas(request):
    """Retorna estatísticas via AJAX"""
    
    periodo = request.GET.get('periodo', '30')
    
    if periodo == '30':
        data_inicio = timezone.now() - timedelta(days=30)
    elif periodo == '90':
        data_inicio = timezone.now() - timedelta(days=90)
    else:
        data_inicio = timezone.now() - timedelta(days=365)
    
    respostas = AvaliacaoResposta.objects.filter(
        data_resposta__gte=data_inicio
    )
    
    stats = {
        'total_respostas': respostas.count(),
        'media_geral': respostas.aggregate(
            media=Avg('nota_relacionamento_professor')
        )['media'] or 0,
        'respostas_por_dia': []
    }
    
    return JsonResponse(stats)


# === VIEWS DE GERENCIAMENTO DE USUÁRIOS ===

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .models import PerfilUsuario
from .forms import CadastroUsuarioForm, EditarUsuarioForm, AlterarSenhaForm


@login_required
def listar_usuarios(request):
    """Lista usuários do sistema FATESA da loja atual"""
    
    # Verificar permissão
    if not hasattr(request.user, 'perfil_fatesa') or not request.user.perfil_fatesa.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    # Identificar a loja atual
    loja_atual = None
    if hasattr(request.user, 'loja_admin'):
        loja_atual = request.user.loja_admin
    elif hasattr(request, 'loja_atual'):
        loja_atual = request.loja_atual
    
    # Filtros
    tipo_perfil = request.GET.get('tipo_perfil', '')
    ativo = request.GET.get('ativo', '')
    busca = request.GET.get('busca', '')
    
    # Query base - filtrar apenas usuários da loja atual
    if loja_atual:
        # Buscar usuários que são admin desta loja ou funcionários desta loja
        usuarios = User.objects.filter(
            Q(loja_admin=loja_atual) |  # Admin da loja
            Q(perfil_fatesa__isnull=False, perfil_fatesa__loja_associada=loja_atual)  # Funcionários da loja
        ).select_related('perfil_fatesa').distinct()
    else:
        # Se não conseguir identificar a loja, mostrar apenas o próprio usuário
        usuarios = User.objects.filter(id=request.user.id, perfil_fatesa__isnull=False).select_related('perfil_fatesa')
    
    # Aplicar filtros
    if tipo_perfil:
        usuarios = usuarios.filter(perfil_fatesa__tipo_perfil=tipo_perfil)
    
    if ativo == 'true':
        usuarios = usuarios.filter(perfil_fatesa__ativo=True)
    elif ativo == 'false':
        usuarios = usuarios.filter(perfil_fatesa__ativo=False)
    
    if busca:
        usuarios = usuarios.filter(
            Q(perfil_fatesa__nome_completo__icontains=busca) |
            Q(username__icontains=busca) |
            Q(email__icontains=busca)
        )
    
    # Ordenação
    usuarios = usuarios.order_by('perfil_fatesa__nome_completo')
    
    # Paginação
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipo_perfil_filter': tipo_perfil,
        'ativo_filter': ativo,
        'busca_filter': busca,
        'tipos_perfil': PerfilUsuario.TIPO_PERFIL_CHOICES,
        'total_usuarios': usuarios.count(),
    }
    
    return render(request, 'avaliacao_qualidade/usuarios/listar.html', context)


@login_required
def cadastrar_usuario(request):
    """Cadastra um novo usuário no sistema"""
    
    # Verificar permissão
    if not hasattr(request.user, 'perfil_fatesa') or not request.user.perfil_fatesa.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    # Identificar a loja atual
    loja_atual = None
    if hasattr(request.user, 'loja_admin'):
        loja_atual = request.user.loja_admin
    elif hasattr(request, 'loja_atual'):
        loja_atual = request.loja_atual
    
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(loja_associada=loja_atual)
                messages.success(request, f'Usuário {user.username} cadastrado com sucesso!')
                return redirect('avaliacao_qualidade:listar_usuarios')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar usuário: {str(e)}')
    else:
        form = CadastroUsuarioForm()
    
    context = {
        'form': form,
        'titulo': 'Cadastrar Usuário',
        'cursos': Curso.objects.filter(ativo=True),
    }
    
    return render(request, 'avaliacao_qualidade/usuarios/cadastrar.html', context)


@login_required
def editar_usuario(request, user_id):
    """Edita um usuário existente"""
    
    # Verificar permissão
    if not hasattr(request.user, 'perfil_fatesa') or not request.user.perfil_fatesa.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    user = get_object_or_404(User, id=user_id, perfil_fatesa__isnull=False)
    perfil = user.perfil_fatesa
    
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=user, perfil=perfil)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Usuário {user.username} atualizado com sucesso!')
                return redirect('avaliacao_qualidade:listar_usuarios')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar usuário: {str(e)}')
    else:
        form = EditarUsuarioForm(instance=user, perfil=perfil)
    
    context = {
        'form': form,
        'user_editado': user,
        'perfil': perfil,
        'titulo': f'Editar Usuário - {user.username}',
        'cursos': Curso.objects.filter(ativo=True),
    }
    
    return render(request, 'avaliacao_qualidade/usuarios/editar.html', context)


@login_required
def alterar_senha_usuario(request, user_id):
    """Altera a senha de um usuário (apenas diretoria)"""
    
    # Verificar permissão
    if not hasattr(request.user, 'perfil_fatesa') or not request.user.perfil_fatesa.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    user = get_object_or_404(User, id=user_id, perfil_fatesa__isnull=False)
    
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if nova_senha and nova_senha == confirmar_senha:
            user.set_password(nova_senha)
            user.save()
            messages.success(request, f'Senha do usuário {user.username} alterada com sucesso!')
            return redirect('avaliacao_qualidade:listar_usuarios')
        else:
            messages.error(request, 'As senhas não coincidem.')
    
    context = {
        'user_editado': user,
        'titulo': f'Alterar Senha - {user.username}',
    }
    
    return render(request, 'avaliacao_qualidade/usuarios/alterar_senha.html', context)


@login_required
def meu_perfil(request):
    """Permite ao usuário editar seu próprio perfil"""
    
    if not hasattr(request.user, 'perfil_fatesa'):
        messages.error(request, 'Perfil não encontrado.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    perfil = request.user.perfil_fatesa
    
    if request.method == 'POST':
        # Atualizar dados básicos
        nome_completo = request.POST.get('nome_completo')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        
        if nome_completo:
            perfil.nome_completo = nome_completo
            perfil.save()
            
            # Atualizar email do usuário
            if email and email != request.user.email:
                if not User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                    request.user.email = email
                    request.user.save()
                else:
                    messages.error(request, 'Este email já está em uso.')
                    return render(request, 'avaliacao_qualidade/usuarios/meu_perfil.html', {'perfil': perfil})
            
            if telefone:
                perfil.telefone = telefone
                perfil.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('avaliacao_qualidade:meu_perfil')
    
    context = {
        'perfil': perfil,
        'titulo': 'Meu Perfil',
    }
    
    return render(request, 'avaliacao_qualidade/usuarios/meu_perfil.html', context)


@login_required
def alterar_minha_senha(request):
    """Permite ao usuário alterar sua própria senha"""
    
    # Verificar se tem perfil FATESA
    if not hasattr(request.user, 'perfil_fatesa'):
        messages.error(request, 'Perfil não encontrado.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    perfil = request.user.perfil_fatesa
    primeira_alteracao = perfil.deve_alterar_senha
    
    if request.method == 'POST':
        form = AlterarSenhaForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            
            # Marcar que a senha foi alterada
            if primeira_alteracao:
                perfil.deve_alterar_senha = False
                perfil.save()
                messages.success(request, 'Senha alterada com sucesso! Agora você pode acessar o sistema normalmente.')
            else:
                messages.success(request, 'Senha alterada com sucesso!')
            
            return redirect('avaliacao_qualidade:dashboard_avaliacao')
    else:
        form = AlterarSenhaForm(request.user)
    
    context = {
        'form': form,
        'titulo': 'Alterar Senha' if primeira_alteracao else 'Alterar Minha Senha',
        'primeira_alteracao': primeira_alteracao,
    }
    
    return render(request, 'avaliacao_qualidade/usuarios/alterar_minha_senha.html', context)


@login_required
def desativar_usuario(request, user_id):
    """Desativa/ativa um usuário"""
    
    # Verificar permissão
    if not hasattr(request.user, 'perfil_fatesa') or not request.user.perfil_fatesa.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    
    user = get_object_or_404(User, id=user_id, perfil_fatesa__isnull=False)
    
    if request.method == 'POST':
        perfil = user.perfil_fatesa
        perfil.ativo = not perfil.ativo
        perfil.save()
        
        # Também desativar/ativar o usuário Django
        user.is_active = perfil.ativo
        user.save()
        
        status = 'ativado' if perfil.ativo else 'desativado'
        messages.success(request, f'Usuário {user.username} {status} com sucesso!')
    
    return redirect('avaliacao_qualidade:listar_usuarios')


def cadastro_publico(request):
    """Página de cadastro público (se habilitada)"""
    
    # Esta view pode ser usada para permitir auto-cadastro
    # Por enquanto, redireciona para login
    messages.info(request, 'Entre em contato com a administração para criar sua conta.')
    return redirect('login')


# === DASHBOARDS ESPECÍFICOS POR PERFIL ===

from django.contrib.auth.decorators import user_passes_test


def is_diretoria(user):
    """Verifica se o usuário pertence ao grupo Diretoria"""
    return user.groups.filter(name='Avaliacao_Diretoria').exists()


def is_coordenacao(user):
    """Verifica se o usuário pertence ao grupo Coordenação"""
    return user.groups.filter(name='Avaliacao_Coordenacao').exists()


def is_professor(user):
    """Verifica se o usuário pertence ao grupo Professor"""
    return user.groups.filter(name='Avaliacao_Professor').exists()


def is_admin_completo(user):
    """Verifica se o usuário pertence ao grupo Admin Completo"""
    return user.groups.filter(name='Admin_Completo').exists()


@login_required
@user_passes_test(is_diretoria, login_url='/avaliacao-qualidade/')
def dashboard_diretoria(request):
    """Dashboard específico para Diretoria - Visão estratégica e relatórios gerais"""
    
    # Estatísticas gerais para diretoria
    total_cursos = Curso.objects.filter(ativo=True).count()
    total_coordenadores = Coordenador.objects.filter(ativo=True).count()
    total_professores = Professor.objects.filter(ativo=True).count()
    total_avaliacoes = AvaliacaoConfig.objects.count()
    total_respostas = AvaliacaoResposta.objects.count()
    
    # Médias institucionais
    medias_institucionais = AvaliacaoResposta.objects.aggregate(
        media_relacionamento=Avg('nota_relacionamento_professor'),
        media_didatica=Avg('nota_didatica_professor'),
        media_dominio=Avg('nota_dominio_assunto'),
        media_teorico=Avg('nota_conteudo_teorico'),
        media_pratico=Avg('nota_atividade_pratica'),
        media_administracao=Avg('nota_portaria')
    )
    
    # Calcular média geral institucional
    medias_valores = [v for v in medias_institucionais.values() if v is not None]
    media_geral_institucional = sum(medias_valores) / len(medias_valores) if medias_valores else 0
    
    # Ranking de cursos por média
    ranking_cursos = []
    for curso in Curso.objects.filter(ativo=True):
        avaliacoes_curso = AvaliacaoConfig.objects.filter(curso=curso)
        if avaliacoes_curso.exists():
            respostas_curso = AvaliacaoResposta.objects.filter(avaliacao_config__in=avaliacoes_curso)
            if respostas_curso.exists():
                media_curso = respostas_curso.aggregate(
                    media=Avg('nota_relacionamento_professor')
                )['media'] or 0
                
                ranking_cursos.append({
                    'curso': curso.nome,
                    'media': media_curso,
                    'total_avaliacoes': respostas_curso.count()
                })
    
    ranking_cursos.sort(key=lambda x: x['media'], reverse=True)
    
    # Alertas críticos (médias abaixo de 6.0)
    alertas_criticos = []
    for resposta in AvaliacaoResposta.objects.all():
        media_resposta = resposta.get_media_geral()
        if media_resposta < 6.0:
            alertas_criticos.append({
                'curso': resposta.avaliacao_config.curso.nome,
                'turma': resposta.avaliacao_config.turma,
                'professor': resposta.avaliacao_config.professor.nome if resposta.avaliacao_config.professor else 'N/A',
                'media': media_resposta,
                'data': resposta.data_resposta
            })
    
    # Estatísticas por período (últimos 30 dias)
    data_limite = timezone.now() - timedelta(days=30)
    respostas_recentes = AvaliacaoResposta.objects.filter(data_resposta__gte=data_limite)
    
    context = {
        'titulo_dashboard': 'Dashboard Diretoria',
        'perfil_usuario': 'Diretoria',
        'total_cursos': total_cursos,
        'total_coordenadores': total_coordenadores,
        'total_professores': total_professores,
        'total_avaliacoes': total_avaliacoes,
        'total_respostas': total_respostas,
        'media_geral_institucional': round(media_geral_institucional, 2),
        'medias_institucionais': medias_institucionais,
        'ranking_cursos': ranking_cursos[:10],  # Top 10
        'alertas_criticos': alertas_criticos[:10],  # 10 mais críticos
        'respostas_mes_atual': respostas_recentes.count(),
        'pode_exportar': True,
        'pode_visualizar_todos': True,
    }
    
    return render(request, 'avaliacao_qualidade/dashboards/diretoria.html', context)


@login_required
@user_passes_test(is_coordenacao, login_url='/avaliacao-qualidade/')
def dashboard_coordenacao(request):
    """Dashboard específico para Coordenação - Gestão de cursos e professores"""
    
    # Estatísticas para coordenação
    total_cursos = Curso.objects.filter(ativo=True).count()
    total_professores = Professor.objects.filter(ativo=True).count()
    avaliacoes_ativas = AvaliacaoConfig.objects.filter(status='ativa').count()
    
    # Cursos sob responsabilidade (todos os cursos para coordenação)
    cursos_responsabilidade = Curso.objects.filter(ativo=True)
    
    # Avaliações recentes dos cursos
    avaliacoes_recentes = AvaliacaoConfig.objects.filter(
        curso__in=cursos_responsabilidade
    ).order_by('-data_criacao')[:10]
    
    # Professores que precisam de atenção (média < 7.0)
    professores_atencao = []
    for professor in Professor.objects.filter(ativo=True):
        avaliacoes_professor = AvaliacaoConfig.objects.filter(professor=professor)
        if avaliacoes_professor.exists():
            respostas_professor = AvaliacaoResposta.objects.filter(
                avaliacao_config__in=avaliacoes_professor
            )
            if respostas_professor.exists():
                media_professor = respostas_professor.aggregate(
                    media=Avg('nota_relacionamento_professor')
                )['media'] or 0
                
                if media_professor < 7.0:
                    professores_atencao.append({
                        'professor': professor.nome,
                        'media': media_professor,
                        'total_avaliacoes': respostas_professor.count()
                    })
    
    # Estatísticas por curso
    estatisticas_cursos = []
    for curso in cursos_responsabilidade:
        avaliacoes_curso = AvaliacaoConfig.objects.filter(curso=curso)
        respostas_curso = AvaliacaoResposta.objects.filter(avaliacao_config__in=avaliacoes_curso)
        
        if respostas_curso.exists():
            media_curso = respostas_curso.aggregate(
                media=Avg('nota_relacionamento_professor')
            )['media'] or 0
            
            estatisticas_cursos.append({
                'curso': curso.nome,
                'total_avaliacoes': avaliacoes_curso.count(),
                'total_respostas': respostas_curso.count(),
                'media': media_curso,
                'status': 'Bom' if media_curso >= 8.0 else 'Atenção' if media_curso >= 6.0 else 'Crítico'
            })
    
    context = {
        'titulo_dashboard': 'Dashboard Coordenação',
        'perfil_usuario': 'Coordenação',
        'total_cursos': total_cursos,
        'total_professores': total_professores,
        'avaliacoes_ativas': avaliacoes_ativas,
        'cursos_responsabilidade': cursos_responsabilidade.count(),
        'avaliacoes_recentes': avaliacoes_recentes,
        'professores_atencao': professores_atencao,
        'estatisticas_cursos': estatisticas_cursos,
        'pode_criar_avaliacoes': True,
        'pode_gerenciar_professores': True,
        'pode_gerenciar_cursos': True,
    }
    
    return render(request, 'avaliacao_qualidade/dashboards/coordenacao.html', context)


@login_required
@user_passes_test(is_professor, login_url='/avaliacao-qualidade/')
def dashboard_professor(request):
    """Dashboard específico para Professor - Visualização das próprias avaliações"""
    
    # Tentar encontrar o professor associado ao usuário
    professor_atual = None
    try:
        # Assumindo que existe uma relação entre User e Professor
        # Isso pode precisar ser ajustado baseado na estrutura real do modelo
        professor_atual = Professor.objects.filter(
            # Aqui você precisa definir como associar o usuário ao professor
            # Por exemplo, se houver um campo user no modelo Professor:
            # user=request.user
            # Ou se for por email:
            email=request.user.email
        ).first()
    except:
        pass
    
    if not professor_atual:
        # Se não encontrar o professor, mostrar mensagem
        context = {
            'titulo_dashboard': 'Dashboard Professor',
            'perfil_usuario': 'Professor',
            'professor_nao_encontrado': True,
            'mensagem': 'Perfil de professor não encontrado. Entre em contato com a coordenação.'
        }
        return render(request, 'avaliacao_qualidade/dashboards/professor.html', context)
    
    # Avaliações do professor
    avaliacoes_professor = AvaliacaoConfig.objects.filter(professor=professor_atual)
    total_avaliacoes = avaliacoes_professor.count()
    
    # Respostas às avaliações
    respostas_professor = AvaliacaoResposta.objects.filter(
        avaliacao_config__in=avaliacoes_professor
    )
    total_respostas = respostas_professor.count()
    
    # Médias do professor
    medias_professor = respostas_professor.aggregate(
        media_relacionamento=Avg('nota_relacionamento_professor'),
        media_didatica=Avg('nota_didatica_professor'),
        media_dominio=Avg('nota_dominio_assunto'),
        media_teorico=Avg('nota_conteudo_teorico'),
        media_pratico=Avg('nota_atividade_pratica')
    )
    
    # Calcular média geral
    medias_valores = [v for v in medias_professor.values() if v is not None]
    media_geral = sum(medias_valores) / len(medias_valores) if medias_valores else 0
    
    # Avaliações por curso
    avaliacoes_por_curso = []
    cursos_professor = Curso.objects.filter(
        avaliacaoconfig__professor=professor_atual
    ).distinct()
    
    for curso in cursos_professor:
        avaliacoes_curso = avaliacoes_professor.filter(curso=curso)
        respostas_curso = respostas_professor.filter(avaliacao_config__in=avaliacoes_curso)
        
        if respostas_curso.exists():
            media_curso = respostas_curso.aggregate(
                media=Avg('nota_relacionamento_professor')
            )['media'] or 0
            
            avaliacoes_por_curso.append({
                'curso': curso.nome,
                'total_avaliacoes': avaliacoes_curso.count(),
                'total_respostas': respostas_curso.count(),
                'media': media_curso,
                'ultima_avaliacao': avaliacoes_curso.order_by('-data_criacao').first()
            })
    
    # Evolução temporal (últimos 6 meses)
    evolucao_temporal = []
    for i in range(6):
        data_inicio = timezone.now() - timedelta(days=30 * (i + 1))
        data_fim = timezone.now() - timedelta(days=30 * i)
        
        respostas_periodo = respostas_professor.filter(
            data_resposta__gte=data_inicio,
            data_resposta__lt=data_fim
        )
        
        if respostas_periodo.exists():
            media_periodo = respostas_periodo.aggregate(
                media=Avg('nota_relacionamento_professor')
            )['media'] or 0
            
            evolucao_temporal.append({
                'periodo': f'{data_inicio.strftime("%m/%Y")}',
                'media': media_periodo,
                'total_respostas': respostas_periodo.count()
            })
    
    evolucao_temporal.reverse()  # Ordem cronológica
    
    context = {
        'titulo_dashboard': 'Dashboard Professor',
        'perfil_usuario': 'Professor',
        'professor_atual': professor_atual,
        'total_avaliacoes': total_avaliacoes,
        'total_respostas': total_respostas,
        'media_geral': round(media_geral, 2),
        'medias_professor': medias_professor,
        'avaliacoes_por_curso': avaliacoes_por_curso,
        'evolucao_temporal': evolucao_temporal,
        'avaliacoes_recentes': avaliacoes_professor.order_by('-data_criacao')[:5],
        'pode_visualizar_proprias': True,
    }
    
    return render(request, 'avaliacao_qualidade/dashboards/professor.html', context)


# === MIDDLEWARE DE REDIRECIONAMENTO BASEADO EM PERFIL ===

def dashboard_redirect_by_profile(request):
    """Redireciona para o dashboard apropriado baseado no perfil do usuário"""
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Verificar grupos do usuário e redirecionar para o dashboard apropriado
    if request.user.groups.filter(name='Admin_Completo').exists():
        # Admin completo pode escolher ou ir para dashboard geral
        return redirect('avaliacao_qualidade:dashboard_avaliacao')
    elif request.user.groups.filter(name='Avaliacao_Diretoria').exists():
        return redirect('avaliacao_qualidade:dashboard_diretoria')
    elif request.user.groups.filter(name='Avaliacao_Coordenacao').exists():
        return redirect('avaliacao_qualidade:dashboard_coordenacao')
    elif request.user.groups.filter(name='Avaliacao_Professor').exists():
        return redirect('avaliacao_qualidade:dashboard_professor')
    else:
        # Se não tem grupo específico, vai para dashboard geral
        return redirect('avaliacao_qualidade:dashboard_avaliacao')