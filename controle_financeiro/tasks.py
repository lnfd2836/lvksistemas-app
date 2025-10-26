"""
Tasks automáticas para o sistema financeiro
"""
from django.utils import timezone
from datetime import timedelta
from .models import ControleFinanceiro, CobrancaAsaas

# Importações condicionais para Celery
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    # Celery não está instalado - criar decorator dummy
    def shared_task(func):
        return func
    CELERY_AVAILABLE = False

from django.utils import timezone
from .asaas_sync_service import AsaasSyncService
import logging

logger = logging.getLogger(__name__)

# Importações condicionais para evitar erros se módulos não existirem
try:
    from .services import BoletoService, FinanceiroService
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    logger.warning("Serviços de boleto não disponíveis")


@shared_task
def gerar_boletos_automaticos_task(dias_antecedencia=10):
    """
    Task para gerar boletos automaticamente
    Deve ser executada diariamente
    """
    if not SERVICES_AVAILABLE:
        logger.warning("Serviços de boleto não disponíveis")
        return {'error': 'Serviços não disponíveis'}
    
    try:
        boleto_service = BoletoService()
        resultado = boleto_service.gerar_boletos_automaticos(dias_antecedencia)
        
        logger.info(
            f"Boletos automáticos gerados: {resultado['boletos_gerados']} novos, "
            f"{resultado['boletos_ja_existentes']} já existentes, "
            f"{len(resultado['erros'])} erros"
        )
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao gerar boletos automáticos: {str(e)}")
        raise


@shared_task
def verificar_vencimentos_task():
    """
    Task para verificar vencimentos automaticamente
    Deve ser executada diariamente
    """
    if not SERVICES_AVAILABLE:
        logger.warning("Serviços financeiros não disponíveis")
        return {'error': 'Serviços não disponíveis'}
    
    try:
        financeiro_service = FinanceiroService()
        resultado = financeiro_service.verificar_vencimentos_automatico()
        
        logger.info(
            f"Vencimentos verificados: {resultado['total_verificados']} total, "
            f"{resultado['atualizados']} atualizados, "
            f"{resultado['bloqueados']} bloqueados"
        )
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao verificar vencimentos: {str(e)}")
        raise


@shared_task
def verificar_boletos_vencidos_task():
    """
    Task para verificar e atualizar boletos vencidos
    Deve ser executada diariamente
    """
    if not SERVICES_AVAILABLE:
        logger.warning("Serviços de boleto não disponíveis")
        return {'error': 'Serviços não disponíveis'}
    
    try:
        boleto_service = BoletoService()
        boletos_atualizados = boleto_service.verificar_boletos_vencidos()
        
        logger.info(f"Boletos vencidos atualizados: {boletos_atualizados}")
        
        return {'boletos_atualizados': boletos_atualizados}
        
    except Exception as e:
        logger.error(f"Erro ao verificar boletos vencidos: {str(e)}")
        raise


@shared_task
def processar_renovacoes_automaticas_task():
    """
    Task para processar renovações automáticas
    Deve ser executada diariamente
    """
    if not SERVICES_AVAILABLE:
        logger.warning("Serviços financeiros não disponíveis")
        return {'error': 'Serviços não disponíveis'}
    
    try:
        financeiro_service = FinanceiroService()
        resultado = financeiro_service.processar_renovacoes_automaticas()
        
        logger.info(
            f"Renovações processadas: {resultado['renovacoes_processadas']}, "
            f"erros: {len(resultado['erros'])}"
        )
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao processar renovações automáticas: {str(e)}")
        raise


# === TASKS DE SINCRONIZAÇÃO ASAAS ===

@shared_task
def sync_asaas_charges_task():
    """
    Task para sincronizar cobranças com Asaas
    Deve ser executada a cada 5 minutos
    """
    try:
        sync_service = AsaasSyncService()
        resultado = sync_service.sync_all_charges()
        
        logger.info(
            f"Sincronização Asaas concluída: {resultado['total_processed']} processadas, "
            f"{resultado['updates_made']} atualizadas, "
            f"{resultado['new_charges']} novas, "
            f"{len(resultado['errors'])} erros"
        )
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na sincronização Asaas: {str(e)}")
        raise


