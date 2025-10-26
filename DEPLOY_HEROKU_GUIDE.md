# Guia de Deploy para Heroku - LVK Sistemas

## 🚀 Deploy Automatizado

### Opção 1: Script Automatizado (Recomendado)

```bash
# Executar script de deploy
python deploy_heroku.py
```

O script irá:
- ✅ Verificar Heroku CLI
- ✅ Verificar status do Git
- ✅ Configurar app Heroku
- ✅ Configurar variáveis de ambiente
- ✅ Configurar banco PostgreSQL
- ✅ Fazer deploy
- ✅ Executar migrações
- ✅ Configurar isolamento de lojas

## 🔧 Deploy Manual

### 1. Pré-requisitos

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Fazer login
heroku login

# Verificar se está logado
heroku auth:whoami
```

### 2. Criar App Heroku

```bash
# Criar novo app (nome será gerado automaticamente)
heroku create

# OU criar com nome específico
heroku create meu-app-lvk

# OU usar app existente
heroku git:remote -a meu-app-existente
```

### 3. Configurar Variáveis de Ambiente

```bash
# Variáveis obrigatórias
heroku config:set SECRET_KEY="sua-chave-secreta-muito-longa-e-segura"
heroku config:set DEBUG=False
heroku config:set ASAAS_API_KEY="sua-chave-asaas"
heroku config:set ASAAS_ENVIRONMENT="production"  # ou "sandbox"

# Email (opcional mas recomendado)
heroku config:set EMAIL_HOST_USER="seu-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="sua-senha-app"
heroku config:set DEFAULT_FROM_EMAIL="noreply@seudominio.com"

# Configurações automáticas (o Heroku define)
# DATABASE_URL - Configurado automaticamente pelo PostgreSQL
# SITE_URL - Será https://seu-app.herokuapp.com
```

### 4. Configurar Banco de Dados

```bash
# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:mini

# Verificar se foi criado
heroku addons
```

### 5. Deploy

```bash
# Fazer commit das mudanças
git add .
git commit -m "Deploy para Heroku"

# Push para Heroku
git push heroku main
# OU se sua branch principal é master:
git push heroku master
```

### 6. Configurações Pós-Deploy

```bash
# Executar migrações
heroku run python manage.py migrate

# Coletar arquivos estáticos
heroku run python manage.py collectstatic --noinput

# Criar superusuário
heroku run python manage.py createsuperuser

# Configurar isolamento de lojas
heroku run python manage.py setup_isolamento --setup
```

## 🔍 Verificação e Monitoramento

### Verificar Deploy

```bash
# Abrir app no navegador
heroku open

# Ver logs em tempo real
heroku logs --tail

# Ver logs específicos
heroku logs --tail --source app

# Status do app
heroku ps
```

### URLs Importantes

```
App Principal: https://seu-app.herokuapp.com
Admin: https://seu-app.herokuapp.com/admin/
Dashboard: https://seu-app.herokuapp.com/dashboard/
Login Personalizado: https://seu-app.herokuapp.com/login/{loja_url}/
```

### Comandos Úteis

```bash
# Reiniciar app
heroku restart

# Executar comandos no servidor
heroku run python manage.py shell

# Ver configurações
heroku config

# Escalar dynos (se necessário)
heroku ps:scale web=1
```

## 🛠️ Troubleshooting

### Problemas Comuns

#### 1. Erro de SECRET_KEY
```bash
# Gerar nova chave secreta
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configurar no Heroku
heroku config:set SECRET_KEY="nova-chave-gerada"
```

#### 2. Erro de Banco de Dados
```bash
# Verificar se PostgreSQL está ativo
heroku addons

# Executar migrações novamente
heroku run python manage.py migrate

# Reset do banco (CUIDADO!)
heroku pg:reset DATABASE_URL --confirm seu-app
heroku run python manage.py migrate
```

#### 3. Erro de Arquivos Estáticos
```bash
# Coletar arquivos estáticos
heroku run python manage.py collectstatic --noinput

# Verificar configuração do WhiteNoise
heroku logs --tail | grep -i static
```

#### 4. Erro de Isolamento de Lojas
```bash
# Configurar isolamento
heroku run python manage.py setup_isolamento --setup

# Validar isolamento
heroku run python manage.py setup_isolamento --validate

# Ver status
heroku run python manage.py setup_isolamento --status
```

### Logs Importantes

```bash
# Logs gerais
heroku logs --tail

# Logs de erro
heroku logs --tail | grep -i error

# Logs de uma app específica
heroku logs --tail --app seu-app

# Logs de deploy
heroku releases
heroku releases:output v123  # substituir pelo número da versão
```

## 🔒 Segurança em Produção

### Variáveis Obrigatórias

```bash
# Sempre configurar em produção
DEBUG=False
SECRET_KEY="chave-muito-longa-e-aleatoria"
ALLOWED_HOSTS="seu-app.herokuapp.com"

# Para HTTPS (Heroku configura automaticamente)
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
```

### Monitoramento

```bash
# Verificar saúde do app
heroku ps

# Métricas (se disponível)
heroku logs --tail | grep -E "(ERROR|WARNING|CRITICAL)"

# Status do banco
heroku pg:info
```

## 📊 Configurações Específicas do Sistema

### Isolamento de Lojas

O sistema usa bancos separados por loja. Após o deploy:

1. **Configurar isolamento inicial:**
   ```bash
   heroku run python manage.py setup_isolamento --setup
   ```

2. **Para cada nova loja criada:**
   ```bash
   heroku run python manage.py setup_isolamento --setup --loja-id ID_DA_LOJA
   ```

3. **Validar isolamento:**
   ```bash
   heroku run python manage.py setup_isolamento --validate
   ```

### Login Personalizado

Cada loja terá sua URL de login:
- `https://seu-app.herokuapp.com/login/loja1/`
- `https://seu-app.herokuapp.com/login/loja2/`

### Webhooks Asaas

Configure no painel Asaas:
- URL: `https://seu-app.herokuapp.com/financeiro/asaas/webhook/`
- Eventos: Todos relacionados a pagamentos

## 🎯 Checklist de Deploy

### Antes do Deploy
- [ ] Todas as mudanças commitadas
- [ ] Variáveis de ambiente configuradas
- [ ] Heroku CLI instalado e logado
- [ ] App Heroku criado

### Durante o Deploy
- [ ] Push para Heroku executado
- [ ] Build bem-sucedido
- [ ] Release executado sem erros

### Após o Deploy
- [ ] App acessível no navegador
- [ ] Admin funcionando
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Isolamento configurado
- [ ] Logs sem erros críticos

### Testes Finais
- [ ] Login de super admin funciona
- [ ] Login personalizado por loja funciona
- [ ] Dashboard carrega corretamente
- [ ] Isolamento de dados funcionando
- [ ] Webhooks Asaas configurados (se aplicável)

## 📞 Suporte

Em caso de problemas:

1. **Verificar logs:** `heroku logs --tail`
2. **Verificar status:** `heroku ps`
3. **Executar diagnósticos:** `heroku run python manage.py check`
4. **Validar isolamento:** `heroku run python manage.py setup_isolamento --validate`

## 🔄 Atualizações Futuras

Para atualizações do sistema:

```bash
# Fazer mudanças no código
git add .
git commit -m "Descrição das mudanças"

# Deploy da atualização
git push heroku main

# Se houver novas migrações
heroku run python manage.py migrate

# Se houver mudanças no isolamento
heroku run python manage.py setup_isolamento --setup
```

---

**🎉 Parabéns! Seu sistema LVK está rodando no Heroku com isolamento completo por loja!**