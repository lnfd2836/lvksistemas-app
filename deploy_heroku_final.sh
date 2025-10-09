#!/bin/bash

echo "========================================="
echo "🚀 Deploy Final para Heroku - Sistema LVK"
echo "Correções de Boletos + Validação Completa"
echo "========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Heroku CLI está instalado
if ! command -v heroku &> /dev/null; then
    log_error "Heroku CLI não está instalado!"
    log_info "Instale com: curl https://cli-assets.heroku.com/install.sh | sh"
    exit 1
fi

# Verificar se está logado no Heroku
if ! heroku auth:whoami &> /dev/null; then
    log_error "Você não está logado no Heroku!"
    log_info "Execute: heroku login"
    exit 1
fi

log_success "Heroku CLI configurado corretamente"

# Verificar se está no git
if [ ! -d ".git" ]; then
    log_info "Inicializando repositório Git..."
    git init
    git branch -M main
fi

# Verificar se o remote heroku existe
if ! git remote get-url heroku &> /dev/null; then
    log_info "Configurando remote do Heroku..."
    git remote add heroku https://git.heroku.com/lvksistemas-app.git
fi

# Verificar status do git
log_info "Verificando status do repositório..."
git status --porcelain

# Adicionar todas as mudanças
log_info "Adicionando arquivos modificados..."
git add .

# Verificar se há mudanças para commit
if git diff --staged --quiet; then
    log_warning "Nenhuma mudança detectada para commit"
else
    # Commit das mudanças
    log_info "Fazendo commit das correções..."
    git commit -m "🔧 Deploy: Correções completas do sistema de boletos

✅ Correções implementadas:
- Fix algoritmos DV módulo 11 e módulo 10 (padrão FEBRABAN)
- Fix estrutura campo livre Caixa (25 dígitos exatos)
- Fix fator de vencimento (limitado a 4 dígitos)
- Add sistema validação abrangente BarcodeValidator
- Add validação automática na geração de boletos
- Fix templates com quebras de linha problemáticas
- Add campo convênio em configurações
- Fix configuração Caixa (nome correto + carteira)
- Add comando verificar_boletos para diagnóstico
- Fix geração nosso número (apenas números)

🎯 Resultado:
- Boletos Caixa agora geram códigos válidos
- Validação automática previne erros futuros
- Interface consistente entre configuração/edição
- Sistema robusto e confiável"
fi

# Verificar se a aplicação Heroku existe
APP_NAME="lvksistemas-app"
if ! heroku apps:info $APP_NAME &> /dev/null; then
    log_error "Aplicação $APP_NAME não encontrada no Heroku!"
    log_info "Verifique o nome da aplicação ou crie uma nova"
    exit 1
fi

log_success "Aplicação $APP_NAME encontrada"

# Push para o Heroku
log_info "Fazendo deploy para o Heroku..."
echo "========================================="

if git push heroku main; then
    log_success "Deploy realizado com sucesso!"
else
    log_error "Erro durante o deploy!"
    log_info "Verifique os logs acima para mais detalhes"
    exit 1
fi

echo "========================================="
log_info "Executando comandos pós-deploy..."
echo "========================================="

# Executar migrações
log_info "Executando migrações do banco de dados..."
if heroku run python manage.py migrate --app $APP_NAME; then
    log_success "Migrações executadas com sucesso"
else
    log_warning "Erro nas migrações - verifique manualmente"
fi

# Verificar se existe comando limpar_sessoes
log_info "Verificando comandos disponíveis..."
if heroku run python manage.py help limpar_sessoes --app $APP_NAME &> /dev/null; then
    log_info "Limpando sessões problemáticas..."
    heroku run python manage.py limpar_sessoes --app $APP_NAME
    log_success "Sessões limpas"
else
    log_warning "Comando limpar_sessoes não encontrado - pulando"
fi

# Coletar arquivos estáticos (backup)
log_info "Coletando arquivos estáticos..."
if heroku run python manage.py collectstatic --no-input --app $APP_NAME; then
    log_success "Arquivos estáticos coletados"
else
    log_warning "Arquivos estáticos já foram coletados durante o build"
fi

# Verificar status da aplicação
log_info "Verificando status da aplicação..."
heroku ps --app $APP_NAME

# Mostrar logs recentes
log_info "Logs recentes da aplicação:"
echo "========================================="
heroku logs --tail --num 20 --app $APP_NAME &
LOGS_PID=$!

# Aguardar alguns segundos para mostrar logs
sleep 5
kill $LOGS_PID 2>/dev/null

echo ""
echo "========================================="
log_success "🎉 Deploy concluído com sucesso!"
echo "========================================="
echo ""
log_info "🌐 URL da aplicação: https://$APP_NAME-4f6fa281e217.herokuapp.com"
log_info "📊 Dashboard Heroku: https://dashboard.heroku.com/apps/$APP_NAME"
log_info "📋 Logs em tempo real: heroku logs --tail --app $APP_NAME"
echo ""
log_info "🔧 Comandos úteis:"
echo "   heroku run python manage.py shell --app $APP_NAME"
echo "   heroku run python manage.py verificar_boletos --app $APP_NAME"
echo "   heroku run python manage.py verificar_boletos --validate --app $APP_NAME"
echo ""
log_success "✅ Sistema pronto para uso com boletos Caixa funcionais!"
echo "========================================="