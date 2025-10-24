from django.contrib import admin

# Todos os modelos do dashboard já estão registrados em lojas/admin.py
# para evitar conflitos de registro duplicado

# Importar admin personalizado para exclusão segura de usuários
from . import admin_user_safe