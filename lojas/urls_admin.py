from django.urls import path
from . import views_admin

app_name = 'lojas_admin'

urlpatterns = [
    # Exclusão de loja
    path('loja/<uuid:loja_id>/confirmar-exclusao/', 
         views_admin.confirmar_exclusao_loja, 
         name='confirmar_exclusao_loja'),
    
    path('loja/<uuid:loja_id>/exclusao-rapida/', 
         views_admin.exclusao_rapida_loja, 
         name='exclusao_rapida_loja'),
]