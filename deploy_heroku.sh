#!/bin/bash

echo "========================================="
echo "Deploy para Heroku - Correção Redirect Loop"
echo "========================================="

# Verifica se está no git
if [ ! -d ".git" ]; then
    echo "Inicializando repositório Git..."
    git init
    git remote add heroku https://git.heroku.com/lvksistemas-app-4f6fa281e217.git
fi

# Adiciona todas as mudanças
echo "Adicionando arquivos modificados..."
git add .

# Commit das mudanças
echo "Fazendo commit das correções..."
git commit -m "Fix: Corrige redirect loop entre /dashboard/ e /login/

- Melhora middleware SessaoUnicaMiddleware para evitar loops
- Adiciona criação automática de sessão quando necessário
- Corrige view de login para gerenciar sessões corretamente
- Adiciona comando para limpar sessões problemáticas"

# Push para o Heroku
echo "Fazendo deploy para o Heroku..."
git push heroku main

echo "========================================="
echo "Deploy concluído!"
echo "Executando comandos pós-deploy..."
echo "========================================="

# Executa migrações
echo "Executando migrações..."
heroku run python manage.py migrate

# Limpa sessões problemáticas
echo "Limpando sessões problemáticas..."
heroku run python manage.py limpar_sessoes

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
heroku run python manage.py collectstatic --noinput

echo "========================================="
echo "Deploy e configuração concluídos!"
echo "Teste o sistema em: https://lvksistemas-app-4f6fa281e217.herokuapp.com"
echo "========================================="