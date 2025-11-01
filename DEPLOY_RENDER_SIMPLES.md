# 🚀 Deploy SIMPLES no Render (SEM Redis)

## ✅ Versão Simplificada - Aplicação Básica

Esta versão **NÃO** inclui Redis/Celery, então tarefas assíncronas ficarão desabilitadas. Perfeito para teste e uso básico!

---

## 📋 PASSO A PASSO

### **PASSO 1: Criar PostgreSQL Database**

No dashboard do Render (https://dashboard.render.com):

1. Clique em **New** → **PostgreSQL**
2. Preencha:
   - **Name:** `lvk-database`
   - **Region:** `Oregon (US West)`
   - **Plan:** `Free` (para teste)
3. Clique em **Create Database**
4. ⚠️ **NÃO** precisa copiar nada ainda

---

### **PASSO 2: Criar Web Service**

1. No Render: **New** → **Web Service**

2. **Connect Repository:**
   - Clique em **"Connect a repository"**
   - Selecione **GitHub**
   - Autorize o Render se necessário
   - Procure por `lnfd2836/lvksistemas-app`
   - **Selecione o repositório**

3. **Basic Settings:**
   - **Name:** `lvksistemas-app`
   - **Region:** Mesma do banco
   - **Branch:** `main`
   - **Root Directory:** `lvksistemas-app` ⚠️ **IMPORTANTE!**

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

   **Adicione estas variáveis (uma por vez):**

   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | `-8t07F-izHHtXzu954f2CEahMWk1BWmTEPFvseHJNurragygs29IlBK6iKkg9wyaCCk` |
   | `DEBUG` | `False` |
   | `PYTHON_VERSION` | `3.11.9` |
   
   **Link Database:**
   - Clique em **"Link database"**
   - Selecione `lvk-database` → Link como `DATABASE_URL`
   
   **⚠️ NÃO adicione REDIS_URL** - não é necessário para versão simples!

6. **Advanced:**
   - **Auto-Deploy:** `Yes`

7. **Clique em "Create Web Service"**

---

### **PASSO 3: Aguardar Build**

O Render irá:
- ✅ Clonar seu repositório
- ✅ Instalar dependências
- ✅ Coletar arquivos estáticos
- ✅ Iniciar o servidor

**⏱️ Tempo:** 5-10 minutos

---

### **PASSO 4: Executar Migrações**

Após o build completar:

1. No Render: vá para **Web Service** → **Shell**
2. Execute:
```bash
python manage.py migrate
```

---

### **PASSO 5: Criar Superusuário**

No mesmo Shell:

```bash
python manage.py createsuperuser
```

Informe:
- **Username:** `admin`
- **Email:** `admin@lvksistemas.com.br`
- **Password:** *(sua senha segura)*

---

### **PASSO 6: Testar**

1. Copie a URL do serviço (ex: `https://lvksistemas-app.onrender.com`)
2. Acesse no navegador
3. Faça login com o superusuário criado

---

## 🎉 **PRONTO!**

Seu sistema LVK está funcionando!

---

## ⚠️ **LIMITAÇÕES**

### **O que NÃO funciona sem Redis:**

- ❌ Backup automático diário
- ❌ Boletos automáticos
- ❌ Sincronização automática com Asaas
- ❌ Notificações por email automáticas
- ❌ Tarefas agendadas

### **O que FUNCIONA:**

- ✅ Login/Autenticação
- ✅ Dashboard
- ✅ CRUD de lojas, produtos, clientes
- ✅ Vendas manuais
- ✅ Relatórios
- ✅ Todas as funcionalidades básicas!

---

## 🔄 **Adicionar Redis Depois (Opcional)**

Se você quiser habilitar tarefas automáticas depois:

1. Criar Redis no Render
2. Adicionar variável `REDIS_URL` no Web Service
3. Criar serviço Worker Celery (opcional)

---

**Deploy simplificado concluído! 🚀**

