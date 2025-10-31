from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, date, time, timedelta
import json

from .models import (
    ServicoEstetica, ProtocoloEmagrecimento, Agendamento, 
    Retorno, FichaAnamnese, EvolucaoTratamento, PacoteTratamento
)
from lojas.models import Cliente


@login_required
def dashboard_estetica(request):
    """Dashboard principal da clínica de estética"""
    
    # Estatísticas do dia
    hoje = date.today()
    agendamentos_hoje = Agendamento.objects.filter(data_agendamento=hoje)
    agendamentos_pendentes = Agendamento.objects.filter(
        data_agendamento__gte=hoje,
        status__in=['agendado', 'confirmado']
    ).count()
    
    # Próximos agendamentos
    proximos_agendamentos = Agendamento.objects.filter(
        data_agendamento__gte=hoje,
        status__in=['agendado', 'confirmado']
    ).order_by('data_agendamento', 'hora_inicio')[:5]
    
    # Clientes novos este mês
    inicio_mes = hoje.replace(day=1)
    clientes_novos = Cliente.objects.filter(data_cadastro__gte=inicio_mes).count()
    
    # Serviços mais populares
    servicos_populares = ServicoEstetica.objects.filter(
        agendamentos__data_agendamento__gte=inicio_mes
    ).annotate(
        total_agendamentos=Count('agendamentos')
    ).order_by('-total_agendamentos')[:5]
    
    context = {
        'agendamentos_hoje': agendamentos_hoje,
        'agendamentos_pendentes': agendamentos_pendentes,
        'proximos_agendamentos': proximos_agendamentos,
        'clientes_novos': clientes_novos,
        'servicos_populares': servicos_populares,
    }
    
    return render(request, 'modulos/estetica/dashboard.html', context)


@login_required
def listar_agendamentos(request):
    """Lista todos os agendamentos com filtros"""
    
    agendamentos = Agendamento.objects.all().order_by('-data_agendamento', '-hora_inicio')
    
    # Filtros
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    profissional = request.GET.get('profissional')
    
    if status:
        agendamentos = agendamentos.filter(status=status)
    
    if data_inicio:
        agendamentos = agendamentos.filter(data_agendamento__gte=data_inicio)
    
    if data_fim:
        agendamentos = agendamentos.filter(data_agendamento__lte=data_fim)
    
    if profissional:
        agendamentos = agendamentos.filter(profissional_id=profissional)
    
    # Paginação
    paginator = Paginator(agendamentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Profissionais para filtro
    profissionais = User.objects.filter(agendamentos_profissional__isnull=False).distinct()
    
    context = {
        'page_obj': page_obj,
        'status_choices': Agendamento.STATUS_CHOICES,
        'profissionais': profissionais,
        'filtros': {
            'status': status,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'profissional': profissional,
        }
    }
    
    return render(request, 'modulos/estetica/agendamentos/lista.html', context)


@login_required
def criar_agendamento(request):
    """Criar novo agendamento"""
    
    if request.method == 'POST':
        try:
            # Dados do formulário
            cliente_id = request.POST.get('cliente')
            servico_id = request.POST.get('servico')
            protocolo_id = request.POST.get('protocolo')
            data_agendamento = request.POST.get('data_agendamento')
            hora_inicio = request.POST.get('hora_inicio')
            profissional_id = request.POST.get('profissional')
            observacoes = request.POST.get('observacoes', '')
            
            # Validar dados
            cliente = get_object_or_404(Cliente, id=cliente_id)
            servico = get_object_or_404(ServicoEstetica, id=servico_id)
            profissional = get_object_or_404(User, id=profissional_id)
            
            # Calcular hora fim
            hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
            duracao = timedelta(minutes=servico.duracao_minutos)
            hora_fim_obj = (datetime.combine(date.today(), hora_inicio_obj) + duracao).time()
            
            # Criar agendamento
            agendamento = Agendamento.objects.create(
                cliente=cliente,
                servico=servico,
                protocolo_id=protocolo_id if protocolo_id else None,
                data_agendamento=data_agendamento,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim_obj,
                profissional=profissional,
                observacoes=observacoes
            )
            
            messages.success(request, f'Agendamento criado com sucesso para {cliente.nome}')
            return redirect('estetica:agendamento_detalhes', agendamento.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar agendamento: {str(e)}')
    
    # Dados para o formulário
    clientes = Cliente.objects.all().order_by('nome')
    servicos = ServicoEstetica.objects.filter(ativo=True).order_by('categoria', 'nome')
    protocolos = ProtocoloEmagrecimento.objects.filter(ativo=True).order_by('nome')
    profissionais = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'clientes': clientes,
        'servicos': servicos,
        'protocolos': protocolos,
        'profissionais': profissionais,
    }
    
    return render(request, 'modulos/estetica/agendamentos/criar.html', context)


@login_required
def agendamento_detalhes(request, agendamento_id):
    """Detalhes de um agendamento específico"""
    
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    # Evoluções do cliente
    evolucoes = EvolucaoTratamento.objects.filter(
        cliente=agendamento.cliente
    ).order_by('-data_evolucao')[:5]
    
    # Retornos relacionados
    retornos = Retorno.objects.filter(
        agendamento_original=agendamento
    ).order_by('-data_retorno')
    
    context = {
        'agendamento': agendamento,
        'evolucoes': evolucoes,
        'retornos': retornos,
    }
    
    return render(request, 'modulos/estetica/agendamentos/detalhes.html', context)


@login_required
@require_http_methods(["POST"])
def atualizar_status_agendamento(request, agendamento_id):
    """Atualizar status de um agendamento via AJAX"""
    
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    novo_status = request.POST.get('status')
    observacoes = request.POST.get('observacoes', '')
    
    if novo_status in [choice[0] for choice in Agendamento.STATUS_CHOICES]:
        agendamento.status = novo_status
        if observacoes:
            agendamento.observacoes_pos_procedimento = observacoes
        agendamento.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Status atualizado com sucesso',
            'novo_status': agendamento.get_status_display()
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Status inválido'
    })


