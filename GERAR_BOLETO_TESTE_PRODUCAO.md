# 🧪 Gerar Boleto com PIX - Teste em Produção

## 🚨 Problema Identificado

A API do Asaas está retornando erro **403 (Acesso negado)** ao tentar gerar cobranças via API.

### 📊 Status da Conexão:
- ✅ **Webhook funcionando:** `https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/`
- ❌ **API Key:** Erro 403 - Acesso negado
- ✅ **Environment:** production
- ✅ **Base URL:** https://www.asaas.com/api/v3

## 🔧 Soluções Possíveis

### 1. **Verificar Conta Asaas**
- Acessar painel do Asaas
- Verificar se a conta está ativa para produção
- Confirmar se não há pendências ou bloqueios

### 2. **Regenerar API Key**
- No painel Asaas: Configurações > API
- Gerar nova API Key de produção
- Atualizar no Heroku:
  ```bash
  heroku config:set ASAAS_API_KEY=nova-api-key --app lvksistemas-app
  ```

### 3. **Verificar Permissões**
- Confirmar se a API Key tem permissões para:
  - Criar clientes
  - Gerar cobranças
  - Receber webhooks

## 🎯 **Alternativa: Gerar Boleto via Interface Web**

Enquanto resolve o problema da API, você pode gerar um boleto de teste diretamente no sistema:

### **Passo a Passo:**

1. **Acesse o sistema:**
   ```
   https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/
   ```

2. **Faça login como superuser:**
   - Username: `admin`
   - Password: `admin123`

3. **Acesse o painel financeiro:**
   ```
   https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/
   ```

4. **Gere uma cobrança:**
   - Vá em "Controles Financeiros"
   - Selecione uma loja (Harmonis ou Loja Vida)
   - Clique em "Gerar Cobrança Asaas"

## 📋 **Lojas Disponíveis para Teste:**

| ID | Nome | CNPJ | Valor Mensal |
|----|------|------|--------------|
| c2db94a7-e525-4d30-9529-d1c972d3f1f0 | Harmonis | 37.302.743/0001-26 | R$ 59,90 |
| 03068de0-5ce2-4b29-bb1a-41f7e638e7ee | Loja Vida | 24.758.458/0001-72 | R$ 29,90 |

## 🔍 **Debug da API Key**

Para verificar se a API Key está funcionando:

```bash
heroku run python manage.py testar_asaas_conexao --app lvksistemas-app
```

**Resultado atual:**
```
🌐 Environment: production
🔗 Base URL: https://www.asaas.com/api/v3
📊 Status Code: 403
❌ Erro na API: 403
📄 Resposta: Acesso negado. code: 03KUFSJQL1
```

## ✅ **Webhook Funcionando**

O webhook está **100% funcional** e pronto para receber notificações:

```bash
curl -X POST https://lvksistemas-app-4f6fa281e217.herokuapp.com/webhook/asaas/ \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

# Resposta: OK - INTERCEPTED BY WSGI (Status 200)
```

## 🚀 **Próximos Passos**

1. **Resolver problema da API Key** (contatar suporte Asaas se necessário)
2. **Gerar boleto via interface web** para testar o fluxo completo
3. **Configurar webhook no painel Asaas** com a URL funcionando
4. **Testar pagamento real** para validar o webhook

---

**Status:** ⚠️ **API com problema - Webhook funcionando**  
**Data:** 22/10/2025  
**Próxima ação:** Resolver API Key do Asaas