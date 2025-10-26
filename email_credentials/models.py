"""
Modelos para o sistema de credenciais por email
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class ExtendedUserProfile(models.Model):
    """
    Perfil estendido no banco principal - controle de acesso e roteamento
    """
    
    USER_TYPE_CHOICES = [
        ('super_admin', 'Super Administrador'),
        ('loja_admin', 'Administrador de Loja'),
        ('loja_user', 'Usuário de Loja'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='extended_profile',
        verbose_name="Usuário"
    )
    
    # Controle de senha
    has_provisional_password = models.BooleanField(
        default=False,
        verbose_name="Tem senha provisória"
    )
    provisional_password_created = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Data criação senha provisória"
    )
    password_changed_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Data última alteração de senha"
    )
    
    # Contexto do usuário
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='loja_user',
        verbose_name="Tipo de usuário"
    )
    
    # Associação com loja (para roteamento de banco)
    associated_loja = models.ForeignKey(
        'lojas.Loja',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='extended_profiles',
        verbose_name="Loja associada"
    )
    
    # Configuração de banco individual
    database_alias = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name="Alias do banco"
    )
    
    # Auditoria
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        related_name='created_extended_profiles', 
        null=True,
        blank=True,
        verbose_name="Criado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    last_login_attempt = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Última tentativa de login"
    )
    
    class Meta:
        verbose_name = "Perfil Estendido de Usuário"
        verbose_name_plural = "Perfis Estendidos de Usuário"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    def requires_password_change(self):
        """Verifica se o usuário precisa alterar a senha"""
        return self.has_provisional_password
    
    def mark_password_as_permanent(self):
        """Marca a senha como permanente após alteração"""
        self.has_provisional_password = False
        self.password_changed_at = timezone.now()
        self.save()
    
    def get_loja_database(self):
        """Retorna o alias do banco da loja"""
        if self.associated_loja:
            return f"loja_{self.associated_loja.id}"
        return 'default'
    
    def can_access_loja(self, loja):
        """Verifica se pode acessar uma loja específica"""
        if self.user_type == 'super_admin':
            return True
        return self.associated_loja == loja


class LojaUserProfile(models.Model):
    """
    Perfil específico no banco individual da loja
    Contém dados detalhados do usuário
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.IntegerField(
        unique=True,
        verbose_name="ID do usuário principal"
    )
    username = models.CharField(
        max_length=150, 
        unique=True,
        verbose_name="Nome de usuário"
    )
    
    # Perfil de acesso dentro da loja
    loja_access_profile = models.CharField(
        max_length=50,
        verbose_name="Perfil de acesso na loja"
    )
    
    # Dados específicos da loja
    permissions = models.JSONField(
        default=dict,
        verbose_name="Permissões específicas"
    )
    settings = models.JSONField(
        default=dict,
        verbose_name="Configurações do usuário"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    # Auditoria no banco da loja
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    last_access = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Último acesso"
    )
    
    class Meta:
        verbose_name = "Perfil de Usuário da Loja"
        verbose_name_plural = "Perfis de Usuários da Loja"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.loja_access_profile})"
    
    def update_last_access(self):
        """Atualiza timestamp do último acesso"""
        self.last_access = timezone.now()
        self.save(update_fields=['last_access'])
    
    def has_permission(self, permission_key):
        """Verifica se tem uma permissão específica"""
        return self.permissions.get(permission_key, False)
    
    def set_permission(self, permission_key, value):
        """Define uma permissão específica"""
        self.permissions[permission_key] = value
        self.save(update_fields=['permissions'])
    
    def get_setting(self, setting_key, default=None):
        """Obtém uma configuração específica"""
        return self.settings.get(setting_key, default)
    
    def set_setting(self, setting_key, value):
        """Define uma configuração específica"""
        self.settings[setting_key] = value
        self.save(update_fields=['settings'])


