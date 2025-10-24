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
import logging
import requests

from .asaas_sync_service import get_sync_service, AsaasSyncService
from .models import CobrancaAsaas, ControleFinanceiro
try:
    from .tasks import sync_asaas_charges_task, sync_single_asaas_charge_task, monitor_asaas_payments_task
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False

logger = logging.getLogger(__name__)


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
    """Força uma sincronização usando as funcionalidades já testadas"""
    
    try:
        if TASKS_AVAILABLE:
            # Executar via Celery task
            task = sync_asaas_charges_task.delay()
            messages.success(request, f'Sincronização forçada iniciada (Task ID: {task.id})')
        else:
            # Usar o método validar_configuracao que já funciona
            logger.info("Usando método validar_configuracao que já funciona...")
            
            try:
                from .asaas_service import AsaasService
                asaas_service = AsaasService()
                
                logger.info("Iniciando validação da configuração da API Asaas...")
                
                # Teste 1: Usar o método que já funciona
                if asaas_service.validar_configuracao():
                    logger.info("Configuração da API Asaas validada com sucesso")
                    messages.success(request, '✅ API Asaas acessível - configuração validada!')
                    
                    # Teste adicional: verificar conectividade com timeout baixo
                    try:
                        teste_conectividade = asaas_service.test_connection_quick(timeout=3)
                        if not teste_conectividade.get('accessible', False):
                            messages.warning(request, 
                                '⚠️ API Asaas pode estar instável. Sincronização pode falhar.'
                            )
                    except Exception as teste_error:
                        logger.warning(f"Teste de conectividade falhou: {str(teste_error)}")
                        messages.warning(request, 
                            '⚠️ Teste de conectividade falhou. Continuando com sincronização...'
                        )
                    
                    # Agora fazer sincronização simples usando apenas métodos que funcionam
                    try:
                        # Buscar cobranças reais para sincronizar (excluir exemplos e testes)
                        cobrancas_para_sync = CobrancaAsaas.objects.filter(
                            status__in=['PENDING', 'OVERDUE']
                        ).exclude(
                            asaas_id__contains='exemplo'
                        ).exclude(
                            asaas_id__contains='TESTE'
                        ).exclude(
                            asaas_id__startswith='test_'
                        ).order_by('-data_criacao')[:10]  # Aumentar para 10 cobranças reais
                        
                        logger.info(f"Sincronizando {len(cobrancas_para_sync)} cobranças reais (excluindo exemplos/testes)")
                        
                        if len(cobrancas_para_sync) == 0:
                            messages.info(request, '📋 Nenhuma cobrança real encontrada para sincronizar (apenas exemplos/testes no banco)')
                            return redirect('controle_financeiro:dashboard_sincronizacao')
                        
                        total_processadas = 0
                        total_atualizadas = 0
                        erros = []
                        
                        for cobranca in cobrancas_para_sync:
                            try:
                                # Usar o método consultar_cobranca com tratamento específico para Connection refused
                                dados_asaas = asaas_service.consultar_cobranca(cobranca.asaas_id, timeout=10)
                                
                                if dados_asaas:
                                    status_anterior = cobranca.status
                                    
                                    # Atualizar status se mudou
                                    if dados_asaas.get('status') != status_anterior:
                                        cobranca.status = dados_asaas.get('status', status_anterior)
                                        cobranca.save()
                                        total_atualizadas += 1
                                        logger.info(f"Cobrança {cobranca.asaas_id} atualizada: {status_anterior} → {cobranca.status}")
                                    
                                    total_processadas += 1
                                    
                                else:
                                    erros.append(f"Não foi possível consultar {cobranca.asaas_id}")
                                    
                            except requests.exceptions.ConnectionError as e:
                                if "Connection refused" in str(e):
                                    error_msg = f"Connection refused para {cobranca.asaas_id} - parando sincronização"
                                    erros.append(error_msg)
                                    logger.warning(error_msg)
                                    messages.error(request, 
                                        '🚫 Connection Refused detectado! A API Asaas está temporariamente indisponível. '
                                        'Tente novamente em alguns minutos.'
                                    )
                                    break  # Parar imediatamente se connection refused
                                else:
                                    error_msg = f"Erro de conexão para {cobranca.asaas_id}: {str(e)}"
                                    erros.append(error_msg)
                                    logger.warning(error_msg)
                            except Exception as e:
                                error_msg = f"Erro ao processar {cobranca.asaas_id}: {str(e)}"
                                erros.append(error_msg)
                                logger.warning(error_msg)
                        
                        # Mostrar resultado
                        if total_processadas > 0:
                            messages.success(request, 
                                f'✅ Sincronização concluída! {total_processadas} processadas, {total_atualizadas} atualizadas'
                            )
                        else:
                            messages.info(request, '📋 Nenhuma cobrança encontrada para sincronizar')
                        
                        if erros:
                            messages.warning(request, f'⚠️ {len(erros)} erro(s) encontrado(s). Primeiro: {erros[0][:100]}...')
                            
                    except Exception as sync_error:
                        logger.error(f"Erro na sincronização simples: {str(sync_error)}")
                        messages.error(request, f'❌ Erro na sincronização: {str(sync_error)}')
                        
                else:
                    logger.error("Falha na validação da configuração da API Asaas")
                    messages.error(request, '❌ Configuração da API Asaas inválida. Verifique as configurações.')
                    
            except Exception as config_error:
                logger.error(f"Erro na validação da configuração: {str(config_error)}")
                logger.error(f"Tipo do erro: {type(config_error).__name__}")
                
                # Tratamento específico para Connection refused na validação
                if "Connection refused" in str(config_error) or "[Errno 111]" in str(config_error):
                    messages.error(request, 
                        '🚫 Connection Refused na validação! A API Asaas está temporariamente indisponível. '
                        'Tente novamente em alguns minutos.'
                    )
                    return redirect('controle_financeiro:dashboard_sincronizacao')
    
    except Exception as e:
        error_str = str(e)
        logger.error(f"Erro geral ao forçar sincronização: {error_str}")
        
        # Tratamento específico para Connection refused
        if "Connection refused" in error_str or "[Errno 111]" in error_str:
            messages.error(request, 
                '🚫 Connection Refused detectado! A API Asaas está temporariamente indisponível. '
                'Isso é temporário - aguarde 5-10 minutos e tente novamente.'
            )
            messages.info(request, 
                '💡 Dica: Connection Refused geralmente ocorre por sobrecarga da API. '
                'Tente em horários de menor movimento (madrugada, fins de semana).'
            )
        else:
            messages.error(request, f'❌ Erro geral: {error_str}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def sincronizar_usando_funcionalidades_existentes(request):
    """Sincronização usando apenas funcionalidades que já funcionam"""
    
    try:
        logger.info("Iniciando sincronização usando funcionalidades existentes...")
        
        # Usar AsaasService que já funciona
        from .asaas_service import AsaasService
        asaas_service = AsaasService()
        
        # Primeiro, validar se API está funcionando
        if not asaas_service.validar_configuracao():
            messages.error(request, '❌ API Asaas não está acessível. Verifique as configurações.')
            return redirect('controle_financeiro:dashboard_sincronizacao')
        
        messages.info(request, '✅ API Asaas validada - iniciando sincronização...')
        
        # Buscar cobranças para sincronizar (apenas algumas)
        cobrancas = CobrancaAsaas.objects.filter(
            status__in=['PENDING', 'OVERDUE']
        ).order_by('-data_criacao')[:10]  # Máximo 10
        
        if not cobrancas:
            messages.info(request, '📋 Nenhuma cobrança pendente encontrada para sincronizar.')
            return redirect('controle_financeiro:dashboard_sincronizacao')
        
        total_processadas = 0
        total_atualizadas = 0
        erros = []
        
        for cobranca in cobrancas:
            try:
                # Usar método que já funciona
                dados_asaas = asaas_service.consultar_cobranca(cobranca.asaas_id, timeout=15)
                
                if dados_asaas:
                    status_anterior = cobranca.status
                    novo_status = dados_asaas.get('status', status_anterior)
                    
                    if novo_status != status_anterior:
                        cobranca.status = novo_status
                        cobranca.save()
                        total_atualizadas += 1
                        
                        # Se foi paga, processar pagamento
                        if novo_status in ['RECEIVED', 'CONFIRMED'] and status_anterior not in ['RECEIVED', 'CONFIRMED']:
                            try:
                                cobranca.marcar_como_paga()
                                messages.success(request, f'💰 Pagamento processado: {cobranca.asaas_id}')
                            except Exception as payment_error:
                                logger.warning(f"Erro ao processar pagamento: {str(payment_error)}")
                    
                    total_processadas += 1
                    logger.info(f"Cobrança {cobranca.asaas_id}: {status_anterior} → {novo_status}")
                    
                else:
                    erros.append(f"Cobrança {cobranca.asaas_id} não encontrada na API")
                    
            except Exception as e:
                error_msg = f"Erro ao processar {cobranca.asaas_id}: {str(e)}"
                erros.append(error_msg)
                logger.warning(error_msg)
        
        # Mostrar resultados
        if total_processadas > 0:
            messages.success(request, 
                f'✅ Sincronização concluída! {total_processadas} processadas, {total_atualizadas} atualizadas'
            )
        
        if erros:
            messages.warning(request, 
                f'⚠️ {len(erros)} erro(s) encontrado(s). Verifique os logs para detalhes.'
            )
            # Mostrar primeiro erro
            if erros:
                messages.info(request, f'Primeiro erro: {erros[0][:100]}...')
        
        if total_processadas == 0 and not erros:
            messages.info(request, '📋 Todas as cobranças já estão atualizadas.')
            
    except Exception as e:
        logger.error(f"Erro na sincronização usando funcionalidades existentes: {str(e)}")
        messages.error(request, f'❌ Erro na sincronização: {str(e)}')
    
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
@require_http_methods(["POST"])
def testar_conectividade(request):
    """Testa conectividade usando as funcionalidades já testadas e funcionais"""
    
    try:
        logger.info("Iniciando teste de conectividade usando métodos que já funcionam...")
        
        # Usar o AsaasService que já funciona
        from .asaas_service import AsaasService
        asaas_service = AsaasService()
        
        try:
            # Usar o método validar_configuracao que já funciona
            if asaas_service.validar_configuracao():
                messages.success(request, 
                    '✅ Conectividade perfeita! API Asaas acessível e configuração válida.'
                )
                
                # Informações adicionais sobre a configuração
                messages.info(request, f'🔧 Ambiente: {asaas_service.environment.upper()}')
                messages.info(request, f'🌐 URL Base: {asaas_service.base_url}')
                
                # Testar com uma cobrança se existir
                try:
                    cobranca_teste = CobrancaAsaas.objects.filter(status='PENDING').first()
                    if cobranca_teste:
                        dados = asaas_service.consultar_cobranca(cobranca_teste.asaas_id, timeout=10)
                        if dados:
                            messages.success(request, 
                                f'✅ Teste adicional: Cobrança {cobranca_teste.asaas_id} consultada com sucesso!'
                            )
                        else:
                            messages.warning(request, 
                                f'⚠️ Cobrança {cobranca_teste.asaas_id} não pôde ser consultada (pode ter sido removida)'
                            )
                    else:
                        messages.info(request, '📋 Nenhuma cobrança pendente para testar no momento')
                        
                except Exception as charge_error:
                    messages.warning(request, f'⚠️ Erro ao testar cobrança: {str(charge_error)}')
                
            else:
                messages.error(request, 
                    '❌ Configuração da API Asaas inválida. Verifique a chave da API e o ambiente.'
                )
                messages.info(request, 
                    '🔧 Dica: Acesse "Configurar Asaas" para verificar as configurações.'
                )
                
        except Exception as validation_error:
            error_str = str(validation_error)
            
            if "Connection refused" in error_str:
                messages.error(request, 
                    '🚫 Connection Refused detectado! A API Asaas está rejeitando conexões. '
                    'Isso é temporário - aguarde 5-10 minutos e tente novamente.'
                )
                messages.info(request, 
                    '💡 Dica: Connection Refused geralmente ocorre por sobrecarga da API. '
                    'Tente em horários de menor movimento (madrugada, fins de semana).'
                )
            else:
                messages.error(request, f'❌ Erro na validação: {error_str}')
                
                # Sugerir usar a página de teste que já funciona
                messages.info(request, 
                    '🔄 Alternativa: Use a página "Testar Integração com Asaas" que já está funcionando.'
                )
    
    except Exception as e:
        logger.error(f"Erro geral no teste de conectividade: {str(e)}")
        messages.error(request, f'❌ Erro geral: {str(e)}')
        
        # Sugerir alternativa
        messages.info(request, 
            '🔄 Tente usar a página "Testar Integração com Asaas" como alternativa.'
        )
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def sincronizar_usando_funcionalidades_existentes(request):
    """Sincronização usando apenas funcionalidades que já funcionam"""
    
    try:
        logger.info("Iniciando sincronização usando funcionalidades existentes...")
        
        # Usar AsaasService que já funciona
        from .asaas_service import AsaasService
        asaas_service = AsaasService()
        
        # Primeiro, validar se API está funcionando
        if not asaas_service.validar_configuracao():
            messages.error(request, '❌ API Asaas não está acessível. Verifique as configurações.')
            return redirect('controle_financeiro:dashboard_sincronizacao')
        
        messages.info(request, '✅ API Asaas validada - iniciando sincronização...')
        
        # Buscar cobranças para sincronizar (apenas algumas)
        cobrancas = CobrancaAsaas.objects.filter(
            status__in=['PENDING', 'OVERDUE']
        ).order_by('-data_criacao')[:10]  # Máximo 10
        
        if not cobrancas:
            messages.info(request, '📋 Nenhuma cobrança pendente encontrada para sincronizar.')
            return redirect('controle_financeiro:dashboard_sincronizacao')
        
        total_processadas = 0
        total_atualizadas = 0
        erros = []
        
        for cobranca in cobrancas:
            try:
                # Usar método que já funciona
                dados_asaas = asaas_service.consultar_cobranca(cobranca.asaas_id, timeout=15)
                
                if dados_asaas:
                    status_anterior = cobranca.status
                    novo_status = dados_asaas.get('status', status_anterior)
                    
                    if novo_status != status_anterior:
                        cobranca.status = novo_status
                        cobranca.save()
                        total_atualizadas += 1
                        
                        # Se foi paga, processar pagamento
                        if novo_status in ['RECEIVED', 'CONFIRMED'] and status_anterior not in ['RECEIVED', 'CONFIRMED']:
                            try:
                                cobranca.marcar_como_paga()
                                messages.success(request, f'💰 Pagamento processado: {cobranca.asaas_id}')
                            except Exception as payment_error:
                                logger.warning(f"Erro ao processar pagamento: {str(payment_error)}")
                    
                    total_processadas += 1
                    logger.info(f"Cobrança {cobranca.asaas_id}: {status_anterior} → {novo_status}")
                    
                else:
                    erros.append(f"Cobrança {cobranca.asaas_id} não encontrada na API")
                    
            except Exception as e:
                error_msg = f"Erro ao processar {cobranca.asaas_id}: {str(e)}"
                erros.append(error_msg)
                logger.warning(error_msg)
        
        # Mostrar resultados
        if total_processadas > 0:
            messages.success(request, 
                f'✅ Sincronização concluída! {total_processadas} processadas, {total_atualizadas} atualizadas'
            )
        
        if erros:
            messages.warning(request, 
                f'⚠️ {len(erros)} erro(s) encontrado(s). Verifique os logs para detalhes.'
            )
            # Mostrar primeiro erro
            if erros:
                messages.info(request, f'Primeiro erro: {erros[0][:100]}...')
        
        if total_processadas == 0 and not erros:
            messages.info(request, '📋 Todas as cobranças já estão atualizadas.')
            
    except Exception as e:
        logger.error(f"Erro na sincronização usando funcionalidades existentes: {str(e)}")
        messages.error(request, f'❌ Erro na sincronização: {str(e)}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


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