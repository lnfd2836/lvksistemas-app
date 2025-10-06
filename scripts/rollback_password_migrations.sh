#!/bin/bash

# Script de rollback para migrações de senha
# ATENÇÃO: Use apenas em caso de emergência

APP_NAME=${1:-"seu-app-heroku"}
BACKUP_SUFFIX=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "ROLLBACK DE MIGRAÇÕES DE SENHA"
echo "App: $APP_NAME"
echo "Backup suffix: $BACKUP_SUFFIX"
echo "=========================================="
echo ""
echo "⚠️  ATENÇÃO: Este script irá reverter as migrações de senha!"
echo "⚠️  Certifique-se de ter um backup da base de dados!"
echo ""

# Confirmação do usuário
read -p "Tem certeza que deseja continuar? (digite 'CONFIRMO' para prosseguir): " confirmation

if [ "$confirmation" != "CONFIRMO" ]; then
    echo "Operação cancelada."
    exit 1
fi

echo ""
echo "1. Criando backup da base de dados..."

# Criar backup (PostgreSQL)
heroku pg:backups:capture --app $APP_NAME
if [ $? -eq 0 ]; then
    echo "✅ Backup criado com sucesso"
else
    echo "❌ Falha ao criar backup"
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "2. Verificando estado atual das migrações..."
heroku run python manage.py showmigrations usuarios --app $APP_NAME

echo ""
echo "3. Executando rollback da migração 0005..."

# Reverter para a migração anterior
heroku run python manage.py migrate usuarios 0004 --app $APP_NAME

if [ $? -eq 0 ]; then
    echo "✅ Rollback da migração executado"
else
    echo "❌ Falha no rollback da migração"
    echo "Tentando rollback manual..."
    
    # Rollback manual via SQL
    echo ""
    echo "4. Executando rollback manual via SQL..."
    
    heroku pg:psql --app $APP_NAME << 'EOF'
-- Remover colunas de gestão de senha
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS requires_password_change;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS provisional_password_created;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_changed_at;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_change_reminders_sent;

-- Verificar se as colunas foram removidas
\d usuarios_perfilusuario;
EOF

    if [ $? -eq 0 ]; then
        echo "✅ Rollback manual executado"
    else
        echo "❌ Falha no rollback manual"
        echo "Intervenção manual necessária!"
        exit 1
    fi
fi

echo ""
echo "5. Verificando estado após rollback..."
heroku run python manage.py showmigrations usuarios --app $APP_NAME

echo ""
echo "6. Testando acesso à base de dados..."
heroku run python manage.py shell --app $APP_NAME << 'EOF'
from usuarios.models import PerfilUsuario
try:
    count = PerfilUsuario.objects.count()
    print(f"✅ Acesso ao modelo PerfilUsuario OK - {count} registros")
except Exception as e:
    print(f"❌ Erro ao acessar PerfilUsuario: {e}")

# Testar se as colunas foram removidas
try:
    PerfilUsuario.objects.filter(requires_password_change=True).count()
    print("❌ Coluna requires_password_change ainda existe!")
except Exception as e:
    print("✅ Coluna requires_password_change removida com sucesso")
EOF

echo ""
echo "7. Reiniciando aplicação..."
heroku restart --app $APP_NAME

echo ""
echo "8. Verificando logs para erros..."
sleep 10
heroku logs --num 50 --app $APP_NAME | grep -i error

echo ""
echo "=========================================="
echo "ROLLBACK CONCLUÍDO"
echo "=========================================="
echo ""
echo "PRÓXIMOS PASSOS:"
echo "1. Monitore os logs: heroku logs --tail --app $APP_NAME"
echo "2. Teste a aplicação manualmente"
echo "3. Se necessário, desative o middleware de senha temporariamente"
echo "4. Considere aplicar uma correção alternativa"
echo ""
echo "PARA RESTAURAR BACKUP (se necessário):"
echo "heroku pg:backups:restore --app $APP_NAME"