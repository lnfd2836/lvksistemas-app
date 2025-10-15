"""
URL configuration for lojad project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from dashboard.views import redirect_to_appropriate_dashboard
from dashboard.loja_login import loja_login
from dashboard.simple_login import simple_login

def estetica_redirect(request):
    """Redireciona /estetica/ para /modulos/estetica/"""
    return redirect('/modulos/estetica/')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root URL redireciona inteligentemente baseado no usuário
    path('', redirect_to_appropriate_dashboard, name='root_redirect'),
    
    # URLs principais
    path('dashboard/', include('dashboard.urls')),
    path('lojas/', include('lojas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('planos/', include('planos.urls')),
    path('financeiro/', include('controle_financeiro.urls')),
    path('modulos/', include('modulos.urls')),
    
    # Redirecionamento para clínica de estética
    path('estetica/', estetica_redirect, name='estetica_redirect'),
    path('estetica/<path:path>', lambda request, path: redirect(f'/modulos/estetica/{path}')),
    
    # URLs de autenticação - ordem importante para evitar conflitos
    path('login/', simple_login, name='simple_login'),
    path('loja/login/', loja_login, name='loja_login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
