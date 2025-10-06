#!/bin/bash

# Script de inicialização do Sistema de Gerenciamento de Lojas

echo "========================================="
echo "Sistema de Gerenciamento de Lojas"
echo "Inicializando..."
echo "========================================="

# Ativa o ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "Ambiente virtual não encontrado!"
    echo "Execute: python3 -m venv venv"
    exit 1
fi

# Verifica se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "Arquivo .env não encontrado!"
    echo "Copiando arquivo de exemplo..."
    cp env_example.txt .env
    echo "Por favor, configure o arquivo .env antes de continuar."
    exit 1
fi

# Executa as migrações
echo "Executando migrações..."
python manage.py migrate

# Cria diretórios necessários
echo "Criando diretórios necessários..."
mkdir -p logs media staticfiles backups

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Pergunta se quer criar um super usuário
read -p "Deseja criar um super usuário? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]
then
    python manage.py createsuperuser
fi

# Inicia o servidor
echo "========================================="
echo "Iniciando servidor de desenvolvimento..."
echo "Acesse: http://127.0.0.1:8000"
echo "========================================="
python manage.py runserver





