# 🚀 Comandos e Informações para Deploy no Render

## ⚠️ IMPORTANTE: Você Precisa conectar um repositório Git

O Render **NÃO** faz deploy direto do Heroku. Você precisa ter o código em um repositório Git (GitHub, GitLab, ou Bitbucket).

---

## 🔑 SECRET_KEY Gerada

Use esta chave no Render:

```
SECRET_KEY=-8t07F-izHHtXzu954f2CEahMWk1BWmTEPFvseHJNurragygs29IlBK6iKkg9wyaCCk
```

---

## 📋 Checklist Passo a Passo

### ✅ PASSO 1: Conectar Repositório Git

Você tem 2 opções:

#### Opção A: Usar GitHub (Recomendado)

1. Vá para https://github.com
2. Crie um novo repositório chamado `lvksistemas-app`
3. No terminal local, execute:

```bash
cd "/home/luiz/Músicas/lvksistemas-app/lvksistemas-app"
git remote add github https://github.com/SEU_USUARIO/lvksistemas-app.git
git push github main
```

#### Opção B: Usar GitLab

1. Vá para https://gitlab.com
2. Crie um novo repositório chamado `lvksistemas-app`
3. No terminal local, execute:

```bash
cd "/home/luiz/Músicas/lvksistemas-app/lvksistemas-app"
git remote add gitlab https://gitlab.com/SEU_USUARIO/lvksistemas-app.git
git push gitlab main
```

---

### ✅ PASSO 2: Criar Database PostgreSQL no Render

1. No dashboard do Render: **New** → **PostgreSQL**
2. Configurações:
   - **Name:** `lvk-database`
   - **Region:** `Oregon (US West)`
   - **Plan:** `Free` (para teste) ou `Starter` ($7/mês)
3. Clique em **Create Database**
4. **COPIE** a **Internal Database URL** que aparece na tela

---

### ✅ PASSO 3: Criar Redis no Render

1. No dashboard do Render: **New** → **Redis**
2. Configurações:
   - **Name:** `lvk-redis`
   - **Region:** Mesma do banco
   - **Plan:** `Free` (para teste) ou `Starter` ($7/mês)
3. Clique em **Create Redis**
4. **COPIE** a **Internal Redis URL** que aparece na tela

---

### ✅ PASSO 4: Criar Web Service no Render

1. No dashboard do Render: **New** → **Web Service**
2. **Connect Repository:**
   - Conecte seu repositório GitHub/GitLab
   - Selecione a branch `main`

3. **Basic Settings:**
   - **Name:** `lvksistemas-app`
   - **Region:** Mesma do banco
   - **Branch:** `main`
   - **Root Directory:** `lvksistemas-app`

4. **Build & Deploy:**
   - **Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```
   - **Start Command:**
   ```bash
   gunicorn lojad.wsgi --log-file -
   ```

5. **Environment Variables:**

Adicione estas variáveis **UMA POR VEZ**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `-8t07F-izHHtXzu954f2CEahMWk1BWmTEPFvseHJNurragygs29IlBK6iKkg9wyaCCk` |
| `DEBUG` | `False` |
| `PYTHON_VERSION` | `3.11.9` |

Para `DATABASE_URL` e `REDIS_URL`:
- Clique em **Link database**
- Selecione `lvk-database` → Link como `DATABASE_URL`
- Clique em **Link database** novamente
- Selecione `lvk-redis` → Link como `REDIS_URL`

**Opcionais:**

| Key | Value |
|-----|-------|
| `ASAAS_API_KEY` | (sua chave se tiver) |
| `ASAAS_ENVIRONMENT` | `sandbox` |
| `EMAIL_HOST_USER` | (seu email) |
| `EMAIL_HOST_PASSWORD` | (sua senha app) |
| `DEFAULT_FROM_EMAIL` | `noreply@lvksistemas.com.br` |

6. **Advanced:**
   - **Auto-Deploy:** `Yes`

7. Clique em **Create Web Service**

---

### ✅ PASSO 5: Aguardar Build

O Render irá:
1. Clonar seu repositório
2. Instalar dependências
3. Coletar arquivos estáticos
4. Iniciar o servidor

**Tempo:** 5-10 minutos

---

### ✅ PASSO 6: Executar Migrações

1. No Render: vá para **Web Service** → **Shell**
2. Execute:

```bash
python manage.py migrate
```

---

### ✅ PASSO 7: Criar Superusuário

No mesmo Shell:

```bash
python manage.py createsuperuser
```

Informe:
- Username: `admin`
- Email: `admin@lvksistemas.com.br`
- Password: `SuaSenhaSegura123!`

---

### ✅ PASSO 8: Testar

1. Copie a URL do seu serviço (ex: `https://lvksistemas-app.onrender.com`)
2. Acesse no navegador
3. Faça login com o superusuário

---

## 🎉 Pronto!

Seu sistema está no ar!

---

## 🔄 Atualizar no Futuro

Sempre que fizer mudanças no código:

```bash
git add .
git commit -m "Sua mensagem"
git push github main  # ou gitlab, conforme configurado
```

O Render faz deploy automático! ✅

---

## 🚨 Problemas Comuns

### Erro: "No such file or directory: requirements.txt"
- Verifique se o Root Directory está como `lvksistemas-app`

### Erro 500
- Verifique os logs
- Execute migrações novamente

### Arquivos estáticos não carregam
```bash
python manage.py collectstatic --noinput
```

---

## 📞 Precisa de Ajuda?

- Dashboard Render: https://dashboard.render.com
- Documentação: https://render.com/docs
- Ver logs: Render → Web Service → Logs

