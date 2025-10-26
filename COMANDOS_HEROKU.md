# Comandos para Corrigir Problemas no Heroku

## 🚨 Problema Identificado

O erro no Heroku é causado por **tabelas faltando no banco de dados**:
- `no such table: controle_financeiro_controlefinanceiro`
- `no such table: modulos_tipoloja`

Isso indica que as **migrações não foram executadas** corretamente.

## 🔧 Solução - Executar Migrações

### 1. Via Heroku CLI (Recomendado)

```bash
# Conectar ao Heroku
heroku login

# Executar migrações
heroku run python manage.py makemigrations --app lvksistemas-app-4f6fa281e217
heroku run python manage.py migrate --app lvksistemas-app-4f6fa281e217

# Verificar se funcionou
heroku logs --tail --app lvksistemas-app-4f6fa281e217
```

### 2. Via Script Personalizado

```bash
# Executar script de migração
heroku run python heroku_migrate.py --app lvksistemas-app-4f6fa281e217

# Ou script completo de correção
heroku run python corrigir_migracao_heroku.py --app lvksistemas-app-4f6fa281e217
```

### 3. Verificar Status do Banco

```bash
# Conectar ao banco diretamente
heroku pg:psql --app lvksistemas-app-4f6fa281e217

# Ou se for SQLite, executar shell
heroku run python manage.py shell --app lvksistemas-app-4f6fa281e217
```

## 📋 Comandos de Diagnóstico

### Verificar Logs
```bash
# Ver logs em tempo real
heroku logs --tail --app lvksistemas-app-4f6fa281e217

# Ver logs específicos
heroku logs --source app --app lvksistemas-app-4f6fa281e217
```

### Verificar Configurações
```bash
# Ver variáveis de ambiente
heroku config --app lvksistemas-app-4f6fa281e217

# Ver informações do app
heroku info --app lvksistemas-app-4f6fa281e217
```

### Verificar Banco de Dados
```bash
# Se for PostgreSQL
heroku pg:info --app lvksistemas-app-4f6fa281e217

# Executar shell Django
heroku run python manage.py shell --app lvksistemas-app-4f6fa281e217
```

## 🔄 Processo Completo de Correção

### Passo 1: Fazer Deploy das Correções
```bash
# Commit das alterações locais
git add .
git commit -m "Fix: Adiciona função dashboard_fatesa e scripts de migração"

# Push para Heroku
git push heroku main
```

### Passo 2: Executar Migrações
```bash
# Executar migrações
heroku run python manage.py makemigrations --app lvksistemas-app-4f6fa281e217
heroku run python manage.py migrate --app lvksistemas-app-4f6fa281e217
```

### Passo 3: Criar Superuser (se necessário)
```bash
# Criar superuser
heroku run python manage.py createsuperuser --app lvksistemas-app-4f6fa281e217
```

### Passo 4: Verificar Funcionamento
```bash
# Ver logs
heroku logs --tail --app lvksistemas-app-4f6fa281e217

# Testar no navegador
# https://lvksistemas-app-4f6fa281e217.herokuapp.com/
```

## 🎯 Comandos Específicos para Tabelas Faltando

### Verificar Migrações Pendentes
```bash
heroku run python manage.py showmigrations --app lvksistemas-app-4f6fa281e217
```

### Executar Migrações por App
```bash
# Controle Financeiro
heroku run python manage.py migrate controle_financeiro --app lvksistemas-app-4f6fa281e217

# Módulos
heroku run python manage.py migrate modulos --app lvksistemas-app-4f6fa281e217

# Lojas
heroku run python manage.py migrate lojas --app lvksistemas-app-4f6fa281e217
```

### Forçar Recriação de Migrações
```bash
# Deletar migrações (cuidado!)
heroku run python manage.py migrate --fake-initial --app lvksistemas-app-4f6fa281e217

# Recriar migrações
heroku run python manage.py makemigrations --app lvksistemas-app-4f6fa281e217
heroku run python manage.py migrate --app lvksistemas-app-4f6fa281e217
```

## 🚨 Comandos de Emergência

### Reset Completo do Banco (CUIDADO!)
```bash
# Apenas se necessário - APAGA TODOS OS DADOS
heroku pg:reset DATABASE_URL --app lvksistemas-app-4f6fa281e217 --confirm lvksistemas-app-4f6fa281e217

# Depois executar migrações
heroku run python manage.py migrate --app lvksistemas-app-4f6fa281e217
heroku run python manage.py createsuperuser --app lvksistemas-app-4f6fa281e217
```

### Restart da Aplicação
```bash
# Reiniciar dynos
heroku restart --app lvksistemas-app-4f6fa281e217
```

## ✅ Verificação Final

Após executar as migrações, testar:

1. **Dashboard Principal**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/dashboard/
2. **Login Personalizado FATESA**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/fatesa-escola-de-ultrassonografia/
3. **Login Personalizado Felix**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/loja-felix/

## 📞 Comandos de Monitoramento

```bash
# Monitorar logs em tempo real
heroku logs --tail --app lvksistemas-app-4f6fa281e217

# Ver métricas
heroku ps --app lvksistemas-app-4f6fa281e217

# Ver releases
heroku releases --app lvksistemas-app-4f6fa281e217
```

---

**⚠️ IMPORTANTE**: Execute os comandos na ordem apresentada e monitore os logs para verificar se não há erros.