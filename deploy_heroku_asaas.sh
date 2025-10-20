#!/bin/bash

# Script de Deploy Heroku - Integração Asaas
# Uso: ./deploy_heroku_asaas.sh

echo "🚀 Deploy Heroku - Integração Asaas"
echo "=================================="

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto Django"
    exit 1
fi

# Verificar se o Heroku CLI está instalado
if ! command -v heroku &> /dev/null; then
    echo "❌ Erro: Heroku CLI não está instalado"
    echo "Instale em: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Verificar se está logado no Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Erro: Faça login no Heroku primeiro"
    echo "Execute: heroku login"
    exit 1
fi

echo ""
echo "📋 Verificando configurações..."

# Verificar se as variáveis essenciais estão definidas
ASAAS_API_KEY=$(heroku config:get ASAAS_API_KEY 2>/dev/null)
if [ -z "$ASAAS_API_KEY" ]; then
    echo "⚠️  ASAAS_API_KEY não configurada"
    read -p "Digite sua API Key do Asaas (produção): " API_KEY
    heroku config:set ASAAS_API_KEY="$API_KEY"
    echo "✅ API Key configurada"
fi

# Configurar ambiente de produção
heroku config:set ASAAS_ENVIRONMENT="production"
heroku config:set DEBUG="False"

# Configurar URL do site
APP_NAME=$(heroku apps:info --json | python3 -c "import sys, json; print(json.load(sys.stdin)['app']['name'])" 2>/dev/null)
if [ ! -z "$APP_NAME" ]; then
    SITE_URL="https://$APP_NAME.herokuapp.com"
    heroku config:set SITE_URL="$SITE_URL"
    echo "✅ SITE_URL configurada: $SITE_URL"
fi

echo ""
echo "📦 Preparando deploy..."

# Adicionar requests ao requirements.txt se não existir
if ! grep -q "requests" requirements.txt; then
    echo "requests>=2.32.5" >> requirements.txt
    echo "✅ Requests adicionado ao requirements.txt"
fi

# Verificar se o Procfile existe
if [ ! -f "Procfile" ]; then
    echo "web: gunicorn lojad.wsgi --log-file -" > Procfile
    echo "✅ Procfile criado"
fi

# Commit das alterações
echo ""
echo "📝 Fazendo commit das alterações..."
git add .
git commit -m "Deploy: Configurar Asaas para produção no Heroku" || echo "Nenhuma alteração para commit"

echo ""
echo "🚀 Fazendo deploy..."
git push heroku main

if [ $? -eq 0 ]; then
    echo "✅ Deploy realizado com sucesso!"
else
    echo "❌ Erro no deploy"
    exit 1
fi

echo ""
echo "🔧 Executando migrações..."
heroku run python manage.py migrate

echo ""
echo "⚙️  Configurando conta padrão Asaas..."
heroku run python manage.py configurar_asaas_padrao

echo ""
echo "🧪 Testando integração..."
heroku run python manage.py testar_asaas --apenas-conexao

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure o webhook no painel do Asaas:"
echo "   URL: $SITE_URL/financeiro/asaas/webhook/"
echo "2. Teste a geração de cobranças no sistema"
echo "3. Monitore os logs: heroku logs --tail"
echo ""
echo "🌐 Acesse seu sistema: $SITE_URL"
echo "🔧 Admin: $SITE_URL/admin/"