class EmailLog(models.Model):
    """
    Log de emails enviados para auditoria
    """
    
    EMAIL_TYPE_CHOICES = [
        ('credentials', 'Credenciais'),
        ('recovery', 'Recuperação de senha'),
        ('notification', 'Notificação'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Destinatário
    to_email = models.EmailField(verbose_name="Email destinatário")
    subject = models.CharField(max_length=200, verbose_name="Assunto")
    
    # Tipo e status
    email_type = models.CharField(
        max_length=20, 
        choices=EMAIL_TYPE_CHOICES,
        default='credentials',
        verbose_name="Tipo de email"
    )
    success = models.BooleanField(verbose_name="Enviado com sucesso")
    error_message = models.TextField(
        blank=True,
        verbose_name="Mensagem de erro"
    )
    
    # Relacionamentos
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
        verbose_name="Usuário"
    )
    loja = models.ForeignKey(
        'lojas.Loja',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
        verbose_name="Loja"
    )
    
    # Auditoria
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado em")
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="Endereço IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    # Metadados
    attempts = models.IntegerField(
        default=1,
        verbose_name="Tentativas de envio"
    )
    fallback_used = models.BooleanField(
        default=False,
        verbose_name="Fallback utilizado"
    )
    
    class Meta:
        verbose_name = "Log de Email"
        verbose_name_plural = "Logs de Email"
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'email_type']),
            models.Index(fields=['loja', 'sent_at']),
            models.Index(fields=['success', 'sent_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.get_email_type_display()} para {self.to_email}"
    
    @classmethod
    def get_success_rate(cls, days=30):
        """Calcula taxa de sucesso dos últimos N dias"""
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        total = cls.objects.filter(sent_at__gte=cutoff_date).count()
        if total == 0:
            return 0
        
        successful = cls.objects.filter(
            sent_at__gte=cutoff_date, 
            success=True
        ).count()
        
        return (successful / total) * 100
    
    @classmethod
    def get_stats_by_type(cls, days=30):
        """Retorna estatísticas por tipo de email"""
        from datetime import timedelta
        from django.db.models import Count, Q
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        stats = cls.objects.filter(sent_at__gte=cutoff_date).values('email_type').annotate(
            total=Count('id'),
            successful=Count('id', filter=Q(success=True)),
            failed=Count('id', filter=Q(success=False))
        )
        
        return list(stats)
    
    @classmethod
    def get_recent_failures(cls, limit=10):
        """Retorna falhas recentes para análise"""
        return cls.objects.filter(success=False).order_by('-sent_at')[:limit]


class PasswordRecoveryAttempt(models.Model):
    """
    Controle de tentativas de recuperação de senha para rate limiting
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Usuário e identificação
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='recovery_attempts',
        verbose_name="Usuário"
    )
    email_or_username = models.CharField(
        max_length=254,
        verbose_name="Email ou username usado"
    )
    
    # Controle
    attempted_at = models.DateTimeField(auto_now_add=True, verbose_name="Tentativa em")
    success = models.BooleanField(verbose_name="Sucesso")
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="Endereço IP"
    )
    
    class Meta:
        verbose_name = "Tentativa de Recuperação"
        verbose_name_plural = "Tentativas de Recuperação"
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['user', 'attempted_at']),
            models.Index(fields=['ip_address', 'attempted_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} Recuperação para {self.user.username} em {self.attempted_at}"
    
    @classmethod
    def can_attempt_recovery(cls, user, hours=1, max_attempts=3):
        """
        Verifica se o usuário pode tentar recuperação baseado no rate limiting
        """
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        recent_attempts = cls.objects.filter(
            user=user,
            attempted_at__gte=cutoff_time
        ).count()
        
        return recent_attempts < max_attempts
    
    @classmethod
    def record_attempt(cls, user, email_or_username, success, ip_address=None):
        """
        Registra uma tentativa de recuperação
        """
        return cls.objects.create(
            user=user,
            email_or_username=email_or_username,
            success=success,
            ip_address=ip_address
        )