"""
Django settings for lojad project.
"""

import os
from pathlib import Path
import environ
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file (apenas se existir - no Heroku não existe)
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '0.0.0.0', 
    'testserver', 
    'lvksistemas.herokuapp.com', 
    'lvksistemas-app-4f6fa281e217.herokuapp.com',
    'lvksistemas.com.br', 
    'www.lvksistemas.com.br', 
    'crmvendas.net.br', 
    'www.crmvendas.net.br', 
    'loja-conveniencia-pdv-7fed430df60a.herokuapp.com',
    '.herokuapp.com',  # Permite todos os subdomínios do Heroku
    '.asaas.com'  # Permite webhooks do Asaas
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'modulos',
    'lojas',
    'usuarios',
    'dashboard',
    'planos',
    'controle_financeiro',
]

MIDDLEWARE = [
    'controle_financeiro.asaas_ip_validation_middleware.AsaasWebhookIPValidationMiddleware',  # Validação de IP para webhooks
    'controle_financeiro.webhook_middleware.WebhookBypassMiddleware',  # Detecta webhooks primeiro
    'django.middleware.security.SecurityMiddleware',
    'dashboard.middleware.error_capture.ErrorCaptureMiddleware',  # Captura de erros deve ser primeiro
    'dashboard.middleware.middleware_profiler.MiddlewareProfiler',  # Profiling de middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Necessário para admin
    'usuarios.mandatory_password_middleware.MandatoryPasswordChangeMiddleware',  # Troca obrigatória de senha
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.improved_middleware.ImprovedAuthenticationMiddleware',
    'usuarios.password_middleware.PasswordChangeMiddleware',
    'lojas.middleware.LojaMiddleware',
    'controle_financeiro.middleware.ControleFinanceiroMiddleware',
]

# URLs que devem ser excluídas de todos os middlewares de autenticação
WEBHOOK_EXCLUDED_PATHS = [
    '/financeiro/asaas/webhook/',
    '/financeiro/asaas/webhook-debug/',
    '/financeiro/asaas/webhook-test/',
]

def is_webhook_path(path):
    """
    Verifica se o caminho é um webhook que deve ser excluído de middlewares de autenticação
    """
    return any(path.startswith(excluded_path) for excluded_path in WEBHOOK_EXCLUDED_PATHS) or '/asaas/webhook' in path

ROOT_URLCONF = 'lojad.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lojas.permissions.permissions_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'lojad.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3')
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# URLs para as views padrão do Django Auth
# Redireciona para nossa view personalizada
LOGOUT_URL = '/logout/'


# Cache (simplificado para desenvolvimento)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@lvksistemas.com.br')
SERVER_EMAIL = env('SERVER_EMAIL', default='noreply@lvksistemas.com.br')

# Session Configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Heroku Configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configurações da API Asaas
ASAAS_API_KEY = os.environ.get('ASAAS_API_KEY') or env('ASAAS_API_KEY', default='')
ASAAS_ENVIRONMENT = os.environ.get('ASAAS_ENVIRONMENT') or env('ASAAS_ENVIRONMENT', default='sandbox')  # sandbox ou production
SITE_URL = os.environ.get('SITE_URL') or env('SITE_URL', default='http://localhost:8000')

# Dados da conta Asaas (para referência)
ASAAS_WALLET_ID = '5193cd6d-899f-4219-b45a-a8a2012eae05'
ASAAS_PIX_KEY = '0be79c1f-73f8-41d9-a795-3401856ce31b'

# Configurações específicas para Heroku
if 'DYNO' in os.environ:
    # Estamos no Heroku - configurações de produção
    SECURE_SSL_REDIRECT = False  # Desabilitado para permitir webhooks HTTP
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Configurações específicas para webhooks no Heroku
    # ALLOWED_HOSTS já configurado acima
    
    # Forçar HTTPS para URLs do Asaas em produção
    if ASAAS_ENVIRONMENT == 'production':
        SITE_URL = SITE_URL.replace('http://', 'https://')
    
    # Logging otimizado para Heroku
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'controle_financeiro.asaas_service': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'controle_financeiro.asaas_views': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '{levelname} {asctime} {name} {module} {funcName} {lineno} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'authentication.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'formatter': 'detailed',
            'level': 'ERROR',
        },
        'debug_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'debug.log',
            'formatter': 'detailed',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'usuarios.services': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'usuarios.improved_middleware': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'dashboard.middleware.error_capture': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'dashboard.middleware.middleware_profiler': {
            'handlers': ['console', 'debug_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'dashboard.utils.database_health': {
            'handlers': ['console', 'debug_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'debug_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(exist_ok=True)

# Heroku specific settings
if 'DYNO' in os.environ:
    DEBUG = False
    SECURE_SSL_REDIRECT = False  # Desabilitado para permitir webhooks HTTP do Asaas
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Disable file logging on Heroku - remove file handler completely
    LOGGING['handlers'] = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    }
    # Update all loggers to use only console handler
    for logger_name in LOGGING['loggers']:
        LOGGING['loggers'][logger_name]['handlers'] = ['console']
