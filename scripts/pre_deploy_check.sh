#!/bin/bash

# Script de verificação pré-deployment para Heroku
# Execute este script antes de fazer deploy para verificar se tudo está pronto

APP_NAME=${1:-"seu-app-heroku"}  # Use o primeiro argumento ou valor padrão

echo "=========================================="
echo "VERIFICAÇÃO PRÉ-DEPLOYMENT"
echo "App: $APP_NAME"
echo "=========================================="

# Verificar se o app existe
echo "1. Verificando se o app existe..."
if ! heroku apps:info --app $APP_NAME > /dev/null 2>&1; then
    echo "❌ App $APP_NAME não encontrado. Verifique o nome do app."
    exit 1
fi
echo "✅ App $APP_NAME encontrado"

# Verificar migrações locais
echo ""
echo "2. Verificando migrações locais..."
if ! python manage.py makemigrations --dry-run --check > /dev/null 2>&1; then
    echo "⚠️  Existem mudanças no modelo que precisam de migração"
    echo "Execute: python manage.py makemigrations"
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Nenhuma migração pendente localmente"
fi

# Verificar migrações no Heroku
echo ""
echo "3. Verificando migrações no Heroku..."
PENDING_MIGRATIONS=$(heroku run python manage.py showmigrations --plan --app $APP_NAME 2>/dev/null | grep -c "^\[ \]" || echo "0")

if [ "$PENDING_MIGRATIONS" -gt 0 ]; then
    echo "⚠️  $PENDING_MIGRATIONS migrações pendentes no Heroku"
    echo "Estas serão aplicadas automaticamente durante o deploy"
else
    echo "✅ Nenhuma migração pendente no Heroku"
fi

# Verificar se o Procfile tem release phase
echo ""
echo "4. Verificando Procfile..."
if grep -q "^release:" Procfile; then
    echo "✅ Procfile contém fase de release para migrações"
else
    echo "❌ Procfile não contém fase de release"
    echo "Adicione: release: python manage.py migrate --noinput"
    exit 1
fi

# Verificar comandos de verificação
echo ""
echo "5. Verificando comandos de verificação..."
COMMANDS=("check_migrations" "apply_password_migrations" "verify_schema" "test_password_functionality")

for cmd in "${COMMANDS[@]}"; do
    if [ -f "usuarios/management/commands/${cmd}.py" ]; then
        echo "✅ Comando $cmd disponível"
    else
        echo "❌ Comando $cmd não encontrado"
    fi
done

# Verificar variáveis de ambiente críticas
echo ""
echo "6. Verificando variáveis de ambiente..."
REQUIRED_VARS=("DATABASE_URL" "SECRET_KEY")

for var in "${REQUIRED_VARS[@]}"; do
    if heroku config:get $var --app $APP_NAME > /dev/null 2>&1; then
        echo "✅ $var configurada"
    else
        echo "❌ $var não configurada"
    fi
done

echo ""
echo "=========================================="
echo "VERIFICAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "Para fazer o deploy:"
echo "git push heroku main"
echo ""
echo "Para monitorar o deploy:"
echo "heroku logs --tail --app $APP_NAME"
echo ""
echo "Para verificar após deploy:"
echo "heroku run python manage.py check_migrations --app $APP_NAME"