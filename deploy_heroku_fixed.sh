#!/bin/bash

echo "🚀 DEPLOY PARA HEROKU - Sistema de Gestão de Lojas"
echo "=================================================="

# Verificar se o Heroku CLI está instalado
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI não encontrado. Instale primeiro:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Verificar se está logado no Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Não está logado no Heroku. Execute: heroku login"
    exit 1
fi

echo "✅ Heroku CLI encontrado e usuário logado"

# Nome do app (você pode alterar)
APP_NAME="loja-gestao-$(date +%s)"

echo "📱 Nome do app: $APP_NAME"

# Verificar se o Git está inicializado
if [ ! -d ".git" ]; then
    echo "🔧 Inicializando repositório Git..."
    git init
    git add .
    git commit -m "Initial commit"
fi

echo "🔧 Criando aplicação no Heroku..."
heroku create $APP_NAME --region us

echo "🔧 Configurando variáveis de ambiente..."
heroku config:set DEBUG=False --app $APP_NAME
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())') --app $APP_NAME

echo "🔧 Adicionando add-on do PostgreSQL..."
heroku addons:create heroku-postgresql:essential-0 --app $APP_NAME

echo "🔧 Configurando buildpacks..."
heroku buildpacks:add heroku/python --app $APP_NAME

echo "📦 Fazendo deploy..."
git add .
git commit -m "Deploy to Heroku with barcode fixes" || echo "Nada para commitar"

# Adicionar remote do Heroku se não existir
if ! git remote get-url heroku &> /dev/null; then
    heroku git:remote -a $APP_NAME
fi

# Deploy
git push heroku main || git push heroku master

echo "🔧 Executando migrações..."
heroku run python manage.py migrate --app $APP_NAME

echo "🔧 Coletando arquivos estáticos..."
heroku run python manage.py collectstatic --noinput --app $APP_NAME

echo "👤 Criando superusuário..."
echo "Você precisará criar um superusuário manualmente:"
echo "heroku run python manage.py createsuperuser --app $APP_NAME"

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "=================================================="
echo "🌐 URL da aplicação: https://$APP_NAME.herokuapp.com"
echo "⚙️  Admin: https://$APP_NAME.herokuapp.com/admin"
echo ""
echo "📋 Próximos passos:"
echo "1. Criar superusuário: heroku run python manage.py createsuperuser --app $APP_NAME"
echo "2. Acessar o admin e configurar os dados"
echo "3. Testar a geração de boletos"
echo ""
echo "🔧 Comandos úteis:"
echo "   heroku logs --tail --app $APP_NAME  # Ver logs"
echo "   heroku run bash --app $APP_NAME     # Acessar terminal"
echo "   heroku config --app $APP_NAME       # Ver variáveis"
echo ""