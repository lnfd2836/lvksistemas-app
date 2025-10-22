"""
URLs específicas para webhooks - sem middlewares
"""
from django.urls import path
from controle_financeiro.webhook_direct import webhook_asaas_direct

# URLs que bypassam middlewares de autenticação
urlpatterns = [
    path('asaas-webhook-direct/', webhook_asaas_direct, name='webhook_asaas_direct'),
]
