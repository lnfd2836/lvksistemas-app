# Sistema de Sincronização em Tempo Real com Asaas

## 📋 Visão Geral

Este sistema implementa sincronização automática e em tempo real entre o sistema LVK e a API do Asaas, mantendo os boletos e cobranças sempre atualizados entre os dois sistemas.

## 🚀 Funcionalidades

### ✅ Sincronização Automática
- **Monitoramento contínuo** de cobranças no Asaas
- **Atualização automática** de status de pagamento
- **Processamento imediato** de pagamentos recebidos
- **Detecção de cobranças vencidas**
- **Busca de novas cobranças** criadas externamente

### ✅ Interface de Controle
- **Dashboard completo** de monitoramento
- **Controles de start/stop** da sincronização
- **Estatísticas detalhadas** de performance
- **Lista de problemas** e cobranças com erro
- **Configurações personalizáveis**

### ✅ Automação via Celery
- **Tasks periódicas** automáticas
- **Retry automático** em caso de erro
- **Filas separadas** para diferentes tipos de operação
- **Monitoramento de execução**

### ✅ Webhooks e APIs
- **Endpoint para webhooks** do Asaas
- **APIs REST** para integração
- **Sincronização sob demanda**

## 📁 Estrutura dos Arquivos

```
controle_financeiro/
├── asaas_sync_service.py      # Serviço principal de sincronização
├── asaas_sync_views.py        # Views para interface web
├── celery_config.py           # Configuração do Celery
├── tasks.py                   # Tasks automáticas (atualizado)
├── management/commands/
│   └── start_asaas_sync.py    # Comando Django
└── templates/controle_financeiro/
    ├── sync_dashboard.html    # Dashboard principal
    ├── configurar_sync.html   # Configurações
    └── cobrancas_problemas.html # Lista de problemas

setup_asaas_sync.py           # Script de configuração inicial
```

## 🛠️ Instalação e Configuração

### 1. Configuração Inicial

Execute o script de configuração:

```bash
python setup_asaas_sync.py
```

Este script irá:
- ✅ Verificar configuração da API Asaas
- ✅ Executar migrações necessárias
- ✅ Testar conectividade
- ✅ Configurar Celery (se disponível)

### 2. Iniciar Sincronização

#### Opção A: Via Script
```bash
# Iniciar com intervalo padrão (5 minutos)
python setup_asaas_sync.py --start

# Iniciar com intervalo personalizado
python setup_asaas_sync.py --start --interval 300
```

#### Opção B: Via Comando Django
```bash
# Iniciar sincronização
python manage.py start_asaas_sync

# Com intervalo personalizado
python manage.py start_asaas_sync --interval 300

# Como daemon (não bloqueia terminal)
python manage.py start_asaas_sync --daemon

# Verificar status
python manage.py start_asaas_sync --status

# Parar sincronização
python manage.py start_asaas_sync --stop
```

#### Opção C: Via Interface Web
Acesse: `http://seu-site.com/financeiro/sync/`

### 3. Configurar Tasks Automáticas (Celery)

```bash
# Terminal 1: Worker
celery -A lojad worker --loglevel=info

# Terminal 2: Beat (scheduler)
celery -A lojad beat --loglevel=info
```

## 📊 Dashboard de Controle

### Acesso
- **URL:** `/financeiro/sync/`
- **Permissão:** Apenas Super Admin

### Funcionalidades
- **Status em tempo real** da sincronização
- **Estatísticas** de performance
- **Controles** de start/stop
- **Lista de cobranças** atualizadas recentemente
- **Histórico de execuções**

### Páginas Disponíveis
- `/financeiro/sync/` - Dashboard principal
- `/financeiro/sync/configurar/` - Configurações
- `/financeiro/sync/problemas/` - Cobranças com problemas

## 🔄 Como Funciona

### 1. Sincronização Contínua
```python
# A cada 5 minutos (configurável):
1. Busca cobranças locais dos últimos 30 dias
2. Consulta status atual no Asaas
3. Atualiza dados se houve mudanças
4. Processa pagamentos automaticamente
5. Busca novas cobranças no Asaas
6. Verifica cobranças vencidas
```

### 2. Processamento de Pagamentos
```python
# Quando uma cobrança é paga:
1. Status muda para 'RECEIVED' ou 'CONFIRMED'
2. Sistema chama cobranca.marcar_como_paga()
3. Atualiza ControleFinanceiro automaticamente
4. Renova período de acesso da loja
5. Registra no histórico
```

### 3. Detecção de Problemas
```python
# Sistema identifica:
- Cobranças não sincronizadas há > 1 hora
- Cobranças sem dados da API
- Erros de conectividade
- Timeouts de requisição
```

## ⚙️ Configurações

