# Comandos para Sincronizar Cobranças no Heroku

## 🚀 Comandos Principais

### 1. Sincronização Básica (apenas cobranças faltantes)
```bash
heroku run python manage.py sync_heroku_asaas
```

### 2. Sincronização Forçada (todas as cobranças)
```bash
heroku run python manage.py sync_heroku_asaas --force
```

### 3. Sincronização dos últimos 60 dias
```bash
heroku run python manage.py sync_heroku_asaas --days 60
```

### 4. Verificar status atual
```bash
heroku run python manage.py shell -c "
from controle_financeiro.models import CobrancaAsaas
print(f'Total de cobranças: {CobrancaAsaas.objects.count()}')
for c in CobrancaAsaas.objects.all()[:10]:
    print(f'{c.asaas_id} | {c.controle_financeiro.loja.nome} | R$ {c.valor} | {c.status}')
"
```

### 5. Testar notificações
```bash
heroku run python manage.py processar_notificacoes_boleto --dry-run
```

## 🔧 Comandos de Diagnóstico

### Verificar variáveis de ambiente
```bash
heroku config | grep -E "(ASAAS|EMAIL)"
```

### Ver logs em tempo real
```bash
heroku logs --tail
```

### Verificar workers
```bash
heroku ps
```

### Reiniciar aplicação
```bash
heroku restart
```

## 📊 Comandos de Monitoramento

### Status das cobranças
```bash
heroku run python manage.py shell -c "
from controle_financeiro.models import CobrancaAsaas
from collections import Counter
statuses = [c.status for c in CobrancaAsaas.objects.all()]
for status, count in Counter(statuses).items():
    print(f'{status}: {count}')
"
```

### Verificar lojas
```bash
heroku run python manage.py shell -c "
from lojas.models import Loja
from controle_financeiro.models import ControleFinanceiro
for loja in Loja.objects.all():
    controle = ControleFinanceiro.objects.filter(loja=loja).first()
    print(f'{loja.nome} | {loja.db_name} | Controle: {controle.id if controle else \"Não encontrado\"}')
"
```

## 🎯 Sequência Recomendada para Resolver o Problema

### Passo 1: Verificar configuração
```bash
heroku config | grep ASAAS_API_KEY
```

### Passo 2: Executar sincronização
```bash
heroku run python manage.py sync_heroku_asaas --force
```

### Passo 3: Verificar resultado
```bash
heroku run python manage.py shell -c "
from controle_financeiro.models import CobrancaAsaas
print(f'✅ Total sincronizado: {CobrancaAsaas.objects.count()} cobranças')
"
```

### Passo 4: Testar interface web
Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/cobrancas/

### Passo 5: Configurar workers (se necessário)
```bash
heroku ps:scale worker=1 beat=1
```

## 🚨 Em Caso de Problemas

### Se API key estiver incorreta:
```bash
heroku config:set ASAAS_API_KEY="sua_nova_chave_aqui"
heroku restart
```

### Se cobranças não aparecerem:
```bash
# Verificar se existem controles financeiros
heroku run python manage.py shell -c "
from controle_financeiro.models import ControleFinanceiro
print(f'Controles financeiros: {ControleFinanceiro.objects.count()}')
"

# Criar controle se necessário
heroku run python manage.py shell -c "
from lojas.models import Loja
from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro
from django.utils import timezone
from datetime import timedelta

for loja in Loja.objects.all():
    if not ControleFinanceiro.objects.filter(loja=loja).exists():
        plano = PlanoFinanceiro.objects.first()
        if plano:
            ControleFinanceiro.objects.create(
                loja=loja,
                plano=plano,
                status='ativa',
                valor_mensal=plano.valor_mensal,
                data_inicio=timezone.now(),
                data_vencimento=timezone.now() + timedelta(days=30)
            )
            print(f'Controle criado para {loja.nome}')
"
```

### Se emails não estão sendo enviados:
```bash
# Verificar configuração de email
heroku config | grep EMAIL

# Testar envio
heroku run python manage.py processar_notificacoes_boleto --dry-run
```

## 📝 Logs Importantes

### Ver logs específicos do Celery
```bash
heroku logs --dyno=worker --tail
heroku logs --dyno=beat --tail
```

### Ver logs da aplicação
```bash
heroku logs --source=app --tail
```

### Filtrar logs por erro
```bash
heroku logs --tail | grep ERROR
```