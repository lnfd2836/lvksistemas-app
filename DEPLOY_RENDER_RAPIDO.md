# 🚀 Guia Rápido de Deploy no Render

## 📋 Checklist Rápido

Siga estes passos na ordem para fazer o deploy do sistema LVK Sistemas no Render.

---

## 1️⃣ Criar PostgreSQL Database

1. No dashboard do Render: **New** → **PostgreSQL**
2. Configurações:
   - **Name:** `lvk-database`
   - **Region:** Escolha a região (EU/USA/EU)
   - **Database:** `lvksistemas`
   - **User:** `lvk_user`
   - **Plan:** `Starter` ($7/mês) ou `Free` (teste)
3. Clique em **Create Database**
4. **IMPORTANTE:** Copie a **Internal Database URL** (ela será usada depois)

---

## 2️⃣ Criar Redis

1. No dashboard do Render: **New** → **Redis**
2. Configurações:
   - **Name:** `lvk-redis`
   - **Region:** Mesma do banco
   - **Plan:** `Starter` ($7/mês) ou `Free` (teste)
3. Clique em **Create Redis**
4. **IMPORTANTE:** Copie a **Internal Redis URL**

---

## 3️⃣ Criar Web Service

1. No dashboard do Render: **New** → **Web Service**
2. Conecte seu repositório Git (GitHub/GitLab/Bitbucket)
3. Configurações:

### Basic Settings
- **Name:** `lvksistemas-app`
- **Region:** Mesma do banco
- **Branch:** `main` (ou sua branch principal)
- **Root Directory:** `lvksistemas-app`

### Build & Deploy
- **Environment:** `Python 3`
- **Build Command:** 
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command:**
  ```bash
  gunicorn lojad.wsgi --log-file -
  ```

### Environment Variables

Adicione TODAS estas variáveis:

#### Django Básicas
```
SECRET_KEY=<GERE_UMA_CHAVE_SEGRETA>
DEBUG=False
PYTHON_VERSION=3.11.9
```

#### Database & Redis
```
DATABASE_URL=<Internal_Database_URL_do_Passo_1>
REDIS_URL=<Internal_Redis_URL_do_Passo_2>
```

#### Asaas (Opcional, mas recomendado)
```
ASAAS_API_KEY=<sua-chave-asaas>
ASAAS_ENVIRONMENT=sandbox
```

#### Email (Opcional, mas recomendado)
```
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@lvksistemas.com.br
```

#### Site
```
SITE_URL=https://seu-app.onrender.com
```

### Advanced - Auto-Deploy
- **Auto-Deploy:** `Yes` (deploy automático a cada push)

4. Clique em **Create Web Service**

---

## 4️⃣ Configurar Ambiente

### Gerar SECRET_KEY

No terminal local:
```bash
cd lvksistemas-app
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie a chave gerada e adicione como `SECRET_KEY` no Render.

### Adicionar Database URL

No Render:
1. Vá para seu **Web Service**
2. Aba **Environment**
3. Role até encontrar `DATABASE_URL`
4. Clique em **Link database from:**
5. Selecione `lvk-database`
6. Clique em **Link** e salve

### Adicionar Redis URL

Repita o processo para Redis:
1. Clique em **Add Environment Variable**
2. Clique em **Link**
3. Selecione `lvk-redis`
4. Link como `REDIS_URL`

---

## 5️⃣ Primeiro Deploy

O Render irá:
1. ✅ Clonar seu repositório
2. ✅ Instalar dependências (`pip install -r requirements.txt`)
3. ✅ Coletar arquivos estáticos
4. ✅ Iniciar o servidor

**Aguarde o build completar (5-10 minutos)**

---

## 6️⃣ Executar Migrações

1. Vá para seu **Web Service**
2. Aba **Shell**
3. Execute:

```bash
python manage.py migrate
```

Aguarde completar.

---

## 7️⃣ Criar Superusuário

No mesmo Shell:

```bash
python manage.py createsuperuser
```

Informe:
- Username: `admin`
- Email: `admin@lvksistemas.com.br`
- Password: **(sua senha segura)**

---

## 8️⃣ Testar

1. Copie a URL do seu serviço (ex: `https://lvksistemas-app.onrender.com`)
2. Abra no navegador
3. Faça login com o superusuário criado

---

## ✅ Pronto!

Seu sistema está no ar! 🎉

---

## 🔧 Comandos Úteis

### Ver Logs
No Render → Web Service → Logs

### Shell
No Render → Web Service → Shell

### Reiniciar
No Render → Web Service → Manual Deploy → Deploy latest commit

### Reexecutar Migrações
```bash
python manage.py migrate
```

### Criar Novos Usuários
```bash
python manage.py createsuperuser
```

### Coletar Estáticos Novamente
```bash
python manage.py collectstatic --noinput
```

---

## 🚨 Solução Rápida de Problemas

### Site não carrega (erro 502)
- Verificar logs: Web Service → Logs
- Verificar se build completou
- Verificar DATABASE_URL configurado

### Erro 500
- Executar migrações: `python manage.py migrate`
- Verificar logs para erro específico

### Arquivos estáticos quebrados
```bash
python manage.py collectstatic --noinput
```

### Não consigo fazer login
- Criar superusuário novamente

---

## 🔄 Atualizar Sistema

```bash
# No seu terminal local
git add .
git commit -m "Atualização"
git push origin main
```

O Render irá fazer deploy automático! ✅

---

## 📞 Suporte

- Dashboard Render: https://dashboard.render.com
- Documentação: https://render.com/docs
- Status: https://status.render.com

---

**Boa sorte com o deploy! 🚀**

