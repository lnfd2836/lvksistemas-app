#!/bin/bash
# Script para configurar variáveis de ambiente no Heroku

echo "🚀 Configurando variáveis de ambiente no Heroku..."

# Configurações de Email (CONFIGURE SEUS DADOS)
heroku config:set EMAIL_HOST_USER="seu-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="sua-senha-de-app"
heroku config:set DEFAULT_FROM_EMAIL="Sistema LVK <seu-email@gmail.com>"

# Configurações de Email Backend
heroku config:set EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
heroku config:set EMAIL_HOST="smtp.gmail.com"
heroku config:set EMAIL_PORT="587"
heroku config:set EMAIL_USE_TLS="True"

# Configurações do Celery (serão configuradas automaticamente com Redis addon)
echo "📦 Adicionando Redis addon..."
heroku addons:create heroku-redis:mini

echo "⚙️ Configurando Celery..."
heroku config:set CELERY_BROKER_URL="$REDIS_URL"
heroku config:set CELERY_RESULT_BACKEND="$REDIS_URL"
heroku config:set CELERY_ACCEPT_CONTENT="json"
heroku config:set CELERY_TASK_SERIALIZER="json"
heroku config:set CELERY_RESULT_SERIALIZER="json"
heroku config:set CELERY_TIMEZONE="America/Sao_Paulo"

echo "✅ Configuração concluída!"
echo ""
echo "⚠️  IMPORTANTE:"
echo "1. Configure EMAIL_HOST_USER com seu email real"
echo "2. Configure EMAIL_HOST_PASSWORD com senha de app do Gmail"
echo "3. Execute: heroku ps:scale worker=1 beat=1"
echo ""
echo "🧪 Para testar:"
echo "heroku run python manage.py processar_notificacoes_boleto --dry-run"
