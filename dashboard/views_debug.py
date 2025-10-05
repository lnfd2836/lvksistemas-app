"""
Views de debug para testar o sistema de captura de erros.
"""
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from lojas.models import Loja


def test_500_error(request):
    """View que gera um erro 500 intencionalmente para testar o sistema."""
    # Gera diferentes tipos de erro baseado no parâmetro
    error_type = request.GET.get('type', 'generic')
    
    if error_type == 'database':
        # Erro de banco de dados
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tabela_inexistente")
    
    elif error_type == 'import':
        # Erro de importação
        import modulo_inexistente
    
    elif error_type == 'attribute':
        # Erro de atributo
        obj = None
        return obj.metodo_inexistente()
    
    elif error_type == 'template':
        # Erro de template
        return render(request, 'template_inexistente.html')
    
    elif error_type == 'model':
        # Erro de modelo
        loja = Loja.objects.get(id='uuid-inexistente')
        return HttpResponse(f"Loja: {loja.nome}")
    
    else:
        # Erro genérico
        raise Exception("Erro de teste gerado intencionalmente")


@login_required
def test_auth_error(request):
    """View que testa erros relacionados à autenticação."""
    # Força um erro no sistema de autenticação
    request.user.loja_admin.nome_inexistente
    return HttpResponse("Não deveria chegar aqui")


def test_middleware_error(request):
    """View que testa erros no middleware."""
    # Adiciona um atributo que pode causar problemas no middleware
    request.force_middleware_error = True
    return HttpResponse("Teste de middleware")


def debug_info(request):
    """View que mostra informações de debug do sistema."""
    from dashboard.utils.database_health import DatabaseHealthChecker
    from dashboard.middleware.middleware_profiler import create_middleware_diagnostics
    
    # Coleta informações de debug
    db_health = DatabaseHealthChecker.run_comprehensive_health_check()
    middleware_info = create_middleware_diagnostics()
    
    context = {
        'db_health': db_health,
        'middleware_info': middleware_info,
        'request_info': {
            'path': request.path,
            'method': request.method,
            'user': str(request.user),
            'session_key': request.session.session_key,
            'middleware_profile': getattr(request, 'middleware_profile', None),
        }
    }
    
    return render(request, 'debug/system_info.html', context)