@shared_task
def sync_single_asaas_charge_task(asaas_id):
    """
    Task para sincronizar uma cobrança específica
    """
    try:
        sync_service = AsaasSyncService()
        resultado = sync_service.sync_single_charge(asaas_id)
        
        logger.info(f"Cobrança {asaas_id} sincronizada: {resultado}")
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao sincronizar cobrança {asaas_id}: {str(e)}")
        raise


@shared_task
def monitor_asaas_payments_task():
    """
    Task para monitorar pagamentos no Asaas
    Deve ser executada a cada 2 minutos
    """
    try:
        from .models import CobrancaAsaas
        from .asaas_service import AsaasService
        
        asaas_service = AsaasService()
        
        # Buscar cobranças pendentes dos últimos 30 dias
        data_limite = timezone.now() - timezone.timedelta(days=30)
        cobrancas_pendentes = CobrancaAsaas.objects.filter(
            status__in=['PENDING', 'OVERDUE'],
            data_criacao__gte=data_limite
        )
        
        atualizadas = 0
        pagamentos_processados = 0
        
        for cobranca in cobrancas_pendentes:
            try:
                # Consultar status atual
                dados_asaas = asaas_service.consultar_cobranca(cobranca.asaas_id)
                
                if dados_asaas:
                    status_anterior = cobranca.status
                    cobranca.atualizar_dados_asaas(dados_asaas)
                    
                    if cobranca.status != status_anterior:
                        atualizadas += 1
                        
                        # Se foi pago, processar pagamento
                        if cobranca.status in ['RECEIVED', 'CONFIRMED'] and status_anterior not in ['RECEIVED', 'CONFIRMED']:
                            cobranca.marcar_como_paga()
                            pagamentos_processados += 1
                            logger.info(f"Pagamento processado automaticamente: {cobranca.asaas_id}")
                
            except Exception as e:
                logger.error(f"Erro ao monitorar cobrança {cobranca.asaas_id}: {str(e)}")
        
        resultado = {
            'cobrancas_verificadas': cobrancas_pendentes.count(),
            'atualizadas': atualizadas,
            'pagamentos_processados': pagamentos_processados
        }
        
        logger.info(f"Monitoramento Asaas: {resultado}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro no monitoramento Asaas: {str(e)}")
        raise


@shared_task
def cleanup_old_sync_data_task():
    """
    Task para limpeza de dados antigos de sincronização
    Deve ser executada semanalmente
    """
    try:
        from .models import CobrancaAsaas
        
        # Remover cobranças muito antigas (mais de 1 ano) que estão pagas
        data_limite = timezone.now() - timezone.timedelta(days=365)
        
        cobrancas_antigas = CobrancaAsaas.objects.filter(
            status__in=['RECEIVED', 'CONFIRMED', 'REFUNDED'],
            data_criacao__lt=data_limite
        )
        
        count = cobrancas_antigas.count()
        cobrancas_antigas.delete()
        
        logger.info(f"Limpeza concluída: {count} cobranças antigas removidas")
        
        return {'cobrancas_removidas': count}
        
    except Exception as e:
        logger.error(f"Erro na limpeza de dados: {str(e)}")
        raise


