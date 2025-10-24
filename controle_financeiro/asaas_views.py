"""
Views para integração com a API do Asaas
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings

from .models import ControleFinanceiro, CobrancaAsaas
from .asaas_service import AsaasService

logger = logging.getLogger(__name__)


@login_required
def gerar_cobranca_asaas(request, controle_id):
    """
    Gera nova cobrança no Asaas com boleto e PIX
    """
    controle = get_object_or_404(ControleFinanceiro, id=controle_id)
    
    # Verificar permissões
    if not request.user.is_superuser and controle.loja.admin != request.user:
        messages.error(request, "Você não tem permissão para acessar esta funcionalidade.")
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        try:
            # Parâmetros da cobrança
            dias_vencimento = int(request.POST.get('dias_vencimento', 30))
            descricao = request.POST.get('descricao', '')
            
            # Inicializar serviço do Asaas
            asaas_service = AsaasService()
            
            # Gerar cobrança
            resultado = asaas_service.gerar_cobranca_com_pix(
                controle, 
                dias_vencimento=dias_vencimento,
                descricao=descricao
            )
            
            if resultado.get('success'):
                # Salvar cobrança no banco de dados
                cobranca_data = resultado['cobranca']
                pix_data = resultado.get('pix', {})
                
                cobranca = CobrancaAsaas.objects.create(
                    asaas_id=cobranca_data['id'],
                    controle_financeiro=controle,
                    customer_id=cobranca_data['customer'],
                    valor=cobranca_data['value'],
                    data_vencimento=timezone.datetime.fromisoformat(cobranca_data['dueDate']).replace(tzinfo=timezone.utc),
                    descricao=cobranca_data['description'],
                    status=cobranca_data['status'],
                    invoice_url=cobranca_data.get('invoiceUrl', ''),
                    bank_slip_url=cobranca_data.get('bankSlipUrl', ''),
                    invoice_number=cobranca_data.get('invoiceNumber', ''),
                    external_reference=cobranca_data.get('externalReference', ''),
                    api_response=cobranca_data
                )
                
                # Atualizar dados do PIX se disponível
                if pix_data:
                    cobranca.pix_qr_code = pix_data.get('qrCode', '')
                    cobranca.pix_copy_paste = pix_data.get('payload', '')
                    if pix_data.get('expirationDate'):
                        cobranca.pix_expires_date = timezone.datetime.fromisoformat(
                            pix_data['expirationDate'].replace('Z', '+00:00')
                        )
                    cobranca.save()
                
                messages.success(request, f"Cobrança gerada com sucesso! ID: {cobranca.asaas_id}")
                return redirect('controle_financeiro:visualizar_cobranca_asaas', cobranca_id=cobranca.id)
                
            else:
                error_msg = resultado.get('error', 'Erro desconhecido')
                messages.error(request, f"Erro ao gerar cobrança: {error_msg}")
                
        except Exception as e:
            logger.error(f"Erro ao gerar cobrança Asaas: {str(e)}")
            messages.error(request, f"Erro interno: {str(e)}")
    
    context = {
        'controle': controle,
        'loja': controle.loja,
        'plano': controle.plano,
    }
    
    return render(request, 'controle_financeiro/gerar_cobranca_asaas.html', context)


@login_required
def visualizar_cobranca_asaas(request, cobranca_id):
    """
    Visualiza detalhes de uma cobrança do Asaas
    """
    cobranca = get_object_or_404(CobrancaAsaas, id=cobranca_id)
    
    # Verificar permissões
    if not request.user.is_superuser and cobranca.controle_financeiro.loja.admin != request.user:
        messages.error(request, "Você não tem permissão para acessar esta cobrança.")
        return redirect('dashboard:index')
    
    # Atualizar status da cobrança
    if request.GET.get('atualizar') == '1':
        try:
            asaas_service = AsaasService()
            dados_atualizados = asaas_service.consultar_cobranca(cobranca.asaas_id)
            
            if dados_atualizados:
                # Log para debug do PDF
                logger.info(f"Atualizando cobrança {cobranca.asaas_id}")
                logger.info(f"Bank slip URL: {dados_atualizados.get('bankSlipUrl', 'N/A')}")
                logger.info(f"Invoice URL: {dados_atualizados.get('invoiceUrl', 'N/A')}")
                
                cobranca.atualizar_dados_asaas(dados_atualizados)
                
                # Verificar se PDF foi gerado
                if dados_atualizados.get('bankSlipUrl'):
                    messages.success(request, "Status atualizado! PDF do boleto está disponível.")
                elif cobranca.status == 'PENDING':
                    messages.info(request, "Status atualizado. PDF do boleto ainda está sendo gerado pelo Asaas.")
                else:
                    messages.success(request, "Status da cobrança atualizado com sucesso!")
            else:
                # Cobrança não encontrada no Asaas - pode ter sido removida
                logger.warning(f"Cobrança {cobranca.asaas_id} não encontrada no Asaas - pode ter sido removida")
                
                # Verificar se retornou erro 404 (cobrança removida)
                try:
                    import requests
                    response = requests.get(
                        f"{asaas_service.base_url}/payments/{cobranca.asaas_id}",
                        headers=asaas_service.headers,
                        timeout=30
                    )
                    
                    if response.status_code == 404:
                        # Cobrança foi removida do Asaas
                        messages.warning(request, 
                            "⚠️ Esta cobrança foi removida do Asaas. "
                            "Ela será marcada como cancelada no sistema."
                        )
                        cobranca.status = 'DELETED'
                        cobranca.observacoes = f"Cobrança removida do Asaas em {timezone.now().strftime('%d/%m/%Y %H:%M')}"
                        cobranca.save()
                        
                    elif response.status_code == 401:
                        messages.error(request, "❌ Erro de autenticação com Asaas. Verifique a API Key.")
                    else:
                        messages.warning(request, f"⚠️ Erro ao consultar cobrança no Asaas: {response.status_code}")
                        
                except Exception as api_error:
                    logger.error(f"Erro ao verificar cobrança no Asaas: {str(api_error)}")
                    messages.warning(request, "⚠️ Não foi possível verificar o status da cobrança no Asaas.")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar cobrança {cobranca.asaas_id}: {str(e)}")
            messages.error(request, f"Erro ao atualizar: {str(e)}")
    
    # Log para debug se PDF não estiver disponível
    if not cobranca.bank_slip_url:
        logger.warning(f"PDF não disponível para cobrança {cobranca.asaas_id} - Status: {cobranca.status}")
        logger.info(f"Cobrança criada em: {cobranca.data_criacao}")
        logger.info(f"Última atualização: {cobranca.data_atualizacao}")
    
    # Verificar se precisa forçar atualização automática
    auto_refresh = False
    if not cobranca.bank_slip_url and cobranca.status == 'PENDING':
        # Se a cobrança foi criada há menos de 10 minutos e não tem PDF, auto-refresh
        from datetime import timedelta
        if cobranca.data_criacao > timezone.now() - timedelta(minutes=10):
            auto_refresh = True
    
    context = {
        'cobranca': cobranca,
        'controle': cobranca.controle_financeiro,
        'loja': cobranca.controle_financeiro.loja,
        'auto_refresh': auto_refresh,
        'pdf_debug_info': {
            'bank_slip_url': cobranca.bank_slip_url,
            'invoice_url': cobranca.invoice_url,
            'status': cobranca.status,
            'created_minutes_ago': int((timezone.now() - cobranca.data_criacao).total_seconds() / 60),
        }
    }
    
    return render(request, 'controle_financeiro/visualizar_cobranca_asaas.html', context)


@login_required
def listar_cobrancas_asaas(request):
    """
    Lista todas as cobranças do Asaas
    """
    try:
        # Debug: Log do usuário
        logger.info(f"Usuário acessando listagem: {request.user.username} (superuser: {request.user.is_superuser})")
        
        if request.user.is_superuser:
            # Super admin vê todas as cobranças
            cobrancas = CobrancaAsaas.objects.select_related('controle_financeiro__loja').all()
        else:
            # Admin de loja vê apenas suas cobranças
            cobrancas = CobrancaAsaas.objects.select_related('controle_financeiro__loja').filter(
                controle_financeiro__loja__admin=request.user
            )
        
        # Debug: Log da quantidade de cobranças
        logger.info(f"Total de cobranças encontradas: {cobrancas.count()}")
        
        # Filtros
        status_filter = request.GET.get('status')
        if status_filter:
            cobrancas = cobrancas.filter(status=status_filter)
            logger.info(f"Filtro de status aplicado: {status_filter}")
        
        loja_filter = request.GET.get('loja')
        if loja_filter and request.user.is_superuser:
            cobrancas = cobrancas.filter(controle_financeiro__loja__id=loja_filter)
            logger.info(f"Filtro de loja aplicado: {loja_filter}")
        
        # Ordenação
        cobrancas = cobrancas.order_by('-data_criacao')
        
        # Paginação
        from django.core.paginator import Paginator
        paginator = Paginator(cobrancas, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Debug: Log das cobranças na página atual
        logger.info(f"Cobranças na página atual: {len(page_obj.object_list)}")
        
        context = {
            'page_obj': page_obj,
            'cobrancas': page_obj.object_list,
            'status_filter': status_filter,
            'loja_filter': loja_filter,
        }
        
        return render(request, 'controle_financeiro/listar_cobrancas_asaas_simple.html', context)
        
    except Exception as e:
        logger.error(f"Erro na listagem de cobranças: {str(e)}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        
        # Em caso de erro, mostrar página com erro amigável
        from django.contrib import messages
        messages.error(request, f"Erro ao carregar cobranças: {str(e)}")
        
        # Contexto mínimo para evitar erro no template
        context = {
            'page_obj': None,
            'cobrancas': [],
            'status_filter': None,
            'loja_filter': None,
        }
        
        return render(request, 'controle_financeiro/listar_cobrancas_asaas_simple.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_debug(request):
    """
    Endpoint de debug para webhook - sem processamento, apenas retorna OK
    """
    logger.info(f"=== WEBHOOK DEBUG ENDPOINT ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"Path: {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
    logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'N/A')}")
    logger.info(f"Body length: {len(request.body)}")
    
    return HttpResponse("DEBUG OK", status=200)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_test(request):
    """
    Webhook de teste simples para debug
    """
    try:
        # Parsear dados do webhook
        webhook_data = json.loads(request.body.decode('utf-8'))
        
        logger.info(f"Webhook de teste recebido: {webhook_data}")
        
        return HttpResponse("OK - Webhook funcionando!", status=200)
        
    except json.JSONDecodeError:
        logger.error("Webhook com JSON inválido")
        return HttpResponse("Invalid JSON", status=400)
        
    except Exception as e:
        logger.error(f"Erro no webhook de teste: {str(e)}")
        return HttpResponse("Internal Error", status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_asaas(request):
    """
    Webhook para receber notificações do Asaas
    """
    try:
        # Log detalhado da requisição para debug
        logger.info(f"=== WEBHOOK ASAAS DEBUG ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'N/A')}")
        logger.info(f"Body length: {len(request.body)}")
        
        # Verificar se é uma requisição válida do Asaas
        # (Implementar validação de assinatura se necessário)
        
        # Parsear dados do webhook
        webhook_data = json.loads(request.body.decode('utf-8'))
        
        logger.info(f"Webhook recebido do Asaas: {webhook_data}")
        
        # Processar webhook
        asaas_service = AsaasService()
        resultado = asaas_service.processar_webhook(webhook_data)
        
        if resultado.get('success'):
            logger.info(f"Webhook processado com sucesso: {resultado.get('message')}")
            return HttpResponse("OK", status=200)
        else:
            logger.error(f"Erro ao processar webhook: {resultado.get('error')}")
            return HttpResponse("Error", status=400)
            
    except json.JSONDecodeError:
        logger.error("Webhook com JSON inválido")
        return HttpResponse("Invalid JSON", status=400)
        
    except Exception as e:
        logger.error(f"Erro no webhook Asaas: {str(e)}")
        return HttpResponse("Internal Error", status=500)


@login_required
def callback_success_asaas(request):
    """
    Callback de sucesso após pagamento no Asaas
    """
    payment_id = request.GET.get('payment_id')
    
    if payment_id:
        try:
            # Buscar cobrança
            cobranca = CobrancaAsaas.objects.get(asaas_id=payment_id)
            
            # Atualizar status
            asaas_service = AsaasService()
            dados_atualizados = asaas_service.consultar_cobranca(payment_id)
            
            if dados_atualizados:
                cobranca.atualizar_dados_asaas(dados_atualizados)
                
                if dados_atualizados.get('status') in ['RECEIVED', 'CONFIRMED']:
                    cobranca.marcar_como_paga()
                    messages.success(request, "Pagamento confirmado com sucesso!")
                else:
                    messages.info(request, f"Status do pagamento: {dados_atualizados.get('status')}")
            
            return redirect('controle_financeiro:visualizar_cobranca_asaas', cobranca_id=cobranca.id)
            
        except CobrancaAsaas.DoesNotExist:
            messages.error(request, "Cobrança não encontrada.")
            
        except Exception as e:
            logger.error(f"Erro no callback de sucesso: {str(e)}")
            messages.error(request, f"Erro ao processar callback: {str(e)}")
    
    return redirect('controle_financeiro:listar_cobrancas_asaas')


@login_required
def configurar_asaas(request):
    """
    Página de configuração da integração com Asaas
    """
    if not request.user.is_superuser:
        messages.error(request, "Apenas super administradores podem acessar as configurações.")
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Salvar configurações (implementar conforme necessário)
        api_key = request.POST.get('api_key')
        environment = request.POST.get('environment', 'sandbox')
        
        # Validar configuração
        try:
            # Temporariamente definir as configurações para teste
            original_api_key = getattr(settings, 'ASAAS_API_KEY', None)
            original_env = getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox')
            
            settings.ASAAS_API_KEY = api_key
            settings.ASAAS_ENVIRONMENT = environment
            
            asaas_service = AsaasService()
            if asaas_service.validar_configuracao():
                messages.success(request, "Configuração validada com sucesso!")
                # Aqui você salvaria as configurações no banco ou arquivo
            else:
                messages.error(request, "Configuração inválida. Verifique a API Key e o ambiente.")
                # Restaurar configurações originais
                settings.ASAAS_API_KEY = original_api_key
                settings.ASAAS_ENVIRONMENT = original_env
                
        except Exception as e:
            messages.error(request, f"Erro ao validar configuração: {str(e)}")
            # Restaurar configurações originais
            settings.ASAAS_API_KEY = original_api_key
            settings.ASAAS_ENVIRONMENT = original_env
    
    # Obter configurações atuais
    current_config = {
        'api_key': getattr(settings, 'ASAAS_API_KEY', ''),
        'environment': getattr(settings, 'ASAAS_ENVIRONMENT', 'sandbox'),
    }
    
    context = {
        'config': current_config,
    }
    
    return render(request, 'controle_financeiro/configurar_asaas.html', context)


@login_required
def testar_asaas(request):
    """
    Página para testar a integração com Asaas
    """
    if not request.user.is_superuser:
        messages.error(request, "Apenas super administradores podem testar a integração.")
        return redirect('dashboard:index')
    
    resultado_teste = None
    
    if request.method == 'POST':
        try:
            asaas_service = AsaasService()
            
            # Testar conexão
            if asaas_service.validar_configuracao():
                resultado_teste = {
                    'success': True,
                    'message': 'Conexão com Asaas estabelecida com sucesso!',
                    'environment': asaas_service.environment,
                    'base_url': asaas_service.base_url,
                    'conta_dados': asaas_service.conta_dados
                }
            else:
                resultado_teste = {
                    'success': False,
                    'message': 'Falha na conexão com Asaas. Verifique as configurações.'
                }
                
        except Exception as e:
            resultado_teste = {
                'success': False,
                'message': f'Erro ao testar conexão: {str(e)}'
            }
    
    # Obter configurações atuais
    from django.conf import settings as django_settings
    
    context = {
        'resultado_teste': resultado_teste,
        'settings': {
            'ASAAS_API_KEY': getattr(django_settings, 'ASAAS_API_KEY', ''),
            'ASAAS_ENVIRONMENT': getattr(django_settings, 'ASAAS_ENVIRONMENT', 'sandbox'),
        }
    }
    
    return render(request, 'controle_financeiro/testar_asaas.html', context)
    
    resultado_teste = None
    
    if request.method == 'POST':
        try:
            asaas_service = AsaasService()
            
            # Testar conexão
            if asaas_service.validar_configuracao():
                resultado_teste = {
                    'success': True,
                    'message': 'Conexão com Asaas estabelecida com sucesso!',
                    'environment': asaas_service.environment,
                    'base_url': asaas_service.base_url,
                    'conta_dados': asaas_service.conta_dados
                }
            else:
                resultado_teste = {
                    'success': False,
                    'message': 'Falha na conexão com Asaas. Verifique as configurações.'
                }
                
        except Exception as e:
            resultado_teste = {
                'success': False,
                'message': f'Erro ao testar conexão: {str(e)}'
            }
    
    context = {
        'resultado_teste': resultado_teste,
    }
    
    return render(request, 'controle_financeiro/testar_asaas.html', context)


@login_required
def criar_cobranca_asaas(request):
    """
    Página para criar nova cobrança no Asaas
    """
    if request.method == 'POST':
        try:
            controle_id = request.POST.get('controle_financeiro')
            dias_vencimento = int(request.POST.get('dias_vencimento', 30))
            descricao = request.POST.get('descricao', '')
            
            controle = get_object_or_404(ControleFinanceiro, id=controle_id)
            
            # Verificar permissões
            if not request.user.is_superuser and controle.loja.admin != request.user:
                messages.error(request, "Você não tem permissão para criar cobrança para esta loja.")
                return redirect('controle_financeiro:criar_cobranca_asaas')
            
            # Gerar cobrança
            asaas_service = AsaasService()
            resultado = asaas_service.gerar_cobranca_com_pix(
                controle, 
                dias_vencimento=dias_vencimento,
                descricao=descricao
            )
            
            if resultado.get('success'):
                messages.success(request, f'✅ Cobrança {resultado["cobranca"]["id"]} criada com sucesso!')
                return redirect('controle_financeiro:listar_cobrancas_asaas')
            else:
                messages.error(request, f'❌ Erro ao criar cobrança: {resultado.get("error", "Erro desconhecido")}')
                
        except Exception as e:
            logger.error(f"Erro ao criar cobrança: {str(e)}")
            messages.error(request, f'❌ Erro interno: {str(e)}')
    
    # Buscar controles financeiros disponíveis
    if request.user.is_superuser:
        controles = ControleFinanceiro.objects.filter(status='ativa')
    else:
        controles = ControleFinanceiro.objects.filter(
            loja__admin=request.user,
            status='ativa'
        )
    
    context = {
        'controles': controles,
    }
    
    return render(request, 'controle_financeiro/criar_cobranca_asaas.html', context)


@login_required
def excluir_cobranca_asaas(request, cobranca_id):
    """
    Exclui uma cobrança do Asaas
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        cobranca = get_object_or_404(CobrancaAsaas, id=cobranca_id)
        
        # Verificar permissões
        if not request.user.is_superuser and cobranca.controle_financeiro.loja.admin != request.user:
            return JsonResponse({'success': False, 'message': 'Você não tem permissão para excluir esta cobrança.'})
        
        # Permitir exclusão de qualquer status (como no painel Asaas)
        
        # Tentar cancelar/remover no Asaas baseado no status
        asaas_message = ""
        try:
            asaas_service = AsaasService()
            import requests
            
            if cobranca.status == 'PENDING':
                # Para cobranças pendentes, tentar cancelar
                response = requests.delete(
                    f"{asaas_service.base_url}/payments/{cobranca.asaas_id}",
                    headers=asaas_service.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"Cobrança {cobranca.asaas_id} cancelada no Asaas")
                    asaas_message = " e cancelada no Asaas"
                else:
                    logger.warning(f"Erro ao cancelar no Asaas: {response.status_code} - {response.text}")
                    asaas_message = " (erro ao cancelar no Asaas, mas removida do sistema)"
            else:
                # Para cobranças pagas/processadas, apenas remover do sistema local
                logger.info(f"Cobrança {cobranca.asaas_id} com status {cobranca.status} removida apenas do sistema local")
                asaas_message = " (mantida no histórico do Asaas)"
                
        except Exception as e:
            logger.error(f"Erro ao processar cobrança no Asaas: {str(e)}")
            asaas_message = " (erro na comunicação com Asaas, mas removida do sistema)"
        
        # Excluir do banco local
        asaas_id = cobranca.asaas_id
        cobranca.delete()
        
        logger.info(f"Cobrança {asaas_id} excluída do sistema por {request.user.username}")
        
        return JsonResponse({
            'success': True, 
            'message': f'Cobrança {asaas_id} excluída com sucesso{asaas_message}!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao excluir cobrança: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': f'Erro ao excluir cobrança: {str(e)}'
        })