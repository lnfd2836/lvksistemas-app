# ✅ Checklist Pré-Deploy Heroku

## 📋 Verificações Obrigatórias

### 1. **Arquivos de Deploy**
- [x] `Procfile` - Configurado com gunicorn
- [x] `requirements.txt` - Todas as dependências listadas
- [x] `runtime.txt` - Python 3.11.9 (compatível com Heroku)
- [x] `deploy_heroku_final.sh` - Script de deploy atualizado

### 2. **Configurações Django**
- [x] `DEBUG=False` em produção (via variável de ambiente)
- [x] `ALLOWED_HOSTS` inclui domínio do Heroku
- [x] `dj_database_url` configurado para PostgreSQL
- [x] `whitenoise` para arquivos estáticos
- [x] `SECRET_KEY` via variável de ambiente

### 3. **Correções Implementadas**
- [x] ✅ **BoletoCaixaService** - Algoritmos DV corrigidos
- [x] ✅ **BarcodeValidator** - Sistema de validação completo
- [x] ✅ **Fator de vencimento** - Limitado a 4 dígitos (padrão FEBRABAN)
- [x] ✅ **Campo livre** - Estrutura correta 25 dígitos
- [x] ✅ **Templates** - Quebras de linha corrigidas
- [x] ✅ **Configuração Caixa** - Nome e carteira corretos
- [x] ✅ **Validação automática** - Integrada no fluxo de geração

### 4. **Variáveis de Ambiente Heroku**
Configurar no Heroku Dashboard ou via CLI:

```bash
# Configurações básicas
heroku config:set SECRET_KEY="sua-chave-secreta-aqui" --app lvksistemas-app
heroku config:set DEBUG=False --app lvksistemas-app

# Email (se necessário)
heroku config:set EMAIL_HOST_USER="seu-email@gmail.com" --app lvksistemas-app
heroku config:set EMAIL_HOST_PASSWORD="sua-senha-app" --app lvksistemas-app
```

### 5. **Banco de Dados**
- [x] PostgreSQL será provisionado automaticamente pelo Heroku
- [x] Migrações serão executadas via `release` no Procfile
- [x] Comando `verificar_boletos` disponível para diagnóstico

## 🚀 Comandos de Deploy

### Deploy Completo:
```bash
./deploy_heroku_final.sh
```

### Deploy Manual (se necessário):
```bash
# 1. Commit das mudanças
git add .
git commit -m "Deploy: Correções sistema boletos"

# 2. Push para Heroku
git push heroku main

# 3. Executar migrações
heroku run python manage.py migrate --app lvksistemas-app

# 4. Verificar status
heroku ps --app lvksistemas-app
```

## 🔧 Comandos Pós-Deploy

### Verificar Boletos:
```bash
# Verificar configurações e boletos existentes
heroku run python manage.py verificar_boletos --app lvksistemas-app

# Validar códigos de barras existentes
heroku run python manage.py verificar_boletos --validate --app lvksistemas-app

# Corrigir problemas automaticamente
heroku run python manage.py verificar_boletos --fix --app lvksistemas-app
```

### Monitoramento:
```bash
# Logs em tempo real
heroku logs --tail --app lvksistemas-app

# Status da aplicação
heroku ps --app lvksistemas-app

# Abrir aplicação
heroku open --app lvksistemas-app
```

## 🎯 URLs Importantes

- **Aplicação**: https://lvksistemas-app-4f6fa281e217.herokuapp.com
- **Dashboard Heroku**: https://dashboard.heroku.com/apps/lvksistemas-app
- **Configuração Boletos**: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/boletos/configurar/

## ⚠️ Pontos de Atenção

1. **Primeira execução**: Pode demorar alguns minutos para inicializar
2. **Banco de dados**: Será criado vazio - precisará configurar usuários e dados
3. **Arquivos de mídia**: Heroku não persiste uploads - considere usar AWS S3
4. **Logs**: Heroku mantém apenas logs recentes - configure logging externo se necessário

## 🔍 Testes Pós-Deploy

### 1. Teste Básico:
- [ ] Aplicação carrega sem erros
- [ ] Login funciona
- [ ] Dashboard acessível

### 2. Teste Boletos:
- [ ] Configuração da Caixa funciona
- [ ] Geração de boleto produz código válido
- [ ] Validação automática funciona
- [ ] Linha digitável está correta

### 3. Teste Funcionalidades:
- [ ] Criação de lojas
- [ ] Controle financeiro
- [ ] Relatórios básicos

## 🆘 Troubleshooting

### Erro de Deploy:
```bash
# Ver logs detalhados
heroku logs --tail --app lvksistemas-app

# Reiniciar aplicação
heroku restart --app lvksistemas-app
```

### Erro de Banco:
```bash
# Executar migrações manualmente
heroku run python manage.py migrate --app lvksistemas-app

# Verificar status do banco
heroku pg:info --app lvksistemas-app
```

### Erro de Configuração:
```bash
# Ver variáveis de ambiente
heroku config --app lvksistemas-app

# Acessar shell Django
heroku run python manage.py shell --app lvksistemas-app
```