### Intervalos Recomendados
- **1 minuto:** Apenas para testes
- **5 minutos:** Uso normal (recomendado)
- **10 minutos:** Baixo volume de transações
- **30+ minutos:** Apenas para backup

### Configurações Avançadas
```python
# Em asaas_sync_service.py
sync_interval = 300        # Intervalo padrão (segundos)
timeout = 60              # Timeout de requisições
retry_attempts = 3        # Tentativas em caso de erro
batch_size = 100          # Cobranças por lote
```

## 📈 Monitoramento

### Estatísticas Disponíveis
- **Total sincronizado:** Número de cobranças processadas
- **Atualizações encontradas:** Mudanças detectadas
- **Erros:** Falhas de sincronização
- **Último erro:** Detalhes do último problema

### Logs
```python
# Configurar logging em settings.py
LOGGING = {
    'loggers': {
        'controle_financeiro.asaas_sync_service': {
            'level': 'INFO',
            'handlers': ['file'],
        }
    }
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Sincronização não inicia
```bash
# Verificar configuração
python manage.py start_asaas_sync --status

# Verificar API Asaas
python manage.py shell
>>> from controle_financeiro.asaas_service import AsaasService
>>> AsaasService().validar_configuracao()
```

#### 2. Erros de conectividade
- Verificar ASAAS_API_KEY nas settings
- Verificar conectividade com internet
- Verificar se não há firewall bloqueando

#### 3. Cobranças não atualizando
- Verificar se as cobranças existem no Asaas
- Verificar se external_reference está correto
- Forçar sincronização manual

#### 4. Tasks do Celery não executam
```bash
# Verificar se Celery está rodando
celery -A lojad inspect active

# Verificar filas
celery -A lojad inspect reserved

# Limpar filas
celery -A lojad purge
```

### Comandos de Diagnóstico

```bash
# Status completo
python manage.py start_asaas_sync --status

# Forçar sincronização
python setup_asaas_sync.py --start --interval 60

# Verificar logs
tail -f logs/django.log | grep asaas_sync
```

## 🔒 Segurança

### Validações Implementadas
- ✅ Verificação de permissões (apenas Super Admin)
- ✅ Validação de dados da API
- ✅ Timeout de requisições
- ✅ Rate limiting automático
- ✅ Retry com backoff exponencial

### Dados Sensíveis
- API Key do Asaas protegida em settings
- Logs não expõem dados sensíveis
- Webhooks com validação de origem

## 📚 APIs Disponíveis

### Endpoints REST
```
GET  /financeiro/api/sync/status/     # Status da sincronização
GET  /financeiro/api/sync/stats/      # Estatísticas detalhadas
POST /financeiro/api/sync/webhook/    # Webhook para trigger
```

### Webhook do Asaas
```
POST /financeiro/asaas/webhook/       # Webhook oficial do Asaas
```

## 🚀 Performance

### Otimizações Implementadas
- **Consultas em lote** para reduzir requisições
- **Cache de resultados** para evitar consultas desnecessárias
- **Processamento assíncrono** via Celery
- **Timeout configurável** para evitar travamentos
- **Retry inteligente** com backoff exponencial

### Métricas Esperadas
- **Latência:** < 2 segundos por cobrança
- **Throughput:** 100+ cobranças por minuto
- **Disponibilidade:** 99.9% (dependente da API Asaas)
- **Precisão:** 100% (com retry automático)

## 📝 Logs e Auditoria

### Eventos Registrados
- Início/parada da sincronização
- Cobranças atualizadas
- Pagamentos processados
- Erros e exceções
- Estatísticas de performance

### Formato dos Logs
```
[2024-01-15 10:30:00] INFO: Sincronização iniciada (intervalo: 300s)
[2024-01-15 10:35:00] INFO: Cobrança pay_123 atualizada: PENDING → RECEIVED
[2024-01-15 10:35:01] INFO: Pagamento processado: Loja ABC - R$ 99.90
```

## 🔄 Atualizações Futuras

### Melhorias Planejadas
- [ ] Dashboard em tempo real com WebSockets
- [ ] Notificações push para administradores
- [ ] Relatórios avançados de sincronização
- [ ] Integração com outros gateways de pagamento
- [ ] API GraphQL para consultas complexas

### Compatibilidade
- ✅ Django 3.2+
- ✅ Python 3.8+
- ✅ Celery 5.0+
- ✅ Redis/RabbitMQ para Celery

## 📞 Suporte

### Em caso de problemas:
1. Verificar logs do sistema
2. Executar diagnósticos automáticos
3. Consultar esta documentação
4. Verificar status da API Asaas

### Contato
- **Desenvolvedor:** Sistema LVK
- **Documentação:** Este arquivo
- **Logs:** `/logs/django.log`