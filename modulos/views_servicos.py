"""
Views para gerenciamento de serviços de estética
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from decimal import Decimal

from .models import ServicoEstetica
from lojas.permissions import require_loja_access
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


@login_required
@require_loja_access
def listar_servicos(request):
    """Lista todos os serviços da loja"""
    
    try:
        # Obter loja do usuário
        loja = AuthenticationService.get_user_store(request.user)
        if not loja:
            messages.error(request, 'Loja não encontrada.')
            return redirect('dashboard:principal')
        
        # Filtros
        busca = request.GET.get('busca', '')
        categoria = request.GET.get('categoria', '')
        ativo = request.GET.get('ativo', '')
        
        # Query base
        servicos = ServicoEstetica.objects.all()
        
        # Aplicar filtros
        if busca:
            servicos = servicos.filter(
                Q(nome__icontains=busca) | 
                Q(descricao__icontains=busca)
            )
        
        if categoria:
            servicos = servicos.filter(categoria=categoria)
        
        if ativo == 'true':
            servicos = servicos.filter(ativo=True)
        elif ativo == 'false':
            servicos = servicos.filter(ativo=False)
        
        # Ordenação
        servicos = servicos.order_by('categoria', 'nome')
        
        # Paginação
        paginator = Paginator(servicos, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Estatísticas
        total_servicos = ServicoEstetica.objects.count()
        servicos_ativos = ServicoEstetica.objects.filter(ativo=True).count()
        servicos_inativos = total_servicos - servicos_ativos
        
        # Categorias para filtro
        categorias = ServicoEstetica.CATEGORIA_CHOICES
        
        context = {
            'loja': loja,
            'page_obj': page_obj,
            'servicos': page_obj.object_list,
            'total_servicos': total_servicos,
            'servicos_ativos': servicos_ativos,
            'servicos_inativos': servicos_inativos,
            'categorias': categorias,
            'filtros': {
                'busca': busca,
                'categoria': categoria,
                'ativo': ativo,
            },
            'page_title': 'Gerenciar Serviços',
        }
        
        return render(request, 'modulos/servicos/listar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao listar serviços: {str(e)}")
        messages.error(request, 'Erro interno ao carregar serviços.')
        return redirect('dashboard:loja')


@login_required
@require_loja_access
def criar_servico(request):
    """Cria um novo serviço"""
    
    try:
        # Obter loja do usuário
        loja = AuthenticationService.get_user_store(request.user)
        if not loja:
            messages.error(request, 'Loja não encontrada.')
            return redirect('dashboard:principal')
        
        if request.method == 'POST':
            # Dados do formulário
            nome = request.POST.get('nome', '').strip()
            descricao = request.POST.get('descricao', '').strip()
            categoria = request.POST.get('categoria', '')
            duracao_minutos = request.POST.get('duracao_minutos', '')
            preco = request.POST.get('preco', '').replace(',', '.')
            preco_promocional = request.POST.get('preco_promocional', '').replace(',', '.')
            requer_consulta_medica = request.POST.get('requer_consulta_medica') == 'on'
            idade_minima = request.POST.get('idade_minima', '16')
            contraindicacoes = request.POST.get('contraindicacoes', '').strip()
            cuidados_pos_procedimento = request.POST.get('cuidados_pos_procedimento', '').strip()
            ativo = request.POST.get('ativo') == 'on'
            
            # Validações
            if not nome:
                messages.error(request, 'Nome do serviço é obrigatório.')
                return render(request, 'modulos/servicos/criar.html', {
                    'loja': loja,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            if not categoria:
                messages.error(request, 'Categoria é obrigatória.')
                return render(request, 'modulos/servicos/criar.html', {
                    'loja': loja,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            try:
                duracao_minutos = int(duracao_minutos)
            except (ValueError, TypeError):
                messages.error(request, 'Duração deve ser um número válido.')
                return render(request, 'modulos/servicos/criar.html', {
                    'loja': loja,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            try:
                preco = Decimal(preco)
                if preco <= 0:
                    raise ValueError("Preço deve ser maior que zero")
            except (ValueError, TypeError):
                messages.error(request, 'Preço deve ser um valor válido maior que zero.')
                return render(request, 'modulos/servicos/criar.html', {
                    'loja': loja,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            # Preço promocional (opcional)
            if preco_promocional:
                try:
                    preco_promocional = Decimal(preco_promocional)
                    if preco_promocional <= 0 or preco_promocional >= preco:
                        raise ValueError("Preço promocional inválido")
                except (ValueError, TypeError):
                    messages.error(request, 'Preço promocional deve ser um valor válido menor que o preço normal.')
                    return render(request, 'modulos/servicos/criar.html', {
                        'loja': loja,
                        'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                        'duracoes': ServicoEstetica.DURACAO_CHOICES,
                    })
            else:
                preco_promocional = None
            
            try:
                idade_minima = int(idade_minima)
                if idade_minima < 0 or idade_minima > 100:
                    raise ValueError("Idade mínima inválida")
            except (ValueError, TypeError):
                messages.error(request, 'Idade mínima deve ser um número válido entre 0 e 100.')
                return render(request, 'modulos/servicos/criar.html', {
                    'loja': loja,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            # Criar serviço
            servico = ServicoEstetica.objects.create(
                nome=nome,
                descricao=descricao,
                categoria=categoria,
                duracao_minutos=duracao_minutos,
                preco=preco,
                preco_promocional=preco_promocional,
                requer_consulta_medica=requer_consulta_medica,
                idade_minima=idade_minima,
                contraindicacoes=contraindicacoes,
                cuidados_pos_procedimento=cuidados_pos_procedimento,
                ativo=ativo,
            )
            
            logger.info(f"Serviço '{nome}' criado com sucesso por {request.user.username}")
            messages.success(request, f'Serviço "{nome}" criado com sucesso!')
            return redirect('modulos:listar_servicos')
        
        # GET - Mostrar formulário
        context = {
            'loja': loja,
            'categorias': ServicoEstetica.CATEGORIA_CHOICES,
            'duracoes': ServicoEstetica.DURACAO_CHOICES,
            'page_title': 'Criar Serviço',
        }
        
        return render(request, 'modulos/servicos/criar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao criar serviço: {str(e)}")
        messages.error(request, 'Erro interno ao criar serviço.')
        return redirect('modulos:listar_servicos')


@login_required
@require_loja_access
def editar_servico(request, servico_id):
    """Edita um serviço existente"""
    
    try:
        # Obter loja do usuário
        loja = AuthenticationService.get_user_store(request.user)
        if not loja:
            messages.error(request, 'Loja não encontrada.')
            return redirect('dashboard:principal')
        
        # Obter serviço
        servico = get_object_or_404(ServicoEstetica, id=servico_id)
        
        if request.method == 'POST':
            # Dados do formulário
            nome = request.POST.get('nome', '').strip()
            descricao = request.POST.get('descricao', '').strip()
            categoria = request.POST.get('categoria', '')
            duracao_minutos = request.POST.get('duracao_minutos', '')
            preco = request.POST.get('preco', '').replace(',', '.')
            preco_promocional = request.POST.get('preco_promocional', '').replace(',', '.')
            requer_consulta_medica = request.POST.get('requer_consulta_medica') == 'on'
            idade_minima = request.POST.get('idade_minima', '16')
            contraindicacoes = request.POST.get('contraindicacoes', '').strip()
            cuidados_pos_procedimento = request.POST.get('cuidados_pos_procedimento', '').strip()
            ativo = request.POST.get('ativo') == 'on'
            
            # Validações (mesmas da criação)
            if not nome:
                messages.error(request, 'Nome do serviço é obrigatório.')
                return render(request, 'modulos/servicos/editar.html', {
                    'loja': loja,
                    'servico': servico,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            if not categoria:
                messages.error(request, 'Categoria é obrigatória.')
                return render(request, 'modulos/servicos/editar.html', {
                    'loja': loja,
                    'servico': servico,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            try:
                duracao_minutos = int(duracao_minutos)
            except (ValueError, TypeError):
                messages.error(request, 'Duração deve ser um número válido.')
                return render(request, 'modulos/servicos/editar.html', {
                    'loja': loja,
                    'servico': servico,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            try:
                preco = Decimal(preco)
                if preco <= 0:
                    raise ValueError("Preço deve ser maior que zero")
            except (ValueError, TypeError):
                messages.error(request, 'Preço deve ser um valor válido maior que zero.')
                return render(request, 'modulos/servicos/editar.html', {
                    'loja': loja,
                    'servico': servico,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            # Preço promocional (opcional)
            if preco_promocional:
                try:
                    preco_promocional = Decimal(preco_promocional)
                    if preco_promocional <= 0 or preco_promocional >= preco:
                        raise ValueError("Preço promocional inválido")
                except (ValueError, TypeError):
                    messages.error(request, 'Preço promocional deve ser um valor válido menor que o preço normal.')
                    return render(request, 'modulos/servicos/editar.html', {
                        'loja': loja,
                        'servico': servico,
                        'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                        'duracoes': ServicoEstetica.DURACAO_CHOICES,
                    })
            else:
                preco_promocional = None
            
            try:
                idade_minima = int(idade_minima)
                if idade_minima < 0 or idade_minima > 100:
                    raise ValueError("Idade mínima inválida")
            except (ValueError, TypeError):
                messages.error(request, 'Idade mínima deve ser um número válido entre 0 e 100.')
                return render(request, 'modulos/servicos/editar.html', {
                    'loja': loja,
                    'servico': servico,
                    'categorias': ServicoEstetica.CATEGORIA_CHOICES,
                    'duracoes': ServicoEstetica.DURACAO_CHOICES,
                })
            
            # Atualizar serviço
            servico.nome = nome
            servico.descricao = descricao
            servico.categoria = categoria
            servico.duracao_minutos = duracao_minutos
            servico.preco = preco
            servico.preco_promocional = preco_promocional
            servico.requer_consulta_medica = requer_consulta_medica
            servico.idade_minima = idade_minima
            servico.contraindicacoes = contraindicacoes
            servico.cuidados_pos_procedimento = cuidados_pos_procedimento
            servico.ativo = ativo
            servico.save()
            
            logger.info(f"Serviço '{nome}' atualizado com sucesso por {request.user.username}")
            messages.success(request, f'Serviço "{nome}" atualizado com sucesso!')
            return redirect('modulos:listar_servicos')
        
        # GET - Mostrar formulário
        context = {
            'loja': loja,
            'servico': servico,
            'categorias': ServicoEstetica.CATEGORIA_CHOICES,
            'duracoes': ServicoEstetica.DURACAO_CHOICES,
            'page_title': f'Editar Serviço - {servico.nome}',
        }
        
        return render(request, 'modulos/servicos/editar.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao editar serviço {servico_id}: {str(e)}")
        messages.error(request, 'Erro interno ao editar serviço.')
        return redirect('modulos:listar_servicos')


@login_required
@require_loja_access
def excluir_servico(request, servico_id):
    """Exclui um serviço"""
    
    try:
        # Obter loja do usuário
        loja = AuthenticationService.get_user_store(request.user)
        if not loja:
            messages.error(request, 'Loja não encontrada.')
            return redirect('dashboard:principal')
        
        # Obter serviço
        servico = get_object_or_404(ServicoEstetica, id=servico_id)
        
        if request.method == 'POST':
            nome_servico = servico.nome
            servico.delete()
            
            logger.info(f"Serviço '{nome_servico}' excluído por {request.user.username}")
            messages.success(request, f'Serviço "{nome_servico}" excluído com sucesso!')
            return redirect('modulos:listar_servicos')
        
        # GET - Mostrar confirmação
        context = {
            'loja': loja,
            'servico': servico,
            'page_title': f'Excluir Serviço - {servico.nome}',
        }
        
        return render(request, 'modulos/servicos/excluir.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao excluir serviço {servico_id}: {str(e)}")
        messages.error(request, 'Erro interno ao excluir serviço.')
        return redirect('modulos:listar_servicos')


@login_required
@require_loja_access
def detalhes_servico(request, servico_id):
    """Mostra detalhes de um serviço"""
    
    try:
        # Obter loja do usuário
        loja = AuthenticationService.get_user_store(request.user)
        if not loja:
            messages.error(request, 'Loja não encontrada.')
            return redirect('dashboard:principal')
        
        # Obter serviço
        servico = get_object_or_404(ServicoEstetica, id=servico_id)
        
        context = {
            'loja': loja,
            'servico': servico,
            'page_title': f'Detalhes - {servico.nome}',
        }
        
        return render(request, 'modulos/servicos/detalhes.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao mostrar detalhes do serviço {servico_id}: {str(e)}")
        messages.error(request, 'Erro interno ao carregar detalhes do serviço.')
        return redirect('modulos:listar_servicos')


@login_required
@require_loja_access
def toggle_ativo_servico(request, servico_id):
    """Ativa/desativa um serviço via AJAX"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Obter loja do usuário
        loja = AuthenticationService.get_user_store(request.user)
        if not loja:
            return JsonResponse({'error': 'Loja não encontrada'}, status=400)
        
        # Obter serviço
        servico = get_object_or_404(ServicoEstetica, id=servico_id)
        
        # Toggle status
        servico.ativo = not servico.ativo
        servico.save()
        
        status_text = 'ativado' if servico.ativo else 'desativado'
        logger.info(f"Serviço '{servico.nome}' {status_text} por {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'ativo': servico.ativo,
            'message': f'Serviço "{servico.nome}" {status_text} com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao alterar status do serviço {servico_id}: {str(e)}")
        return JsonResponse({'error': 'Erro interno'}, status=500)