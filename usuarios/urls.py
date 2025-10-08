from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # URLs de autenticação padrão do Django
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # URLs para troca obrigatória de senha
    path('change-mandatory-password/', views.change_mandatory_password, name='change_mandatory_password'),
    path('password-change-success/', views.password_change_success, name='password_change_success'),
    path('api/check-password-requirement/', views.check_password_requirement, name='check_password_requirement'),
    path('api/password-strength/', views.password_strength_check, name='password_strength_check'),
]

