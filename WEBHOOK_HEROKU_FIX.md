# Fix para Webhook Asaas no Heroku

## 🔍 Problema Identificado

O webhook `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/` estava retornando erro 302 (redirecionamento) em vez de processar corretamente.

## ✅ Soluções Implementadas

### 1. Webhook Específico para Heroku
- Criado `webhook_heroku.py` com máxima compatibilidade
- Bypassa todos os middlewares problemáticos
- Log detalhado para debug no Heroku

### 2. URLs Atualizadas
```python
# Nova estrutura de URLs (prioridade)
path('webhook/asaas/', webhook_asaas_heroku, name='webhook_asaas_heroku'),
path('webhook/asaas/test/', webhook_asaas_test_heroku, name='webhook_asaas_test_heroku'),
```

### 3. Middlewares Atualizados
- Todos os middlewares agora excluem paths de webhook
- Adicionado `WebhookBypassMiddleware` para detectar webhooks
- Configuração específica para Heroku

### 4. Configurações de Produção
```python
# Heroku específico
SECURE_SSL_REDIRECT = False  # Permite webhooks HTTP
ALLOWED_HOSTS.extend([
    'lvksistemas-app-4f6fa281e217.herokuapp.com',
    '.herokuapp.com',
    '.asaas.com'
])
```

## 🧪 URLs de Teste

### Produção (Heroku):
- **Principal:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/`
- **Teste:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/test/`
- **Debug:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/debug/`

### Teste Manual:
```bash
curl -X POST https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/test/ \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

## 📋 Checklist de Deploy

- [x] Webhook específico para Heroku criado
- [x] URLs atualizadas com prioridade correta
- [x] Middlewares configurados para excluir webhooks
- [x] Configurações de produção ajustadas
- [x] Logs detalhados implementados
- [ ] Deploy no Heroku
- [ ] Teste do webhook em produção
- [ ] Configuração no painel Asaas

## 🚀 Próximos Passos

1. **Deploy no Heroku:**
   ```bash
   git add .
   git commit -m "Fix webhook Asaas para Heroku"
   git push heroku main
   ```

2. **Testar webhook:**
   - Acessar URL de teste
   - Verificar logs no Heroku
   - Configurar no painel Asaas

3. **Monitorar logs:**
   ```bash
   heroku logs --tail --app lvksistemas-app-4f6fa281e217
   ```

## 🔧 Configuração no Asaas

No painel do Asaas, configurar:
- **URL do Webhook:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/`
- **Eventos:** PAYMENT_RECEIVED, PAYMENT_OVERDUE, PAYMENT_DELETED
- **Método:** POST
- **Content-Type:** application/json

## 📊 Monitoramento

Os logs agora incluem:
- Detalhes da requisição (headers, IP, etc.)
- Dados do webhook recebido
- Status do processamento
- Erros detalhados se houver

---
**Status:** ✅ Implementado - Aguardando deploy
**Data:** 22/10/2025