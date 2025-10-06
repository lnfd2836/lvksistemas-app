# Documentação Completa - Correção de Migração de Base de Dados

## Resumo Executivo

Este documento descreve a correção implementada para resolver o erro de migração de base de dados que estava a impedir o funcionamento da funcionalidade de gestão de senhas obrigatórias no ambiente de produção Heroku.

### Problema Original
```
ERROR Erro durante processo de login: column usuarios_perfilusuario.requires_password_change does not exist
```

### Solução Implementada
Criação de ferramentas de diagnóstico, aplicação segura de migrações e implementação de monitoramento proativo.

## Ferramentas Criadas

### 1. Comandos de Diagnóstico

#### `check_migrations.py`
**Propósito**: Verificar status das migrações e existência de colunas
**Uso**:
```bash
python manage.py check_migrations [--verbose]
```
**Funcionalidades**:
- Identifica migrações pendentes
- Verifica existência de colunas específicas
- Compatível com PostgreSQL e SQLite
- Fornece informações detalhadas sobre o estado da base de dados

#### `verify_schema.py`
**Propósito**: Comparar schema do modelo Django com a base de dados
**Uso**:
```bash
python manage.py verify_schema [--app APP] [--model MODEL] [--verbose]
```
**Funcionalidades**:
- Compara definições do modelo com colunas da base de dados
- Identifica campos em falta ou extras
- Suporte para verificação detalhada
- Relatórios de diferenças de schema

### 2. Comandos de Correção

#### `apply_password_migrations.py`
**Propósito**: Aplicar migrações de forma segura com verificações
**Uso**:
```bash
python manage.py apply_password_migrations [--dry-run] [--force]
```
**Funcionalidades**:
- Verificações pré-migração
- Aplicação transacional
- Verificação pós-migração
- Modo dry-run para preview

#### `rollback_password_fields.py`
**Propósito**: Reverter migrações em caso de emergência
**Uso**:
```bash
python manage.py rollback_password_fields [--confirm] [--dry-run]
```
**Funcionalidades**:
- Rollback seguro com confirmação
- Verificações de segurança
- Remoção manual de colunas se necessário
- Verificação pós-rollback

### 3. Comandos de Teste

#### `test_password_functionality.py`
**Propósito**: Testar funcionalidade de gestão de senhas
**Uso**:
```bash
python manage.py test_password_functionality [--create-test-user] [--cleanup]
```
**Funcionalidades**:
- Teste de acesso aos campos
- Teste de operações do modelo
- Teste de compatibilidade com middleware
- Criação e limpeza de dados de teste

#### `test_system_complete.py`
**Propósito**: Teste completo do sistema após correções
**Uso**:
```bash
python manage.py test_system_complete [--create-test-data] [--cleanup]
```
**Funcionalidades**:
- Testes de base de dados
- Testes de modelo
- Testes de interface web
- Testes de integração
- Relatório detalhado de resultados

### 4. Comandos de Monitoramento

#### `monitor_database_health.py`
**Propósito**: Monitoramento contínuo da saúde da base de dados
**Uso**:
```bash
python manage.py monitor_database_health [--json] [--alert-threshold N]
```
**Funcionalidades**:
- Verificação de conectividade
- Teste de campos de senha
- Verificação de migrações
- Alertas automáticos
- Saída em JSON para integração

## Scripts de Automação

### 1. `apply_heroku_migrations.sh`
Script completo para aplicar migrações no Heroku com verificações.

### 2. `pre_deploy_check.sh`
Verificações pré-deployment para prevenir problemas.

### 3. `heroku_health_monitor.sh`
Monitoramento contínuo da saúde da aplicação no Heroku.

### 4. `rollback_password_migrations.sh`
Script de emergência para rollback completo.

## Processo de Correção Implementado

### Fase 1: Diagnóstico
1. Identificação do problema através dos logs
2. Verificação do estado das migrações
3. Confirmação da existência dos campos localmente
4. Identificação da migração em falta no Heroku

### Fase 2: Desenvolvimento de Ferramentas
1. Criação de comandos de diagnóstico
2. Desenvolvimento de ferramentas de aplicação segura
3. Implementação de testes automatizados
4. Criação de procedimentos de rollback

### Fase 3: Aplicação da Correção
1. Backup da base de dados
2. Aplicação da migração `0005_add_password_management_fields`
3. Verificação da correção
4. Testes de funcionalidade

