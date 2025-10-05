"""
Utilitários para validação de URLs e padrões
"""
import logging
from django.urls import reverse, NoReverseMatch
from django.conf import settings

logger = logging.getLogger(__name__)


class URLValidator:
    """
    Classe para validar URLs e padrões de URL
    """
    
    @staticmethod
    def validate_url_pattern(url_name, **kwargs):
        """
        Valida se um padrão de URL pode ser resolvido
        
        Args:
            url_name (str): Nome da URL a ser validada
            **kwargs: Argumentos para a URL
            
        Returns:
            tuple: (is_valid, url_or_error)
        """
        try:
            url = reverse(url_name, kwargs=kwargs)
            return True, url
        except NoReverseMatch as e:
            logger.warning(f"URL pattern validation failed: {url_name} - {str(e)}")
            return False, str(e)
    
    @staticmethod
    def validate_dashboard_urls():
        """
        Valida todas as URLs críticas do dashboard
        
        Returns:
            dict: Resultado da validação de cada URL
        """
        results = {}
        
        # URLs básicas do dashboard
        basic_urls = [
            'dashboard:principal',
            'dashboard:super_admin',
            'dashboard:loja',
            'dashboard:admin_usuarios_lista',
            'dashboard:admin_usuarios_criar',
            'dashboard:api_estatisticas',
        ]
        
        for url_name in basic_urls:
            is_valid, result = URLValidator.validate_url_pattern(url_name)
            results[url_name] = {
                'valid': is_valid,
                'result': result
            }
        
        # URLs com parâmetros
        param_urls = [
            ('dashboard:loja_especifica', {'loja_id': '12345678-1234-1234-1234-123456789012'}),
            ('dashboard:admin_usuarios_editar', {'user_id': 1}),
            ('dashboard:admin_usuarios_alterar_senha', {'user_id': 1}),
            ('dashboard:admin_usuarios_excluir', {'user_id': 1}),
        ]
        
        for url_name, params in param_urls:
            is_valid, result = URLValidator.validate_url_pattern(url_name, **params)
            results[url_name] = {
                'valid': is_valid,
                'result': result,
                'params': params
            }
        
        return results
    
    @staticmethod
    def validate_loja_urls():
        """
        Valida URLs relacionadas às lojas
        
        Returns:
            dict: Resultado da validação de cada URL
        """
        results = {}
        
        # URLs básicas de lojas
        basic_urls = [
            'listar_lojas',
            'criar_loja',
        ]
        
        for url_name in basic_urls:
            is_valid, result = URLValidator.validate_url_pattern(url_name)
            results[url_name] = {
                'valid': is_valid,
                'result': result
            }
        
        # URLs com parâmetros UUID
        param_urls = [
            ('editar_loja', {'loja_id': '12345678-1234-1234-1234-123456789012'}),
            ('detalhar_loja', {'loja_id': '12345678-1234-1234-1234-123456789012'}),
            ('excluir_loja', {'loja_id': '12345678-1234-1234-1234-123456789012'}),
        ]
        
        for url_name, params in param_urls:
            is_valid, result = URLValidator.validate_url_pattern(url_name, **params)
            results[url_name] = {
                'valid': is_valid,
                'result': result,
                'params': params
            }
        
        return results
    
    @staticmethod
    def generate_validation_report():
        """
        Gera um relatório completo de validação de URLs
        
        Returns:
            dict: Relatório completo com todas as validações
        """
        report = {
            'dashboard_urls': URLValidator.validate_dashboard_urls(),
            'loja_urls': URLValidator.validate_loja_urls(),
            'summary': {
                'total_urls': 0,
                'valid_urls': 0,
                'invalid_urls': 0,
                'errors': []
            }
        }
        
        # Calcular estatísticas
        all_results = {**report['dashboard_urls'], **report['loja_urls']}
        
        for url_name, result in all_results.items():
            report['summary']['total_urls'] += 1
            
            if result['valid']:
                report['summary']['valid_urls'] += 1
            else:
                report['summary']['invalid_urls'] += 1
                report['summary']['errors'].append({
                    'url_name': url_name,
                    'error': result['result']
                })
        
        return report


def log_url_validation_report():
    """
    Executa e registra um relatório de validação de URLs
    """
    if settings.DEBUG:
        report = URLValidator.generate_validation_report()
        
        logger.info("=== URL Validation Report ===")
        logger.info(f"Total URLs: {report['summary']['total_urls']}")
        logger.info(f"Valid URLs: {report['summary']['valid_urls']}")
        logger.info(f"Invalid URLs: {report['summary']['invalid_urls']}")
        
        if report['summary']['errors']:
            logger.warning("URL Validation Errors:")
            for error in report['summary']['errors']:
                logger.warning(f"  - {error['url_name']}: {error['error']}")
        else:
            logger.info("All URLs validated successfully!")
        
        return report
    
    return None