# Monitoramento de Base de Dados

## Comandos de Monitoramento Criados

### monitor_database_health.py

Comando principal para verificar a saúde da base de dados:

```bash
# Verificação básica
python manage.py monitor_database_health

# Saída em JSON (para integração com sistemas de monitoramento)
python manage.py monitor_database_health --json

# Definir limite de alertas
python manage.py monitor_database_health --alert-threshold 3
```

#### Verificações Realizadas

1. **Conectividade da Base de Dados**
   - Testa conexão básica
   - Verifica vendor (PostgreSQL/SQLite)
   - Mede tempo de resposta

2. **Campos de Gestão de Senha**
   - `requires_password_change`
   - `provisional_password_created`
   - `password_changed_at`
   - `password_change_reminders_sent`

3. **Status das Migrações**
   - Identifica migrações pendentes
   - Lista migrações não aplicadas

4. **Perfis de Utilizador**
   - Conta utilizadores sem perfis
   - Verifica utilizadores que precisam trocar senha

## Monitoramento no Heroku

### Verificação Manual

```bash
# Verificação única
heroku run python manage.py monitor_database_health --app seu-app-name

# Verificação com saída JSON
heroku run python manage.py monitor_database_health --json --app seu-app-name
```

### Monitoramento Contínuo

Execute o script de monitoramento contínuo:

```bash
# Monitoramento a cada 5 minutos
./scripts/heroku_health_monitor.sh seu-app-name 300

# Monitoramento a cada 1 minuto (para debugging)
./scripts/heroku_health_monitor.sh seu-app-name 60
```

## Alertas e Notificações

### Tipos de Alertas

1. **Críticos** (Status: critical)
   - Base de dados inacessível
   - Campos de senha não existem
   - Múltiplas migrações pendentes

2. **Avisos** (Status: warning)
   - Utilizadores sem perfis
   - Algumas migrações pendentes
   - Problemas menores de conectividade

### Configuração de Alertas

#### Slack (Exemplo)
```bash
# Adicionar ao script de monitoramento
if [ "$STATUS" == "critical" ]; then
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🚨 ALERTA CRÍTICO: Base de dados com problemas"}' \
    YOUR_SLACK_WEBHOOK_URL
fi
```

#### Email (Exemplo)
```bash
# Usar sendmail ou serviço de email
echo "Problemas detectados na base de dados" | mail -s "Alerta DB" admin@exemplo.com
```

## Logs e Histórico

### Localização dos Logs

- **Local**: `heroku_health_YYYYMMDD.log`
- **Heroku**: `heroku logs --app seu-app-name`

### Análise de Logs

```bash
# Procurar por erros específicos
heroku logs --app seu-app-name | grep "requires_password_change"

# Logs das últimas 24 horas
heroku logs --since="24 hours ago" --app seu-app-name

# Logs em tempo real
heroku logs --tail --app seu-app-name
```

## Métricas de Saúde

### Indicadores Chave

1. **Disponibilidade da Base de Dados**: > 99.9%
2. **Tempo de Resposta**: < 100ms
3. **Erros de Coluna**: 0
4. **Migrações Pendentes**: 0
5. **Utilizadores sem Perfil**: < 1%

### Dashboard de Métricas

Para criar um dashboard, use a saída JSON:

```bash
heroku run python manage.py monitor_database_health --json --app seu-app-name | jq '.checks'
```

## Troubleshooting

### Problema: Campos de Senha Não Acessíveis

**Diagnóstico**:
```bash
heroku run python manage.py verify_schema --app usuarios --model PerfilUsuario --app seu-app-name
```

**Solução**:
```bash
heroku run python manage.py apply_password_migrations --app seu-app-name
```

### Problema: Muitos Utilizadores sem Perfil

**Diagnóstico**:
```bash
heroku run python manage.py shell --app seu-app-name
# No shell: User.objects.filter(perfil__isnull=True).count()
```

**Solução**: Criar perfis para utilizadores existentes

### Problema: Migrações Pendentes

**Diagnóstico**:
```bash
heroku run python manage.py showmigrations --app seu-app-name
```

**Solução**:
```bash
heroku run python manage.py migrate --app seu-app-name
```

## Automação

### Cron Job (para servidores próprios)

```bash
# Adicionar ao crontab
*/5 * * * * /path/to/your/project/scripts/heroku_health_monitor.sh >> /var/log/db_health.log 2>&1
```

### Heroku Scheduler

```bash
# Adicionar ao Heroku Scheduler
heroku addons:create scheduler:standard --app seu-app-name
heroku addons:open scheduler --app seu-app-name

# Comando para adicionar:
python manage.py monitor_database_health --json
```

## Integração com Ferramentas Externas

### New Relic
```bash
heroku addons:create newrelic:wayne --app seu-app-name
```

### Datadog
```bash
heroku addons:create heroku-datadog:lite --app seu-app-name
```

### Papertrail (Logs)
```bash
heroku addons:create papertrail:choklad --app seu-app-name
```

## Checklist de Monitoramento

- [ ] Comando de monitoramento instalado
- [ ] Script de monitoramento contínuo configurado
- [ ] Alertas configurados (Slack/Email)
- [ ] Logs sendo coletados
- [ ] Métricas sendo acompanhadas
- [ ] Procedimentos de troubleshooting documentados
- [ ] Equipe treinada nos comandos de diagnóstico

## Comandos de Emergência

```bash
# Verificação rápida de saúde
heroku run python manage.py monitor_database_health --app seu-app-name

# Aplicar correções de migração
heroku run python manage.py apply_password_migrations --app seu-app-name

# Testar funcionalidade de senhas
heroku run python manage.py test_password_functionality --app seu-app-name

# Reiniciar aplicação
heroku restart --app seu-app-name

# Verificar status dos dynos
heroku ps --app seu-app-name
```