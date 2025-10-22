# 🔧 COMANDOS PARA CONFIGURAR MANUALMENTE

## **📋 EXECUTE ESTES COMANDOS NO TERMINAL:**

### **1. Configurar API Key de Produção:**
```bash
heroku config:set ASAAS_API_KEY='$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl' --app lvksistemas-app
```

### **2. Configurar Ambiente como Produção:**
```bash
heroku config:set ASAAS_ENVIRONMENT='production' --app lvksistemas-app
```

### **3. Verificar se foi Configurado:**
```bash
heroku config --app lvksistemas-app
```

### **4. Testar a Configuração:**
```bash
heroku run "python -c \"
import os
from controle_financeiro.asaas_service import AsaasService
print('🔑 API Key:', os.environ.get('ASAAS_API_KEY', 'NÃO CONFIGURADA')[:30] + '...')
print('🌐 Environment:', os.environ.get('ASAAS_ENVIRONMENT', 'NÃO CONFIGURADO'))
asaas = AsaasService()
if asaas.validar_configuracao():
    print('✅ API funcionando!')
else:
    print('❌ API com problemas')
\"" --app lvksistemas-app
```

## **🌐 ALTERNATIVA: Via Dashboard do Heroku**

Se não tiver Heroku CLI instalado:

1. **Acesse**: https://dashboard.heroku.com/apps/lvksistemas-app
2. **Vá para**: Settings → Config Vars
3. **Adicione**:
   - **Key**: `ASAAS_API_KEY`
   - **Value**: `$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmQ3NThmNTk3LTUyNjgtNGJjMC04NmMzLWFjNGM2YmY3NGFkZjo6JGFhY2hfZDRkYzJjMzAtZDNhYy00ZThiLTgzY2UtZjAxZGVjZmM2Y2Jl`
4. **Adicione**:
   - **Key**: `ASAAS_ENVIRONMENT`
   - **Value**: `production`
5. **Clique**: "Add" para cada uma

## **🧪 TESTE FINAL**

Após configurar:

1. **Acesse**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/
2. **Login**: admin / admin123
3. **Vá para**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/67/
4. **Gere o boleto** - deve funcionar sem erro!

## **📊 RESULTADO ESPERADO**

✅ **Sem erro de configuração**  
✅ **Boleto gerado com sucesso**  
✅ **PIX funcionando**  
✅ **Sistema operacional**  

---

**Execute um dos métodos acima e teste!** 🚀