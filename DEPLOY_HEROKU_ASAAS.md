# 🚀 Deploy no Heroku - Asaas em Produção

## 📋 Pré-requisitos

- Conta no Heroku
- Heroku CLI instalado
- Conta no Asaas (ambiente de produção)
- API Key de produção do Asaas

## 🔧 1. Configurar Variáveis de Ambiente no Heroku

### Via Heroku CLI:
```bash
# Configurações básicas
heroku config:set SECRET_KEY="sua-chave-secreta-super-forte-aqui"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="lvksistemas-app-4f6fa281e217.herokuapp.com,lvksistemas.com.br,www.lvksistemas.com.br"

# Configurações do Asaas (PRODUÇÃO)
heroku config:set ASAAS_API_KEY="sua-api-key-de-producao"
heroku config:set ASAAS_ENVIRONMENT="production"
heroku config:set SITE_URL="https://lvksistemas-app-4f6fa281e217.herokuapp.com"

# Email (opcional)
heroku config:set EMAIL_HOST="smtp.gmail.com"
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER="seu-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="sua-senha-app"
heroku config:set DEFAULT_FROM_EMAIL="noreply@lvksistemas.com.br"
```

### Via Dashboard do Heroku:
1. Acesse seu app no dashboard do Heroku
2. Vá em **Settings > Config Vars**
3. Adicione as variáveis:

| Key | Value |
|-----|-------|
| `ASAAS_API_KEY` | `sua-api-key-de-producao` |
| `ASAAS_ENVIRONMENT` | `production` |
| `SITE_URL` | `https://lvksistemas-app-4f6fa281e217.herokuapp.com` |
| `SECRET_KEY` | `sua-chave-secreta-forte` |
| `DEBUG` | `False` |

## 🌐 2. Configurar Webhook no Asaas (Produção)

### URL do Webhook:
```
https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/
```

### Configurações no Painel Asaas:
- **Nome:** `LVK Sistemas - Produção`
- **URL:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/`
- **Versão:** `v3`
- **Eventos:** `PAYMENT_RECEIVED`, `PAYMENT_CONFIRMED`, `PAYMENT_OVERDUE`
- **Ativo:** `Sim`

## 📦 3. Preparar Código para Deploy

### Atualizar requirements.txt:
```bash
# Adicionar requests se não estiver
echo "requests==2.32.5" >> requirements.txt
```

### Verificar Procfile:
```bash
# Verificar se existe o Procfile
cat Procfile
```

Se não existir, criar:
```bash
echo "web: gunicorn lojad.wsgi --log-file -" > Procfile
```

### Atualizar settings.py para produção:
```python
# Adicionar no final do settings.py
import os

# Configurações específicas para Heroku
if 'DYNO' in os.environ:
    # Estamos no Heroku
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Logging para Heroku
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
        },
        'loggers': {
            'controle_financeiro.asaas_service': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
```

## 🚀 4. Deploy no Heroku

### Fazer commit das alterações:
```bash
git add .
git commit -m "Configurar Asaas para produção no Heroku"
```

### Deploy:
```bash
git push heroku main
```

### Executar migrações:
```bash
heroku run python manage.py migrate
```

### Configurar conta padrão Asaas:
```bash
heroku run python manage.py configurar_asaas_padrao
```

### Criar superusuário (se necessário):
```bash
heroku run python manage.py createsuperuser
```

## 🧪 5. Testar a Integração

### Testar conexão com Asaas:
```bash
heroku run python manage.py testar_asaas --apenas-conexao
```

### Verificar logs:
```bash
heroku logs --tail
```

### Testar webhook:
```bash
curl -X POST https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"event":"PAYMENT_RECEIVED","payment":{"id":"test"}}'
```

## 🔐 6. Obter API Key de Produção

### No Painel do Asaas:
1. Acesse [www.asaas.com](https://www.asaas.com)
2. Faça login na sua conta
3. Vá em **Configurações > API**
4. **IMPORTANTE:** Mude para ambiente de **PRODUÇÃO**
5. Gere uma nova API Key de produção
6. Copie a chave e configure no Heroku

### ⚠️ ATENÇÃO:
- API Key de **sandbox** ≠ API Key de **produção**
- Sempre use a chave correta para cada ambiente
- Nunca commite API Keys no código

## 📊 7. Monitoramento em Produção

### Verificar status do app:
```bash
heroku ps
```

### Monitorar logs em tempo real:
```bash
heroku logs --tail --app lvksistemas-app
```

### Verificar métricas:
```bash
heroku addons:create papertrail:choklad  # Logs avançados (opcional)
```

## 🔧 8. Comandos Úteis de Produção

### Reiniciar aplicação:
```bash
heroku restart
```

### Executar shell Django:
```bash
heroku run python manage.py shell
```

### Backup do banco:
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

### Verificar configurações:
```bash
heroku config
```

## 🛡️ 9. Segurança em Produção

### Configurações obrigatórias:
```bash
heroku config:set DEBUG=False
heroku config:set SECURE_SSL_REDIRECT=True
```

### Adicionar domínio personalizado (opcional):
```bash
heroku domains:add lvksistemas.com.br
heroku domains:add www.lvksistemas.com.br
```

### Configurar SSL (automático no Heroku):
```bash
heroku certs:auto:enable
```

## 📝 10. Checklist de Deploy

### Antes do deploy:
- [ ] API Key de produção obtida
- [ ] Variáveis de ambiente configuradas
- [ ] Webhook configurado no Asaas
- [ ] Código testado localmente
- [ ] Requirements.txt atualizado

### Após o deploy:
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Conta Asaas configurada
- [ ] Teste de conexão realizado
- [ ] Webhook testado
- [ ] Primeira cobrança de teste gerada

## 🚨 11. Troubleshooting

### Erro: "API Key inválida"
```bash
# Verificar se a chave está correta
heroku config:get ASAAS_API_KEY

# Verificar se o ambiente está correto
heroku config:get ASAAS_ENVIRONMENT
```

### Erro: "Webhook não recebido"
```bash
# Verificar se a URL está acessível
curl -I https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/

# Verificar logs
heroku logs --tail | grep webhook
```

### Erro: "Internal Server Error"
```bash
# Ver logs detalhados
heroku logs --tail

# Verificar se DEBUG está False
heroku config:get DEBUG
```

## 📞 12. URLs Importantes

### Aplicação:
- **App:** https://lvksistemas-app-4f6fa281e217.herokuapp.com
- **Admin:** https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/
- **Webhook:** https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/

### Asaas:
- **Painel:** https://www.asaas.com
- **Documentação:** https://docs.asaas.com
- **Suporte:** suporte@asaas.com

---

## 🎉 Pronto!

Após seguir todos esses passos, seu sistema estará funcionando em produção no Heroku com a integração completa do Asaas para geração de boletos com PIX!

### Teste final:
1. Acesse o sistema em produção
2. Gere uma cobrança de teste
3. Verifique se o boleto e PIX são gerados
4. Faça um pagamento de teste
5. Confirme se o webhook processa corretamente