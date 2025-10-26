# 🔐 Comandos para Resetar Admin no Heroku

## 🚨 PROBLEMA IDENTIFICADO
Pelos logs, o login está falhando no Heroku:
```
WARNING Tentativa de login falhada para username/email: admin
```

## 🔧 SOLUÇÕES IMEDIATAS

### 1️⃣ **Comando Mais Simples (Recomendado)**
```bash
heroku run python heroku_reset_admin.py
```

### 2️⃣ **Comando Django Management**
```bash
heroku run python manage.py reset_heroku_admin --create-all
```

### 3️⃣ **Resetar Usuário Específico**
```bash
heroku run python manage.py reset_heroku_admin --username admin --password "MinhaNovaSenh@123"
```

### 4️⃣ **Comando Shell Direto**
```bash
heroku run python manage.py shell -c "
from django.contrib.auth.models import User
user, created = User.objects.get_or_create(username='admin')
user.set_password('Admin@LVK2024!')
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.email = 'admin@lvksistemas.com.br'
user.save()
print('✅ Admin resetado!')
print('👤 Username: admin')
print('🔑 Password: Admin@LVK2024!')
"
```

## 🎯 **CREDENCIAIS APÓS RESET**

### Opção Principal:
```
👤 Username: admin
🔑 Password: Admin@LVK2024!
📧 Email: admin@lvksistemas.com.br
```

### Opções Alternativas:
```
👤 Username: superadmin
🔑 Password: SuperAdmin@LVK2024!

👤 Username: luiz  
🔑 Password: Luiz@LVK2024!
```

## 🌐 **URLs de Acesso**

### Login Principal:
```
🔗 https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/
```

### Admin Django:
```
🔗 https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/
```

## 🧪 **Testar Após Reset**

### 1. Verificar se usuário existe:
```bash
heroku run python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
print(f'Ativo: {user.is_active}')
print(f'Superuser: {user.is_superuser}')
print(f'Email: {user.email}')
"
```

### 2. Testar autenticação:
```bash
heroku run python manage.py shell -c "
from django.contrib.auth import authenticate
user = authenticate(username='admin', password='Admin@LVK2024!')
print('✅ Login OK' if user else '❌ Login falhou')
"
```

### 3. Listar todos os superusuários:
```bash
heroku run python manage.py shell -c "
from django.contrib.auth.models import User
for user in User.objects.filter(is_superuser=True):
    print(f'{user.username} | {user.email} | Ativo: {user.is_active}')
"
```

## 🔄 **Sequência Recomendada**

Execute os comandos nesta ordem:

```bash
# 1. Resetar admin
heroku run python heroku_reset_admin.py

# 2. Verificar se funcionou
heroku run python manage.py shell -c "
from django.contrib.auth import authenticate
user = authenticate(username='admin', password='Admin@LVK2024!')
print('✅ Pronto para usar!' if user else '❌ Ainda com problema')
"

# 3. Testar no navegador
# Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/
# Use: admin / Admin@LVK2024!
```

## 🚨 **Se Ainda Não Funcionar**

### Opção A - Criar novo admin:
```bash
heroku run python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.filter(username='admin').delete()
user = User.objects.create_superuser('admin', 'admin@lvk.com', 'NovaSenh@123')
print('✅ Novo admin criado!')
print('👤 admin / NovaSenh@123')
"
```

### Opção B - Usar admin Django:
```bash
# Acesse diretamente o admin Django:
# https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/
# Use qualquer uma das credenciais resetadas
```

### Opção C - Verificar logs:
```bash
heroku logs --tail | grep -i login
```

## 💡 **DICAS IMPORTANTES**

1. **Sempre use aspas** nas senhas com caracteres especiais
2. **Teste no shell** antes de tentar no navegador  
3. **Limpe cache** do navegador se necessário
4. **Use modo incógnito** para testar login
5. **Verifique se não há middleware** bloqueando login

## 🎯 **RESULTADO ESPERADO**

Após executar os comandos, você deve conseguir:
- ✅ Fazer login com `admin / Admin@LVK2024!`
- ✅ Acessar dashboard de super admin
- ✅ Ver as 6 cobranças sincronizadas
- ✅ Gerenciar sistema completo

Execute o **Comando 1** primeiro e teste!