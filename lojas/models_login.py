from django.db import models
from django.core.validators import FileExtensionValidator
from lojas.models import Loja
import uuid


class LoginPersonalizado(models.Model):
    """Modelo para configurações de login personalizadas por loja"""
    
    TEMA_CHOICES = [
        ('padrao', 'Padrão'),
        ('moderno', 'Moderno'),
        ('minimalista', 'Minimalista'),
        ('corporativo', 'Corporativo'),
        ('personalizado', 'Personalizado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loja = models.OneToOneField(
        Loja, 
        on_delete=models.CASCADE, 
        related_name='login_personalizado',
        verbose_name="Loja"
    )
    
    # Configurações visuais
    titulo = models.CharField(
        max_length=200, 
        default="Login",
        verbose_name="Título da Página"
    )
    subtitulo = models.CharField(
        max_length=300, 
        blank=True,
        verbose_name="Subtítulo"
    )
    
    # Logo e imagens
    logo = models.ImageField(
        upload_to='login_personalizado/logos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])],
        verbose_name="Logo da Loja"
    )
    imagem_fundo = models.ImageField(
        upload_to='login_personalizado/fundos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Imagem de Fundo"
    )
    
    # Cores personalizadas
    cor_primaria = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name="Cor Primária",
        help_text="Formato hexadecimal (#000000)"
    )
    cor_secundaria = models.CharField(
        max_length=7,
        default="#6c757d",
        verbose_name="Cor Secundária",
        help_text="Formato hexadecimal (#000000)"
    )
    cor_fundo = models.CharField(
        max_length=7,
        default="#ffffff",
        verbose_name="Cor de Fundo",
        help_text="Formato hexadecimal (#000000)"
    )
    cor_texto = models.CharField(
        max_length=7,
        default="#333333",
        verbose_name="Cor do Texto",
        help_text="Formato hexadecimal (#000000)"
    )
    
    # Tema e layout
    tema = models.CharField(
        max_length=20,
        choices=TEMA_CHOICES,
        default='padrao',
        verbose_name="Tema"
    )
    
    # CSS personalizado
    css_personalizado = models.TextField(
        blank=True,
        verbose_name="CSS Personalizado",
        help_text="CSS adicional para personalização avançada"
    )
    
    # Configurações de comportamento
    mostrar_logo = models.BooleanField(
        default=True,
        verbose_name="Mostrar Logo"
    )
    mostrar_nome_loja = models.BooleanField(
        default=True,
        verbose_name="Mostrar Nome da Loja"
    )
    permitir_lembrar_senha = models.BooleanField(
        default=True,
        verbose_name="Permitir 'Lembrar de Mim'"
    )
    mostrar_link_recuperar_senha = models.BooleanField(
        default=True,
        verbose_name="Mostrar Link 'Esqueci Minha Senha'"
    )
    
    # Mensagens personalizadas
    mensagem_boas_vindas = models.TextField(
        blank=True,
        verbose_name="Mensagem de Boas-vindas",
        help_text="Mensagem exibida na tela de login"
    )
    mensagem_rodape = models.TextField(
        blank=True,
        verbose_name="Mensagem do Rodapé",
        help_text="Mensagem exibida no rodapé da página"
    )
    
    # URL personalizada
    url_personalizada = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        verbose_name="URL Personalizada",
        help_text="Ex: minha-loja (acessível via /login/minha-loja/)"
    )
    
    # Controle
    ativo = models.BooleanField(
        default=True,
        verbose_name="Login Personalizado Ativo"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )
    
    class Meta:
        verbose_name = "Login Personalizado"
        verbose_name_plural = "Logins Personalizados"
        ordering = ['loja__nome']
    
    def __str__(self):
        return f"Login Personalizado - {self.loja.nome}"
    
    def save(self, *args, **kwargs):
        # Gerar URL personalizada se não existir
        if not self.url_personalizada:
            self.url_personalizada = self.gerar_url_personalizada()
        
        super().save(*args, **kwargs)
    
    def gerar_url_personalizada(self):
        """Gera uma URL personalizada baseada no nome da loja"""
        import re
        from django.utils.text import slugify
        
        # Criar slug baseado no nome da loja
        base_slug = slugify(self.loja.nome)
        
        # Remover caracteres especiais e limitar tamanho
        base_slug = re.sub(r'[^a-z0-9-]', '', base_slug)[:50]
        
        # Verificar se já existe
        counter = 1
        url_slug = base_slug
        
        while LoginPersonalizado.objects.filter(url_personalizada=url_slug).exclude(id=self.id).exists():
            url_slug = f"{base_slug}-{counter}"
            counter += 1
        
        return url_slug
    
    def get_login_url(self):
        """Retorna a URL completa para o login personalizado"""
        if self.url_personalizada:
            return f"/login/{self.url_personalizada}/"
        return f"/login/loja/{self.loja.id}/"
    
    def get_css_variaveis(self):
        """Retorna as variáveis CSS para personalização"""
        return {
            '--cor-primaria': self.cor_primaria,
            '--cor-secundaria': self.cor_secundaria,
            '--cor-fundo': self.cor_fundo,
            '--cor-texto': self.cor_texto,
        }
    
    def get_template_name(self):
        """Retorna o nome do template baseado no tema"""
        # Template especial para FATESA
        if 'fatesa' in self.loja.nome.lower():
            return 'auth/login_personalizado_fatesa.html'
        
        template_map = {
            'padrao': 'auth/login_personalizado_padrao.html',
            'moderno': 'auth/login_personalizado_moderno.html',
            'minimalista': 'auth/login_personalizado_minimalista.html',
            'corporativo': 'auth/login_personalizado_corporativo_limpo.html',
            'personalizado': 'auth/login_personalizado_custom.html',
        }
        return template_map.get(self.tema, 'auth/login_personalizado_padrao.html')