# Task combinada que executa todas as operações diárias
@shared_task
def executar_rotinas_financeiras_diarias():
    """
    Task principal que executa todas as rotinas financeiras diárias
    """
    try:
        resultados = {}
        
        # 1. Verificar vencimentos - se disponível
        if SERVICES_AVAILABLE:
            if CELERY_AVAILABLE:
                resultados['vencimentos'] = verificar_vencimentos_task.delay().get()
            else:
                resultados['vencimentos'] = verificar_vencimentos_task()
        
        # 2. Gerar boletos automáticos (10 dias antes) - se disponível
        if SERVICES_AVAILABLE:
            if CELERY_AVAILABLE:
                resultados['boletos'] = gerar_boletos_automaticos_task.delay(10).get()
            else:
                resultados['boletos'] = gerar_boletos_automaticos_task(10)
        
        # 3. Verificar boletos vencidos - se disponível
        if SERVICES_AVAILABLE:
            if CELERY_AVAILABLE:
                resultados['boletos_vencidos'] = verificar_boletos_vencidos_task.delay().get()
            else:
                resultados['boletos_vencidos'] = verificar_boletos_vencidos_task()
        
        # 4. Processar renovações automáticas - se disponível
        if SERVICES_AVAILABLE:
            if CELERY_AVAILABLE:
                resultados['renovacoes'] = processar_renovacoes_automaticas_task.delay().get()
            else:
                resultados['renovacoes'] = processar_renovacoes_automaticas_task()
        
        # 5. Sincronizar com Asaas
        if CELERY_AVAILABLE:
            resultados['sync_asaas'] = sync_asaas_charges_task.delay().get()
        else:
            resultados['sync_asaas'] = sync_asaas_charges_task()
        
        # 6. Monitorar pagamentos Asaas
        if CELERY_AVAILABLE:
            resultados['monitor_asaas'] = monitor_asaas_payments_task.delay().get()
        else:
            resultados['monitor_asaas'] = monitor_asaas_payments_task()
        
        logger.info("Rotinas financeiras diárias executadas com sucesso")
        return resultados
        
    except Exception as e:
        logger.error(f"Erro nas rotinas financeiras diárias: {str(e)}")
        raise


# Task para execução contínua (a cada 5 minutos)
@shared_task
def executar_rotinas_continuas():
    """
    Task para rotinas que devem ser executadas continuamente
    """
    try:
        resultados = {}
        
        # Sincronização Asaas
        if CELERY_AVAILABLE:
            resultados['sync_asaas'] = sync_asaas_charges_task.delay().get()
        else:
            resultados['sync_asaas'] = sync_asaas_charges_task()
        
        # Monitoramento de pagamentos
        if CELERY_AVAILABLE:
            resultados['monitor_asaas'] = monitor_asaas_payments_task.delay().get()
        else:
            resultados['monitor_asaas'] = monitor_asaas_payments_task()
        
        return resultados
        
    except Exception as e:
        logger.error(f"Erro nas rotinas contínuas: {str(e)}")
        raise

"""
Tasks do Celery para processamento automático de notificações
"""

from celery import shared_task
from django.utils import timezone
from .email_notification_service import email_service
import logging

logger = logging.getLogger(__name__)


@shared_task
def processar_notificacoes_boleto():
    """
    Task para processar notificações de boletos automaticamente
    Deve ser executada diariamente
    """
    try:
        logger.info("Iniciando processamento automático de notificações de boleto")
        
        enviados = email_service.processar_notificacoes_pendentes()
        
        logger.info(f"Processamento automático concluído: {enviados} emails enviados")
        
        return {
            'success': True,
            'emails_enviados': enviados,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no processamento automático de notificações: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def enviar_boleto_especifico(cobranca_id, dias_antecedencia=10):
    """
    Task para enviar boleto específico por email
    
    Args:
        cobranca_id: ID da cobrança
        dias_antecedencia: Dias de antecedência (padrão: 10)
    """
    try:
        from .models import CobrancaAsaas
        
        cobranca = CobrancaAsaas.objects.get(id=cobranca_id)
        
        sucesso = email_service.enviar_boleto_por_email(cobranca, dias_antecedencia)
        
        return {
            'success': sucesso,
            'cobranca_id': str(cobranca_id),
            'asaas_id': cobranca.asaas_id,
            'timestamp': timezone.now().isoformat()
        }
        
    except CobrancaAsaas.DoesNotExist:
        logger.error(f"Cobrança {cobranca_id} não encontrada")
        return {
            'success': False,
            'error': 'Cobrança não encontrada',
            'cobranca_id': str(cobranca_id)
        }
    except Exception as e:
        logger.error(f"Erro ao enviar boleto específico {cobranca_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'cobranca_id': str(cobranca_id)
        }
