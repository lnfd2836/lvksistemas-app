# Integração com API do Asaas - Geração de Boletos com PIX

Este documento descreve a implementação da integração com a API do Asaas para geração de boletos bancários com PIX no sistema LVK Sistemas.

## 📋 Visão Geral

A integração permite:
- ✅ Geração automática de boletos bancários
- ✅ Geração simultânea de PIX (QR Code + Copia e Cola)
- ✅ Notificações automáticas via webhook
- ✅ Controle de status de pagamentos
- ✅ Multa e juros automáticos
- ✅ Interface administrativa completa

## 🏦 Dados da Conta Asaas

**Conta configurada no sistema:**
- **Banco:** 461 - Asaas I.P S.A
- **Agência:** 0001
- **Conta:** 194116-2
- **Tipo:** Conta de Pagamento
- **Beneficiário:** FELIX REPRESENTACOES E COMERCIO LTDA
- **CNPJ:** 41.449.198/0001-72
- **Wallet ID:** 8bc96229-9853-40f4-b315-265090f1d524
- **Chave PIX:** 0be79c1f-73f8-41d9-a795-3401856ce31b

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Adicione no arquivo `.env`:

```env
# API Asaas
ASAAS_API_KEY=sua-api-key-aqui
ASAAS_ENVIRONMENT=sandbox  # ou production
SITE_URL=http://localhost:8000  # URL do seu sistema
```

### 2. Obter API Key

1. Acesse o painel do Asaas
2. Vá em **Configurações > API**
3. Gere uma nova chave de API
4. Configure no `.env` do sistema

### 3. Configurar Webhook

No painel do Asaas:
1. Vá em **Configurações > Webhooks**
2. Adicione nova URL: `{SEU_DOMINIO}/financeiro/asaas/webhook/`
3. Selecione os eventos:
   - `PAYMENT_RECEIVED` (Pagamento recebido)
   - `PAYMENT_OVERDUE` (Pagamento vencido)
   - `PAYMENT_CONFIRMED` (Pagamento confirmado)

## 🚀 Como Usar

### 1. Gerar Nova Cobrança

**Via Interface Web:**
1. Acesse **Controle Financeiro > Cobranças Asaas**
2. Clique em **Gerar Nova Cobrança**
3. Selecione a loja e configure os parâmetros
4. Clique em **Gerar Cobrança com PIX**

**Via Código:**
```python
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import ControleFinanceiro

# Inicializar serviço
asaas_service = AsaasService()

# Buscar controle financeiro
controle = ControleFinanceiro.objects.get(id=1)

# Gerar cobrança
resultado = asaas_service.gerar_cobranca_com_pix(
    controle_financeiro=controle,
    dias_vencimento=30,
    descricao="Mensalidade do sistema"
)

if resultado['success']:
    cobranca_data = resultado['cobranca']
    pix_data = resultado['pix']
    print(f"Cobrança criada: {cobranca_data['id']}")
else:
    print(f"Erro: {resultado['error']}")
```

### 2. Consultar Status

```python
# Consultar cobrança específica
dados = asaas_service.consultar_cobranca('pay_123456789')

# Verificar status
if dados['status'] == 'RECEIVED':
    print("Pagamento recebido!")
```

### 3. Processar Webhook

O sistema processa automaticamente os webhooks do Asaas. Quando um pagamento é recebido:

1. O webhook é recebido em `/financeiro/asaas/webhook/`
2. O sistema atualiza o status da cobrança
3. O controle financeiro é atualizado automaticamente
4. A loja é desbloqueada se necessário

## 📊 Modelos de Dados

### CobrancaAsaas

```python
class CobrancaAsaas(models.Model):
    asaas_id = models.CharField(max_length=100, unique=True)
    controle_financeiro = models.ForeignKey(ControleFinanceiro)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    
    # URLs do boleto
    invoice_url = models.URLField(blank=True)
    bank_slip_url = models.URLField(blank=True)
    
    # Dados do PIX
    pix_qr_code = models.TextField(blank=True)
    pix_copy_paste = models.TextField(blank=True)
    
    # Metadados
    data_vencimento = models.DateTimeField()
    data_pagamento = models.DateTimeField(null=True, blank=True)
```

