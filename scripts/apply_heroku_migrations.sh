#!/bin/bash

# Script para aplicar migrações no Heroku
# Este script deve ser executado localmente para aplicar migrações no ambiente de produção

APP_NAME="your-heroku-app-name"  # Substitua pelo nome real do app

echo "=========================================="
echo "APLICANDO MIGRAÇÕES NO HEROKU"
echo "=========================================="

echo "1. Verificando status atual das migrações..."
heroku run python manage.py check_migrations --app $APP_NAME

echo ""
echo "2. Verificando migrações pendentes..."
heroku run python manage.py showmigrations --plan --app $APP_NAME

echo ""
echo "3. Aplicando migrações de forma segura..."
heroku run python manage.py apply_password_migrations --app $APP_NAME

echo ""
echo "4. Verificando schema após migração..."
heroku run python manage.py verify_schema --app usuarios --model PerfilUsuario --app $APP_NAME

echo ""
echo "5. Testando acesso aos campos de senha..."
heroku run python manage.py shell --app $APP_NAME << 'EOF'
from usuarios.models import PerfilUsuario
print("Testando acesso aos campos...")
try:
    count = PerfilUsuario.objects.filter(requires_password_change=True).count()
    print(f"✅ requires_password_change acessível - {count} registros")
except Exception as e:
    print(f"❌ Erro ao acessar requires_password_change: {e}")

try:
    count = PerfilUsuario.objects.filter(password_change_reminders_sent=0).count()
    print(f"✅ password_change_reminders_sent acessível - {count} registros")
except Exception as e:
    print(f"❌ Erro ao acessar password_change_reminders_sent: {e}")

print("Teste concluído!")
EOF

echo ""
echo "=========================================="
echo "MIGRAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "Para monitorar logs em tempo real:"
echo "heroku logs --tail --app $APP_NAME"
echo ""
echo "Para verificar se os erros de coluna foram resolvidos:"
echo "heroku logs --app $APP_NAME | grep 'requires_password_change'"