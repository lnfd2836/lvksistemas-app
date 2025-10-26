"""
Exemplo de views usando o sistema de isolamento por loja
"""
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from .services.isolamento_service import IsolamentoService, require_loja_isolation
from .models import Loja
from controle_financeiro.models import Transacao  # Exemplo de modelo de loja

logger = logging.getLogger(__name__)


@login_required
@require_loja_isolation
def dashboard_loja_isolado(request):
    """
    Dashboard da loja com isolamento completo
    """
    try:
        # O contexto da loja já foi definido pelo decorador
        loja_context = IsolamentoService.get_user_loja_context(request.user)
        
        if not loja_context:
            raise PermissionDenied("Contexto de loja não encontrado")
        
        # Para super admins, mostrar seletor de loja
        if loja_context['is_super_admin']:
            lojas = Loja.objects.filter(status='ativa')
            return render(request, 'lojas/dashboard_super_admin.html', {
                'lojas': lojas,
                'is_super_admin': True
            })
        
        # Para usuários de loja, mostrar dados isolados
        loja = loja_context['loja']
        
        # Buscar dados da loja (automaticamente isolados pelo router)
        transacoes_recentes = Transacao.objects.filter(
            loja=loja
        ).order_by('-data_criacao')[:10]
        
        context = {
            'loja': loja,
            'loja_context': loja_context,
            'transacoes_recentes': transacoes_recentes,
            'is_super_admin': False
        }
        
        return render(request, 'lojas/dashboard_loja_isolado.html', context)
        
    except Exception as e:
        logger.error(f"Erro no dashboard isolado: {str(e)}")
        raise


@login_required
@require_http_methods(["GET"])
def api_dados_loja_isolados(request):
    """
    API que retorna dados isolados da loja do usuário
    """
    try:
        # Executar no contexto da loja do usuário
        def get_dados():
            loja_context = IsolamentoService.get_user_loja_context(request.user)
            
            if not loja_context:
                return {'error': 'Contexto de loja não encontrado'}
            
            if loja_context['is_super_admin']:
                # Super admin vê dados agregados
                return {
                    'tipo': 'super_admin',
                    'total_lojas': Loja.objects.filter(status='ativa').count(),
                    'dados': 'Dados agregados do sistema'
                }
            else:
                # Usuário de loja vê apenas seus dados
                loja = loja_context['loja']
                
                # Dados automaticamente isolados pelo router
                total_transacoes = Transacao.objects.filter(loja=loja).count()
                
                return {
                    'tipo': 'loja_user',
                    'loja_id': loja.id,
                    'loja_nome': loja.nome,
                    'total_transacoes': total_transacoes,
                    'db_alias': loja_context['db_alias']
                }
        
        dados = IsolamentoService.execute_with_loja_context(
            request.user, get_dados
        )
        
        return JsonResponse(dados)
        
    except Exception as e:
        logger.error(f"Erro na API de dados isolados: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def validar_isolamento(request):
    """
    View para validar se o isolamento está funcionando
    """
    try:
        # Obter status do isolamento
        status = IsolamentoService.get_isolation_status()
        
        # Obter contexto do usuário
        loja_context = IsolamentoService.get_user_loja_context(request.user)
        
        # Verificar acesso a dados
        def test_data_access():
            # Tentar acessar dados de diferentes lojas
            results = {}
            
            for loja in Loja.objects.filter(status='ativa')[:3]:
                try:
                    # Verificar se pode acessar esta loja
                    can_access = IsolamentoService.validate_user_loja_access(
                        request.user, str(loja.id)
                    )
                    
                    results[f'loja_{loja.id}'] = {
                        'nome': loja.nome,
                        'can_access': can_access,
                        'is_own_loja': (
                            loja_context and 
                            not loja_context['is_super_admin'] and 
                            str(loja_context['loja'].id) == str(loja.id)
                        )
                    }
                    
                except Exception as e:
                    results[f'loja_{loja.id}'] = {
                        'nome': loja.nome,
                        'error': str(e)
                    }
            
            return results
        
        access_results = IsolamentoService.execute_with_loja_context(
            request.user, test_data_access
        )
        
        context = {
            'status': status,
            'loja_context': loja_context,
            'access_results': access_results,
            'user_type': request.user.is_superuser and 'super_admin' or 'loja_user'
        }
        
        return render(request, 'lojas/validar_isolamento.html', context)
        
    except Exception as e:
        logger.error(f"Erro na validação de isolamento: {str(e)}")
        return render(request, 'lojas/validar_isolamento.html', {
            'error': str(e)
        })


@login_required
def switch_loja_context(request, loja_id):
    """
    View para super admins mudarem o contexto de loja (apenas para testes)
    """
    try:
        # Apenas super admins podem fazer isso
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas super admins podem mudar contexto de loja")
        
        # Verificar se a loja existe
        loja = get_object_or_404(Loja, id=loja_id, status='ativa')
        
        # Executar no contexto da loja específica
        def get_loja_data():
            # Dados da loja específica
            total_transacoes = Transacao.objects.filter(loja=loja).count()
            
            return {
                'loja': loja,
                'total_transacoes': total_transacoes,
                'db_alias': f'loja_{loja.id}'
            }
        
        # Usar context manager para executar no contexto da loja
        from .database_router_isolado import LojaContextManager
        
        with LojaContextManager(str(loja.id)):
            dados = get_loja_data()
        
        return JsonResponse({
            'success': True,
            'loja_id': loja.id,
            'loja_nome': loja.nome,
            'dados': dados
        })
        
    except Exception as e:
        logger.error(f"Erro ao mudar contexto de loja: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# Exemplo de view que NÃO deve usar isolamento (dados do sistema)
@login_required
def sistema_stats(request):
    """
    Estatísticas do sistema (sem isolamento)
    """
    try:
        # Apenas super admins podem ver stats do sistema
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas super admins podem ver estatísticas do sistema")
        
        # Dados do sistema (banco principal)
        total_lojas = Loja.objects.filter(status='ativa').count()
        total_usuarios = User.objects.count()
        
        # Status do isolamento
        isolation_status = IsolamentoService.get_isolation_status()
        
        context = {
            'total_lojas': total_lojas,
            'total_usuarios': total_usuarios,
            'isolation_status': isolation_status
        }
        
        return render(request, 'lojas/sistema_stats.html', context)
        
    except Exception as e:
        logger.error(f"Erro nas estatísticas do sistema: {str(e)}")
        raise