### Fase 4: Monitoramento e Prevenção
1. Implementação de monitoramento contínuo
2. Atualização do processo de deployment
3. Documentação de procedimentos
4. Treino da equipe

## Medidas de Prevenção

### 1. Processo de Deployment Atualizado

#### Procfile Melhorado
```
release: python manage.py migrate --noinput
web: gunicorn lojad.wsgi --log-file -
```

#### Verificações Pré-Deployment
- Script `pre_deploy_check.sh` obrigatório antes de cada deploy
- Verificação de migrações pendentes
- Teste de comandos de verificação
- Validação de variáveis de ambiente

### 2. Monitoramento Proativo

#### Verificações Automáticas
- Monitoramento de saúde da base de dados a cada 5 minutos
- Alertas automáticos para problemas críticos
- Logs estruturados para análise

#### Métricas de Saúde
- Disponibilidade da base de dados > 99.9%
- Tempo de resposta < 100ms
- Zero erros de coluna
- Zero migrações pendentes

### 3. Procedimentos de Emergência

#### Rollback Rápido
- Comandos de rollback testados e documentados
- Backups automáticos antes de cada migração
- Procedimentos de restauração documentados

#### Contactos de Emergência
- Equipe de desenvolvimento
- Administrador de sistema
- Suporte técnico

## Testes e Validação

### Testes Automatizados
- ✅ Conectividade da base de dados
- ✅ Acessibilidade dos campos de senha
- ✅ Operações CRUD do modelo
- ✅ Compatibilidade com middleware
- ✅ Interface web funcional
- ✅ Cenários de integração

### Testes Manuais
- ✅ Login de utilizadores
- ✅ Criação de utilizadores
- ✅ Funcionalidade de troca de senha
- ✅ Acesso ao dashboard
- ✅ Gestão de utilizadores

## Resultados Obtidos

### Antes da Correção
- ❌ Erros de coluna em todos os logins
- ❌ Middleware de senha não funcional
- ❌ Impossibilidade de aceder à gestão de utilizadores
- ❌ Aplicação instável

### Após a Correção
- ✅ Login funcionando normalmente
- ✅ Middleware de senha operacional
- ✅ Gestão de utilizadores acessível
- ✅ Sistema estável e monitorizado

## Lições Aprendidas

### 1. Importância do Processo de Deployment
- Migrações devem ser aplicadas automaticamente
- Verificações pré-deployment são essenciais
- Testes em ambiente de staging são obrigatórios

### 2. Monitoramento Proativo
- Detecção precoce de problemas
- Alertas automáticos reduzem tempo de resposta
- Logs estruturados facilitam diagnóstico

### 3. Ferramentas de Diagnóstico
- Comandos específicos aceleram resolução
- Testes automatizados garantem qualidade
- Documentação detalhada facilita manutenção

## Recomendações Futuras

### 1. Melhorias no Processo
- Implementar CI/CD com testes automáticos
- Usar Heroku Review Apps para testes
- Implementar Heroku Pipelines para staging/production

### 2. Monitoramento Avançado
- Integração com ferramentas de APM (New Relic, Datadog)
- Alertas via Slack/Email
- Dashboard de métricas em tempo real

### 3. Automação Adicional
- Backups automáticos programados
- Testes de carga regulares
- Verificações de segurança automatizadas

## Comandos de Referência Rápida

### Verificação de Saúde
```bash
heroku run python manage.py monitor_database_health --app seu-app-name
```

### Aplicar Migrações
```bash
heroku run python manage.py apply_password_migrations --app seu-app-name
```

### Verificar Schema
```bash
heroku run python manage.py verify_schema --app usuarios --app seu-app-name
```

### Teste Completo
```bash
heroku run python manage.py test_system_complete --app seu-app-name
```

### Monitoramento Contínuo
```bash
./scripts/heroku_health_monitor.sh seu-app-name
```

### Rollback de Emergência
```bash
heroku run python manage.py rollback_password_fields --confirm --app seu-app-name
```

## Conclusão

A correção foi implementada com sucesso, resultando em:
- **Sistema estável** e funcional
- **Ferramentas robustas** de diagnóstico e correção
- **Processo melhorado** de deployment
- **Monitoramento proativo** implementado
- **Documentação completa** para manutenção futura

O sistema está agora preparado para prevenir problemas similares e responder rapidamente a qualquer issue que possa surgir.