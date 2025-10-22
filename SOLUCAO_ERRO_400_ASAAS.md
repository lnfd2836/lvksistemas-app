# 🔧 SOLUÇÃO COMPLETA - ERRO 400 API ASAAS

## 🎯 **PROBLEMA IDENTIFICADO**

❌ **API Key Inválida**: O sistema está usando uma API Key de exemplo/placeholder:
```
ASAAS_API_KEY=3f12cef7-f5a3-446e-b1ba-1eb37090298d
```

Esta não é uma API Key real do Asaas, é apenas um UUID genérico usado como placeholder.

## ✅ **SOLUÇÃO COMPLETA**

### **PASSO 1: Obter API Key Real do Asaas**

1. **Acesse**: https://www.asaas.com
2. **Faça login** na sua conta Asaas
3. **Vá para**: Configurações → Integrações → API
4. **Escolha o ambiente**:
   - **Sandbox** (para testes)
   - **Produção** (para uso real)
5. **Clique em**: "Gerar nova chave"
6. **Copie** a chave gerada

### **PASSO 2: Configurar no Heroku (Produção)**

```bash
# Configurar API Key de PRODUÇÃO
heroku config:set ASAAS_API_KEY='SUA_API_KEY_DE_PRODUCAO_AQUI' --app lvksistemas-app

# Configurar ambiente como produção
heroku config:set ASAAS_ENVIRONMENT='production' --app lvksistemas-app

# Verificar configuração
heroku config --app lvksistemas-app
```

### **PASSO 3: Configurar Localmente (Desenvolvimento)**

Edite o arquivo `.env`:

```env
# Configurações da API Asaas
ASAAS_API_KEY=SUA_API_KEY_AQUI
ASAAS_ENVIRONMENT=sandbox  # ou production
SITE_URL=https://lvksistemas-app-4f6fa281e217.herokuapp.com
```

### **PASSO 4: Testar a Configuração**

Execute o comando no Heroku para testar:

```bash
heroku run "python -c \"
import os
print('API Key:', os.environ.get('ASAAS_API_KEY', 'NÃO CONFIGURADA')[:20] + '...')
print('Environment:', os.environ.get('ASAAS_ENVIRONMENT', 'NÃO CONFIGURADO'))
\"" --app lvksistemas-app
```

## 🧪 **TESTE COMPLETO**

Após configurar a API Key, teste a geração de boleto:

1. **Acesse**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/
2. **Login**: admin / admin123
3. **Vá para**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/gerar/67/
4. **Selecione**: "Asaas I.P S.A"
5. **Clique**: "Gerar Boleto"

## 📋 **FORMATOS DE API KEY VÁLIDOS**

### **Sandbox (Testes)**
```
$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDI2NzA6OiRhYWNoXzlmNzMwMjNkLTc4YzItNGY4Zi1hZGY2LTQyMzAzZGY5NzI4Nw==
```

### **Produção**
```
$aact_prod_1234567890abcdef1234567890abcdef
```

## ⚠️ **IMPORTANTE**

- ✅ **API Key de Sandbox**: Só funciona no ambiente de testes
- ✅ **API Key de Produção**: Só funciona no ambiente real
- ❌ **Nunca compartilhe** sua API Key de produção
- 🔒 **Mantenha segura** - não commite no Git

## 🔍 **VERIFICAR SE FUNCIONOU**

### **Logs do Heroku**
```bash
heroku logs --tail --app lvksistemas-app
```

### **Teste Manual**
1. Gere um boleto pelo sistema
2. Verifique se não há mais erro 400
3. Confirme se o PIX é gerado

## 📊 **RESULTADO ESPERADO**

Após configurar corretamente:

✅ **Conexão com API**: Estabelecida  
✅ **Criação de Cliente**: Funcionando  
✅ **Geração de Boleto**: Funcionando  
✅ **PIX Integrado**: QR Code + Copia e Cola  
✅ **Webhook**: Recebendo notificações  

## 🆘 **SE AINDA NÃO FUNCIONAR**

1. **Verifique** se a conta Asaas está ativa
2. **Confirme** se escolheu o ambiente correto (sandbox/produção)
3. **Teste** a API Key diretamente no Postman
4. **Contate** o suporte do Asaas: suporte@asaas.com

## 🎉 **RESUMO**

**Problema**: API Key inválida (UUID genérico)  
**Solução**: Configurar API Key real do Asaas  
**Resultado**: Sistema funcionando 100% com boletos e PIX  

---

**🔧 Execute os comandos acima e seu sistema estará funcionando perfeitamente!**