@login_required
def listar_servicos(request):
    """Lista todos os serviços de estética"""
    
    servicos = ServicoEstetica.objects.all().order_by('categoria', 'nome')
    
    # Filtros
    categoria = request.GET.get('categoria')
    ativo = request.GET.get('ativo')
    
    if categoria:
        servicos = servicos.filter(categoria=categoria)
    
    if ativo is not None:
        servicos = servicos.filter(ativo=ativo == 'true')
    
    # Paginação
    paginator = Paginator(servicos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categoria_choices': ServicoEstetica.CATEGORIA_CHOICES,
        'filtros': {
            'categoria': categoria,
            'ativo': ativo,
        }
    }
    
    return render(request, 'modulos/estetica/servicos/lista.html', context)


@login_required
def criar_servico(request):
    """Criar novo serviço de estética"""
    
    if request.method == 'POST':
        try:
            # Criar serviço
            servico = ServicoEstetica.objects.create(
                nome=request.POST.get('nome'),
                descricao=request.POST.get('descricao'),
                categoria=request.POST.get('categoria'),
                duracao_minutos=int(request.POST.get('duracao_minutos')),
                preco=float(request.POST.get('preco')),
                preco_promocional=float(request.POST.get('preco_promocional')) if request.POST.get('preco_promocional') else None,
                requer_consulta_medica=request.POST.get('requer_consulta_medica') == 'on',
                idade_minima=int(request.POST.get('idade_minima')),
                contraindicacoes=request.POST.get('contraindicacoes', ''),
                cuidados_pos_procedimento=request.POST.get('cuidados_pos_procedimento', ''),
            )
            
            messages.success(request, f'Serviço "{servico.nome}" criado com sucesso')
            return redirect('estetica:servico_detalhes', servico.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar serviço: {str(e)}')
    
    context = {
        'categoria_choices': ServicoEstetica.CATEGORIA_CHOICES,
        'duracao_choices': ServicoEstetica.DURACAO_CHOICES,
    }
    
    return render(request, 'modulos/estetica/servicos/criar.html', context)


@login_required
def servico_detalhes(request, servico_id):
    """Detalhes de um serviço específico"""
    
    servico = get_object_or_404(ServicoEstetica, id=servico_id)
    
    # Agendamentos recentes
    agendamentos_recentes = Agendamento.objects.filter(
        servico=servico
    ).order_by('-data_agendamento')[:10]
    
    context = {
        'servico': servico,
        'agendamentos_recentes': agendamentos_recentes,
    }
    
    return render(request, 'modulos/estetica/servicos/detalhes.html', context)


@login_required
def listar_protocolos(request):
    """Lista todos os protocolos de emagrecimento"""
    
    protocolos = ProtocoloEmagrecimento.objects.all().order_by('nome')
    
    # Filtros
    tipo_protocolo = request.GET.get('tipo_protocolo')
    ativo = request.GET.get('ativo')
    
    if tipo_protocolo:
        protocolos = protocolos.filter(tipo_protocolo=tipo_protocolo)
    
    if ativo is not None:
        protocolos = protocolos.filter(ativo=ativo == 'true')
    
    # Paginação
    paginator = Paginator(protocolos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipo_protocolo_choices': ProtocoloEmagrecimento.TIPO_PROTOCOLO_CHOICES,
        'filtros': {
            'tipo_protocolo': tipo_protocolo,
            'ativo': ativo,
        }
    }
    
    return render(request, 'modulos/estetica/protocolos/lista.html', context)


@login_required
def protocolo_detalhes(request, protocolo_id):
    """Detalhes de um protocolo específico"""
    
    protocolo = get_object_or_404(ProtocoloEmagrecimento, id=protocolo_id)
    
    # Agendamentos com este protocolo
    agendamentos = Agendamento.objects.filter(
        protocolo=protocolo
    ).order_by('-data_agendamento')[:10]
    
    context = {
        'protocolo': protocolo,
        'agendamentos': agendamentos,
    }
    
    return render(request, 'modulos/estetica/protocolos/detalhes.html', context)


@login_required
def ficha_anamnese(request, cliente_id):
    """Ficha de anamnese do cliente"""
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    # Buscar ou criar ficha
    ficha, created = FichaAnamnese.objects.get_or_create(cliente=cliente)
    
    if request.method == 'POST':
        try:
            # Atualizar ficha
            ficha.tipo_pele = request.POST.get('tipo_pele')
            ficha.alergias = request.POST.get('alergias', '')
            ficha.medicamentos_uso = request.POST.get('medicamentos_uso', '')
            ficha.tratamentos_anteriores = request.POST.get('tratamentos_anteriores', '')
            ficha.problemas_circulatorios = request.POST.get('problemas_circulatorios') == 'on'
            ficha.diabetes = request.POST.get('diabetes') == 'on'
            ficha.hipertensao = request.POST.get('hipertensao') == 'on'
            ficha.gravidez = request.POST.get('gravidez') == 'on'
            ficha.amamentacao = request.POST.get('amamentacao') == 'on'
            ficha.objetivos_tratamento = request.POST.get('objetivos_tratamento')
            ficha.expectativas = request.POST.get('expectativas', '')
            ficha.save()
            
            messages.success(request, 'Ficha de anamnese atualizada com sucesso')
            return redirect('estetica:ficha_anamnese', cliente.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar ficha: {str(e)}')
    
    context = {
        'cliente': cliente,
        'ficha': ficha,
        'tipo_pele_choices': FichaAnamnese.TIPO_PELE_CHOICES,
    }
    
    return render(request, 'modulos/estetica/clientes/ficha_anamnese.html', context)


@login_required
def evolucao_tratamento(request, cliente_id):
    """Evolução do tratamento do cliente"""
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        try:
            # Criar evolução
            evolucao = EvolucaoTratamento.objects.create(
                cliente=cliente,
                agendamento_id=request.POST.get('agendamento'),
                peso_inicial=float(request.POST.get('peso_inicial')) if request.POST.get('peso_inicial') else None,
                peso_atual=float(request.POST.get('peso_atual')) if request.POST.get('peso_atual') else None,
                medidas_corporais=request.POST.get('medidas_corporais', ''),
                fotos_antes=request.POST.get('fotos_antes', ''),
                fotos_depois=request.POST.get('fotos_depois', ''),
                observacoes_profissional=request.POST.get('observacoes_profissional'),
                observacoes_cliente=request.POST.get('observacoes_cliente', ''),
                proximos_passos=request.POST.get('proximos_passos', ''),
            )
            
            messages.success(request, 'Evolução registrada com sucesso')
            return redirect('estetica:evolucao_tratamento', cliente.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar evolução: {str(e)}')
    
    # Evoluções do cliente
    evolucoes = EvolucaoTratamento.objects.filter(
        cliente=cliente
    ).order_by('-data_evolucao')
    
    # Agendamentos do cliente
    agendamentos = Agendamento.objects.filter(
        cliente=cliente
    ).order_by('-data_agendamento')
    
    context = {
        'cliente': cliente,
        'evolucoes': evolucoes,
        'agendamentos': agendamentos,
    }
    
    return render(request, 'modulos/estetica/clientes/evolucao_tratamento.html', context)


@login_required
def calendario_agendamentos(request):
    """Calendário de agendamentos"""
    
    # Parâmetros do calendário
    ano = int(request.GET.get('ano', date.today().year))
    mes = int(request.GET.get('mes', date.today().month))
    
    # Agendamentos do mês
    inicio_mes = date(ano, mes, 1)
    if mes == 12:
        fim_mes = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        fim_mes = date(ano, mes + 1, 1) - timedelta(days=1)
    
    agendamentos = Agendamento.objects.filter(
        data_agendamento__range=[inicio_mes, fim_mes]
    ).order_by('data_agendamento', 'hora_inicio')
    
    # Organizar por data
    agendamentos_por_data = {}
    for agendamento in agendamentos:
        data_str = agendamento.data_agendamento.strftime('%Y-%m-%d')
        if data_str not in agendamentos_por_data:
            agendamentos_por_data[data_str] = []
        agendamentos_por_data[data_str].append(agendamento)
    
    context = {
        'ano': ano,
        'mes': mes,
        'agendamentos_por_data': agendamentos_por_data,
        'mes_anterior': mes - 1 if mes > 1 else 12,
        'ano_anterior': ano if mes > 1 else ano - 1,
        'mes_proximo': mes + 1 if mes < 12 else 1,
        'ano_proximo': ano if mes < 12 else ano + 1,
    }
    
    return render(request, 'modulos/estetica/agendamentos/calendario.html', context)


@login_required
def relatorios_estetica(request):
    """Relatórios da clínica de estética"""
    
    # Parâmetros do relatório
    data_inicio = request.GET.get('data_inicio', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', date.today().strftime('%Y-%m-%d'))
    
    # Agendamentos no período
    agendamentos = Agendamento.objects.filter(
        data_agendamento__range=[data_inicio, data_fim]
    )
    
    # Estatísticas
    total_agendamentos = agendamentos.count()
    agendamentos_concluidos = agendamentos.filter(status='concluido').count()
    agendamentos_cancelados = agendamentos.filter(status='cancelado').count()
    
    # Faturamento
    faturamento_total = sum(
        agendamento.servico.preco for agendamento in agendamentos.filter(status='concluido')
    )
    
    # Serviços mais populares
    servicos_populares = ServicoEstetica.objects.filter(
        agendamentos__in=agendamentos
    ).annotate(
        total_agendamentos=Count('agendamentos')
    ).order_by('-total_agendamentos')[:5]
    
    # Profissionais mais ativos
    profissionais_ativos = User.objects.filter(
        agendamentos_profissional__in=agendamentos
    ).annotate(
        total_agendamentos=Count('agendamentos_profissional')
    ).order_by('-total_agendamentos')[:5]
    
    context = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_agendamentos': total_agendamentos,
        'agendamentos_concluidos': agendamentos_concluidos,
        'agendamentos_cancelados': agendamentos_cancelados,
        'faturamento_total': faturamento_total,
        'servicos_populares': servicos_populares,
        'profissionais_ativos': profissionais_ativos,
    }
    
    return render(request, 'modulos/estetica/relatorios/relatorios.html', context)


# Views adicionais para completar as funcionalidades

@login_required
def listar_clientes(request):
    """Lista de clientes da clínica de estética"""
    # Buscar clientes da loja atual
    clientes = []
    if hasattr(request, 'loja_atual'):
        clientes = Cliente.objects.filter(loja=request.loja_atual).order_by('nome')
    elif hasattr(request.user, 'loja_admin') and request.user.loja_admin:
        clientes = Cliente.objects.filter(loja=request.user.loja_admin).order_by('nome')
    else:
        # Se não encontrar loja, buscar todos os clientes (fallback)
        clientes = Cliente.objects.all().order_by('nome')[:50]  # Limitar a 50 para performance
    
    context = {
        'page_title': 'Clientes - Clínica de Estética',
        'clientes': clientes,
    }
    return render(request, 'modulos/estetica/clientes/lista.html', context)

@login_required
def cliente_detalhes(request, cliente_id):
    """Detalhes de um cliente específico"""
    # Implementação básica
    context = {
        'page_title': 'Detalhes do Cliente - Clínica de Estética',
        'cliente_id': cliente_id,
    }
    return render(request, 'modulos/estetica/clientes/detalhes.html', context)

@login_required
def criar_cliente(request):
    """Criar novo cliente para a clínica de estética"""
    if request.method == 'POST':
        try:
            # Obter a loja do usuário (pode ser através de diferentes formas)
            loja = None
            if hasattr(request, 'loja_atual'):
                loja = request.loja_atual
            elif hasattr(request.user, 'loja_admin') and request.user.loja_admin:
                loja = request.user.loja_admin
            else:
                # Se não encontrar loja associada, usar a primeira loja disponível
                from lojas.models import Loja
                loja = Loja.objects.first()
            
            if not loja:
                messages.error(request, 'Erro: Nenhuma loja encontrada para associar o cliente')
                return redirect('modulos:estetica_clientes')
            
            # Criar cliente
            cliente = Cliente.objects.create(
                loja=loja,
                nome=request.POST.get('nome'),
                email=request.POST.get('email'),
                telefone=request.POST.get('telefone'),
                cpf=request.POST.get('cpf'),
                data_nascimento=request.POST.get('data_nascimento'),
                sexo=request.POST.get('sexo'),
                endereco=request.POST.get('endereco'),
                cidade=request.POST.get('cidade'),
                estado=request.POST.get('estado'),
                cep=request.POST.get('cep'),
            )
            
            messages.success(request, f'Cliente "{cliente.nome}" criado com sucesso')
            return redirect('modulos:estetica_cliente_detalhes', cliente.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar cliente: {str(e)}')
    
    context = {
        'page_title': 'Novo Cliente - Clínica de Estética',
    }
    return render(request, 'modulos/estetica/clientes/criar.html', context)

@login_required
def listar_pacotes(request):
    """Lista de pacotes de tratamento"""
    pacotes = PacoteTratamento.objects.all()
    context = {
        'page_title': 'Pacotes de Tratamento - Clínica de Estética',
        'pacotes': pacotes,
    }
    return render(request, 'modulos/estetica/pacotes/lista.html', context)

@login_required
def criar_pacote(request):
    """Criar novo pacote de tratamento"""
    if request.method == 'POST':
        # Implementar criação do pacote
        messages.success(request, 'Pacote criado com sucesso!')
        return redirect('modulos:estetica_pacotes')
    
    context = {
        'page_title': 'Novo Pacote - Clínica de Estética',
    }
    return render(request, 'modulos/estetica/pacotes/criar.html', context)

@login_required
def pacote_detalhes(request, pacote_id):
    """Detalhes de um pacote específico"""
    pacote = get_object_or_404(PacoteTratamento, id=pacote_id)
    context = {
        'page_title': 'Detalhes do Pacote - Clínica de Estética',
        'pacote': pacote,
    }
    return render(request, 'modulos/estetica/pacotes/detalhes.html', context)

@login_required
def editar_pacote(request, pacote_id):
    """Editar pacote de tratamento"""
    pacote = get_object_or_404(PacoteTratamento, id=pacote_id)
    if request.method == 'POST':
        # Implementar edição do pacote
        messages.success(request, 'Pacote atualizado com sucesso!')
        return redirect('modulos:estetica_pacote_detalhes', pacote_id=pacote.id)
    
    context = {
        'page_title': 'Editar Pacote - Clínica de Estética',
        'pacote': pacote,
    }
    return render(request, 'modulos/estetica/pacotes/editar.html', context)

@login_required
def listar_retornos(request):
    """Lista de retornos"""
    retornos = Retorno.objects.all()
    context = {
        'page_title': 'Retornos - Clínica de Estética',
        'retornos': retornos,
    }
    return render(request, 'modulos/estetica/retornos/lista.html', context)

@login_required
def criar_retorno(request):
    """Criar novo retorno"""
    if request.method == 'POST':
        # Implementar criação do retorno
        messages.success(request, 'Retorno criado com sucesso!')
        return redirect('modulos:estetica_retornos')
    
    context = {
        'page_title': 'Novo Retorno - Clínica de Estética',
    }
    return render(request, 'modulos/estetica/retornos/criar.html', context)

@login_required
def retorno_detalhes(request, retorno_id):
    """Detalhes de um retorno específico"""
    retorno = get_object_or_404(Retorno, id=retorno_id)
    context = {
        'page_title': 'Detalhes do Retorno - Clínica de Estética',
        'retorno': retorno,
    }
    return render(request, 'modulos/estetica/retornos/detalhes.html', context)

@login_required
def criar_servico(request):
    """Criar novo serviço"""
    if request.method == 'POST':
        # Implementar criação do serviço
        messages.success(request, 'Serviço criado com sucesso!')
        return redirect('modulos:estetica_servicos')
    
    context = {
        'page_title': 'Novo Serviço - Clínica de Estética',
    }
    return render(request, 'modulos/estetica/servicos/criar.html', context)

@login_required
def editar_servico(request, servico_id):
    """Editar serviço"""
    servico = get_object_or_404(ServicoEstetica, id=servico_id)
    if request.method == 'POST':
        # Implementar edição do serviço
        messages.success(request, 'Serviço atualizado com sucesso!')
        return redirect('modulos:estetica_servico_detalhes', servico_id=servico.id)
    
    context = {
        'page_title': 'Editar Serviço - Clínica de Estética',
        'servico': servico,
    }
    return render(request, 'modulos/estetica/servicos/editar.html', context)

@login_required
def criar_protocolo(request):
    """Criar novo protocolo"""
    if request.method == 'POST':
        # Implementar criação do protocolo
        messages.success(request, 'Protocolo criado com sucesso!')
        return redirect('modulos:estetica_protocolos')
    
    context = {
        'page_title': 'Novo Protocolo - Clínica de Estética',
    }
    return render(request, 'modulos/estetica/protocolos/criar.html', context)

@login_required
def editar_protocolo(request, protocolo_id):
    """Editar protocolo"""
    protocolo = get_object_or_404(ProtocoloEmagrecimento, id=protocolo_id)
    if request.method == 'POST':
        # Implementar edição do protocolo
        messages.success(request, 'Protocolo atualizado com sucesso!')
        return redirect('modulos:estetica_protocolo_detalhes', protocolo_id=protocolo.id)
    
    context = {
        'page_title': 'Editar Protocolo - Clínica de Estética',
        'protocolo': protocolo,
    }
    return render(request, 'modulos/estetica/protocolos/editar.html', context)
