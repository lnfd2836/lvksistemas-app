# Sistema de Boletos Automáticos

## Visão Geral

O sistema foi configurado para gerar boletos automaticamente **apenas 10 dias antes do vencimento** das lojas, evitando gerar boletos muito cedo e garantindo que as lojas recebam o boleto no momento adequado.

## Como Funciona

### 1. Regra Principal
- **Boletos são gerados automaticamente 10 dias antes do vencimento da loja**
- **NÃO são gerados boletos antes desse período**
- Cada loja recebe apenas um boleto por período de vencimento

### 2. Verificações Automáticas
O sistema executa as seguintes verificações automaticamente:

#### Diariamente (24h):
- **Rotinas Financeiras Completas**: Verifica vencimentos, gera boletos e processa renovações
- **Backup e Manutenção**: Backup dos dados e otimização do banco

#### A cada 12 horas:
- **Geração de Boletos**: Verifica lojas que vencem em 10 dias e gera boletos se necessário

#### A cada 6 horas:
- **Boletos Vencidos**: Atualiza status de boletos que venceram

### 3. Funcionalidades Implementadas

#### Comando Manual
```bash
# Executar geração de boletos (modo teste)
python manage.py gerar_boletos_automaticos --dry-run

# Executar geração real
python manage.py gerar_boletos_automaticos

# Personalizar dias de antecedência
python manage.py gerar_boletos_automaticos --dias-antecedencia 15
```

#### Interface Web
- **Dashboard Financeiro**: Botões para executar rotinas manualmente
- **Automação Financeira**: Seção dedicada com controles de execução
- **Monitoramento**: Visualização de boletos gerados e status

#### API/Serviços
- `BoletoService.gerar_boletos_automaticos()`: Gera boletos programaticamente
- `FinanceiroService.verificar_vencimentos_automatico()`: Verifica e atualiza vencimentos
- Tasks do Celery para execução automática

## Fluxo de Funcionamento

### 1. Verificação Diária
```
1. Sistema verifica todas as lojas ativas
2. Identifica lojas que vencem em exatamente 10 dias
3. Verifica se já existe boleto pendente para a loja
4. Se não existe, gera novo boleto
5. Envia notificação (se configurado)
```

### 2. Geração de Boleto
```
1. Busca configuração bancária ativa
2. Gera número único do boleto
3. Calcula data de vencimento (30 dias)
4. Gera linha digitável e código de barras
5. Salva boleto no banco de dados
6. Atualiza status da loja se necessário
```

### 3. Prevenção de Duplicatas
- Verifica se já existe boleto pendente antes de gerar novo
- Apenas um boleto ativo por loja por período
- Boletos vencidos não impedem geração de novos

## Configurações

### Dias de Antecedência
- **Padrão**: 10 dias
- **Configurável**: Via comando ou código
- **Recomendado**: Entre 7-15 dias

### Horários de Execução
- **Rotinas Completas**: 02:00 (diário)
- **Geração de Boletos**: 08:00 e 20:00 (12h)
- **Verificação de Vencidos**: 06:00, 12:00, 18:00, 00:00 (6h)

### Configuração Bancária
- Apenas uma configuração ativa por vez
- Todos os boletos usam a mesma configuração
- Configuração deve estar ativa para gerar boletos

## Monitoramento

### Logs
- Todas as operações são registradas
- Erros são capturados e reportados
- Estatísticas de execução disponíveis

### Dashboard
- Visualização de boletos gerados
- Status das lojas em tempo real
- Controles manuais para execução

### Alertas
- Lojas próximas do vencimento (5 dias)
- Lojas em atraso
- Falhas na geração de boletos

## Benefícios

### Para o Administrador
- **Automação Completa**: Sem necessidade de intervenção manual
- **Controle Total**: Pode executar operações manualmente quando necessário
- **Visibilidade**: Dashboard com todas as informações importantes
- **Flexibilidade**: Configurações ajustáveis conforme necessidade

### Para as Lojas
- **Recebimento Pontual**: Boletos chegam no momento certo (10 dias antes)
- **Sem Duplicatas**: Apenas um boleto ativo por período
- **Tempo Adequado**: 10 dias para organizar o pagamento
- **Previsibilidade**: Sempre recebem no mesmo período

## Troubleshooting

### Boletos Não Estão Sendo Gerados
1. Verificar se há configuração bancária ativa
2. Verificar se as lojas estão com status 'ativa'
3. Verificar se não há boletos pendentes já existentes
4. Verificar logs de erro no sistema

### Execução Manual
```bash
# Verificar o que seria feito
python manage.py gerar_boletos_automaticos --dry-run

# Executar com mais detalhes
python manage.py gerar_boletos_automaticos -v 2

# Forçar execução para teste
python manage.py gerar_boletos_automaticos --dias-antecedencia 30
```

### Via Interface Web
1. Acessar Dashboard Financeiro
2. Seção "Automação Financeira"
3. Clicar em "Executar" ou "Executar Tudo"
4. Verificar mensagens de sucesso/erro

## Próximos Passos

### Melhorias Futuras
- [ ] Notificações por email/SMS
- [ ] Configuração de horários personalizados
- [ ] Relatórios de geração de boletos
- [ ] Integração com APIs bancárias reais
- [ ] Dashboard de métricas financeiras

### Manutenção
- Monitorar logs regularmente
- Verificar execução das tasks do Celery
- Manter configuração bancária atualizada
- Backup regular dos dados financeiros

---

**Importante**: Este sistema garante que as lojas recebam seus boletos exatamente quando precisam (10 dias antes do vencimento), evitando boletos muito antecipados ou muito em cima da hora.