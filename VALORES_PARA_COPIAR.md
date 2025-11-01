# 📋 VALORES PARA COPIAR E COLAR NO RENDER

## No topo da página: "Connect Repository"

Selecione:
```
lnfd2836/lvksistemas-app
```

---

## Name:
```
lvksistemas-app
```

---

## Region:
```
Oregon (US West)
```

---

## Branch:
```
main
```

---

## Root Directory: ⚠️ IMPORTANTE!
```
lvksistemas-app
```

---

## Build Command:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

---

## Start Command:
```
gunicorn lojad.wsgi --log-file -
```

---

## Environment Variables:

### 1ª Variável:
- **Key:** `SECRET_KEY`
- **Value:** `-8t07F-izHHtXzu954f2CEahMWk1BWmTEPFvseHJNurragygs29IlBK6iKkg9wyaCCk`

### 2ª Variável:
- **Key:** `DEBUG`
- **Value:** `False`

### 3ª Variável:
- **Key:** `PYTHON_VERSION`
- **Value:** `3.11.9`

---

## ⚠️ IMPORTANTE: Crie o PostgreSQL PRIMEIRO!

Antes de criar o Web Service, vá para:
https://dashboard.render.com

1. Clique em **New** → **PostgreSQL**
2. Name: `lvk-database`
3. Create Database

Depois volta e linka o banco!

---

## ✅ Depois que preencher tudo:

Clique em **"Create Web Service"** no final da página

---

**Copie e cole cada valor acima!** 📝

