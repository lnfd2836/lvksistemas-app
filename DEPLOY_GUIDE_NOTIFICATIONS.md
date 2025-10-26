# Guia de Deploy - Sistema de Notificações de Boleto

## Configurações Necessárias no Heroku

### 1. Variáveis de Ambiente

Configure as seguintes variáveis no Heroku:

```bash
# Email
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-gmail

# Redis (Heroku Redis addon)
REDIS_URL=redis://...  # Automaticamente configurado pelo addon

# Celery
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
```

### 2. Addons Necessários

```bash
# Redis para Celery
heroku addons:create heroku-redis:mini

# Scheduler para Celery Beat (alternativa)
heroku addons:create scheduler:standard
```

### 3. Procfile

Adicione ao seu Procfile:

```
web: gunicorn lojad.wsgi
worker: celery -A lojad worker --loglevel=info
beat: celery -A lojad beat --loglevel=info
```

### 4. Comandos de Deploy

```bash
# Deploy da aplicação
git add .
git commit -m "Implementar sistema de notificações de boleto"
git push heroku main

# Executar migrações
heroku run python manage.py migrate

# Testar comando de notificações
heroku run python manage.py processar_notificacoes_boleto --dry-run

# Escalar workers (se necessário)
heroku ps:scale worker=1 beat=1
```

### 5. Configuração de Email Gmail

1. Ative a verificação em 2 etapas na sua conta Gmail
2. Gere uma senha de app específica
3. Use essa senha na variável EMAIL_HOST_PASSWORD

### 6. Teste Local

```bash
# Instalar Redis localmente
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Iniciar Redis
redis-server

# Em terminais separados:
celery -A lojad worker --loglevel=info
celery -A lojad beat --loglevel=info

# Testar comando
python manage.py processar_notificacoes_boleto --dry-run
```

### 7. Monitoramento

```bash
# Ver logs do worker
heroku logs --tail --dyno=worker

# Ver logs do beat
heroku logs --tail --dyno=beat

# Ver logs da aplicação
heroku logs --tail --dyno=web
```

### 8. Alternativa com Heroku Scheduler

Se preferir usar o Heroku Scheduler em vez do Celery Beat:

1. Configure o addon: `heroku addons:create scheduler:standard`
2. Adicione job diário: `python manage.py processar_notificacoes_boleto`
3. Configure para executar às 09:00 UTC (06:00 BRT)

## Funcionalidades Implementadas

### ✅ Validação de Banco da Loja
- Impede geração de boletos se `db_name` da loja não estiver configurado
- Usa código único do banco na referência externa do boleto

### ✅ Sistema de Notificações por Email
- Envia PDF do boleto 10 dias antes do vencimento
- Template HTML responsivo
- Anexa PDF do boleto automaticamente

### ✅ Processamento Automático
- Task do Celery executa diariamente
- Comando Django para execução manual
- Modo dry-run para testes

### ✅ Integração com Asaas
- Usa `db_name` da loja na referência externa
- Validação antes da geração de boletos
- Sincronização bidirecional melhorada

## Comandos Úteis

```bash
# Processar notificações manualmente
python manage.py processar_notificacoes_boleto

# Modo teste (não envia emails)
python manage.py processar_notificacoes_boleto --dry-run

# Processar com antecedência diferente
python manage.py processar_notificacoes_boleto --dias 5

# Testar validação de banco
python test_bank_validation.py

# Verificar sincronização
python check_asaas_payments.py
```

## Troubleshooting

### Emails não são enviados
1. Verifique configurações de email no settings.py
2. Confirme senha de app do Gmail
3. Verifique logs: `heroku logs --tail`

### Celery não executa
1. Verifique se Redis está funcionando
2. Confirme configuração CELERY_BROKER_URL
3. Verifique se worker está rodando: `heroku ps`

### Boletos não são gerados
1. Verifique se loja tem `db_name` configurado
2. Confirme API key do Asaas
3. Teste validação: `python test_bank_validation.py`
