# 📧 Sistema de Notificação por Email

## 🎯 **Funcionalidades Implementadas**

### ✅ **Notificações Automáticas**
- **Criação de Super Administrador** → Email com credenciais provisórias
- **Criação de Nova Loja** → Email com credenciais provisórias
- **Notificação para Admins** → Email informando sobre novas criações
- **Troca de Senha Obrigatória** → Email lembrando da necessidade

### ✅ **Segurança Implementada**
- **Senha Provisória** → Gerada automaticamente para novos usuários
- **Troca Obrigatória** → Usuário DEVE trocar senha no primeiro login
- **Middleware de Proteção** → Impede acesso até troca de senha
- **Logs de Segurança** → Registra todas as ações

## 🔧 **Configuração do Sistema**

### 1. **Variáveis de Ambiente**
Configure as seguintes variáveis no Heroku:

```bash
# Configurações de Email
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=seu-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=sua-senha-de-app
heroku config:set DEFAULT_FROM_EMAIL=noreply@lvksistemas.com.br
heroku config:set SITE_URL=https://lvksistemas.com.br
```

### 2. **Configuração do Gmail**
Para usar Gmail como servidor SMTP:

1. **Ative a verificação em 2 etapas** na sua conta Google
2. **Gere uma senha de app**:
   - Acesse: https://myaccount.google.com/security
   - Clique em "Senhas de app"
   - Gere uma nova senha para "Mail"
   - Use esta senha na variável `EMAIL_HOST_PASSWORD`

### 3. **Teste do Sistema**
```bash
# Testar envio de email para usuário
python manage.py testar_email --email=teste@exemplo.com --tipo=usuario

# Testar envio de email para loja
python manage.py testar_email --email=loja@exemplo.com --tipo=loja
```

## 📋 **Fluxo de Funcionamento**

### **Criação de Super Administrador**
1. ✅ Usuário é criado com senha provisória
2. ✅ Email é enviado automaticamente com credenciais
3. ✅ No primeiro login, usuário é obrigado a trocar senha
4. ✅ Após troca, usuário pode acessar o sistema normalmente

### **Criação de Nova Loja**
1. ✅ Loja é criada com usuário administrador
2. ✅ Email é enviado para o administrador da loja
3. ✅ Notificação é enviada para super administradores
4. ✅ Administrador da loja deve trocar senha no primeiro login

## 🎨 **Templates de Email**

### **Templates Criados:**
- `templates/emails/credenciais_usuario.html` - Credenciais para usuários
- `templates/emails/credenciais_loja.html` - Credenciais para lojas
- `templates/emails/notificacao_admin.html` - Notificações para admins
- `templates/emails/troca_senha_obrigatoria.html` - Lembrete de troca de senha

### **Características dos Templates:**
- ✅ **Design Responsivo** - Funciona em desktop e mobile
- ✅ **Visual Moderno** - Cores e ícones atrativos
- ✅ **Informações Completas** - Todas as credenciais necessárias
- ✅ **Instruções Claras** - Passo a passo para o usuário
- ✅ **Versão Texto** - Para clientes que não suportam HTML

## 🔒 **Segurança Implementada**

### **Controle de Senhas:**
- ✅ **Senhas Provisórias** - Geradas automaticamente (12 caracteres)
- ✅ **Troca Obrigatória** - Middleware impede acesso até troca
- ✅ **Logs de Segurança** - Registra todas as alterações
- ✅ **Validação de Senha** - Regras do Django para senhas seguras

### **Middleware de Proteção:**
- ✅ **Verificação Automática** - A cada requisição
- ✅ **Redirecionamento** - Para página de troca de senha
- ✅ **URLs Exemptas** - Login, logout, admin, etc.
- ✅ **Mensagens de Aviso** - Informa o usuário sobre a obrigatoriedade

## 📊 **Monitoramento e Logs**

### **Logs Implementados:**
- ✅ **Criação de Usuários** - Log de emails enviados
- ✅ **Criação de Lojas** - Log de notificações
- ✅ **Troca de Senhas** - Log de alterações
- ✅ **Erros de Email** - Log de falhas no envio

### **Verificação de Status:**
```bash
# Verificar logs do sistema
heroku logs --tail

# Verificar configurações de email
heroku config | grep EMAIL
```

## 🚀 **Deploy e Ativação**

### **1. Fazer Deploy:**
```bash
git add .
git commit -m "feat: Implementar sistema de notificação por email"
git push heroku main
```

### **2. Configurar Variáveis:**
```bash
# Configurar email no Heroku
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=seu-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=sua-senha-de-app
heroku config:set DEFAULT_FROM_EMAIL=noreply@lvksistemas.com.br
heroku config:set SITE_URL=https://lvksistemas.com.br
```

### **3. Testar Sistema:**
```bash
# Testar no Heroku
heroku run python manage.py testar_email --email=teste@exemplo.com --tipo=usuario
```

## 🎯 **Resultado Final**

### **Sistema Completo Ativo:**
- ✅ **Emails Automáticos** - Enviados na criação de usuários/lojas
- ✅ **Segurança Máxima** - Troca obrigatória de senha
- ✅ **Templates Profissionais** - Visual moderno e informativo
- ✅ **Monitoramento** - Logs completos de todas as ações
- ✅ **Configuração Simples** - Variáveis de ambiente no Heroku

**🎉 O sistema de notificação por email está 100% funcional e pronto para uso!**
