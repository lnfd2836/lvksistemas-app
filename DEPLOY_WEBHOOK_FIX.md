# Deploy - Fix Webhook Asaas Heroku

## 🎯 Problema Resolvido
Webhook `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/` retornando erro 302 em vez de processar corretamente.

## ✅ Alterações Implementadas

### 1. Novos Arquivos Criados:
- `controle_financeiro/webhook_heroku.py` - Webhook específico para Heroku
- `controle_financeiro/webhook_middleware.py` - Middleware para detectar webhooks
- `test_webhook_heroku.py` - Script de teste para Heroku
- `WEBHOOK_HEROKU_FIX.md` - Documentação da solução

### 2. Arquivos Modificados:
- `lojad/urls.py` - URLs atualizadas com prioridade para webhook Heroku
- `lojad/settings.py` - Configurações específicas para Heroku
- `controle_financeiro/asaas_service.py` - Processamento melhorado
- `controle_financeiro/middleware.py` - Exclusão de webhooks
- `usuarios/improved_middleware.py` - Exclusão de webhooks
- `usuarios/mandatory_password_middleware.py` - Exclusão de webhooks

## 🚀 Comandos para Deploy

```bash
# 1. Adicionar alterações
git add .

# 2. Commit
git commit -m "Fix webhook Asaas para Heroku - bypassa middlewares e melhora processamento"

# 3. Deploy no Heroku
git push heroku main

# 4. Verificar logs
heroku logs --tail --app lvksistemas-app-4f6fa281e217
```

## 🧪 Teste Após Deploy

```bash
# Executar script de teste
python test_webhook_heroku.py
```

Ou teste manual:
```bash
curl -X POST https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/test/ \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook heroku"}'
```

## 🔧 Configuração no Asaas

1. Acessar painel do Asaas
2. Ir em Configurações > Webhooks
3. Configurar:
   - **URL:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/`
   - **Eventos:** PAYMENT_RECEIVED, PAYMENT_CREATED, PAYMENT_OVERDUE
   - **Método:** POST
   - **Content-Type:** application/json

## 📊 Monitoramento

### Logs no Heroku:
```bash
heroku logs --tail --app lvksistemas-app-4f6fa281e217 | grep "WEBHOOK"
```

### URLs de Teste:
- **Principal:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/`
- **Teste:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/test/`
- **Debug:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/debug/`

## 🔍 Principais Melhorias

1. **Webhook Específico para Heroku:**
   - Bypassa todos os middlewares problemáticos
   - Log detalhado para debug
   - Suporte a GET e POST

2. **Middlewares Atualizados:**
   - Todos excluem paths de webhook
   - Detecção automática de webhooks
   - Prevenção de redirecionamentos

3. **Processamento Melhorado:**
   - Suporte a múltiplos tipos de evento
   - Fallback para referência externa
   - Logs detalhados para debug

4. **Configurações de Produção:**
   - SSL redirect desabilitado para webhooks
   - ALLOWED_HOSTS atualizado
   - Configurações específicas do Heroku

## ✅ Checklist Final

- [x] Webhook específico para Heroku criado
- [x] URLs com prioridade correta
- [x] Middlewares configurados
- [x] Processamento melhorado
- [x] Scripts de teste criados
- [x] Documentação completa
- [ ] **Deploy no Heroku**
- [ ] **Teste em produção**
- [ ] **Configuração no Asaas**

---
**Próximo passo:** Executar deploy e testar em produção