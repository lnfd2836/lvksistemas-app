from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.sessions.models import Session


class PerfilUsuario(models.Model):
    """Modelo para perfil estendido do usuário"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    endereco = models.TextField(blank=True, verbose_name="Endereço")
    
    # Controle de acesso
    is_loja_admin = models.BooleanField(default=False, verbose_name="Administrador de Loja")
    is_super_admin = models.BooleanField(default=False, verbose_name="Super Administrador")
    
    # Controle de sessão
    ultimo_acesso = models.DateTimeField(blank=True, null=True, verbose_name="Último Acesso")
    ip_ultimo_acesso = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP do Último Acesso")
    
    # Controle de senha
    deve_trocar_senha = models.BooleanField(default=True, verbose_name="Deve Trocar Senha")
    senha_alterada_em = models.DateTimeField(blank=True, null=True, verbose_name="Senha Alterada em")
    
    # Campos adicionais para controle de senha provisória
    requires_password_change = models.BooleanField(default=False, verbose_name="Requer Troca de Senha")
    provisional_password_created = models.DateTimeField(blank=True, null=True, verbose_name="Senha Provisória Criada em")
    password_changed_at = models.DateTimeField(blank=True, null=True, verbose_name="Senha Alterada em")
    password_change_reminders_sent = models.IntegerField(default=0, verbose_name="Lembretes de Troca Enviados")
    
    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"


class LogAcesso(models.Model):
    """Modelo para log de acessos dos usuários"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='logs_acesso', null=True)
    acao = models.CharField(max_length=50, verbose_name="Ação")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    user_agent = models.TextField(verbose_name="User Agent")
    data_acesso = models.DateTimeField(auto_now_add=True, verbose_name="Data do Acesso")
    sucesso = models.BooleanField(default=True, verbose_name="Sucesso")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ['-data_acesso']
    
    def __str__(self):
        return f"{self.user.username} - {self.acao} - {self.data_acesso}"


class SessaoAtiva(models.Model):
    """Modelo para rastrear sessões ativas dos usuários"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sessoes_ativas', null=True)
    session_key = models.CharField(max_length=40, unique=True, verbose_name="Chave da Sessão")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    user_agent = models.TextField(verbose_name="User Agent")
    data_login = models.DateTimeField(auto_now_add=True, verbose_name="Data do Login")
    ultima_atividade = models.DateTimeField(auto_now=True, verbose_name="Última Atividade")
    ativa = models.BooleanField(default=True, verbose_name="Sessão Ativa")
    is_super_admin = models.BooleanField(default=False, verbose_name="Sessão de Super Admin")
    
    class Meta:
        verbose_name = "Sessão Ativa"
        verbose_name_plural = "Sessões Ativas"
        ordering = ['-data_login']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key} - {self.data_login}"
    
    @classmethod
    def invalidar_sessoes_anteriores(cls, user, session_key_atual):
        """Invalida todas as sessões anteriores do usuário, exceto a atual (regra aplicada a TODOS os usuários)"""
        # Invalida todas as sessões anteriores para TODOS os usuários (incluindo Super Admins)
        cls.objects.filter(
            user=user,
            ativa=True
        ).exclude(
            session_key=session_key_atual
        ).update(ativa=False)
        
        # Remove qualquer sessão existente com a mesma session_key para evitar duplicatas
        cls.objects.filter(session_key=session_key_atual).delete()
    
    @classmethod
    def limpar_sessoes_expiradas(cls):
        """Remove sessões que não existem mais no banco de sessões do Django"""
        from django.contrib.sessions.models import Session
        
        # Pega todas as chaves de sessão ativas no nosso modelo
        sessoes_ativas = cls.objects.filter(ativa=True).values_list('session_key', flat=True)
        
        # Pega todas as sessões que ainda existem no Django
        sessoes_django = Session.objects.values_list('session_key', flat=True)
        
        # Remove sessões que não existem mais no Django
        sessoes_para_remover = set(sessoes_ativas) - set(sessoes_django)
        cls.objects.filter(session_key__in=sessoes_para_remover).update(ativa=False)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Registra o login do usuário e gerencia sessões ativas"""
    # Registra o log de acesso
    LogAcesso.objects.create(
        user=user,
        acao='LOGIN',
        ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        sucesso=True
    )
    
    # Garante que a sessão existe antes de acessar o session_key
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    
    # Invalida sessões anteriores do usuário (sessão única)
    SessaoAtiva.invalidar_sessoes_anteriores(user, session_key)
    
    # Cria nova sessão ativa (usando get_or_create para evitar duplicatas)
    SessaoAtiva.objects.get_or_create(
        session_key=session_key,
        defaults={
            'user': user,
            'ip_address': request.META.get('REMOTE_ADDR', '127.0.0.1'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ativa': True,
            'is_super_admin': user.is_superuser
        }
    )
    
    # Atualiza perfil do usuário
    if hasattr(user, 'perfil'):
        user.perfil.ultimo_acesso = timezone.now()
        user.perfil.ip_ultimo_acesso = request.META.get('REMOTE_ADDR')
        user.perfil.save()


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Registra o logout do usuário e remove sessão ativa"""
    if user and user.is_authenticated:
        # Registra o log de logout
        LogAcesso.objects.create(
            user=user,
            acao='LOGOUT',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            sucesso=True
        )
        
        # Remove a sessão ativa
        session_key = request.session.session_key
        if session_key:
            SessaoAtiva.objects.filter(
                user=user,
                session_key=session_key
            ).update(ativa=False)
