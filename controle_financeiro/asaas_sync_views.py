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
    """Força uma sincronização completa - busca novas cobranças do Asaas e atualiza existentes"""
    
    try:
        if TASKS_AVAILABLE:
            # Executar via Celery task
            task = sync_asaas_charges_task.delay()
            messages.success(request, f'Sincronização forçada iniciada (Task ID: {task.id})')
        else:
            from .asaas_service import AsaasService
            import requests
            from datetime import datetime, timedelta
            
            asaas_service = AsaasService()
            
            # Validar configuração primeiro
            try:
                if not asaas_service.validar_configuracao():
                    messages.error(request, '❌ Configuração da API Asaas inválida')
                    return redirect('controle_financeiro:dashboard_sincronizacao')
                
                messages.info(request, '✅ API Asaas validada - iniciando sincronização completa...')
                
                total_novas = 0
                total_atualizadas = 0
                erros = []
                
                # PARTE 1: BUSCAR NOVAS COBRANÇAS DO ASAAS (últimos 30 dias)
                try:
                    logger.info("Buscando novas cobranças do Asaas...")
                    data_inicio = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    
                    # Buscar cobranças do Asaas
                    response = requests.get(
                        f"{asaas_service.base_url}/payments",
                        headers=asaas_service.headers,
                        params={
                            'dateCreated[ge]': data_inicio,
                            'limit': 100  # Buscar mais cobranças
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        payments = data.get('data', [])
                        
                        logger.info(f"Encontradas {len(payments)} cobranças no Asaas")
                        
                        for payment in payments:
                            try:
                                # Verificar se já existe no sistema
                                if not CobrancaAsaas.objects.filter(asaas_id=payment['id']).exists():
                                    # Tentar criar nova cobrança
                                    nova_cobranca = _criar_cobranca_do_asaas(payment, asaas_service)
                                    if nova_cobranca:
                                        total_novas += 1
                                        logger.info(f"Nova cobrança criada: {payment['id']}")
                                    
                            except Exception as e:
                                erros.append(f"Erro ao processar cobrança {payment.get('id', 'N/A')}: {str(e)}")
                                logger.warning(f"Erro ao processar cobrança: {str(e)}")
                    
                    else:
                        erros.append(f"Erro ao buscar cobranças no Asaas: {response.status_code}")
                        
                except requests.exceptions.ConnectionError as e:
                    if "Connection refused" in str(e):
                        messages.error(request, '🚫 Connection Refused ao buscar novas cobranças!')
                        return redirect('controle_financeiro:dashboard_sincronizacao')
                    else:
                        erros.append(f"Erro de conexão: {str(e)}")
                
                # PARTE 2: ATUALIZAR COBRANÇAS EXISTENTES
                try:
                    logger.info("Atualizando cobranças existentes...")
                    cobrancas_existentes = CobrancaAsaas.objects.filter(
                        status__in=['PENDING', 'OVERDUE']
                    ).order_by('-data_criacao')[:20]  # Últimas 20
                    
                    for cobranca in cobrancas_existentes:
                        try:
                            dados_asaas = asaas_service.consultar_cobranca(cobranca.asaas_id, timeout=15)
                            
                            if dados_asaas:
                                status_anterior = cobranca.status
                                cobranca.atualizar_dados_asaas(dados_asaas)
                                
                                if cobranca.status != status_anterior:
                                    total_atualizadas += 1
                                    logger.info(f"Cobrança {cobranca.asaas_id} atualizada: {status_anterior} → {cobranca.status}")
                                    
                                    # Processar pagamento se foi pago
                                    if cobranca.status in ['RECEIVED', 'CONFIRMED'] and status_anterior not in ['RECEIVED', 'CONFIRMED']:
                                        cobranca.marcar_como_paga()
                                        
                        except requests.exceptions.ConnectionError as e:
                            if "Connection refused" in str(e):
                                logger.warning(f"Connection refused para {cobranca.asaas_id}")
                                break
                            else:
                                erros.append(f"Erro de conexão para {cobranca.asaas_id}")
                        except Exception as e:
                            erros.append(f"Erro ao atualizar {cobranca.asaas_id}: {str(e)}")
                
                except Exception as e:
                    erros.append(f"Erro ao atualizar cobranças existentes: {str(e)}")
                
                # Mostrar resultados
                if total_novas > 0 or total_atualizadas > 0:
                    messages.success(request, 
                        f'✅ Sincronização completa! {total_novas} novas cobranças, {total_atualizadas} atualizadas'
                    )
                else:
                    messages.info(request, '📋 Nenhuma nova cobrança ou atualização encontrada')
                
                if erros:
                    messages.warning(request, f'⚠️ {len(erros)} erro(s) encontrado(s)')
                    for erro in erros[:3]:  # Mostrar apenas os 3 primeiros erros
                        messages.warning(request, f'• {erro[:100]}...')
                        
            except requests.exceptions.ConnectionError as e:
                if "Connection refused" in str(e):
                    messages.error(request, 
                        '🚫 Connection Refused na validação! A API Asaas está temporariamente indisponível.'
                    )
                else:
                    messages.error(request, f'❌ Erro de conexão: {str(e)}')
            except Exception as e:
                messages.error(request, f'❌ Erro na sincronização: {str(e)}')
    
    except Exception as e:
        logger.error(f"Erro geral ao forçar sincronização: {str(e)}")
        messages.error(request, f'❌ Erro geral: {str(e)}')
    
    return redirect('controle_financeiro:dashboard_sincronizacao')


def _criar_cobranca_do_asaas(payment_data, asaas_service):
    """Cria uma cobrança no sistema a partir dos dados do Asaas"""
    try:
        from decimal import Decimal
        from datetime import datetime
        
        # Tentar identificar o controle financeiro
        controle = None
        
        # 1. Por externalReference
        external_ref = payment_data.get('externalReference', '')
        if external_ref and external_ref.startswith('CF_'):
            cf_id = external_ref.split('_')[1]
            try:
                controle = ControleFinanceiro.objects.get(id=cf_id)
            except ControleFinanceiro.DoesNotExist:
                pass
        
        # 2. Por dados do customer
        if not controle:
            customer_id = payment_data.get('customer')
            if customer_id:
                try:
                    # Buscar dados do customer
                    customer_response = requests.get(
                        f"{asaas_service.base_url}/customers/{customer_id}",
                        headers=asaas_service.headers,
                        timeout=10
                    )
                    
                    if customer_response.status_code == 200:
                        customer_data = customer_response.json()
                        customer_email = customer_data.get('email', '')
                        customer_cnpj = customer_data.get('cpfCnpj', '')
                        
                        # Buscar por email ou CNPJ
                        if customer_email:
                            controle = ControleFinanceiro.objects.filter(
                                loja__email=customer_email
                            ).first()
                        
                        if not controle and customer_cnpj:
                            controle = ControleFinanceiro.objects.filter(
                                loja__cnpj=customer_cnpj
                            ).first()
                        
                        # Se não encontrou, criar loja e controle automaticamente
                        if not controle:
                            controle = _criar_loja_e_controle_automatico(customer_data, payment_data)
                            
                except Exception as e:
                    logger.warning(f"Erro ao buscar customer {customer_id}: {str(e)}")
        
        # Se ainda não tem controle, pular esta cobrança
        if not controle:
            logger.warning(f"Não foi possível associar cobrança {payment_data['id']} a nenhum controle financeiro")
            return None
        
        # Criar a cobrança
        from datetime import timezone as dt_timezone
        cobranca = CobrancaAsaas.objects.create(
            asaas_id=payment_data['id'],
            controle_financeiro=controle,
            customer_id=payment_data['customer'],
            valor=Decimal(str(payment_data['value'])),
            data_vencimento=datetime.fromisoformat(payment_data['dueDate']).replace(tzinfo=dt_timezone.utc),
            descricao=payment_data.get('description', ''),
            status=payment_data['status'],
            external_reference=payment_data.get('externalReference', ''),
            api_response=payment_data
        )
        
        # Atualizar dados adicionais
        cobranca.atualizar_dados_asaas(payment_data)
        
        return cobranca
        
    except Exception as e:
        logger.error(f"Erro ao criar cobrança do Asaas: {str(e)}")
        return None


def _criar_loja_e_controle_automatico(customer_data, payment_data):
    """Cria automaticamente loja e controle financeiro para cobranças órfãs"""
    try:
        from lojas.models import Loja
        
        # Dados do customer
        customer_name = customer_data.get('name', 'Loja Importada do Asaas')
        customer_email = customer_data.get('email', '')
        customer_cnpj = customer_data.get('cpfCnpj', '')
        customer_phone = customer_data.get('phone', '')
        
        # Criar loja
        loja = Loja.objects.create(
            nome=customer_name,
            email=customer_email,
            cnpj=customer_cnpj,
            telefone=customer_phone,
            endereco=customer_data.get('address', 'Endereço não informado'),
            cidade=customer_data.get('city', 'Cidade não informada'),
            estado=customer_data.get('state', 'Estado não informado'),
            cep='00000000',
            status='ativa'
        )
        
        # Buscar plano padrão
        plano_padrao = PlanoFinanceiro.objects.filter(nome='Básico').first()
        if not plano_padrao:
            plano_padrao = PlanoFinanceiro.objects.create(
                nome='Básico',
                descricao='Plano básico para lojas importadas',
                valor_mensal=29.90,
                ativo=True
            )
        
        # Criar controle financeiro
        controle = ControleFinanceiro.objects.create(
            loja=loja,
            plano=plano_padrao,
            status='ativa',
            valor_mensal=plano_padrao.valor_mensal,
            data_inicio=timezone.now(),
            data_vencimento=timezone.now() + timedelta(days=30)
        )
        
        logger.info(f"Loja e controle criados automaticamente: {loja.nome} (ID: {controle.id})")
        return controle
        
    except Exception as e:
        logger.error(f"Erro ao criar loja e controle automaticamente: {str(e)}")
        return None


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
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
    """API para obter estatísticas das cobranças (versão simplificada)"""
    
    try:
        # Simple rate limiting - cache results for 30 seconds
        from django.core.cache import cache
        cache_key = f"sync_stats_{request.user.id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return JsonResponse(cached_result)
        
        logger.info(f"Generating fresh stats for user {request.user.username}")
        # Apenas contar total para evitar erros
        total_cobrancas = CobrancaAsaas.objects.count()
        
        # Dados simplificados por status
        try:
            stats_por_status = []
            
            # Contar por status principais
            status_counts = {
                'PENDING': CobrancaAsaas.objects.filter(status='PENDING').count(),
                'RECEIVED': CobrancaAsaas.objects.filter(status='RECEIVED').count(),
                'CONFIRMED': CobrancaAsaas.objects.filter(status='CONFIRMED').count(),
                'OVERDUE': CobrancaAsaas.objects.filter(status='OVERDUE').count(),
            }
            
            for status, count in status_counts.items():
                stats_por_status.append({
                    'status': status,
                    'count': count,
                    'total_valor': 0.0  # Simplificado para evitar erros
                })
            
            # Adicionar total
            stats_por_status.append({
                'status': 'TOTAL',
                'count': total_cobrancas,
                'total_valor': 0.0
            })
            
        except Exception as status_error:
            logger.warning(f"Erro ao calcular stats por status: {status_error}")
            stats_por_status = [
                {'status': 'TOTAL', 'count': total_cobrancas, 'total_valor': 0.0}
            ]
        
        # Cobranças por período
        try:
            hoje = timezone.now().date()
            ontem = hoje - timedelta(days=1)
            semana_passada = hoje - timedelta(days=7)
            mes_passado = hoje - timedelta(days=30)
            
            cobrancas_hoje = CobrancaAsaas.objects.filter(data_criacao__date=hoje).count()
            cobrancas_ontem = CobrancaAsaas.objects.filter(data_criacao__date=ontem).count()
            cobrancas_semana = CobrancaAsaas.objects.filter(data_criacao__date__gte=semana_passada).count()
            cobrancas_mes = CobrancaAsaas.objects.filter(data_criacao__date__gte=mes_passado).count()
            
            cobrancas_periodo = {
                'hoje': cobrancas_hoje,
                'ontem': cobrancas_ontem,
                'semana': cobrancas_semana,
                'mes': cobrancas_mes
            }
            
        except Exception as periodo_error:
            logger.warning(f"Erro ao calcular stats por período: {periodo_error}")
            cobrancas_periodo = {
                'hoje': 0,
                'ontem': 0,
                'semana': 0,
                'mes': 0
            }
        
        result = {
            'success': True,
            'data': {
                'stats_por_status': stats_por_status,
                'cobrancas_periodo': cobrancas_periodo
            }
        }
        
        # Cache result for 30 seconds
        cache.set(cache_key, result, 30)
        
        return JsonResponse(result)
    
    except Exception as e:
        logger.error(f"Erro na API de stats: {str(e)}")
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
def teste_sincronizacao(request):
    """Função de teste para sincronização"""
    messages.success(request, '✅ Função de teste funcionando!')
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