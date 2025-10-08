"""
Tasks do Celery para controle financeiro
"""

from celery import shared_task
from django.utils import timezone
from .services import BoletoService, FinanceiroService
import logging

logger = logging.getLogger(__name__)


@shared_task
def gerar_boletos_automaticos_task(dias_antecedencia=10):
    """
    Task para gerar boletos automaticamente
    Deve ser executada diariamente
    """
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


# Task combinada que executa todas as operações diárias
@shared_task
def executar_rotinas_financeiras_diarias():
    """
    Task principal que executa todas as rotinas financeiras diárias
    """
    try:
        resultados = {}
        
        # 1. Verificar vencimentos
        resultados['vencimentos'] = verificar_vencimentos_task.delay().get()
        
        # 2. Gerar boletos automáticos (10 dias antes)
        resultados['boletos'] = gerar_boletos_automaticos_task.delay(10).get()
        
        # 3. Verificar boletos vencidos
        resultados['boletos_vencidos'] = verificar_boletos_vencidos_task.delay().get()
        
        # 4. Processar renovações automáticas
        resultados['renovacoes'] = processar_renovacoes_automaticas_task.delay().get()
        
        logger.info("Rotinas financeiras diárias executadas com sucesso")
        return resultados
        
    except Exception as e:
        logger.error(f"Erro nas rotinas financeiras diárias: {str(e)}")
        raise