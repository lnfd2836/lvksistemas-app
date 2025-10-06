# Procedimentos de Deployment - Heroku

## Processo Atualizado de Deployment

### 1. Verificação Pré-Deployment

Antes de fazer qualquer deploy, execute:

```bash
./scripts/pre_deploy_check.sh nome-do-seu-app
```

Este script verifica:
- ✅ Existência do app no Heroku
- ✅ Migrações pendentes localmente
- ✅ Migrações pendentes no Heroku
- ✅ Configuração do Procfile
- ✅ Disponibilidade dos comandos de verificação
- ✅ Variáveis de ambiente críticas

### 2. Procfile Atualizado

O Procfile agora inclui a fase de release:

```
release: python manage.py migrate --noinput
web: gunicorn lojad.wsgi --log-file -
```

**Importante**: A fase `release` executa automaticamente antes de cada deploy, garantindo que as migrações sejam aplicadas.

### 3. Processo de Deploy

1. **Verificação local**:
   ```bash
   python manage.py makemigrations --check
   python manage.py check
   ```

2. **Commit das mudanças**:
   ```bash
   git add .
   git commit -m "Sua mensagem de commit"
   ```

3. **Verificação pré-deploy**:
   ```bash
   ./scripts/pre_deploy_check.sh seu-app-name
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Monitoramento**:
   ```bash
   heroku logs --tail --app seu-app-name
   ```

### 4. Verificação Pós-Deploy

Após o deploy, execute os comandos de verificação:

```bash
# Verificar status das migrações
heroku run python manage.py check_migrations --app seu-app-name

# Verificar schema
heroku run python manage.py verify_schema --app usuarios --app seu-app-name

# Testar funcionalidade de senha
heroku run python manage.py test_password_functionality --app seu-app-name
```

### 5. Comandos de Emergência

Se algo der errado durante o deploy:

#### Rollback Rápido
```bash
heroku rollback --app seu-app-name
```

#### Verificar Logs de Erro
```bash
heroku logs --app seu-app-name | grep ERROR
```

#### Aplicar Migrações Manualmente
```bash
heroku run python manage.py apply_password_migrations --app seu-app-name
```

#### Verificar Saúde da Base de Dados
```bash
heroku pg:info --app seu-app-name
```

### 6. Monitoramento Contínuo

#### Logs em Tempo Real
```bash
heroku logs --tail --app seu-app-name
```

#### Verificar Erros Específicos
```bash
heroku logs --app seu-app-name | grep "requires_password_change"
```

#### Status da Aplicação
```bash
heroku ps --app seu-app-name
```

### 7. Troubleshooting

#### Problema: Migração Falha
**Solução**:
```bash
heroku run python manage.py migrate --fake-initial --app seu-app-name
heroku run python manage.py apply_password_migrations --force --app seu-app-name
```

#### Problema: Campos Não Existem
**Solução**:
```bash
heroku run python manage.py apply_password_migrations --app seu-app-name
```

#### Problema: App Não Inicia
**Solução**:
```bash
heroku restart --app seu-app-name
heroku logs --tail --app seu-app-name
```

### 8. Checklist de Deploy

- [ ] Código testado localmente
- [ ] Migrações criadas se necessário
- [ ] Verificação pré-deploy executada
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy executado
- [ ] Logs monitorados durante deploy
- [ ] Verificação pós-deploy executada
- [ ] Funcionalidade testada em produção

### 9. Configurações Recomendadas

#### Variáveis de Ambiente
```bash
heroku config:set DEBUG=False --app seu-app-name
heroku config:set ALLOWED_HOSTS=seu-dominio.com,seu-app-name.herokuapp.com --app seu-app-name
```

#### Add-ons Recomendados
```bash
heroku addons:create heroku-postgresql:mini --app seu-app-name
heroku addons:create papertrail:choklad --app seu-app-name
```

### 10. Automação Futura

Para automatizar ainda mais o processo, considere:

1. **GitHub Actions** para CI/CD
2. **Heroku Review Apps** para testing
3. **Heroku Pipelines** para staging/production
4. **Automated testing** antes do deploy

## Comandos Criados para Suporte

- `check_migrations`: Verifica status das migrações
- `apply_password_migrations`: Aplica migrações de forma segura
- `verify_schema`: Verifica consistência do schema
- `test_password_functionality`: Testa funcionalidade de senhas

Estes comandos estão disponíveis tanto localmente quanto no Heroku.