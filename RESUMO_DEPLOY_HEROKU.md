# 🚀 RESUMO: Deploy Heroku - Asaas Produção

## ⚡ Deploy Rápido (3 passos)

### 1️⃣ Configurar Variáveis no Heroku
```bash
# Configurações essenciais
heroku config:set ASAAS_API_KEY="sua-api-key-de-producao"
heroku config:set ASAAS_ENVIRONMENT="production"
heroku config:set DEBUG="False"
heroku config:set SITE_URL="https://lvksistemas-app-4f6fa281e217.herokuapp.com"
```

### 2️⃣ Deploy Automático
```bash
# Execute o script de deploy
./deploy_heroku_asaas.sh
```

### 3️⃣ Configurar Webhook no Asaas
- **URL:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/`
- **Eventos:** `PAYMENT_RECEIVED`, `PAYMENT_CONFIRMED`, `PAYMENT_OVERDUE`
- **Versão:** `v3`

---

## 📋 Checklist Completo

### ✅ Antes do Deploy
- [ ] API Key de produção obtida no Asaas
- [ ] Conta no Heroku configurada
- [ ] Heroku CLI instalado e logado
- [ ] Código commitado no Git

### ✅ Configurações Heroku
- [ ] `ASAAS_API_KEY` = sua chave de produção
- [ ] `ASAAS_ENVIRONMENT` = `production`
- [ ] `DEBUG` = `False`
- [ ] `SITE_URL` = URL do seu app Heroku

### ✅ Deploy
- [ ] `git push heroku main`
- [ ] `heroku run python manage.py migrate`
- [ ] `heroku run python manage.py configurar_asaas_padrao`

### ✅ Webhook Asaas
- [ ] URL configurada no painel
- [ ] Eventos selecionados
- [ ] Webhook ativo

### ✅ Testes
- [ ] `heroku run python manage.py verificar_producao`
- [ ] Gerar cobrança de teste
- [ ] Verificar se webhook funciona

---

## 🔧 Comandos Úteis

### Verificar configuração:
```bash
heroku config
heroku run python manage.py verificar_producao
```

### Monitorar logs:
```bash
heroku logs --tail
```

### Testar Asaas:
```bash
heroku run python manage.py testar_asaas --apenas-conexao
```

### Reiniciar app:
```bash
heroku restart
```

---

## 🌐 URLs Importantes

| Descrição | URL |
|-----------|-----|
| **Aplicação** | https://lvksistemas-app-4f6fa281e217.herokuapp.com |
| **Admin** | https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/ |
| **Webhook** | https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/ |
| **Cobranças** | https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/cobrancas/ |

---

## 🆘 Problemas Comuns

### ❌ "API Key inválida"
```bash
# Verificar chave
heroku config:get ASAAS_API_KEY

# Reconfigurar
heroku config:set ASAAS_API_KEY="nova-chave"
```

### ❌ "Webhook não funciona"
```bash
# Testar URL
curl -I https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/

# Ver logs
heroku logs --tail | grep webhook
```

### ❌ "Erro 500"
```bash
# Ver logs detalhados
heroku logs --tail

# Verificar DEBUG
heroku config:set DEBUG="True"  # Temporariamente para debug
```

---

## 🎯 Teste Final

1. **Acesse:** https://lvksistemas-app-4f6fa281e217.herokuapp.com
2. **Login:** admin / admin123
3. **Vá em:** Controle Financeiro > Cobranças Asaas
4. **Gere** uma cobrança de teste
5. **Verifique** se boleto e PIX são gerados
6. **Confirme** se webhook está funcionando

---

## 📞 Suporte

- **Heroku:** https://help.heroku.com
- **Asaas:** suporte@asaas.com
- **Sistema:** Logs do Heroku

---

**🎉 Pronto! Seu sistema está em produção com Asaas integrado!**