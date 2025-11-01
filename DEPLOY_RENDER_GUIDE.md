# Guia de Deploy para Render - LVK Sistemas

## 🚀 Deploy no Render

Este guia fornece instruções passo a passo para fazer o deploy do sistema LVK Sistemas na plataforma Render.

---

## 📋 Pré-requisitos

1. Conta no [Render](https://dashboard.render.com/)
2. Repositório Git (GitHub, GitLab, Bitbucket ou outro)
3. Sistema Django configurado

---

## 🎯 Opção 1: Deploy Automatizado com `render.yaml` (Recomendado)

### 1. Criar Database PostgreSQL

No dashboard do Render:

1. Clique em **New** → **PostgreSQL**
2. Preencha as informações:
   - **Name:** `lvk-database`
   - **Database:** `lvksistemas`
   - **User:** `lvk_user`
   - **Region:** Escolha a região mais próxima (ex: São Paulo, se disponível)
   - **Plan:** `Starter` (ou superior conforme necessário)
3. Clique em **Create Database**

### 2. Criar Redis

No dashboard do Render:

1. Clique em **New** → **Redis**
2. Preencha as informações:
   - **Name:** `lvk-redis`
   - **Plan:** `Starter`
3. Clique em **Create Redis**

### 3. Fazer Deploy da Aplicação Web

No dashboard do Render:

1. Clique em **New** → **Web Service**
2. Conecte seu repositório Git
3. Configure o serviço:
   - **Name:** `lvksistemas-app`
   - **Region:** Mesma região do banco de dados
   - **Branch:** `main` (ou a branch principal)
   - **Root Directory:** `lvksistemas-app` (se o projeto estiver em um subdiretório)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn lojad.wsgi --log-file -`

4. **Variáveis de Ambiente:**

Adicione as seguintes variáveis:

```bash
# Django
SECRET_KEY=<gere-uma-chave-secreta-aleatória>
DEBUG=False
PYTHON_VERSION=3.11.9

# Database (será preenchido automaticamente se você vincular o banco)
DATABASE_URL=<connection-string-do-postgresql>

# Redis (será preenchido automaticamente se você vincular)
REDIS_URL=<connection-string-do-redis>

# Asaas
ASAAS_API_KEY=<sua-chave-asaas>
ASAAS_ENVIRONMENT=sandbox  # ou production

# Email (opcional mas recomendado)
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@lvksistemas.com.br

# Site
SITE_URL=https://seu-app.onrender.com
```

5. Clique em **Create Web Service**

---

## 🔧 Opção 2: Deploy Manual (Passo a Passo)

### 1. Configurar o Banco de Dados

```bash
# No dashboard do Render, crie um PostgreSQL:
# New → PostgreSQL
# Nome: lvk-database
# Salve a connection string (DATABASE_URL)
```

### 2. Configurar Redis

```bash
# No dashboard do Render, crie um Redis:
# New → Redis
# Nome: lvk-redis
# Salve a connection string (REDIS_URL)
```

### 3. Criar Web Service

1. **Repository:**
   - Conecte seu repositório Git

2. **Basic Settings:**
   - **Name:** `lvksistemas-app`
   - **Region:** Escolha a região
   - **Branch:** `main` ou `master`
   - **Root Directory:** `lvksistemas-app`

3. **Build & Deploy:**
   - **Build Command:** 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```bash
     gunicorn lojad.wsgi --log-file -
     ```

4. **Environment Variables:**

   Adicione todas as variáveis listadas na **Opção 1**.

---

## 📝 Comandos Pós-Deploy

Após o deploy, você precisará executar migrações e criar um superusuário:

### 1. Executar Migrações

No dashboard do Render:

1. Vá para seu **Web Service**
2. Clique na aba **Shell**
3. Execute:

```bash
python manage.py migrate
```

### 2. Criar Superusuário

No shell do Render:

```bash
python manage.py createsuperuser
```

Informe:
- Username: admin
- Email: admin@lvksistemas.com.br
- Password: (uma senha segura)

### 3. Coletar Arquivos Estáticos (se necessário)

```bash
python manage.py collectstatic --noinput
```

---

## 🔐 Variáveis de Ambiente Importantes

### Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta do Django | Gere com: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | Modo debug | `False` |
| `DATABASE_URL` | URL do PostgreSQL | Preenchido automaticamente pelo Render |
| `REDIS_URL` | URL do Redis | Preenchido automaticamente pelo Render |

### Recomendadas

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `ASAAS_API_KEY` | Chave API Asaas | `$01$...` |
| `ASAAS_ENVIRONMENT` | Ambiente Asaas | `sandbox` ou `production` |
| `EMAIL_HOST_USER` | Email para envio | `sistema@lvksistemas.com.br` |
| `EMAIL_HOST_PASSWORD` | Senha do email | Senha do app |
| `SITE_URL` | URL do site | `https://seu-app.onrender.com` |

---

## 🚨 Solução de Problemas

### Erro 500 Internal Server Error

**Verificar:**
1. Logs no dashboard do Render
2. Variáveis de ambiente configuradas
3. Banco de dados conectado
4. Migrações executadas

**Solução:**
```bash
# Ver logs
# No Render, vá para Web Service → Logs

# Executar migrações novamente
python manage.py migrate

# Verificar configuração
python manage.py check --deploy
```

### Erro: No module named 'xyz'

**Causa:** Dependências não instaladas

**Solução:**
- Verifique o `requirements.txt`
- Refaça o build

### Erro: Database Connection

**Causa:** DATABASE_URL não configurado

**Solução:**
1. Vá para Database no Render
2. Copie a **Internal Database URL**
3. Adicione como variável `DATABASE_URL`

### Arquivos Estáticos Não Carregando

**Solução:**
```bash
# Reexecutar collectstatic
python manage.py collectstatic --noinput

# Verificar whitenoise no settings.py
# Deve estar instalado e configurado
```

---

## 🔄 Atualizações

### Deploy Automático

O Render faz deploy automático quando você faz push para a branch configurada:

```bash
git add .
git commit -m "Atualização do sistema"
git push origin main
```

### Deploy Manual

```bash
# No Render Dashboard:
# Vá para Web Service → Manual Deploy → Deploy latest commit
```

---

## 📊 Monitoramento

### Logs

No Render:
- **Web Service** → **Logs**: Ver logs em tempo real
- **Metrics**: CPU, Memória, Requests

### Health Checks

O Render verifica automaticamente se sua aplicação está respondendo. O endpoint padrão é `/`.

---

## 🔒 Segurança

### HTTPS

O Render fornece HTTPS automaticamente. Certificado SSL renovado automaticamente.

### Headers de Segurança

Já configurados no `settings_production.py`:
- `X_FRAME_OPTIONS = 'DENY'`
- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`

---

## 💰 Custos

### Gratuito (Free Tier)

- **Web Service:** Sono após 15 minutos de inatividade
- **Database:** Dados deletados após 90 dias
- **Redis:** Perda de dados após reiniciar

### Starter Plan

- **Web Service:** $7/mês
- **Database:** $7/mês
- **Redis:** $7/mês
- **Sem sono:** Aplicação sempre online
- **Backups:** Automáticos

---

## 📞 Suporte

- **Documentação Render:** https://render.com/docs
- **Status Render:** https://status.render.com/
- **Suporte:** Via dashboard do Render

---

## ✅ Checklist de Deploy

- [ ] Database PostgreSQL criado
- [ ] Redis criado
- [ ] Web Service criado
- [ ] Repositório conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Build funcionando
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Site acessível
- [ ] HTTPS funcionando
- [ ] Logs sem erros

---

## 🎉 Pronto!

Seu sistema LVK Sistemas está no ar!

**URL:** `https://seu-app.onrender.com`

**Admin:** `https://seu-app.onrender.com/admin/`

---

**Deploy realizado com sucesso! 🚀**

