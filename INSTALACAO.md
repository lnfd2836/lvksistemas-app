# Guia de Instalação - Sistema de Gerenciamento de Lojas

Este guia irá ajudá-lo a configurar e executar o sistema de gerenciamento de lojas.

## Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- Redis (opcional, para cache e tarefas assíncronas)

## Instalação Passo a Passo

### 1. Configurar o Ambiente Virtual

```bash
# Navegue até o diretório do projeto
cd /home/felix/Documentos/lojad

# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar o Banco de Dados PostgreSQL

```bash
# Entre no PostgreSQL como superusuário
sudo -u postgres psql

# Crie o banco de dados e usuário
CREATE DATABASE lojad_main;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE lojad_main TO postgres;

# Saia do PostgreSQL
\q
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp env_example.txt .env
```

Edite o arquivo `.env` com suas configurações:

```env
SECRET_KEY=sua-chave-secreta-gerada-aqui
DEBUG=True
DB_NAME=lojad_main
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### 5. Executar Migrações

```bash
# Criar as migrações
python manage.py makemigrations

# Aplicar as migrações
python manage.py migrate

# Configurar extensões do banco
python manage.py configurar_banco
```

### 6. Criar Super Usuário

```bash
python manage.py createsuperuser
```

Ou usando o comando customizado:

```bash
python manage.py criar_superuser --username admin --email admin@example.com --password admin123 --first-name Admin --last-name Sistema
```

### 7. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Executar o Servidor

```bash
python manage.py runserver
```

O sistema estará disponível em: http://127.0.0.1:8000

### 9. Acessar o Sistema

- **URL:** http://127.0.0.1:8000
- **Login:** Use as credenciais do super usuário criado
- **Admin Django:** http://127.0.0.1:8000/admin

## Instalação com Docker (Alternativa)

### Desenvolvimento

```bash
# Construir e iniciar os containers
docker-compose -f docker-compose.dev.yml up --build

# Executar migrações
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# Criar super usuário
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

### Produção

```bash
# Construir e iniciar os containers
docker-compose up --build -d

# Executar migrações
docker-compose exec web python manage.py migrate

# Criar super usuário
docker-compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

## Tarefas Assíncronas (Celery)

Para usar as funcionalidades de backup automático e outras tarefas assíncronas:

### Terminal 1 - Worker

```bash
celery -A lojad worker --loglevel=info
```

### Terminal 2 - Beat (Agendador)

```bash
celery -A lojad beat --loglevel=info
```

### Com Docker

Os containers de Celery já estão configurados e serão iniciados automaticamente.

## Comandos Úteis

### Criar uma Nova Loja

```bash
python manage.py criar_loja \
  --nome "Minha Loja" \
  --cnpj "12.345.678/0001-90" \
  --email "loja@exemplo.com" \
  --telefone "(11) 99999-9999" \
  --endereco "Rua Exemplo, 123" \
  --cidade "São Paulo" \
  --estado "SP" \
  --cep "01234-567"
```

### Criar Backup

```bash
# Backup de uma loja específica
python manage.py backup_loja --loja-id <uuid-da-loja>

# Backup de todas as lojas
python manage.py backup_loja --todas
```

### Estatísticas do Sistema

```bash
python manage.py estatisticas_sistema
```

### Otimizar Sistema

```bash
# Otimizar todas as lojas
python manage.py otimizar_sistema --todas

# Otimizar loja específica
python manage.py otimizar_sistema --loja-id <uuid-da-loja>
```

### Limpar Dados Antigos

```bash
python manage.py limpar_sistema --dias 90 --confirmar
```

### Exportar Dados

```bash
# Exportar lojas
python manage.py exportar_dados --tipo lojas --arquivo lojas.csv

# Exportar clientes de uma loja
python manage.py exportar_dados --tipo clientes --loja-id <uuid> --arquivo clientes.csv

# Exportar produtos
python manage.py exportar_dados --tipo produtos --arquivo produtos.csv

# Exportar vendas
python manage.py exportar_dados --tipo vendas --arquivo vendas.csv
```

## Solução de Problemas

### Erro de Conexão com o Banco de Dados

1. Verifique se o PostgreSQL está rodando:
```bash
sudo systemctl status postgresql
```

2. Verifique as credenciais no arquivo `.env`

3. Teste a conexão:
```bash
psql -h localhost -U postgres -d lojad_main
```

### Erro de Importação de Módulos

1. Certifique-se de que o ambiente virtual está ativado
2. Reinstale as dependências:
```bash
pip install -r requirements.txt --force-reinstall
```

### Problemas com Redis

Se não estiver usando Redis, você pode desabilitar o cache no `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

## Primeiros Passos Após Instalação

1. **Acesse o sistema** em http://127.0.0.1:8000
2. **Faça login** com o super usuário criado
3. **Crie sua primeira loja** através do menu "Lojas > Nova Loja"
4. **Configure os dados** da loja (clientes, produtos)
5. **Explore o dashboard** e suas funcionalidades

## Suporte

Para questões técnicas ou problemas, consulte a documentação ou entre em contato com o suporte técnico.

## Próximos Passos

- Configure o email para notificações
- Configure backups automáticos
- Personalize as configurações para produção
- Configure SSL/HTTPS para produção
- Configure firewall e segurança



