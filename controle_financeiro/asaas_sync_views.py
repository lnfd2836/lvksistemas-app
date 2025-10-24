"""
Views para controle da sincronização em tempo real com Asaas
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json

from .asaas_sync_service import get_sync_service, AsaasSyncService
from .models import CobrancaAsaas, ControleFinanceiro
try:
    from .tasks import sync_asaas_charges_task, sync_single_asaas_charge_task, monitor_asaas_payments_task
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def dashboard_sincronizacao(request):
    """Dashboard de controle da sincronização"""
    
    sync_service = get_sync_service()
    
    # Status da sincronização
    sync_status = sync_service.get_sync_status()
    
    # Estatísticas das cobranças
    total_cobrancas = CobrancaAsaas.objects.count()
    cobrancas_pendentes = CobrancaAsaas.objects.filter(status='PENDING').count()
    cobrancas_pagas = CobrancaAsaas.objects.filter(status__in=['RECEIVED', 'CONFIRMED']).count()
    cobrancas_vencidas = CobrancaAsaas.objects.filter(status='OVERDUE').count()
    
    # Cobranças recentes (últimas 24h)
    data_limite = timezone.now() - timedelta(hours=24)
    cobrancas_recentes = CobrancaAsaas.objects.filter(
        data_atualizacao__gte=data_limite
    ).order_by('-data_atualizacao')[:10]
    
    # Cobranças com problemas (não sincronizadas há mais de 1 hora)
    data_problema = timezone.now() - timedelta(hours=1)
    cobrancas_problema = CobrancaAsaas.objects.filter(
        status='PENDING',
        data_atualizacao__lt=data_problema
    ).count()
    
    # Últimas sincronizações (se Celery estiver disponível)
    ultimas_tasks = []
    if TASKS_AVAILABLE:
        try:
            from django_celery_results.models import TaskResult
            ultimas_tasks = TaskResult.objects.filter(
                task_name__in=[
                    'controle_financeiro.tasks.sync_asaas_charges_task',
                    'controle_financeiro.tasks.monitor_asaas_payments_task'
                ]
            ).order_by('-date_created')[:10]
        except:
            ultimas_tasks = []
    
    context = {
        'sync_status': sync_status,
        'total_cobrancas': total_cobrancas,
        'cobrancas_pendentes': cobrancas_pendentes,
        'cobrancas_pagas': cobrancas_pagas,
        'cobrancas_vencidas': cobrancas_vencidas,
        'cobrancas_problema': cobrancas_problema,
        'cobrancas_recentes': cobrancas_recentes,
        'ultimas_tasks': ultimas_tasks,
    }
    
    return render(request, 'controle_financeiro/sync_dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def iniciar_sincronizacao(request):
    """Inicia a sincronização em tempo real"""
    
    try:
        interval = int(request.POST.get('interval', 300))  # 5 minutos por padrão
        
        sync_service = get_sync_service()
        
        if sync_service.start_real_time_sync(interval):
            messages.success(request, f'Sincronização em tempo real iniciada (intervalo: {interval}s)')
        else:
            messages.warning(request, 'Sincronização já está em execução')
    
    except Exception as e:
        messages.error(request, f'Erro ao iniciar sincronização: {str(e)}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def parar_sincronizacao(request):
    """Para a sincronização em tempo real"""
    
    try:
        sync_service = get_sync_service()
        
        if sync_service.stop_real_time_sync():
            messages.success(request, 'Sincronização em tempo real parada')
        else:
            messages.warning(request, 'Sincronização não estava em execução')
    
    except Exception as e:
        messages.error(request, f'Erro ao parar sincronização: {str(e)}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def forcar_sincronizacao(request):
    """Força uma sincronização imediata"""
    
    try:
        if TASKS_AVAILABLE:
            # Executar via Celery task
            task = sync_asaas_charges_task.delay()
            messages.success(request, f'Sincronização forçada iniciada (Task ID: {task.id})')
        else:
            # Executar diretamente
            sync_service = get_sync_service()
            result = sync_service.sync_all_charges()
            messages.success(request, f'Sincronização concluída: {result["total_processed"]} processadas, {result["updates_made"]} atualizadas')
    
    except Exception as e:
        messages.error(request, f'Erro ao forçar sincronização: {str(e)}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


@login_required
@user_passes_test(is_superuser)
def sincronizar_cobranca(request, asaas_id):
    """Sincroniza uma cobrança específica"""
    
    try:
        if TASKS_AVAILABLE:
            # Executar via Celery task
            task = sync_single_asaas_charge_task.delay(asaas_id)
            messages.success(request, f'Sincronização da cobrança {asaas_id} iniciada (Task ID: {task.id})')
        else:
            # Executar diretamente
            sync_service = get_sync_service()
            result = sync_service.sync_single_charge(asaas_id)
            if result['success']:
                messages.success(request, f'Cobrança {asaas_id} sincronizada com sucesso')
            else:
                messages.error(request, f'Erro ao sincronizar cobrança: {result["error"]}')
    
    except Exception as e:
        messages.error(request, f'Erro ao sincronizar cobrança: {str(e)}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


@login_required
@user_passes_test(is_superuser)
def resetar_estatisticas(request):
    """Reseta as estatísticas de sincronização"""
    
    try:
        sync_service = get_sync_service()
        sync_service.reset_stats()
        
        messages.success(request, 'Estatísticas de sincronização resetadas')
    
    except Exception as e:
        messages.error(request, f'Erro ao resetar estatísticas: {str(e)}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


# === API ENDPOINTS ===

@login_required
@user_passes_test(is_superuser)
def api_sync_status(request):
    """API para obter status da sincronização"""
    
    try:
        sync_service = get_sync_service()
        status = sync_service.get_sync_status()
        
        # Converter datetime para string
        if status['last_sync']:
            status['last_sync'] = status['last_sync'].isoformat()
        
        return JsonResponse({
            'success': True,
            'data': status
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_superuser)
def api_cobrancas_stats(request):
    """API para obter estatísticas das cobranças"""
    
    try:
        # Estatísticas por status
        from django.db.models import Count, Sum
        
        stats_por_status = CobrancaAsaas.objects.values('status').annotate(
            count=Count('id'),
            total_valor=Sum('valor')
        ).order_by('status')
        
        # Cobranças por período
        hoje = timezone.now().date()
        ontem = hoje - timedelta(days=1)
        semana_passada = hoje - timedelta(days=7)
        mes_passado = hoje - timedelta(days=30)
        
        cobrancas_hoje = CobrancaAsaas.objects.filter(data_criacao__date=hoje).count()
        cobrancas_ontem = CobrancaAsaas.objects.filter(data_criacao__date=ontem).count()
        cobrancas_semana = CobrancaAsaas.objects.filter(data_criacao__date__gte=semana_passada).count()
        cobrancas_mes = CobrancaAsaas.objects.filter(data_criacao__date__gte=mes_passada).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'stats_por_status': list(stats_por_status),
                'cobrancas_periodo': {
                    'hoje': cobrancas_hoje,
                    'ontem': cobrancas_ontem,
                    'semana': cobrancas_semana,
                    'mes': cobrancas_mes
                }
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_sync_trigger(request):
    """
    Webhook para disparar sincronização quando receber notificação do Asaas
    Este endpoint pode ser chamado pelo próprio sistema ou por webhooks externos
    """
    
    try:
        # Verificar se há dados no body
        if request.body:
            data = json.loads(request.body)
            payment_id = data.get('payment', {}).get('id')
            
            if payment_id:
                # Sincronizar cobrança específica
                if TASKS_AVAILABLE:
                    task = sync_single_asaas_charge_task.delay(payment_id)
                    return JsonResponse({
                        'success': True,
                        'message': f'Sincronização da cobrança {payment_id} iniciada',
                        'task_id': task.id
                    })
                else:
                    # Executar diretamente
                    sync_service = get_sync_service()
                    result = sync_service.sync_single_charge(payment_id)
                    return JsonResponse({
                        'success': True,
                        'message': f'Cobrança {payment_id} sincronizada',
                        'result': result
                    })
        
        # Se não há payment_id específico, fazer sincronização geral
        if TASKS_AVAILABLE:
            task = sync_asaas_charges_task.delay()
            return JsonResponse({
                'success': True,
                'message': 'Sincronização geral iniciada',
                'task_id': task.id
            })
        else:
            # Executar diretamente
            sync_service = get_sync_service()
            result = sync_service.sync_all_charges()
            return JsonResponse({
                'success': True,
                'message': 'Sincronização concluída',
                'result': result
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_superuser)
def listar_cobrancas_problemas(request):
    """Lista cobranças com problemas de sincronização"""
    
    # Cobranças não sincronizadas há mais de 1 hora
    data_problema = timezone.now() - timedelta(hours=1)
    
    cobrancas_problema = CobrancaAsaas.objects.filter(
        status='PENDING',
        data_atualizacao__lt=data_problema
    ).select_related('controle_financeiro__loja').order_by('data_atualizacao')
    
    # Cobranças com erro na API (sem dados de resposta)
    cobrancas_sem_dados = CobrancaAsaas.objects.filter(
        api_response__isnull=True
    ).select_related('controle_financeiro__loja').order_by('-data_criacao')[:20]
    
    context = {
        'cobrancas_problema': cobrancas_problema,
        'cobrancas_sem_dados': cobrancas_sem_dados,
    }
    
    return render(request, 'controle_financeiro/cobrancas_problemas.html', context)


@login_required
@user_passes_test(is_superuser)
def configurar_sincronizacao(request):
    """Configurações da sincronização"""
    
    if request.method == 'POST':
        try:
            # Configurações que podem ser alteradas
            auto_start = request.POST.get('auto_start') == 'on'
            interval = int(request.POST.get('interval', 300))
            
            # Salvar configurações (implementar conforme necessário)
            # Por enquanto, apenas aplicar as configurações
            
            sync_service = get_sync_service()
            
            if auto_start and not sync_service.is_running:
                sync_service.start_real_time_sync(interval)
                messages.success(request, 'Sincronização automática ativada')
            elif not auto_start and sync_service.is_running:
                sync_service.stop_real_time_sync()
                messages.success(request, 'Sincronização automática desativada')
            
            messages.success(request, 'Configurações salvas com sucesso')
        
        except Exception as e:
            messages.error(request, f'Erro ao salvar configurações: {str(e)}')
        
        return redirect('controle_financeiro:configurar_sincronizacao')
    
    # Obter configurações atuais
    sync_service = get_sync_service()
    sync_status = sync_service.get_sync_status()
    
    context = {
        'sync_status': sync_status,
    }
    
    return render(request, 'controle_financeiro/configurar_sync.html', context)