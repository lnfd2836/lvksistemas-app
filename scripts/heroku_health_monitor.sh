#!/bin/bash

# Script de monitoramento contínuo para Heroku
# Execute este script para monitorar a saúde da base de dados em produção

APP_NAME=${1:-"seu-app-heroku"}
INTERVAL=${2:-300}  # 5 minutos por padrão
LOG_FILE="heroku_health_$(date +%Y%m%d).log"

echo "=========================================="
echo "MONITORAMENTO CONTÍNUO - HEROKU"
echo "App: $APP_NAME"
echo "Intervalo: ${INTERVAL}s"
echo "Log: $LOG_FILE"
echo "=========================================="

# Função para executar verificação de saúde
run_health_check() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] Executando verificação de saúde..." | tee -a $LOG_FILE
    
    # Executar monitoramento no Heroku
    heroku run python manage.py monitor_database_health --json --app $APP_NAME 2>&1 | tee -a $LOG_FILE
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        echo "[$timestamp] ✅ Verificação concluída com sucesso" | tee -a $LOG_FILE
    else
        echo "[$timestamp] ❌ Verificação falhou (código: $exit_code)" | tee -a $LOG_FILE
        
        # Enviar alerta (você pode personalizar isso)
        echo "[$timestamp] 🚨 ALERTA: Problemas detectados na base de dados" | tee -a $LOG_FILE
        
        # Executar verificações adicionais em caso de falha
        echo "[$timestamp] Executando diagnósticos adicionais..." | tee -a $LOG_FILE
        
        # Verificar logs recentes
        echo "--- LOGS RECENTES ---" >> $LOG_FILE
        heroku logs --num 50 --app $APP_NAME >> $LOG_FILE 2>&1
        
        # Verificar status da aplicação
        echo "--- STATUS DA APLICAÇÃO ---" >> $LOG_FILE
        heroku ps --app $APP_NAME >> $LOG_FILE 2>&1
        
        # Verificar base de dados
        echo "--- INFO DA BASE DE DADOS ---" >> $LOG_FILE
        heroku pg:info --app $APP_NAME >> $LOG_FILE 2>&1
    fi
    
    echo "[$timestamp] Próxima verificação em ${INTERVAL}s" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
}

# Função para verificação específica de campos de senha
check_password_fields() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] Verificando campos de senha especificamente..." | tee -a $LOG_FILE
    
    heroku run python manage.py test_password_functionality --app $APP_NAME 2>&1 | tee -a $LOG_FILE
}

# Função para verificar erros nos logs
check_error_logs() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] Verificando erros nos logs..." | tee -a $LOG_FILE
    
    # Procurar por erros específicos
    local errors=$(heroku logs --num 100 --app $APP_NAME 2>/dev/null | grep -i "requires_password_change does not exist" | wc -l)
    
    if [ $errors -gt 0 ]; then
        echo "[$timestamp] ❌ Encontrados $errors erros de coluna nos logs" | tee -a $LOG_FILE
        return 1
    else
        echo "[$timestamp] ✅ Nenhum erro de coluna encontrado nos logs" | tee -a $LOG_FILE
        return 0
    fi
}

# Trap para limpeza ao sair
cleanup() {
    echo ""
    echo "Monitoramento interrompido. Log salvo em: $LOG_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Verificação inicial
echo "Executando verificação inicial..."
run_health_check

# Verificação específica de campos de senha
check_password_fields

# Loop principal de monitoramento
while true; do
    sleep $INTERVAL
    
    # Verificação de saúde regular
    run_health_check
    
    # A cada 3 verificações, fazer verificação específica de erros
    if [ $(($(date +%s) / $INTERVAL % 3)) -eq 0 ]; then
        check_error_logs
    fi
done