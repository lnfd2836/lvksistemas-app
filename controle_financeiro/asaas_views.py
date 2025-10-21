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
                cobranca.atualizar_dados_asaas(dados_atualizados)
                messages.success(request, "Status da cobrança atualizado com sucesso!")
            else:
                messages.warning(request, "Não foi possível atualizar o status da cobrança.")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar cobrança: {str(e)}")
            messages.error(request, f"Erro ao atualizar: {str(e)}")
    
    context = {
        'cobranca': cobranca,
        'controle': cobranca.controle_financeiro,
        'loja': cobranca.controle_financeiro.loja,
    }
    
    return render(request, 'controle_financeiro/visualizar_cobranca_asaas.html', context)


@login_required
def listar_cobrancas_asaas(request):
    """
    Lista todas as cobranças do Asaas
    """
    if request.user.is_superuser:
        # Super admin vê todas as cobranças
        cobrancas = CobrancaAsaas.objects.all()
    else:
        # Admin de loja vê apenas suas cobranças
        cobrancas = CobrancaAsaas.objects.filter(
            controle_financeiro__loja__admin=request.user
        )
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        cobrancas = cobrancas.filter(status=status_filter)
    
    loja_filter = request.GET.get('loja')
    if loja_filter and request.user.is_superuser:
        cobrancas = cobrancas.filter(controle_financeiro__loja__id=loja_filter)
    
    # Ordenação
    cobrancas = cobrancas.order_by('-data_criacao')
    
    # Paginação (opcional)
    from django.core.paginator import Paginator
    paginator = Paginator(cobrancas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'cobrancas': page_obj.object_list,
        'status_choices': CobrancaAsaas.STATUS_CHOICES,
        'status_filter': status_filter,
        'loja_filter': loja_filter,
    }
    
    return render(request, 'controle_financeiro/listar_cobrancas_asaas.html', context)


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
    
    context = {
        'resultado_teste': resultado_teste,
    }
    
    return render(request, 'controle_financeiro/testar_asaas.html', context)