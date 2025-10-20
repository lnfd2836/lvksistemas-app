# 🔧 Configuração do Webhook no Painel do Asaas

## 📋 Passo a Passo

### 1. Acesse o Painel do Asaas
- Entre em sua conta no [Asaas](https://www.asaas.com)
- Vá em **Configurações > Webhooks**
- Clique em **Adicionar Webhook**

### 2. Preencha os Dados do Webhook

| Campo | Valor | Observação |
|-------|-------|------------|
| **Webhook ativo?** | ✅ Sim | Deve estar ativo |
| **Nome do Webhook** | `LVK Sistemas - Pagamentos` | Até 50 caracteres |
| **URL do Webhook** | `http://localhost:8000/financeiro/asaas/webhook/` | Para desenvolvimento local |
| **E-mail** | `seu-email@exemplo.com` | Para notificações de erro |
| **Versão da API** | `v3` | Versão mais recente |
| **Token de autenticação** | *(deixar vazio)* | Opcional por enquanto |
| **Fila de sincronização** | ✅ Sim | Recomendado |
| **Tipo de envio** | `JSON` | Formato dos dados |

### 3. Selecionar Eventos

Marque os seguintes eventos:

#### ✅ Eventos Obrigatórios:
- **PAYMENT_RECEIVED** - Pagamento recebido
- **PAYMENT_CONFIRMED** - Pagamento confirmado  
- **PAYMENT_OVERDUE** - Pagamento vencido

#### ✅ Eventos Recomendados:
- **PAYMENT_DELETED** - Pagamento cancelado
- **PAYMENT_RESTORED** - Pagamento restaurado
- **PAYMENT_AWAITING_RISK_ANALYSIS** - Aguardando análise

#### ❌ Eventos Opcionais (não necessários):
- PAYMENT_CREATED - Cobrança criada
- PAYMENT_UPDATED - Cobrança atualizada

### 4. URLs por Ambiente

#### 🧪 Desenvolvimento Local:
```
http://localhost:8000/financeiro/asaas/webhook/
```

#### 🌐 Produção (Heroku):
```
https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/webhook/
```

#### 🌐 Produção (Domínio próprio):
```
https://seu-dominio.com/financeiro/asaas/webhook/
```

## 🔒 Configurações de Segurança

### Token de Autenticação (Opcional)
Se quiser adicionar uma camada extra de segurança:

1. Gere um token aleatório:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Adicione no webhook do Asaas
3. Configure no seu `.env`:
```env
ASAAS_WEBHOOK_TOKEN=seu-token-aqui
```

### Validação de IP (Recomendado)
O Asaas envia webhooks dos seguintes IPs:
- `52.67.73.224`
- `52.67.73.225` 
- `52.67.73.226`

## 🧪 Testando o Webhook

### 1. Verificar se a URL está acessível:
```bash
curl -X POST http://localhost:8000/financeiro/asaas/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"event":"PAYMENT_RECEIVED","payment":{"id":"test"}}'
```

### 2. Verificar logs do Django:
```bash
tail -f logs/django.log | grep webhook
```

### 3. Testar com cobrança real:
1. Gere uma cobrança de teste no sistema
2. Faça um pagamento no ambiente sandbox
3. Verifique se o webhook foi recebido

## 📊 Monitoramento

### No Painel do Asaas:
- Vá em **Configurações > Webhooks**
- Clique no webhook criado
- Verifique o **Status** e **Últimas tentativas**

### No Sistema LVK:
- Acesse **Admin > Logs**
- Filtre por "webhook" ou "asaas"
- Verifique se as notificações estão sendo processadas

## ❌ Troubleshooting

### Webhook não está sendo recebido:
1. ✅ Verificar se a URL está correta
2. ✅ Verificar se o servidor está rodando
3. ✅ Verificar se não há firewall bloqueando
4. ✅ Verificar logs de erro no Asaas

### Webhook recebido mas não processado:
1. ✅ Verificar logs do Django
2. ✅ Verificar se o CSRF está desabilitado para a URL
3. ✅ Verificar se o formato JSON está correto

### Erro 401 (Não autorizado):
1. ✅ Verificar se o token está correto
2. ✅ Verificar se a API Key está válida

## 📝 Exemplo de Payload

Quando um pagamento é recebido, o Asaas enviará algo assim:

```json
{
  "event": "PAYMENT_RECEIVED",
  "payment": {
    "object": "payment",
    "id": "pay_123456789",
    "dateCreated": "2024-01-15",
    "customer": "cus_123456789",
    "paymentLink": null,
    "value": 100.00,
    "netValue": 97.51,
    "originalValue": null,
    "interestValue": null,
    "description": "Mensalidade do sistema",
    "billingType": "BOLETO",
    "status": "RECEIVED",
    "pixTransaction": null,
    "confirmedDate": "2024-01-15",
    "paymentDate": "2024-01-15",
    "clientPaymentDate": "2024-01-15",
    "installmentNumber": null,
    "invoiceUrl": "https://www.asaas.com/i/123456789",
    "invoiceNumber": "00000001",
    "externalReference": "CF_1_1705123456",
    "dueDate": "2024-01-15",
    "originalDueDate": "2024-01-15"
  }
}
```

## ✅ Checklist Final

Antes de colocar em produção, verifique:

- [ ] Webhook configurado e ativo no Asaas
- [ ] URL correta para o ambiente
- [ ] Eventos necessários selecionados
- [ ] E-mail de notificação configurado
- [ ] Teste realizado com sucesso
- [ ] Logs funcionando corretamente
- [ ] Sistema processando pagamentos automaticamente

---

**💡 Dica:** Mantenha sempre o webhook do ambiente de desenvolvimento (localhost) e produção separados no painel do Asaas para evitar conflitos durante os testes.