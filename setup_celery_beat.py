#!/usr/bin/env python3
"""
Script para configurar Celery Beat para processamento automático de notificações
"""

import os


def update_celery_config():
    """Atualiza configuração do Celery"""
    
    celery_file = 'lojad/celery.py'
    
    print("🔧 Atualizando configuração do Celery...")
    
    try:
        if os.path.exists(celery_file):
            with open(celery_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            # Criar arquivo básico do Celery
            content = '''import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

app = Celery('lojad')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
'''
        
        # Adicionar configuração do Beat se não existir
        beat_config = '''
# Celery Beat Configuration
app.conf.beat_schedule = {
    'processar-notificacoes-boleto': {
        'task': 'controle_financeiro.tasks.processar_notificacoes_boleto',
        'schedule': 60.0 * 60.0 * 24.0,  # Executar diariamente (24 horas)
        'options': {'queue': 'default'}
    },
}

app.conf.timezone = 'America/Sao_Paulo'
'''
        
        if 'beat_schedule' not in content:
            content += beat_config
        
        # Salvar arquivo
        with open(celery_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Configuração do Celery atualizada")
        return True
        
    except Exception as e:
        print(f"💥 Erro ao atualizar Celery: {str(e)}")
        return False


def update_settings():
    """Atualiza settings.py com configurações de email e Celery"""
    
    settings_file = 'lojad/settings.py'
    
    print("🔧 Verificando configurações no settings.py...")
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        additions = []
        
        # Verificar configurações de email
        if 'EMAIL_BACKEND' not in content:
            additions.append('''
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Configure conforme seu provedor
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'  # Configure seu email
EMAIL_HOST_PASSWORD = 'sua-senha-app'     # Configure sua senha de app
DEFAULT_FROM_EMAIL = 'Sistema LVK <seu-email@gmail.com>'
''')
        
        # Verificar configurações do Celery
        if 'CELERY_BROKER_URL' not in content:
            additions.append('''
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Configure conforme seu Redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
''')
        
        if additions:
            content += '\n'.join(additions)
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Configurações adicionadas ao settings.py")
            print("⚠️ IMPORTANTE: Configure EMAIL_HOST_USER e EMAIL_HOST_PASSWORD")
        else:
            print("✅ Configurações já existem no settings.py")
        
        return True
        
    except Exception as e:
        print(f"💥 Erro ao atualizar settings: {str(e)}")
        return False


def create_deployment_guide():
    """Cria guia de deploy para Heroku"""
    
    guide_content = '''# Guia de Deploy - Sistema de Notificações de Boleto

## Configurações Necessárias no Heroku

### 1. Variáveis de Ambiente

Configure as seguintes variáveis no Heroku:

```bash
# Email
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-gmail

# Redis (Heroku Redis addon)
REDIS_URL=redis://...  # Automaticamente configurado pelo addon

# Celery
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
```

### 2. Addons Necessários

```bash
# Redis para Celery
heroku addons:create heroku-redis:mini

# Scheduler para Celery Beat (alternativa)
heroku addons:create scheduler:standard
```

### 3. Procfile

Adicione ao seu Procfile:

```
web: gunicorn lojad.wsgi
worker: celery -A lojad worker --loglevel=info
beat: celery -A lojad beat --loglevel=info
```

### 4. Comandos de Deploy

```bash
# Deploy da aplicação
git add .
git commit -m "Implementar sistema de notificações de boleto"
git push heroku main

# Executar migrações
heroku run python manage.py migrate

# Testar comando de notificações
heroku run python manage.py processar_notificacoes_boleto --dry-run

# Escalar workers (se necessário)
heroku ps:scale worker=1 beat=1
```

### 5. Configuração de Email Gmail

1. Ative a verificação em 2 etapas na sua conta Gmail
2. Gere uma senha de app específica
3. Use essa senha na variável EMAIL_HOST_PASSWORD

### 6. Teste Local

```bash
# Instalar Redis localmente
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Iniciar Redis
redis-server

# Em terminais separados:
celery -A lojad worker --loglevel=info
celery -A lojad beat --loglevel=info

# Testar comando
python manage.py processar_notificacoes_boleto --dry-run
```

### 7. Monitoramento

```bash
# Ver logs do worker
heroku logs --tail --dyno=worker

# Ver logs do beat
heroku logs --tail --dyno=beat

# Ver logs da aplicação
heroku logs --tail --dyno=web
```

### 8. Alternativa com Heroku Scheduler

Se preferir usar o Heroku Scheduler em vez do Celery Beat:

1. Configure o addon: `heroku addons:create scheduler:standard`
2. Adicione job diário: `python manage.py processar_notificacoes_boleto`
3. Configure para executar às 09:00 UTC (06:00 BRT)

## Funcionalidades Implementadas

### ✅ Validação de Banco da Loja
- Impede geração de boletos se `db_name` da loja não estiver configurado
- Usa código único do banco na referência externa do boleto

### ✅ Sistema de Notificações por Email
- Envia PDF do boleto 10 dias antes do vencimento
- Template HTML responsivo
- Anexa PDF do boleto automaticamente

### ✅ Processamento Automático
- Task do Celery executa diariamente
- Comando Django para execução manual
- Modo dry-run para testes

### ✅ Integração com Asaas
- Usa `db_name` da loja na referência externa
- Validação antes da geração de boletos
- Sincronização bidirecional melhorada

## Comandos Úteis

```bash
# Processar notificações manualmente
python manage.py processar_notificacoes_boleto

# Modo teste (não envia emails)
python manage.py processar_notificacoes_boleto --dry-run

# Processar com antecedência diferente
python manage.py processar_notificacoes_boleto --dias 5

# Testar validação de banco
python test_bank_validation.py

# Verificar sincronização
python check_asaas_payments.py
```

## Troubleshooting

### Emails não são enviados
1. Verifique configurações de email no settings.py
2. Confirme senha de app do Gmail
3. Verifique logs: `heroku logs --tail`

### Celery não executa
1. Verifique se Redis está funcionando
2. Confirme configuração CELERY_BROKER_URL
3. Verifique se worker está rodando: `heroku ps`

### Boletos não são gerados
1. Verifique se loja tem `db_name` configurado
2. Confirme API key do Asaas
3. Teste validação: `python test_bank_validation.py`
'''
    
    with open('DEPLOY_GUIDE_NOTIFICATIONS.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📋 Guia de deploy criado: DEPLOY_GUIDE_NOTIFICATIONS.md")


def main():
    print("🚀 Configurando Celery Beat para processamento automático...")
    
    # Atualizar configuração do Celery
    if update_celery_config():
        print("✅ Celery configurado")
    
    # Atualizar settings
    if update_settings():
        print("✅ Settings verificado")
    
    # Criar guia de deploy
    create_deployment_guide()
    
    print("\n🎯 Configuração concluída!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("  1. Configure EMAIL_HOST_USER e EMAIL_HOST_PASSWORD no settings.py")
    print("  2. Instale Redis: sudo apt-get install redis-server")
    print("  3. Teste localmente: celery -A lojad worker --loglevel=info")
    print("  4. Teste comando: python manage.py processar_notificacoes_boleto --dry-run")
    print("  5. Para Heroku: siga o guia DEPLOY_GUIDE_NOTIFICATIONS.md")
    
    print("\n💡 SISTEMA COMPLETO IMPLEMENTADO:")
    print("  ✅ Validação de banco da loja")
    print("  ✅ Referência externa com código do banco")
    print("  ✅ Notificações por email automáticas")
    print("  ✅ Processamento via Celery")
    print("  ✅ Comandos de gerenciamento")
    print("  ✅ Templates HTML para emails")
    print("  ✅ Sincronização bidirecional")


if __name__ == '__main__':
    main()