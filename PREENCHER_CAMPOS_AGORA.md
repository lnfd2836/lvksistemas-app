# 📝 PREENCHER CAMPOS AGORA - Siga na Ordem!

## ✅ Você tem:
- PostgreSQL criado ✅
- Página do Web Service aberta ✅

---

## 🎯 AGORA PREENCHA NESTA ORDEM:

### **1. Connect Repository (no topo da página):**
- Selecione: `lnfd2836/lvksistemas-app`

### **2. Name:**
- Digite: `lvksistemas-app`

### **3. Region:**
- Selecione: `Oregon (US West)`

### **4. Branch:**
- Selecione: `main`

### **5. Root Directory:** ⚠️ MUITO IMPORTANTE!
- Digite: `lvksistemas-app`
- **CUIDADO:** Só isso! Sem barra, sem ponto!

### **6. Build Command:**
- Cole: `pip install -r requirements.txt && python manage.py collectstatic --noinput`

### **7. Start Command:**
- Cole: `gunicorn lojad.wsgi --log-file -`

### **8. Environment Variables:**

Clique em "Add Environment Variable" e adicione UMA POR VEZ:

**1ª variável:**
- Key: `SECRET_KEY`
- Value: `-8t07F-izHHtXzu954f2CEahMWk1BWmTEPFvseHJNurragygs29IlBK6iKkg9wyaCCk`

**2ª variável:**
- Key: `DEBUG`
- Value: `False`

**3ª variável:**
- Key: `PYTHON_VERSION`
- Value: `3.11.9`

### **9. Link Database:**
- Clique em "Link Database" (ou botão similar)
- Selecione: `lvk-database`
- Link como: `DATABASE_URL` (automático)

### **10. Create!**
- Role até o final da página
- Clique em "Create Web Service"

---

## ⏱️ O que vai acontecer:
- O Render vai fazer o build (5-10 minutos)
- Você verá os logs em tempo real
- Aguarde completar!

---

## 🆘 Se der erro:
**Me diga qual erro aparece!**

---

## ✅ Próximos passos (depois do build):
1. Vá em Shell
2. Execute: `python manage.py migrate`
3. Execute: `python manage.py createsuperuser`

---

**Preencheu tudo? Clicou em "Create"?** 🚀