## 🔧 Comandos de Gerenciamento

### Testar Integração

```bash
# Teste básico de conexão
python manage.py testar_asaas --apenas-conexao

# Teste completo com geração de cobrança
python manage.py testar_asaas --controle-id=1
```

### Verificar Configuração

```bash
# Verificar se a API está funcionando
python manage.py shell
>>> from controle_financeiro.asaas_service import AsaasService
>>> service = AsaasService()
>>> service.validar_configuracao()
True
```

## 🌐 URLs Disponíveis

| URL | Descrição |
|-----|-----------|
| `/financeiro/asaas/gerar/<id>/` | Gerar nova cobrança |
| `/financeiro/asaas/cobrancas/` | Listar cobranças |
| `/financeiro/asaas/cobrancas/<uuid>/` | Visualizar cobrança |
| `/financeiro/asaas/webhook/` | Webhook do Asaas |
| `/financeiro/asaas/configurar/` | Configurações (admin) |
| `/financeiro/asaas/testar/` | Testar integração (admin) |

## 💰 Configurações Financeiras

### Multa e Juros (Automático)
- **Multa:** 2% sobre o valor após vencimento
- **Juros:** 1% ao mês após vencimento
- **Desconto:** Configurável (padrão: 0%)

### Status de Cobrança
- `PENDING` - Aguardando pagamento
- `RECEIVED` - Pagamento recebido
- `CONFIRMED` - Pagamento confirmado
- `OVERDUE` - Vencido
- `REFUNDED` - Estornado

## 🔒 Segurança

### Validação de Webhook
- Verificação de origem (IP do Asaas)
- Validação de assinatura (se configurada)
- Log de todas as requisições

### Dados Sensíveis
- API Key armazenada em variável de ambiente
- Logs não expõem dados sensíveis
- Comunicação via HTTPS obrigatória em produção

## 🐛 Troubleshooting

### Erro: "API Key não configurada"
```bash
# Verificar se a variável está definida
echo $ASAAS_API_KEY

# Ou no Django shell
from django.conf import settings
print(settings.ASAAS_API_KEY)
```

### Erro: "Conexão recusada"
1. Verificar se a API Key está correta
2. Verificar se o ambiente (sandbox/production) está correto
3. Verificar conectividade com a internet

### Webhook não funciona
1. Verificar se a URL está acessível externamente
2. Verificar se o CSRF está desabilitado para a URL do webhook
3. Verificar logs do servidor web

### Cobrança não é criada
1. Verificar se o cliente existe no Asaas
2. Verificar se os dados da loja estão completos
3. Verificar logs de erro no Django

## 📝 Logs

### Ativar Logs Detalhados

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'asaas.log',
        },
    },
    'loggers': {
        'controle_financeiro.asaas_service': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Verificar Logs

```bash
# Ver logs em tempo real
tail -f asaas.log

# Filtrar por erros
grep ERROR asaas.log
```

## 🚀 Deploy em Produção

### 1. Configurar Variáveis
```bash
# Heroku
heroku config:set ASAAS_API_KEY=sua-api-key-producao
heroku config:set ASAAS_ENVIRONMENT=production
heroku config:set SITE_URL=https://seu-dominio.com
```

### 2. Configurar Webhook
- URL: `https://seu-dominio.com/financeiro/asaas/webhook/`
- Eventos: `PAYMENT_RECEIVED`, `PAYMENT_OVERDUE`, `PAYMENT_CONFIRMED`

### 3. Testar em Produção
```bash
# Teste de conexão
heroku run python manage.py testar_asaas --apenas-conexao

# Teste com cobrança real (cuidado!)
heroku run python manage.py testar_asaas --controle-id=1
```

## 📞 Suporte

### Documentação Oficial
- [Guia de Cobranças Asaas](https://docs.asaas.com/docs/guia-de-cobrancas)
- [API Reference](https://docs.asaas.com/reference)

### Contato Asaas
- Suporte: suporte@asaas.com
- Telefone: (11) 4003-2787

### Suporte Técnico LVK
- Email: suporte@lvksistemas.com.br
- Sistema: Abrir chamado no painel administrativo

---

**Implementado por:** LVK Sistemas  
**Data:** Outubro 2024  
**Versão:** 1.0.0