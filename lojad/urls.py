"""
URL configuration for lojad project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from dashboard.loja_login import loja_login
from dashboard.simple_login import simple_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('/login/')),
    path('dashboard/', include('dashboard.urls')),
    path('lojas/', include('lojas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('planos/', include('planos.urls')),
    path('financeiro/', include('controle_financeiro.urls')),
    path('modulos/', include('modulos.urls')),
    path('login/', simple_login, name='login'),  # URL direta para login
    path('loja/login/', loja_login, name='loja_login_direct'),  # URL direta para login da loja
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
