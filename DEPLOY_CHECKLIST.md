# ✅ Checklist de Deploy - Sistema de Notificações

## Antes do Deploy

### 1. Arquivos Verificados
- [ ] requirements.txt atualizado com celery, redis, django-celery-beat
- [ ] Procfile atualizado com worker e beat
- [ ] settings.py com configurações de email e celery
- [ ] Todos os novos arquivos commitados

### 2. Configurações Locais Testadas
- [ ] `python manage.py processar_notificacoes_boleto --dry-run`
- [ ] `python test_bank_validation.py`
- [ ] Validação de banco funcionando

## Durante o Deploy

### 3. Deploy da Aplicação
```bash
git add .
git commit -m "Implementar sistema completo de notificações de boleto"
git push heroku main
```

### 4. Configurar Addons e Variáveis
```bash
# Executar script de configuração
./configure_heroku.sh

# OU configurar manualmente:
heroku addons:create heroku-redis:mini
heroku config:set EMAIL_HOST_USER="seu-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="sua-senha-de-app"
```

### 5. Executar Migrações
```bash
heroku run python manage.py migrate
heroku run python manage.py migrate django_celery_beat
```

### 6. Escalar Workers
```bash
heroku ps:scale worker=1 beat=1
```

## Após o Deploy

### 7. Testes de Funcionamento
- [ ] `heroku run python manage.py processar_notificacoes_boleto --dry-run`
- [ ] Verificar logs: `heroku logs --tail`
- [ ] Testar geração de boleto na interface
- [ ] Verificar se validação de banco funciona

### 8. Monitoramento
- [ ] `heroku logs --tail --dyno=worker`
- [ ] `heroku logs --tail --dyno=beat`
- [ ] Verificar se emails são enviados (após 10 dias)

## Configuração de Email Gmail

### 9. Preparar Email
1. [ ] Ativar verificação em 2 etapas no Gmail
2. [ ] Gerar senha de app específica
3. [ ] Configurar variáveis no Heroku
4. [ ] Testar envio de email

### 10. Teste Final
- [ ] Criar cobrança de teste com vencimento em 10 dias
- [ ] Aguardar execução automática do Celery Beat
- [ ] Verificar recebimento do email com PDF

## Troubleshooting

### Problemas Comuns
- **Worker não inicia**: Verificar REDIS_URL
- **Beat não executa**: Verificar django-celery-beat
- **Email não envia**: Verificar configurações Gmail
- **Boleto não gera**: Verificar db_name da loja

### Comandos Úteis
```bash
# Ver status dos dynos
heroku ps

# Reiniciar workers
heroku ps:restart worker beat

# Ver configurações
heroku config

# Executar comando específico
heroku run python manage.py shell
```

---

## 🎯 Funcionalidades Implementadas

✅ **Validação de Banco da Loja**
- Impede geração sem db_name configurado
- Usa código único na referência externa

✅ **Sistema de Notificações**
- Email automático 10 dias antes do vencimento
- Template HTML com PDF anexado
- Processamento via Celery Beat

✅ **Sincronização Melhorada**
- Detecção de cobranças excluídas
- Sincronização bidirecional
- 6 cobranças sincronizadas ✅

✅ **Automação Completa**
- Task diária do Celery
- Comando manual disponível
- Monitoramento via logs