class HistoricoLoginLoja(models.Model):
    """Modelo para histórico de logins por loja"""
    
    loja = models.ForeignKey(
        Loja,
        on_delete=models.CASCADE,
        related_name='historico_logins',
        verbose_name="Loja"
    )
    usuario = models.CharField(
        max_length=150,
        verbose_name="Usuário"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Endereço IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    sucesso = models.BooleanField(
        default=True,
        verbose_name="Login Bem-sucedido"
    )
    data_tentativa = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Tentativa"
    )
    
    # Informações adicionais
    metodo_login = models.CharField(
        max_length=50,
        default='personalizado',
        verbose_name="Método de Login"
    )
    dispositivo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Dispositivo"
    )
    navegador = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Navegador"
    )
    
    class Meta:
        verbose_name = "Histórico de Login da Loja"
        verbose_name_plural = "Histórico de Logins das Lojas"
        ordering = ['-data_tentativa']
    
    def __str__(self):
        status = "Sucesso" if self.sucesso else "Falha"
        return f"{self.loja.nome} - {self.usuario} ({status})"
    
    def save(self, *args, **kwargs):
        # Extrair informações do user agent
        if self.user_agent and not self.navegador:
            self.extrair_info_user_agent()
        
        super().save(*args, **kwargs)
    
    def extrair_info_user_agent(self):
        """Extrai informações básicas do user agent"""
        user_agent = self.user_agent.lower()
        
        # Detectar navegador
        if 'chrome' in user_agent:
            self.navegador = 'Chrome'
        elif 'firefox' in user_agent:
            self.navegador = 'Firefox'
        elif 'safari' in user_agent:
            self.navegador = 'Safari'
        elif 'edge' in user_agent:
            self.navegador = 'Edge'
        else:
            self.navegador = 'Outro'
        
        # Detectar dispositivo
        if 'mobile' in user_agent:
            self.dispositivo = 'Mobile'
        elif 'tablet' in user_agent:
            self.dispositivo = 'Tablet'
        else:
            self.dispositivo = 'Desktop'