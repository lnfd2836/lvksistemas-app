"""
Formulários para o app usuarios
"""
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re


class MandatoryPasswordChangeForm(PasswordChangeForm):
    """
    Formulário para troca obrigatória de senha com validações customizadas
    """
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        
        # Customiza labels e help text em português
        self.fields['old_password'].label = 'Senha Provisória Atual'
        self.fields['old_password'].help_text = 'Digite a senha provisória que você recebeu por email'
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite sua senha provisória atual'
        })
        
        self.fields['new_password1'].label = 'Nova Senha'
        self.fields['new_password1'].help_text = 'Mínimo 8 caracteres, incluindo letras e números'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite sua nova senha'
        })
        
        self.fields['new_password2'].label = 'Confirmar Nova Senha'
        self.fields['new_password2'].help_text = 'Digite a mesma senha novamente para confirmar'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua nova senha'
        })
    
    def clean_new_password1(self):
        """
        Validação customizada para a nova senha
        """
        password = self.cleaned_data.get('new_password1')
        
        if not password:
            raise ValidationError('Este campo é obrigatório.')
        
        # Validação de tamanho mínimo
        if len(password) < 8:
            raise ValidationError('A senha deve ter pelo menos 8 caracteres.')
        
        # Validação de tamanho máximo
        if len(password) > 128:
            raise ValidationError('A senha não pode ter mais de 128 caracteres.')
        
        # Deve conter pelo menos uma letra
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('A senha deve conter pelo menos uma letra.')
        
        # Deve conter pelo menos um número
        if not re.search(r'\d', password):
            raise ValidationError('A senha deve conter pelo menos um número.')
        
        # Não pode ser muito comum
        common_passwords = [
            '12345678', 'password', 'senha123', '123456789', 'qwerty123',
            'abc12345', 'password123', 'admin123', 'user1234', '87654321'
        ]
        
        if password.lower() in common_passwords:
            raise ValidationError('Esta senha é muito comum. Escolha uma senha mais segura.')
        
        # Não pode ser muito similar ao nome de usuário
        if hasattr(self, 'user') and self.user:
            username = self.user.username.lower()
            if username in password.lower() or password.lower() in username:
                raise ValidationError('A senha não pode ser muito similar ao seu nome de usuário.')
        
        return password
    
    def clean_new_password2(self):
        """
        Validação para confirmação de senha
        """
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('As duas senhas não coincidem.')
        
        return password2
    
    def save(self, commit=True):
        """
        Salva a nova senha e atualiza o perfil do usuário
        """
        user = super().save(commit=commit)
        
        if commit:
            # Atualiza o perfil do usuário
            try:
                from django.utils import timezone
                perfil = user.perfil
                perfil.requires_password_change = False
                perfil.password_changed_at = timezone.now()
                perfil.senha_alterada_em = timezone.now()  # Campo legado
                perfil.deve_trocar_senha = False  # Campo legado
                perfil.save()
            except Exception as e:
                # Log do erro mas não impede o salvamento da senha
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao atualizar perfil após troca de senha para {user.username}: {e}')
        
        return user


class UserPasswordResetForm(forms.Form):
    """
    Formulário para reset de senha por administradores
    """
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def save(self):
        """
        Gera nova senha provisória e marca usuário para troca obrigatória
        """
        import secrets
        import string
        from django.utils import timezone
        
        # Gera nova senha provisória
        alphabet = string.ascii_letters + string.digits
        nova_senha = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Define a nova senha
        self.user.set_password(nova_senha)
        self.user.save()
        
        # Atualiza perfil para forçar troca de senha
        try:
            perfil = self.user.perfil
            perfil.requires_password_change = True
            perfil.provisional_password_created = timezone.now()
            perfil.password_change_reminders_sent = 0
            perfil.save()
        except:
            # Cria perfil se não existir
            from .models import PerfilUsuario
            PerfilUsuario.objects.create(
                user=self.user,
                requires_password_change=True,
                provisional_password_created=timezone.now(),
                is_super_admin=self.user.is_superuser
            )
        
        return nova_senha