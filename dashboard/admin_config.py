"""
Configurações personalizadas para o Django Admin
"""
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from .admin_views import admin_index, admin_stats_api


class CustomAdminSite(admin.AdminSite):
    """
    Site administrativo personalizado com layout do sistema
    """
    
    # Configurações básicas
    site_title = 'LVK Sistemas Admin'
    site_header = 'LVK Sistemas - Administração'
    index_title = 'Dashboard Administrativo'
    
    def get_urls(self):
        """
        URLs personalizadas do admin
        """
        urls = super().get_urls()
        custom_urls = [
            path('', admin_index, name='index'),
            path('api/stats/', admin_stats_api, name='stats_api'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """
        View personalizada para a página inicial
        """
        return admin_index(request)


# Instância do site admin personalizado
admin_site = CustomAdminSite(name='custom_admin')