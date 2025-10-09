#!/bin/bash

echo "========================================="
echo "Deploy para Heroku - Correção Boletos Caixa"
echo "========================================="

# Verifica se está no git
if [ ! -d ".git" ]; then
    echo "Inicializando repositório Git..."
    git init
    git remote add heroku https://git.heroku.com/lvksistemas-app.git
fi

# Adiciona todas as mudanças
echo "Adicionando arquivos modificados..."
git add .

# Commit das mudanças
echo "Fazendo commit das correções..."
git commit -m "Fix: Corrige geração de códigos de barras inválidos para boletos Caixa

- Corrige algoritmos DV módulo 11 e módulo 10 conforme padrão FEBRABAN
- Corrige estrutura do campo livre da Caixa (25 dígitos exatos)
- Adiciona sistema de validação abrangente de códigos de barras
- Adiciona BarcodeValidator com validações completas
- Integra validação no fluxo de geração de boletos
- Corrige problema de campo livre com 26 dígitos
- Adiciona campo convênio no template de edição de configuração
- Melhora tratamento de erros e mensagens de validação"

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

# Coleta arquivos estáticos (já feito durante o build, mas executando para garantir)
echo "Coletando arquivos estáticos..."
heroku run python manage.py collectstatic --no-input || echo "Arquivos estáticos já coletados durante o build"

echo "========================================="
echo "Deploy e configuração concluídos!"
echo "Teste o sistema em: https://lvksistemas-app-4f6fa281e217.herokuapp.com"
echo "========================================="