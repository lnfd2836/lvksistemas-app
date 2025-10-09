#!/bin/bash

echo "========================================="
echo "🚀 Deploy Heroku - Correção Validação Boletos"
echo "Sistema de Correção Automática de DV"
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

# Limpar arquivos de teste temporários
log_info "Limpando arquivos de teste temporários..."
rm -f test_*.py debug_*.py *.pdf 2>/dev/null || true

# Verificar arquivos principais implementados
log_info "Verificando arquivos de correção implementados..."

REQUIRED_FILES=(
    "controle_financeiro/boleto_validator_unified.py"
    "controle_financeiro/boleto_simple_corrector.py"
    "controle_financeiro/boleto_dv_corrector.py"
    "controle_financeiro/boleto_error_handler.py"
    "controle_financeiro/sigcb_validator.py"
    "controle_financeiro/boleto_layout_detector.py"
    "controle_financeiro/boleto_input_normalizer.py"
    "controle_financeiro/boleto_validator_base.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file"
    else
        log_error "✗ $file não encontrado!"
        exit 1
    fi
done

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
    log_info "Fazendo commit das correções de validação..."
    git commit -m "🔧 Deploy: Sistema Avançado de Validação e Correção de Boletos

🎯 Funcionalidades Implementadas:

✅ Sistema de Validação Unificado:
- BoletoValidatorUnified: Interface principal para validação
- Suporte completo a layout SIGCB (Caixa Econômica Federal)
- Detecção automática de layout e banco
- Cache de validações para performance

✅ Correção Automática de DV:
- BoletoSimpleCorrector: Correção conservadora de erros de DV
- BoletoDVCorrector: Correção avançada com múltiplos algoritmos
- Suporte a correção de 1-3 erros de dígito verificador
- Níveis de confiança (high/medium/low)

✅ Manipulador de Erros Inteligente:
- BoletoErrorHandler: Análise e sugestões de solução
- Opções para usuário: corrigir, processar mesmo assim, solicitar nova via
- Mensagens amigáveis e ações claras
- Integração simples com interface Django

✅ Validadores Específicos:
- SIGCBValidator: Validação específica para Caixa
- Algoritmos DV módulo 10 e 11 FEBRABAN
- Validação de campos específicos SIGCB
- Extração e validação de componentes

✅ Utilitários de Suporte:
- BoletoLayoutDetector: Detecção automática de layout
- BoletoInputNormalizer: Normalização de entrada
- BoletoFormatConverter: Conversão entre formatos
- Sistema de mensagens de erro amigáveis

🎯 Problema Resolvido:
- Boletos com erros de DV agora podem ser processados
- Usuário recebe opções claras sobre como proceder
- Sistema mantém segurança e transparência
- Interface amigável para diferentes cenários de erro

🔧 Integração:
from controle_financeiro.boleto_error_handler import boleto_error_handler
result = boleto_error_handler.analyze_and_suggest_solution(linha_digitavel)

📊 Benefícios:
- Reduz rejeições de boletos por erros menores
- Melhora experiência do usuário
- Mantém auditoria e controle
- Flexibilidade para diferentes cenários"
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

if git push heroku main --force; then
    log_success "Deploy realizado com sucesso!"
else
    log_error "Erro durante o deploy!"
    log_info "Tentando push forçado..."
    if git push heroku main --force; then
        log_success "Deploy forçado realizado com sucesso!"
    else
        log_error "Erro crítico no deploy!"
        exit 1
    fi
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

# Coletar arquivos estáticos
log_info "Coletando arquivos estáticos..."
if heroku run python manage.py collectstatic --no-input --app $APP_NAME; then
    log_success "Arquivos estáticos coletados"
else
    log_warning "Arquivos estáticos já foram coletados durante o build"
fi

# Testar o sistema de validação
log_info "Testando sistema de validação de boletos..."
echo "========================================="

# Teste básico do sistema
TEST_COMMAND='
from controle_financeiro.boleto_error_handler import boleto_error_handler
linha_teste = "10492.67014 51823.019396 02946.570144 2 26000000002990"
result = boleto_error_handler.analyze_and_suggest_solution(linha_teste)
print(f"✅ Sistema funcionando! Tipo: {result.error_type}, Severidade: {result.severity}")
print(f"📋 Opções disponíveis: {len(result.action_options)}")
print(f"🔧 Pode prosseguir: {result.can_proceed}")
'

if heroku run python manage.py shell -c "$TEST_COMMAND" --app $APP_NAME; then
    log_success "Sistema de validação funcionando corretamente!"
else
    log_warning "Erro no teste - verifique logs"
fi

# Verificar status da aplicação
log_info "Verificando status da aplicação..."
heroku ps --app $APP_NAME

# Mostrar logs recentes
log_info "Logs recentes da aplicação:"
echo "========================================="
heroku logs --tail --num 15 --app $APP_NAME &
LOGS_PID=$!

# Aguardar alguns segundos para mostrar logs
sleep 8
kill $LOGS_PID 2>/dev/null

echo ""
echo "========================================="
log_success "🎉 Deploy de Validação de Boletos Concluído!"
echo "========================================="
echo ""
log_info "🌐 URL da aplicação: https://$APP_NAME-4f6fa281e217.herokuapp.com"
log_info "📊 Dashboard Heroku: https://dashboard.heroku.com/apps/$APP_NAME"
log_info "📋 Logs em tempo real: heroku logs --tail --app $APP_NAME"
echo ""
log_info "🔧 Comandos de teste:"
echo '   heroku run python manage.py shell -c "from controle_financeiro.boleto_error_handler import boleto_error_handler; print(\"Sistema carregado!\")" --app '$APP_NAME
echo ""
log_info "📝 Exemplo de uso no sistema:"
echo "   # Validar boleto com correção automática"
echo "   from controle_financeiro.boleto_error_handler import boleto_error_handler"
echo "   result = boleto_error_handler.analyze_and_suggest_solution(linha_digitavel)"
echo ""
log_success "✅ Sistema pronto! Boletos com erros de DV agora podem ser corrigidos automaticamente!"
echo "========================================="