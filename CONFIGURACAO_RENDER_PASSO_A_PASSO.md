# 🎯 Configuração Passo a Passo na Página do Render

Você está em: **https://dashboard.render.com/web/new**

Siga EXATAMENTE estes passos:

---

## 📋 **PASSO 1: Connect Repository (no topo)**

1. Você verá: **"Connect a repository"**
2. Clique em **"Connect GitHub"** (ou selecione GitHub se já conectou)
3. Procure por: `lnfd2836/lvksistemas-app`
4. **Selecione** esse repositório

---

## 📋 **PASSO 2: Basic Settings (baixo do Connect)**

### **Name:**
```
lvksistemas-app
```

### **Region:**
```
Oregon (US West)
```
*(ou a região mais próxima)*

### **Branch:**
```
main
```

### **Root Directory:** ⚠️ **MUITO IMPORTANTE!**
```
lvksistemas-app
```
*(Deixe só isso, nada mais!)*

### **Runtime:** *(se aparecer)*
```
Python 3
```

### **Python Version:** *(se aparecer)*
```
3.11.9
```

---

## 📋 **PASSO 3: Build & Deploy**

### **Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**COPIE E COLE EXATAMENTE ASSIM!**

### **Start Command:**
```bash
gunicorn lojad.wsgi --log-file -
```

**COPIE E COLE EXATAMENTE ASSIM!**

---

## 📋 **PASSO 4: Environment Variables**

Você verá uma seção com **"Add Environment Variable"**

### **Adicione estas variáveis UMA POR UMA:**

**1. Primeira variável:**
- **Key:** `SECRET_KEY`
- **Value:** `-8t07F-izHHtXzu954f2CEahMWk1BWmTEPFvseHJNurragygs29IlBK6iKkg9wyaCCk`
- Clique em **Add** ou **Save**

**2. Segunda variável:**
- **Key:** `DEBUG`
- **Value:** `False`
- Clique em **Add** ou **Save**

**3. Terceira variável:**
- **Key:** `PYTHON_VERSION`
- **Value:** `3.11.9`
- Clique em **Add** ou **Save**

---

## 📋 **PASSO 5: Link Database** ⚠️ **MAS ANTES PRECISA CRIAR O BANCO!**

**🛑 PARADO! ANTES DE CRIAR O WEB SERVICE:**

Você precisa **primeiro** criar o PostgreSQL Database. 

### **Como criar o banco:**

1. Volte para: https://dashboard.render.com
2. Clique em **"New"** → **"PostgreSQL"**
3. Preencha:
   - **Name:** `lvk-database`
   - **Region:** `Oregon (US West)`
   - **Plan:** `Free`
4. Clique em **Create Database**
5. Aguarde criar (1-2 minutos)

### **Depois volta aqui e:**

Na página do Web Service, você verá uma seção **"Link Database"** ou **"Connect Database"**:
1. Clique em **"Link Database"** (ou botão similar)
2. Selecione `lvk-database`
3. Será linkado como `DATABASE_URL` automaticamente

---

## 📋 **PASSO 6: Create Web Service**

Depois de tudo preenchido:
1. Role até o final da página
2. Clique em **"Create Web Service"** (ou **"Create"**)

---

## ⏱️ **O que acontece:**

O Render irá:
- Clonar seu repositório
- Instalar dependências
- Fazer build
- Iniciar o servidor

**Tempo:** 5-10 minutos

Você verá os logs em tempo real na tela!

---

## 🆘 **Se der erro:**

### **Erro: "Root Directory not found"**
✅ Certifique-se que digitou: `lvksistemas-app` (sem barra, sem ponto, só isso)

### **Erro: "Failed to install dependencies"**
✅ Certifique-se que os comandos estão CORRETOS (copie e cole exatamente)

### **Erro: "Port already in use"**
✅ Normal no início do build, aguarde

### **Erro: "DATABASE_URL not found"**
✅ Certifique-se que linkou o database `lvk-database`

---

## 🎯 **Resumo Rápido:**

1. ✅ Connect: `lnfd2836/lvksistemas-app`
2. ✅ Root Directory: `lvksistemas-app`
3. ✅ Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. ✅ Start: `gunicorn lojad.wsgi --log-file -`
5. ✅ Variáveis: SECRET_KEY, DEBUG, PYTHON_VERSION
6. ✅ Link: `lvk-database`
7. ✅ Create!

---

**Está conseguindo? Qual campo você está preenchendo agora?** 🤔

