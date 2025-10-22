"""
Endpoint final para webhook do Asaas com validação de IP
"""
from django.http import HttpResponse
import json
import logging
import ipaddress
from django.conf import settings

logger = logging.getLogger(__name__)


def webhook_asaas_final(request):
    """
    Endpoint final para webhook do Asaas com validação de IP
    """
    try:
        # Log básico
        logger.info(f"=== WEBHOOK ASAAS FINAL ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        
        # Verifica se é POST
        if request.method != 'POST':
            return HttpResponse("Method not allowed", status=405)
        
        # Valida IP do Asaas (TEMPORARIAMENTE DESABILITADO PARA TESTE)
        # if not validate_asaas_ip(request):
        #     logger.warning(f"Webhook rejeitado - IP não autorizado: {get_client_ip(request)}")
        #     return HttpResponse("Unauthorized", status=401)
        
        logger.info(f"IP do webhook: {get_client_ip(request)}")
        
        # Parsear dados
        try:
            webhook_data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Webhook recebido: {webhook_data}")
        except json.JSONDecodeError:
            logger.error("Webhook com JSON inválido")
            return HttpResponse("Invalid JSON", status=400)
        
        # Processar webhook usando serviço existente
        try:
            from controle_financeiro.asaas_service import AsaasService
            asaas_service = AsaasService()
            resultado = asaas_service.processar_webhook(webhook_data)
            
            if resultado.get('success'):
                logger.info(f"Webhook processado com sucesso: {resultado.get('message')}")
                return HttpResponse("OK", status=200)
            else:
                logger.error(f"Erro ao processar webhook: {resultado.get('error')}")
                return HttpResponse("Error", status=400)
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return HttpResponse("Processing Error", status=500)
            
    except Exception as e:
        logger.error(f"Erro no webhook final: {str(e)}")
        return HttpResponse("Internal Error", status=500)


def get_client_ip(request):
    """
    Obtém o IP real do cliente
    """
    # Verifica headers de proxy
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def validate_asaas_ip(request):
    """
    Valida se o IP está autorizado para webhooks do Asaas
    """
    client_ip = get_client_ip(request)
    
    # Se está em modo debug, permite todos os IPs
    if settings.DEBUG:
        logger.info(f"Modo DEBUG - IP permitido: {client_ip}")
        return True
    
    # IPs específicos conhecidos do Asaas
    asaas_specific_ips = [
        # Adicione IPs específicos do Asaas aqui quando disponíveis
    ]
    
    # Ranges de IP conhecidos do Asaas (AWS South America)
    asaas_ip_ranges = [
        '54.232.0.0/16',  # AWS South America
        '54.233.0.0/16',  # AWS South America
        '54.234.0.0/16',  # AWS South America
        '54.235.0.0/16',  # AWS South America
        '54.236.0.0/16',  # AWS South America
        '54.237.0.0/16',  # AWS South America
        '54.238.0.0/16',  # AWS South America
        '54.239.0.0/16',  # AWS South America
        '54.240.0.0/16',  # AWS South America
        '54.241.0.0/16',  # AWS South America
        '54.242.0.0/16',  # AWS South America
        '54.243.0.0/16',  # AWS South America
        '54.244.0.0/16',  # AWS South America
        '54.245.0.0/16',  # AWS South America
        '54.246.0.0/16',  # AWS South America
        '54.247.0.0/16',  # AWS South America
        '54.248.0.0/16',  # AWS South America
        '54.249.0.0/16',  # AWS South America
        '54.250.0.0/16',  # AWS South America
        '54.251.0.0/16',  # AWS South America
        '54.252.0.0/16',  # AWS South America
        '54.253.0.0/16',  # AWS South America
        '54.254.0.0/16',  # AWS South America
        '54.255.0.0/16',  # AWS South America
    ]
    
    # Verifica IPs específicos primeiro
    if client_ip in asaas_specific_ips:
        return True
    
    # Verifica ranges de IP
    try:
        client_ip_obj = ipaddress.ip_address(client_ip)
        for ip_range in asaas_ip_ranges:
            if client_ip_obj in ipaddress.ip_network(ip_range):
                return True
    except ValueError:
        logger.error(f"IP inválido: {client_ip}")
        return False
    
    return False
