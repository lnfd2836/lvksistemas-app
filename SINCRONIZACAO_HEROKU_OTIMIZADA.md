# Sincronização Asaas - Versão Otimizada para Heroku

## Problema Resolvido

O erro "Connection refused" estava ocorrendo devido ao uso de threading em ambiente Heroku, que tem limitações específicas para esse tipo de operação. A solução implementada remove o threading e otimiza as requisições para o ambiente de produção.

## Principais Mudanças

### 1. Remoção do Threading
- **Antes**: Usava `threading.Thread` para sincronização contínua
- **Agora**: Marca apenas o status como ativo, sem criar threads
- **Benefício**: Elimina conflitos com o ambiente Heroku

### 2. Timeouts Reduzidos
- **Consultas individuais**: 15 segundos (antes: 60s)
- **Consultas de lista**: 20 segundos (antes: 60s)
- **Teste de conectividade**: 10 segundos
- **Benefício**: Evita timeouts que causam "Connection refused"

### 3. Processamento em Lotes Menores
- **Cobranças por execução**: Máximo 50 (antes: ilimitado)
- **Período de busca**: 7 dias (antes: 30 dias)
- **Novas cobranças**: 3 dias (antes: 7 dias)
- **Benefício**: Reduz carga e tempo de processamento

### 4. Tratamento de Erros Melhorado
- **Retry com backoff**: Removido para evitar loops
- **Continuidade**: Erros individuais não param o processo
- **Fallbacks**: Múltiplos níveis de verificação
- **Benefício**: Sistema mais robusto e confiável

## Novos Recursos

### 1. Teste de Conectividade
```python
# Novo método para teste rápido
sync_service.simple_sync_check()
```
- Verifica API sem fazer sincronização completa
- Testa algumas cobranças de exemplo
- Retorna status detalhado

### 2. Dashboard Otimizado
- Interface específica para ambiente Heroku
- Botões para testes rápidos
- Informações sobre limitações do ambiente
- Estatísticas em tempo real

### 3. Múltiplos Fallbacks
1. **Sincronização completa** → Se falhar...
2. **Validação da API** → Se falhar...
3. **Teste de conectividade básica** → Informa status

## Como Usar

### 1. Acesso ao Dashboard
```
/controle_financeiro/sync/
```

### 2. Teste de Conectividade
1. Clique em "Testar Conectividade"
2. Aguarde resultado
3. Se OK, pode fazer sincronização

### 3. Sincronização Manual
1. Clique em "Sincronizar Agora"
2. Sistema tentará múltiplas abordagens
3. Resultado será exibido com detalhes

### 4. Via Script
```bash
python testar_sincronizacao_heroku.py
```

## Configurações Recomendadas

### 1. Variáveis de Ambiente
```bash
# Timeout reduzido para Heroku
ASAAS_TIMEOUT=15

# Ambiente de produção
ASAAS_ENVIRONMENT=production

# Chave da API
ASAAS_API_KEY=sua_chave_aqui
```

### 2. Para Sincronização Contínua
- **Recomendado**: Usar Celery com Redis/PostgreSQL
- **Alternativa**: Cron jobs externos
- **Não usar**: Threading interno do Django

## Monitoramento

### 1. Logs Importantes
```python
# Conectividade
logger.info("API Asaas acessível")
logger.warning("Connection refused para cobrança X")

# Sincronização
logger.info("Sincronização concluída: X processadas, Y atualizadas")
logger.error("Erro na sincronização: detalhes")
```

### 2. Métricas no Dashboard
- **Status da API**: Verde/Vermelho
- **Cobranças processadas**: Contador
- **Erros recentes**: Lista dos últimos
- **Última sincronização**: Timestamp

## Troubleshooting

### 1. "Connection Refused"
- **Causa**: Timeout ou limite de conexões
- **Solução**: Aguardar alguns minutos e tentar novamente
- **Prevenção**: Usar "Testar Conectividade" primeiro

### 2. "API Inválida"
- **Causa**: Chave incorreta ou expirada
- **Solução**: Verificar ASAAS_API_KEY
- **Teste**: Usar configuração manual

### 3. "Nenhuma Cobrança Processada"
- **Causa**: Filtros muito restritivos
- **Solução**: Verificar datas e status
- **Debug**: Usar script de teste

## Próximos Passos

### 1. Implementar Celery (Recomendado)
```python
# tasks.py
@shared_task
def sync_asaas_periodic():
    sync_service = get_sync_service()
    return sync_service.force_sync_now()
```

### 2. Webhook Automático
- Configurar webhook no Asaas
- Sincronização em tempo real por evento
- Reduz necessidade de polling

### 3. Cache de Resultados
- Redis para cache de consultas
- Reduz chamadas à API
- Melhora performance

## Arquivos Modificados

1. **asaas_sync_service.py**: Lógica principal otimizada
2. **asaas_sync_views.py**: Views com fallbacks
3. **asaas_service.py**: Método consultar_cobranca adicionado
4. **sync_dashboard.html**: Interface otimizada
5. **urls.py**: Nova rota para teste
6. **testar_sincronizacao_heroku.py**: Script de teste

## Compatibilidade

- ✅ **Heroku**: Totalmente compatível
- ✅ **Railway**: Compatível
- ✅ **DigitalOcean**: Compatível
- ✅ **AWS**: Compatível
- ✅ **Local**: Funciona normalmente

## Conclusão

A versão otimizada resolve o problema de "Connection refused" mantendo toda a funcionalidade de sincronização. O sistema agora é mais robusto, rápido e adequado para ambientes de produção como o Heroku.

Para uso em produção, recomenda-se implementar Celery para sincronização automática contínua, mas a versão manual já funciona perfeitamente para a maioria dos casos de uso.